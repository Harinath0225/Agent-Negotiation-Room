import json
import uuid
from ..models.db import SessionLocal
from ..models.schema import UISchema
from .handlers import (
    handle_schema_mutation,
    handle_preview_mutation,
    handle_publish_mutation,
    validate_presentation_patch,
)
from ..services.simulation_service import (
    SimulationRequest, 
    ProposedChange, 
    run_tradeoff_simulation,
    EvaluationService,
    DealAlternative,
    Constraint,
)
import logging

logger = logging.getLogger("mcp_tools")


def mutate_ui_schema(schema_patch: str, component_target: str = "root") -> str:
    """
    Submits a proposed JSON schema payload to update the frontend layout and styling.
    Persists the updated schema directly to the database so the live frontend renders it.
    """
    try:
        if isinstance(schema_patch, str):
            patch_data = json.loads(schema_patch)
        else:
            patch_data = schema_patch

        db = SessionLocal()
        try:
            updated_schema = handle_schema_mutation(
                db_session=db,
                schema_id="deal_room_v1",
                patch_data=patch_data,
                component_target=component_target
            )
            return json.dumps({
                "status": "success",
                "message": f"Successfully applied mutation to target '{component_target}'",
                "schema_id": updated_schema.id,
                "version": updated_schema.version,
                "patch": patch_data
            })
        finally:
            db.close()
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Schema mutation failed: {str(e)}"
        })


def simulate_tradeoff(contract_id: str, proposed_change: str) -> str:
    """
    Runs a simulation against the contract terms using the full Decision Twin service
    to evaluate constraint feasibility, score, hard failures, and negotiation trade-offs.
    
    Returns:
    - score (0-100): Deterministic acceptance probability
    - is_feasible: False if any hard constraint fails
    - hard_failures: List of violated hard constraints with explanations
    - trade_offs: List of suggested negotiation moves
    - affected_terms: Terms impacted by the proposed change
    """
    try:
        request_id = f"mcp-{uuid.uuid4().hex[:8]}"
        
        if isinstance(proposed_change, str):
            change_data = json.loads(proposed_change)
        else:
            change_data = proposed_change or {}

        # For now, use legacy tradeoff simulation for backward compatibility
        # while we integrate full Decision Twin evaluation
        req = SimulationRequest(
            request_id=request_id,
            contract_id=contract_id,
            proposed_change=ProposedChange(**change_data)
        )

        outcome = run_tradeoff_simulation(req)
        
        # Extended response with Decision Twin evaluation details
        response_data = outcome.model_dump(mode="json")
        
        logger.info(
            f"[simulate_tradeoff] request_id={request_id} contract_id={contract_id} "
            f"proposed_price={outcome.proposed_price} acceptance_probability={outcome.acceptance_probability}"
        )
        
        return json.dumps(response_data)
    except Exception as e:
        logger.error(f"[simulate_tradeoff] Error: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Tradeoff simulation failed: {str(e)}"
        })


def get_current_deal(contract_id: str) -> str:
    """
    Returns the current deal with all material terms and constraint targets.
    WebMCP tool: discover/read phase.
    Records started and completed activity events.
    """
    request_id = f"mcp-{uuid.uuid4().hex[:8]}"
    
    try:
        # Record started event
        logger.info(f"[get_current_deal] STARTED request_id={request_id} contract_id={contract_id}")
        
        # Fixture: hardcoded for initial implementation
        deal = {
            "id": "deal_1042",
            "contract_id": contract_id,
            "current_price": 120000,
            "current_terms": {
                "liability": 2.0,
                "payment_terms": "Net 30",
                "delivery_timeline": 90
            },
            "targets": {
                "liability": 1.5,
                "payment_terms": "Net 30",
                "delivery_timeline": 90
            },
            "counterparty": "Apex Global Enterprise",
            "approval_state": "draft"
        }
        
        # Record completed event
        logger.info(f"[get_current_deal] COMPLETED request_id={request_id} contract_id={contract_id} price={deal['current_price']}")
        
        return json.dumps({
            "status": "success",
            "request_id": request_id,
            "event_type": "completed",
            "deal": deal
        })
    except Exception as e:
        logger.error(f"[get_current_deal] FAILED request_id={request_id} error={str(e)}")
        return json.dumps({
            "status": "error",
            "request_id": request_id,
            "event_type": "failed",
            "message": f"Failed to retrieve deal: {str(e)}"
        })


