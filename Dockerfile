# ==============================================================================
# Multi-Stage Dockerfile for Nexus Deal Room
# Combines React Frontend (Vite) + FastAPI Backend into a single Cloud Run container
# ==============================================================================

# --- Stage 1: Build Frontend Assets ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python Backend Runtime ---
FROM python:3.11-slim AS runtime

# System updates & minimal runtime packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy Backend Source Code
COPY backend/ ./backend/

# Copy Built Static Frontend Assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/static
COPY --from=frontend-builder /app/frontend/dist /app/backend/static

# Cloud Run Configuration
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

EXPOSE 8080

WORKDIR /app/backend

CMD ["sh", "-c", "exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
