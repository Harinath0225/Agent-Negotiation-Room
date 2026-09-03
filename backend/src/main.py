import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.db import engine, Base, SessionLocal
from src.models.schema import DealRecord, UISchema
from src.api.schema_routes import router as schema_router
from src.api.simulation_routes import router as simulation_router
from src.api.contract_routes import router as contract_router
from src.api.mcp_proxy_routes import router as mcp_proxy_router
from src.mcp.server import mcp_server

def seed_database():
    """Seed initial UI schemas from seed files or update when a newer seed version exists."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        seeds_dir = os.path.join(current_dir, "seeds")
        
        # Seed or upgrade deal_room.json (Published default)
        deal_room_path = os.path.join(seeds_dir, "deal_room.json")
        if os.path.exists(deal_room_path):
            with open(deal_room_path, "r", encoding="utf-8") as f:
                deal_data = json.load(f)
                schema_id = deal_data.get("id", "deal_room_v1")
                seed_version = deal_data.get("version", 1)
                existing = db.query(UISchema).filter(UISchema.id == schema_id).first()
                if not existing:
                    deal_schema = UISchema(
                        id=schema_id,
                        version=seed_version,
                        layout=deal_data.get("layout", {}),
                        is_published=True
                    )
                    db.add(deal_schema)
                    print(f"[INFO] Seeded default deal room schema (v{seed_version}).")
                elif existing.version <= seed_version:
                    existing.version = seed_version
                    existing.layout = deal_data.get("layout", {})
                    existing.is_published = True
                    print(f"[INFO] Synced deal room schema layout to v{seed_version}.")
        
        # Seed admin_studio.json if missing
        admin_path = os.path.join(seeds_dir, "admin_studio.json")
        if os.path.exists(admin_path):
            with open(admin_path, "r", encoding="utf-8") as f:
                admin_data = json.load(f)
                admin_id = admin_data.get("id", "admin_studio_v1")
                if not db.query(UISchema).filter(UISchema.id == admin_id).first():
                    admin_schema = UISchema(
                        id=admin_id,
                        version=admin_data.get("version", 1),
                        layout=admin_data.get("layout", {}),
                        is_published=False
                    )
                    db.add(admin_schema)

        sample_deals = [
            DealRecord(id="deal_1042", contract_id="1042-B", title="Enterprise Cloud Migration Service Agreement", counterparty="Apex Global Enterprise", status="Under Negotiation", annual_value=120000, liability_cap="2.0x", updated_at="2026-09-03T09:30:00Z"),
            DealRecord(id="deal_0987", contract_id="0987-A", title="Managed Security Operations Agreement", counterparty="Northstar Financial", status="Approved", annual_value=280000, liability_cap="1.5x", updated_at="2026-08-28T14:15:00Z"),
            DealRecord(id="deal_0764", contract_id="0764-C", title="Data Platform Modernization SOW", counterparty="Cobalt Logistics", status="Closed", annual_value=185000, liability_cap="2.0x", updated_at="2026-08-11T16:45:00Z"),
            DealRecord(id="deal_0521", contract_id="0521-D", title="Customer Analytics Subscription", counterparty="Meridian Health", status="Rejected", annual_value=96000, liability_cap="1.0x", updated_at="2026-07-29T11:20:00Z"),
            DealRecord(id="deal_1120", contract_id="1120-E", title="Global AI Infrastructure Licensing Agreement", counterparty="Aether Dynamics", status="Approved", annual_value=450000, liability_cap="2.5x", updated_at="2026-09-01T10:00:00Z"),
            DealRecord(id="deal_1088", contract_id="1088-F", title="Autonomous Workflow Integration SOW", counterparty="Vanguard Retail Systems", status="Under Negotiation", annual_value=75000, liability_cap="1.5x", updated_at="2026-09-02T16:20:00Z"),
            DealRecord(id="deal_0944", contract_id="0944-G", title="Cyber Defense Zero-Trust Retainer", counterparty="Starlight Capital", status="Closed", annual_value=310000, liability_cap="2.0x", updated_at="2026-08-19T11:00:00Z"),
            DealRecord(id="deal_0832", contract_id="0832-H", title="Multi-Tenant Data Warehouse License", counterparty="Syntropy BioTech", status="Rejected", annual_value=140000, liability_cap="0.8x", updated_at="2026-08-04T15:30:00Z"),
            DealRecord(id="deal_1205", contract_id="1205-K", title="Enterprise ERP Microservices Migration", counterparty="Pinnacle Energy Corp", status="Under Negotiation", annual_value=520000, liability_cap="1.5x", updated_at="2026-09-03T08:00:00Z"),
            DealRecord(id="deal_0690", contract_id="0690-M", title="SaaS Telemetry & Observability Pipeline", counterparty="Zenith Media Networks", status="Approved", annual_value=65000, liability_cap="1.0x", updated_at="2026-07-15T09:45:00Z"),
        ]
        for deal in sample_deals:
            if not db.query(DealRecord).filter(DealRecord.contract_id == deal.contract_id).first():
                db.add(deal)
        
        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield

app = FastAPI(
    title="Nexus Deal Room Backend",
    description="FastAPI WebMCP Server for Schema-Driven UI and Decision Twin",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API for Frontend
app.include_router(schema_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(contract_router, prefix="/api")
app.include_router(mcp_proxy_router, prefix="/api")

# Mount Model Context Protocol (WebMCP) SSE server
app.mount("/api/mcp", mcp_server.sse_app())

@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Serve production frontend if built and present (for Cloud Run container)
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

static_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.exists(static_dist):
    static_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")

if os.path.exists(static_dist):
    assets_dir = os.path.join(static_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path in ("openapi.json", "health"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(static_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dist, "index.html"))