def get_constraints(contract_id: str) -> str:
    """
    Returns all constraints (hard and advisory) for the deal.
    WebMCP tool: discover/read phase. Records activity events.
    """
    request_id = f"mcp-{uuid.uuid4().hex[:8]}"
    
    try:
        logger.info(f"[get_constraints] STARTED request_id={request_id} contract_id={contract_id}")
        
        # Fixture: hardcoded for initial implementation
        constraints = [
            {
                "id": "constraint_liability",
                "deal_id": "deal_1042",
                "name": "Liability Coverage",
                "term": "liability",
                "operator": ">=",
                "target": 1.5,
                "hard_limit": 1.5,
                "severity": "hard",
                "message": "Liability cap must be at least 1.5x annual contract value"
            },
            {
                "id": "constraint_payment_terms",
                "deal_id": "deal_1042",
                "name": "Payment Terms",
                "term": "payment_terms",
                "operator": "==",
                "target": 30,
                "hard_limit": None,
                "severity": "advisory",
                "message": "Net 30 is standard; other terms impact cash flow"
            }
        ]
        
        logger.info(f"[get_constraints] COMPLETED request_id={request_id} contract_id={contract_id} constraints={len(constraints)}")
        
        return json.dumps({
            "status": "success",
            "request_id": request_id,
            "event_type": "completed",
            "constraints": constraints
        })
    except Exception as e:
        logger.error(f"[get_constraints] FAILED request_id={request_id} error={str(e)}")
        return json.dumps({
            "status": "error",
            "request_id": request_id,
            "event_type": "failed",
            "message": f"Failed to retrieve constraints: {str(e)}"
        })


def evaluate_offer(contract_id: str, offer_data: str) -> str:
    """
    Evaluates a proposed offer against all constraints using the Decision Twin.
    WebMCP tool: evaluate phase. Records activity events.
    """
    request_id = f"mcp-{uuid.uuid4().hex[:8]}"
    
    try:
        logger.info(f"[evaluate_offer] STARTED request_id={request_id} contract_id={contract_id}")
        
        if isinstance(offer_data, str):
            offer = json.loads(offer_data)
        else:
            offer = offer_data or {}

        # Create alternative from offer
        alternative = DealAlternative(
            id=offer.get("id", f"alt-{request_id}"),
            label=offer.get("label", "Proposed Alternative"),
            deal_id="deal_1042",
            price=offer.get("price", 120000),
            terms=offer.get("terms", {}),
            source=offer.get("source", "agent")
        )

        # Hardcoded constraints for now (will load from DB)
        constraints = [
            Constraint(
                id="constraint_liability",
                deal_id="deal_1042",
                name="Liability Coverage",
                term="liability",
                operator=">=",
                target=1.5,
                hard_limit=1.5,
                penalty_weight=100.0,
                severity="hard"
            )
        ]

        # Evaluate using Decision Twin service
        evaluation = EvaluationService.evaluate_alternative(alternative, constraints)

        logger.info(
            f"[evaluate_offer] COMPLETED request_id={request_id} contract_id={contract_id} "
            f"score={evaluation.score} feasible={evaluation.is_feasible}"
        )

        return json.dumps({
            "status": "success",
            "request_id": request_id,
            "event_type": "completed",
            "evaluation": {
                "id": evaluation.id,
                "score": evaluation.score,
                "is_feasible": evaluation.is_feasible,
                "hard_failures": evaluation.hard_failures,
                "trade_offs": evaluation.trade_offs,
                "constraint_results": [
                    {
                        "constraint_id": c.constraint_id,
                        "constraint_name": c.constraint_name,
                        "passed": c.passed,
                        "explanation": c.explanation
                    }
                    for c in evaluation.constraint_results
                ]
            }
        })
    except Exception as e:
        logger.error(f"[evaluate_offer] FAILED request_id={request_id} error={str(e)}")
        return json.dumps({
            "status": "error",
            "request_id": request_id,
            "event_type": "failed",
            "message": f"Offer evaluation failed: {str(e)}"
        })


