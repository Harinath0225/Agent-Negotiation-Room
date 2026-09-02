import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.db import engine, Base, SessionLocal
from src.models.schema import UISchema
from src.api.schema_routes import router as schema_router
from src.api.simulation_routes import router as simulation_router
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

# Mount Model Context Protocol (WebMCP) SSE server
app.mount("/api/mcp", mcp_server.sse_app())

@app.get("/health")
async def health_check():
    return {"status": "ok"}
