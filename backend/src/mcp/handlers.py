import copy
import uuid
from typing import Dict, Any
from ..models.schema import UISchema

FORBIDDEN_PREFIXES = ["/deal/", "/constraints/", "/evaluation/", "/approval/", "/strategy/"]
FORBIDDEN_KEYS = {"price", "target", "hard_limit", "penalty_weight", "score", "is_feasible", "approval_state", "hard_failures"}

_staged_mutations: Dict[str, Dict[str, Any]] = {}


def validate_presentation_patch(patch_data: dict) -> None:
    """
    Guards schema patches against deal terms, constraints, evaluator behavior, or approval state.
    Raises ValueError on violation.
    """
    def _check(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in FORBIDDEN_KEYS:
                    raise ValueError(f"Forbidden field in mutation patch: '{k}' cannot be mutated by presentation layer.")
                if isinstance(k, str) and any(k.startswith(p) for p in FORBIDDEN_PREFIXES):
                    raise ValueError(f"Forbidden path in mutation patch: '{k}' cannot be mutated by presentation layer.")
                if k == "path" and isinstance(v, str) and any(v.startswith(p) for p in FORBIDDEN_PREFIXES):
                    raise ValueError(f"Forbidden path in mutation patch: '{v}' cannot be mutated by presentation layer.")
                _check(v)
        elif isinstance(obj, list):
            for item in obj:
                _check(item)

    _check(patch_data)


def _deep_patch_node(node: dict, target: str, patch_data: dict) -> bool:
    """Recursively search for matching component target by type, text, or className and apply patch."""
    matched = False
    
    # Check if this node matches target
    node_type = node.get("type", "")
    node_text = node.get("props", {}).get("text", "")
    
    if target.lower() in node_type.lower() or target.lower() in node_text.lower():
        if "className" in patch_data:
            node["className"] = patch_data["className"]
        if "props" in patch_data:
            node.setdefault("props", {}).update(patch_data["props"])
        if "type" in patch_data:
            node["type"] = patch_data["type"]
        matched = True

    # Recurse children
    for child in node.get("children", []):
        if isinstance(child, dict):
            if _deep_patch_node(child, target, patch_data):
                matched = True

    return matched


def handle_schema_mutation(db_session, schema_id: str, patch_data: dict, component_target: str = "root"):
    """
    Applies the mutation to the database schema and increments version.
    """
    validate_presentation_patch(patch_data)

    schema = db_session.query(UISchema).filter(UISchema.is_published == True).first()
    if not schema and schema_id:
        schema = db_session.query(UISchema).filter(UISchema.id == schema_id).first()

    if not schema:
        schema = UISchema(id=schema_id or "deal_room_v1", layout=patch_data, is_published=True, version=1)
        db_session.add(schema)
    else:
        current_layout = copy.deepcopy(schema.layout) if schema.layout else {}

        if component_target.lower() in ("root", "all", "layout"):
            if "children" in patch_data or "type" in patch_data:
                current_layout = patch_data
            else:
                current_layout.update(patch_data)
        else:
            found = _deep_patch_node(current_layout, component_target, patch_data)
            if not found:
                if "children" in current_layout and isinstance(current_layout["children"], list):
                    current_layout["children"].append(patch_data)
                else:
                    current_layout.update(patch_data)

        schema.layout = current_layout
        schema.version = (schema.version or 1) + 1

    db_session.commit()
    db_session.refresh(schema)
    return schema


def handle_preview_mutation(db_session, base_version: int, patch_data: dict, component_target: str = "root") -> Dict[str, Any]:
    """
    Generates a preview layout without persisting changes to the published schema.
    Returns preview result and staged mutation ID.
    """
    validate_presentation_patch(patch_data)

    schema = db_session.query(UISchema).filter(UISchema.is_published == True).first()
    current_version = schema.version if schema else 1
    current_layout = copy.deepcopy(schema.layout) if schema and schema.layout else {}

    if component_target.lower() in ("root", "all", "layout"):
        if "children" in patch_data or "type" in patch_data:
            preview_layout = patch_data
        else:
            preview_layout = current_layout
            preview_layout.update(patch_data)
    else:
        preview_layout = current_layout
        found = _deep_patch_node(preview_layout, component_target, patch_data)
        if not found:
            if "children" in preview_layout and isinstance(preview_layout["children"], list):
                preview_layout["children"].append(patch_data)
            else:
                preview_layout.update(patch_data)

    mutation_id = f"mut-{uuid.uuid4().hex[:8]}"
    staged = {
        "id": mutation_id,
        "base_schema_version": base_version,
        "current_schema_version": current_version,
        "patch": patch_data,
        "preview_layout": preview_layout,
        "component_target": component_target,
        "status": "previewed"
    }
    _staged_mutations[mutation_id] = staged

    return {
        "status": "success",
        "mutation_id": mutation_id,
        "base_schema_version": base_version,
        "preview_layout": preview_layout,
        "validation": "PASSED (presentation-only)"
    }


def handle_publish_mutation(db_session, mutation_id: str) -> Dict[str, Any]:
    """
    Publishes a previously previewed mutation after validation.
    Requires reviewed preview and matching base version.
    """
    staged = _staged_mutations.get(mutation_id)
    if not staged:
        raise ValueError(f"Mutation '{mutation_id}' not found or has expired.")

    if staged["status"] != "previewed":
        raise ValueError(f"Mutation '{mutation_id}' is not in 'previewed' state (current: {staged['status']}).")

    schema = db_session.query(UISchema).filter(UISchema.is_published == True).first()
    if not schema:
        raise ValueError("No active published schema found.")

    if schema.version != staged["base_schema_version"]:
        raise ValueError(
            f"Base version mismatch: current schema version is {schema.version}, "
            f"but mutation was created against version {staged['base_schema_version']}."
        )

    # Apply staged layout
    schema.layout = staged["preview_layout"]
    schema.version += 1
    db_session.commit()
    db_session.refresh(schema)

    staged["status"] = "published"
    staged["published_version"] = schema.version

    return {
        "status": "success",
        "mutation_id": mutation_id,
        "published_version": schema.version,
        "message": f"Successfully published schema version {schema.version}."
    }