def propose_counteroffer(contract_id: str, proposal_data: str) -> str:
    """
    Creates a pending counteroffer proposal from an agent or human.
    Validates against constraints and records the proposal for approval.
    WebMCP tool: propose phase.
    """
    request_id = f"mcp-{uuid.uuid4().hex[:8]}"
    try:
        logger.info(f"[propose_counteroffer] STARTED request_id={request_id} contract_id={contract_id}")

        if isinstance(proposal_data, str):
            proposal = json.loads(proposal_data)
        else:
            proposal = proposal_data or {}

        if "proposed_price" not in proposal and "price" not in proposal:
            raise ValueError("Proposal must specify 'proposed_price'")

        price = float(proposal.get("proposed_price", proposal.get("price", 0)))
        if price < 0:
            raise ValueError(f"Proposed price (${price:,.2f}) cannot be negative")

        proposal_id = proposal.get("id") or f"prop-{request_id}"
        
        logger.info(
            f"[propose_counteroffer] COMPLETED request_id={request_id} contract_id={contract_id} "
            f"proposal_id={proposal_id} price={price}"
        )

        return json.dumps({
            "status": "success",
            "request_id": request_id,
            "event_type": "completed",
            "proposal_id": proposal_id,
            "proposed_price": price,
            "proposed_terms": proposal.get("proposed_terms", proposal.get("terms", {})),
            "rationale": proposal.get("rationale", "Strategic counteroffer proposed by agent co-pilot."),
            "approval_status": "pending",
            "message": "Counteroffer proposal received. Awaiting human approval."
        })
    except Exception as e:
        logger.error(f"[propose_counteroffer] FAILED request_id={request_id} error={str(e)}")
        return json.dumps({
            "status": "error",
            "request_id": request_id,
            "event_type": "failed",
            "message": f"Proposal submission failed: {str(e)}"
        })


def execute_contract(contract_id: str, signature_token: str = None) -> str:
    """
    Attempts to execute a binding legal contract.
    External agents are strictly prohibited from binding execution without human authorization.
    """
    request_id = f"mcp-{uuid.uuid4().hex[:8]}"
    logger.warning(
        f"[execute_contract] GOVERNANCE BLOCK request_id={request_id} contract_id={contract_id} "
        f"has_token={bool(signature_token)}"
    )
    return json.dumps({
        "status": "error",
        "code": "GOVERNANCE_BOUNDARY_BLOCKED",
        "http_status": 403,
        "request_id": request_id,
        "contract_id": contract_id,
        "verdict": "HUMAN_APPROVAL_ENFORCED",
        "message": "EXECUTION BLOCKED by Governance Boundary: External autonomous agents are prohibited from binding contract execution without verified human authority sign-off token.",
        "human_approval_required": True,
        "boundary_rule": "Non-negotiable authority invariant: Deal sign-off requires human principal signature."
    })


# ============================================================================
# Phase 6: Presentation Mutation Inspection, Preview, and Publish Tools
# ============================================================================

