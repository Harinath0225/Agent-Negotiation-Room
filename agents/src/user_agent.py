import os
import sys
import json
import asyncio
import httpx
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

SERVER_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Vertex AI / Gemini API Keys & Settings
VERTEX_AI_API_KEY = (
    os.environ.get("VERTEX_AI_API_KEY") 
    or os.environ.get("GEMINI_API_KEY") 
    or os.environ.get("GOOGLE_API_KEY")
)
USE_VERTEX_AI = os.environ.get("USE_VERTEX_AI", "true").lower() in ("true", "1", "yes")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
GCP_LOCATION = os.environ.get("GCP_LOCATION") or os.environ.get("GCP_REGION", "us-central1")
VERTEX_AI_MODEL = os.environ.get("VERTEX_AI_MODEL", "gemini-1.5-pro")

# Provider preference: 'vertex', 'gemini', 'openai', or 'auto'
MODEL_PROVIDER = os.environ.get("USER_AGENT_PROVIDER", "auto").lower()

SYSTEM_INSTRUCTION = """
You are 'User Agent', an analytical negotiation co-pilot in the 'Nexus Deal Room'.
Your role is to assist the human dealmaker during contract negotiations.
You are directly connected to the backend 'Decision Twin' via the Model Context Protocol (WebMCP).

When the user asks tradeoff questions (e.g., 'If I lower the price by $20k, what is my risk?', 'Can I extend delivery time?'):
You MUST call the tool `simulate_tradeoff` with:
- `contract_id`: The identifier of the contract (default '#1042-B').
- `proposed_change`: JSON string describing the modification (e.g. '{"price_delta": -20000, "current_price": 120000}').
"""

async def execute_simulate_tool(contract_id: str, proposed_change: str) -> dict:
    """Executes the simulation against the backend Decision Twin via WebMCP."""
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    try:
        from backend.src.mcp.tools import simulate_tradeoff
        raw = simulate_tradeoff(contract_id=contract_id, proposed_change=proposed_change)
        return json.loads(raw)
    except Exception as e:
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    f"{SERVER_URL}/api/mcp/messages",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "simulate_tradeoff",
                            "arguments": {"contract_id": contract_id, "proposed_change": proposed_change}
                        },
                        "id": 1
                    },
                    timeout=5.0
                )
                return res.json()
            except Exception as http_err:
                return {"status": "error", "message": f"Tool execution failed: {str(e)} | HTTP: {str(http_err)}"}

async def run_with_vertex_ai(prompt: str):
    """Executes User Agent using Google Cloud Platform (GCP) Vertex AI with an API Key or ADC."""
    from google import genai
    from google.genai import types

    is_vertex = True if (USE_VERTEX_AI and GCP_PROJECT_ID) else False
    if is_vertex:
        print(f"☁️ [GCP Vertex AI] Connecting to Project: '{GCP_PROJECT_ID}', Region: '{GCP_LOCATION}' with API Key")
        client = genai.Client(
            vertexai=True,
            api_key=VERTEX_AI_API_KEY,
            project=GCP_PROJECT_ID,
            location=GCP_LOCATION
        )
    else:
        print("🤖 [Google GenAI] Connecting via API Key...")
        client = genai.Client(api_key=VERTEX_AI_API_KEY)

    print(f"🤖 [Model Registry] Loading Model: '{VERTEX_AI_MODEL}' with Decision Twin tools...")

    tool_def = {
        "function_declarations": [{
            "name": "simulate_tradeoff",
            "description": "Runs a simulation against contract terms using the Decision Twin to compute risk deltas and counterparty acceptance.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "contract_id": {"type": "STRING", "description": "Contract ID"},
                    "proposed_change": {"type": "STRING", "description": "JSON string of proposed term adjustments"}
                },
                "required": ["contract_id", "proposed_change"]
            }
        }]
    }

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[tool_def]
    )

    response = client.models.generate_content(
        model=VERTEX_AI_MODEL,
        contents=prompt,
        config=config
    )

    if response.function_calls:
        for call in response.function_calls:
            if call.name == "simulate_tradeoff":
                args = call.args
                contract_id = args.get("contract_id", "#1042-B")
                change = args.get("proposed_change", "{}")
                print(f"⚡ [Vertex AI Tool Call] simulate_tradeoff(contract_id='{contract_id}', proposed_change='{change}')")
                result = await execute_simulate_tool(contract_id, change)
                print(f"📊 [Decision Twin Analytics Result]:\n{json.dumps(result, indent=2)}\n")
                return result

    print(f"💬 [Vertex AI Response]: {response.text}")
    return response.text

async def run_with_openai(prompt: str):
    """Executes User Agent using OpenAI GPT model with Tool Calling."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
    print(f"💼 [Provider: OpenAI] Calling model '{model_name}' with Decision Twin tools...")

    tools = [{
        "type": "function",
        "function": {
            "name": "simulate_tradeoff",
            "description": "Runs a simulation against contract terms using the Decision Twin to compute risk deltas and counterparty acceptance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string", "description": "Contract ID"},
                    "proposed_change": {"type": "string", "description": "JSON string of proposed term adjustments"}
                },
                "required": ["contract_id", "proposed_change"]
            }
        }
    }]

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt}
        ],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "simulate_tradeoff":
                args = json.loads(tool_call.function.arguments)
                contract_id = args.get("contract_id", "#1042-B")
                change = args.get("proposed_change", "{}")
                print(f"⚡ [OpenAI Tool Call] simulate_tradeoff(contract_id='{contract_id}', proposed_change='{change}')")
                result = await execute_simulate_tool(contract_id, change)
                print(f"📊 [Decision Twin Analytics Result]:\n{json.dumps(result, indent=2)}\n")
                return result
    print(f"💬 [OpenAI Response]: {message.content}")
    return message.content

async def run_user_agent(prompt: str):
    print(f"\n[User Agent] Processing Negotiation Inquiry: '{prompt}'")

    # 1. GCP Vertex AI with API Key or ADC
    if (MODEL_PROVIDER in ("vertex", "vertexai", "gemini") or (MODEL_PROVIDER == "auto" and VERTEX_AI_API_KEY)) and VERTEX_AI_API_KEY:
        try:
            return await run_with_vertex_ai(prompt)
        except Exception as e:
            print(f"[Vertex AI Error]: {e}. Attempting fallback...")

    # 2. OpenAI GPT
    if (MODEL_PROVIDER == "openai" or (MODEL_PROVIDER == "auto" and OPENAI_API_KEY)) and OPENAI_API_KEY:
        try:
            return await run_with_openai(prompt)
        except Exception as e:
            print(f"[OpenAI Error]: {e}. Attempting fallback...")

    # 3. Fallback / WebMCP Direct Demo Mode
    print("ℹ️  [WebMCP Direct Mode] No active API key detected. Querying Decision Twin for tradeoff scenario directly...")
    result = await execute_simulate_tool("#1042-B", json.dumps({"price_delta": -20000, "current_price": 120000}))
    print(f"📊 [Decision Twin Analytics Result]:\n{json.dumps(result, indent=2)}\n")
    return result

async def main():
    print("=" * 60)
    print("💼 NEXUS DEAL ROOM: USER AGENT (Decision Twin Co-Pilot)")
    print("=" * 60)

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "If I lower the contract price from $120,000 to $100,000, how does that impact our risk and deal acceptance?"

    await run_user_agent(user_input)

if __name__ == "__main__":
    asyncio.run(main())
