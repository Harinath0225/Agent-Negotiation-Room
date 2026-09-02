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
MODEL_PROVIDER = os.environ.get("WIRE_AGENT_PROVIDER", "auto").lower()

SYSTEM_INSTRUCTION = """
You are 'Wire-Agent', an AI architectural redesign assistant for the 'Nexus Deal Room' Experience Studio.
The entire website is 100% schema-driven and rendered from a JSON tree.
Your goal is to assist the admin by mutating the website layout, Tailwind CSS styling, and components.

Whenever the admin asks to alter the UI (e.g. change color, make a section visible, modify card style):
You MUST call the tool `mutate_ui_schema` with:
- `component_target`: Name or identifier of the section (e.g. 'terms', 'Terms & Conditions', 'header', 'root').
- `schema_patch`: A valid JSON string containing the style modifications (e.g. '{"className": "col-span-2 bg-amber-950/80 border border-amber-500 p-6 rounded-lg"}').
"""

async def execute_mutate_ui_tool(component_target: str, schema_patch: str) -> dict:
    """Executes the mutation against the backend WebMCP database."""
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    try:
        from backend.src.mcp.tools import mutate_ui_schema
        raw_result = mutate_ui_schema(schema_patch=schema_patch, component_target=component_target)
        return json.loads(raw_result)
    except Exception as e:
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    f"{SERVER_URL}/api/mcp/messages",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "mutate_ui_schema",
                            "arguments": {"component_target": component_target, "schema_patch": schema_patch}
                        },
                        "id": 1
                    },
                    timeout=5.0
                )
                return res.json()
            except Exception as http_err:
                return {"status": "error", "message": f"Tool execution failed: {str(e)} | HTTP: {str(http_err)}"}

async def run_with_vertex_ai(prompt: str):
    """Executes Wire-Agent using Google Cloud Platform (GCP) Vertex AI with an API Key or ADC."""
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

    print(f"🤖 [Model Registry] Loading Model: '{VERTEX_AI_MODEL}' with WebMCP tools...")

    # Define WebMCP Tool Declaration
    tool_def = {
        "function_declarations": [{
            "name": "mutate_ui_schema",
            "description": "Mutates the website UI schema and Tailwind CSS styling in the live application.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "component_target": {"type": "STRING", "description": "Target component (e.g. 'terms', 'header', 'root')"},
                    "schema_patch": {"type": "STRING", "description": "JSON string containing styling/layout patch"}
                },
                "required": ["component_target", "schema_patch"]
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

    # Check for function/tool call
    if response.function_calls:
        for call in response.function_calls:
            if call.name == "mutate_ui_schema":
                args = call.args
                target = args.get("component_target", "root")
                patch = args.get("schema_patch", "{}")
                print(f"⚡ [Vertex AI Tool Call] mutate_ui_schema(target='{target}', patch='{patch}')")
                result = await execute_mutate_ui_tool(target, patch)
                print(f"✅ [WebMCP Result]: {json.dumps(result, indent=2)}")
                print("🌐 The live website at http://localhost:5173 has been automatically updated!\n")
                return result

    print(f"💬 [Vertex AI Response]: {response.text}")
    return response.text

async def run_with_openai(prompt: str):
    """Executes Wire-Agent using OpenAI GPT model with Tool Calling."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
    print(f"🤖 [Provider: OpenAI] Calling model '{model_name}' with WebMCP tools...")

    tools = [{
        "type": "function",
        "function": {
            "name": "mutate_ui_schema",
            "description": "Mutates the website UI schema and Tailwind CSS styling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "component_target": {"type": "string", "description": "Target component (e.g. 'terms', 'header', 'root')"},
                    "schema_patch": {"type": "string", "description": "JSON string containing styling/layout patch"}
                },
                "required": ["component_target", "schema_patch"]
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
            if tool_call.function.name == "mutate_ui_schema":
                args = json.loads(tool_call.function.arguments)
                target = args.get("component_target", "root")
                patch = args.get("schema_patch", "{}")
                print(f"⚡ [OpenAI Tool Call] mutate_ui_schema(target='{target}', patch='{patch}')")
                result = await execute_mutate_ui_tool(target, patch)
                print(f"✅ [WebMCP Result]: {json.dumps(result, indent=2)}")
                print("🌐 The live website at http://localhost:5173 has been automatically updated!\n")
                return result
    print(f"💬 [OpenAI Response]: {message.content}")
    return message.content

async def run_wire_agent(prompt: str):
    print(f"\n[Wire-Agent] Processing Admin Request: '{prompt}'")

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
    print("ℹ️  [WebMCP Direct Mode] No active API key detected. Executing Wire-Agent mutation rule directly...")
    sample_patch = json.dumps({
        "className": "col-span-2 bg-gradient-to-br from-indigo-950/90 to-slate-900 border-2 border-indigo-500/80 p-6 rounded-xl shadow-2xl"
    })
    result = await execute_mutate_ui_tool(component_target="terms", schema_patch=sample_patch)
    print(f"✅ [WebMCP Result]: {json.dumps(result, indent=2)}")
    print("🌐 Check http://localhost:5173 to see the live mutated website!\n")
    return result

async def main():
    print("=" * 60)
    print("🚀 NEXUS EXPERIENCE STUDIO: WIRE-AGENT (WebMCP Live Client)")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "Make the Terms and Conditions section prominent with an amber warning border."

    await run_wire_agent(user_input)

if __name__ == "__main__":
    asyncio.run(main())