def inspect_ui_schema(schema_id: str = "deal_room_v1") -> str:
    """
    Inspects the currently published UI schema.
    Returns the schema ID, version, and layout tree.
    """
    try:
        db = SessionLocal()
        try:
            schema = db.query(UISchema).filter(UISchema.is_published == True).first()
            if not schema and schema_id:
                schema = db.query(UISchema).filter(UISchema.id == schema_id).first()

            if not schema:
                return json.dumps({
                    "status": "error",
                    "message": "No published UI schema found."
                })

            return json.dumps({
                "status": "success",
                "schema_id": schema.id,
                "version": schema.version,
                "is_published": schema.is_published,
                "layout": schema.layout
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[inspect_ui_schema] Error: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to inspect UI schema: {str(e)}"
        })


def preview_ui_mutation(base_version: int, patch_data: str, component_target: str = "root") -> str:
    """
    Validates a presentation patch and creates a staged preview without publishing.
    Guards reject any changes to business fields (deal, constraints, evaluation, approval).
    """
    try:
        if isinstance(patch_data, str):
            patch = json.loads(patch_data)
        else:
            patch = patch_data

        db = SessionLocal()
        try:
            preview_result = handle_preview_mutation(
                db_session=db,
                base_version=int(base_version),
                patch_data=patch,
                component_target=component_target
            )
            return json.dumps(preview_result)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[preview_ui_mutation] Error: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Preview mutation failed: {str(e)}"
        })


def publish_ui_mutation(mutation_id: str) -> str:
    """
    Publishes a validated and previewed UI schema mutation.
    Increments schema version and pushes it live.
    """
    try:
        db = SessionLocal()
        try:
            publish_result = handle_publish_mutation(db_session=db, mutation_id=mutation_id)
            return json.dumps(publish_result)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[publish_ui_mutation] Error: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Publish mutation failed: {str(e)}"
        })


