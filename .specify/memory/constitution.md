<!-- 
Sync Impact Report:
- Version change: 1.0.0 -> 1.1.0
- Added sections: Core Principles, Technical Architecture
- Modified principles: Refined WebMCP Mandate and Schema-Driven UI; Added Quality & Typing constraints
- Follow-up TODOs: None
-->
# Nexus Deal Room Constitution

## Core Principles

### I. Self-Evolving Architecture & Schema-Driven UI
The application is a self-evolving, agent-native web app. The UI MUST be 100% schema-driven. The frontend does not use hardcoded React components for the core application; it renders components dynamically based on a JSON schema provided by the backend.

### II. WebMCP Mandate (STRICT)
You MUST strictly use the Model Context Protocol (WebMCP). The backend acts as the MCP Server, and the AI agent acts as the MCP Client. This pattern is mandatory and MUST NOT be bypassed.

### III. Tech Stack Constraints
The technology stack is strictly defined and dependencies outside of this stack MUST NOT be hallucinated or introduced without amendment:
- **Backend**: Python FastAPI
- **Frontend**: React with Tailwind CSS and Zustand
- **AI Integration**: Microsoft Agentic AI Framework querying OpenAI models via GCP Vertex AI

### IV. Code Quality & Typing
All code MUST be production-grade, clean, and modular. You MUST write modular Python and TypeScript, and enforce strict typing across the entire codebase.

## Technical Architecture

- **Frontend Architecture**: Schema-driven (JSON-based) dynamic rendering
- **Backend Architecture**: Python FastAPI (acting as WebMCP Server)
- **AI/Agent Architecture**: Microsoft Agentic AI Framework (WebMCP Client)

## Governance

This Constitution governs the architecture and development workflow for the Nexus Deal Room project. Amendments require Tech Lead approval. Any deviation from the WebMCP pattern, schema-driven UI design, or technology stack is strictly prohibited without a formal amendment.

**Version**: 1.1.0 | **Ratified**: 2026-09-02 | **Last Amended**: 2026-09-02