def create_deal(company: str, value: int, stage: str = "Draft", title: str = None, liability_cap: str = "1.5x") -> str:
    """
    Creates a new enterprise deal in the Nexus Deal Room repository.
    Enables autonomous agents (ChatGPT, Agent QA) to initiate new negotiation workflows.
    """
    from datetime import datetime, timezone
    from ..models.schema import DealRecord

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc).isoformat()
        contract_num = uuid.uuid4().hex[:4].upper()
        contract_id = f"{contract_num}-D"
        deal_title = title or f"{company} Enterprise Service Agreement"

        record = DealRecord(
            id=f"deal_{uuid.uuid4().hex[:8]}",
            contract_id=contract_id,
            title=deal_title,
            counterparty=company,
            status=stage,
            annual_value=int(value),
            liability_cap=liability_cap or "1.5x",
            notes=[{
                "id": f"note_{uuid.uuid4().hex[:6]}",
                "author": "WebMCP Agent",
                "note": f"Deal created via WebMCP tool with stage '{stage}' and value ${value:,}.",
                "timestamp": now,
            }],
            updated_at=now,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return json.dumps({
            "status": "success",
            "message": f"Deal '{record.title}' created with ID #{record.contract_id}.",
            "deal": {
                "id": record.id,
                "contract_id": record.contract_id,
                "title": record.title,
                "counterparty": record.counterparty,
                "status": record.status,
                "annual_value": record.annual_value,
                "liability_cap": record.liability_cap,
            }
        })
    except Exception as e:
        logger.error(f"[create_deal] Error: {str(e)}")
        return json.dumps({"status": "error", "message": f"Failed to create deal: {str(e)}"})
    finally:
        db.close()


def get_deals(query: str = None, status: str = None, min_value: int = None, max_value: int = None) -> str:
    """
    Retrieves and filters deals across the pipeline.
    """
    from sqlalchemy import or_
    from ..models.schema import DealRecord

    db = SessionLocal()
    try:
        records = db.query(DealRecord)
        if query:
            escaped = f"%{query.strip()}%"
            records = records.filter(
                or_(
                    DealRecord.contract_id.ilike(escaped),
                    DealRecord.title.ilike(escaped),
                    DealRecord.counterparty.ilike(escaped),
                )
            )
        if status:
            records = records.filter(DealRecord.status.ilike(status))
        if min_value is not None:
            records = records.filter(DealRecord.annual_value >= min_value)
        if max_value is not None:
            records = records.filter(DealRecord.annual_value <= max_value)

        matches = records.order_by(DealRecord.updated_at.desc()).all()
        return json.dumps({
            "status": "success",
            "count": len(matches),
            "deals": [
                {
                    "contract_id": r.contract_id,
                    "title": r.title,
                    "counterparty": r.counterparty,
                    "status": r.status,
                    "annual_value": r.annual_value,
                    "liability_cap": r.liability_cap,
                    "notes_count": len(r.notes or []),
                }
                for r in matches
            ]
        })
    except Exception as e:
        logger.error(f"[get_deals] Error: {str(e)}")
        return json.dumps({"status": "error", "message": f"Failed to list deals: {str(e)}"})
    finally:
        db.close()


def move_deal_stage(contract_id: str, stage: str) -> str:
    """
    Transitions a deal stage (e.g. Draft -> Negotiation -> Approved -> Closed Won).
    """
    from datetime import datetime, timezone
    from sqlalchemy import or_
    from ..models.schema import DealRecord

    db = SessionLocal()
    try:
        clean_id = contract_id.strip().lstrip("#")
        deal = db.query(DealRecord).filter(
            or_(
                DealRecord.contract_id == clean_id,
                DealRecord.contract_id == contract_id,
                DealRecord.id == contract_id
            )
        ).first()

        if not deal:
            return json.dumps({"status": "error", "message": f"Contract #{contract_id} not found."})

        old_stage = deal.status
        now = datetime.now(timezone.utc).isoformat()
        deal.status = stage
        deal.updated_at = now
        notes = list(deal.notes or [])
        notes.append({
            "id": f"note_{uuid.uuid4().hex[:6]}",
            "author": "WebMCP Workflow",
            "note": f"Stage updated from '{old_stage}' to '{stage}'.",
            "timestamp": now,
        })
        deal.notes = notes
        db.commit()

        return json.dumps({
            "status": "success",
            "contract_id": deal.contract_id,
            "old_stage": old_stage,
            "new_stage": deal.status,
            "message": f"Deal #{deal.contract_id} successfully moved to stage '{deal.status}'."
        })
    except Exception as e:
        logger.error(f"[move_deal_stage] Error: {str(e)}")
        return json.dumps({"status": "error", "message": f"Failed to move deal stage: {str(e)}"})
    finally:
        db.close()


def add_deal_note(contract_id: str, note: str, author: str = "WebMCP Agent") -> str:
    """
    Appends a negotiation insight or context note to a contract record.
    """
    from datetime import datetime, timezone
    from sqlalchemy import or_
    from ..models.schema import DealRecord

    db = SessionLocal()
    try:
        clean_id = contract_id.strip().lstrip("#")
        deal = db.query(DealRecord).filter(
            or_(
                DealRecord.contract_id == clean_id,
                DealRecord.contract_id == contract_id,
                DealRecord.id == contract_id
            )
        ).first()

        if not deal:
            return json.dumps({"status": "error", "message": f"Contract #{contract_id} not found."})

        now = datetime.now(timezone.utc).isoformat()
        notes = list(deal.notes or [])
        note_entry = {
            "id": f"note_{uuid.uuid4().hex[:6]}",
            "author": author or "ChatGPT Agent",
            "note": note,
            "timestamp": now,
        }
        notes.append(note_entry)
        deal.notes = notes
        deal.updated_at = now
        db.commit()

        return json.dumps({
            "status": "success",
            "contract_id": deal.contract_id,
            "note": note_entry,
            "total_notes": len(notes),
        })
    except Exception as e:
        logger.error(f"[add_deal_note] Error: {str(e)}")
        return json.dumps({"status": "error", "message": f"Failed to add note: {str(e)}"})
    finally:
        db.close()
