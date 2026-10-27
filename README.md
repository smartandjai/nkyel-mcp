# 🦌 Ñkyel — Sovereign SuperAgent Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](./backend/pyproject.toml)
[![Next.js](https://img.shields.io/badge/Next.js-15%2B-000000?logo=next.js&logoColor=white)](./frontend/package.json)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF6F00?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![MCP](https://img.shields.io/badge/Protocol-MCP-8A2BE2)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](./docker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**An open-source, sovereign autonomous agent platform combining LangGraph, Next.js, FastAPI, thread-isolated sandboxes, and Model Context Protocol (MCP) tools.**

[English](./README.md) | [Français](./README_fr.md) | [Documentation](https://nkyel.smartandjai.com)

</div>

---

## 🌟 What is Ñkyel?

**Ñkyel** is an enterprise-ready **SuperAgent Harness** built from the ground up for high-precision autonomous operations, deep multi-step research, code execution, and real-world workflows. 

Unlike simple chatbot wrappers, Ñkyel coordinates **sub-agents**, maintains **long-term contextual memory**, executes code in **thread-isolated sandboxes**, interacts with the web via **visual browser agents (E2B Desktop & Tavily)**, and integrates external enterprise tools through the **Model Context Protocol (MCP)**.

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|                      Next.js 15 (TailwindCSS, Radix, Streaming)                   |
+-----------------------------------------+-----------------------------------------+
                                          | :2026 (Nginx Reverse Proxy)
+-----------------------------------------v-----------------------------------------+
|                                    GATEWAY API                                    |
|                      FastAPI + Embedded LangGraph Agent Runtime                   |
+-------------------+---------------------+--------------------+--------------------+
|   Agent Core      |   Execution Sandbox |   MCP Connectors   | Storage & Checkpts |
|   - Planner       |   - E2B Desktop     |   - Google Drive   | - PostgreSQL       |
|   - Sub-Agents    |   - Docker Sandbox  |   - Tavily Search  | - SQLite           |
|   - Context Memory|   - Local Execution |   - Gmail / Slack  | - Cloudflare R2    |
+-------------------+---------------------+--------------------+--------------------+
```

---

## ✨ Key Features

- 🧠 **LangGraph Multi-Agent Orchestration**: Sophisticated stateful graphs, specialized sub-agents, dynamic context compaction, human-in-the-loop approvals, and checkpointed persistence.
- 🔌 **Model Context Protocol (MCP) Native**: Seamlessly plug in standard MCP servers (Google Drive, Gmail, GitHub, Tavily, PostgreSQL, Slack, Filesystem, custom MCPs) via stdio or HTTP/SSE.
- 🖥️ **Thread-Isolated Sandboxes & Computer Use**: Real visual browser navigation and shell execution powered by **E2B Cloud Desktop** or local Docker containers.
- 📊 **Executive Deliverables Engine**: Autonomous document compilation and report generation into **Typst 0.15 PDFs**, Markdown, and interactive data visualizations.
- 🌐 **Sovereign Multi-LLM Routing**: Zero vendor lock-in. Connect to **RunPod** (self-hosted Qwen3/DeepSeek), **Groq**, **Anthropic Claude**, **OpenAI**, **Ollama**, or any OpenAI-compatible provider.
- 💾 **Production State & Artifact Storage**: Durable state persistence via **PostgreSQL (Neon)** or SQLite, with asset and artifact offloading to **Cloudflare R2** / S3.
- 💬 **Omnichannel Gateway**: Deploy agents across chat platforms including **Slack**, **Telegram**, **Lark/Feishu**, **DingTalk**, and **WeCom**.

---

## 🏗️ Service Topology

A complete Ñkyel deployment runs four tightly coupled services orchestrated behind a single unified reverse proxy:

| Service | Port | Description |
| :--- | :--- | :--- |
| **Nginx** | `2026` | Unified reverse proxy & entrypoint for browser UI, SSE, and WebSocket streams |
| **Frontend** | `3000` | Next.js 15 App Router web interface (chat, workspace, browser view, terminals) |
| **Gateway API** | `8001` | FastAPI REST API + embedded LangGraph agent runtime engine |
| **Provisioner** | `8002` | Sandbox provisioner daemon (*optional, for Kubernetes/dynamic sandbox modes*) |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose v2** (Recommended)
- *Or for local bare-metal development*:
  - **Python 3.12+** with [`uv`](https://docs.astral.sh/uv/) installed
  - **Node.js 22+** with [`pnpm`](https://pnpm.io/)
  - **Nginx**

---

### Option 1: Docker (Fastest)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/smartandjai/nkyel-mcp.git
   cd nkyel-mcp
   ```

2. **Generate default configurations**:
   ```bash
   make config
   ```
   *This copies `config.example.yaml` to `config.yaml` and `extensions_config.example.json` to `extensions_config.json`.*

3. **Configure your API keys**:
   Edit `.env` (or `config.yaml`):
   ```bash
   cp .env.example .env
   # Add your LLM keys (OpenAI, Anthropic, RunPod, or Groq)
   ```

4. **Launch the stack**:
   ```bash
   make up
   ```
   Open **[http://localhost:2026](http://localhost:2026)** in your browser.

---

### Option 2: Local Development

1. **Initialize configurations & dependencies**:
   ```bash
   make config
   make install
   ```

2. **Run all services with hot-reload**:
   ```bash
   make dev
   ```
   *Starts the Gateway API (`:8001`), Next.js Dev Server (`:3000`), and local Nginx proxy (`:2026`).*

3. **Check service health**:
   ```bash
   make doctor
   ```

---

## ⚙️ Configuration & Secrets

Ñkyel uses two primary configuration files:

### 1. `config.yaml` (Core Runtime & Models)

Defines LLM providers, active models, sandbox drivers, and persistence backends:

```yaml
models:
  default: "qwen-32b"
  providers:
    - name: "runpod"
      type: "openai"
      base_url: "https://api.runpod.ai/v2/YOUR_POD_ID/openai/v1"
      api_key: "${RUNPOD_API_KEY}"
      models: ["qwen3-32b-awq"]
    - name: "groq"
      type: "openai"
      base_url: "https://api.groq.com/openai/v1"
      api_key: "${GROQ_API_KEY}"
      models: ["qwen-2.5-32b-instruct"]

sandbox:
  driver: "e2b"  # options: "e2b", "docker", "local"
  e2b_api_key: "${E2B_API_KEY}"
```

### 2. `extensions_config.json` (MCP & Extensible Skills)

Defines enabled Model Context Protocol (MCP) tools:

```json
{
  "mcp_servers": {
    "tavily": {
      "type": "sse",
      "url": "https://mcp.tavily.com/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_TAVILY_API_KEY"
      }
    },
    "google_drive": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"],
      "env": {
        "GOOGLE_CLIENT_ID": "...",
        "GOOGLE_CLIENT_SECRET": "..."
      }
    }
  }
}
```

---

## 📁 Repository Map

```
nkyel-mcp/
├── Makefile                     # Root developer orchestration commands
├── config.example.yaml          # Template for core Gateway & model configuration
├── extensions_config.example.json # Template for MCP server definitions
├── backend/                     # Python 3.12 Backend
│   ├── app/                     # FastAPI Gateway API, WebSockets, and IM channels
│   ├── packages/harness/        # nkyel-harness: LangGraph multi-agent core
│   ├── packages/extension-api/  # nkyel-extension-api: Extension contract interfaces
│   └── tests/                   # Backend TDD test suite
├── frontend/                    # Next.js 15 Frontend
│   ├── src/app/                 # App Router pages (Workspace, Chat, Auth, Settings)
│   ├── src/components/          # Shadcn UI, browser view, terminals, artifact viewer
│   └── src/core/                # Client state, streaming, and i18n
├── docker/                      # Dockerfiles, Nginx proxy configs, and Compose stacks
├── skills/                      # Built-in and custom agent skills
└── tests/                       # End-to-end integration and scenario tests
```

---

## 🛠️ Common Makefile Commands

| Command | Action |
| :--- | :--- |
| `make dev` | Start full local stack with hot-reloading (Gateway + Frontend + Nginx) |
| `make up` | Start full Docker production stack |
| `make down` | Stop running Docker containers |
| `make stop` | Stop local running services |
| `make doctor` | Run configuration, port, and dependency diagnostics |
| `make install` | Install all dependencies (Frontend `pnpm` + Backend `uv`) |
| `make test` | Run backend and frontend automated test suites |

---

## 🔒 Security & Privacy

- **Thread-Isolated Sandboxes**: Code and browser tasks run in isolated E2B microVMs or Docker containers, preventing execution leaks.
- **Sovereign Deployments**: Can be run entirely self-hosted with local LLMs (Ollama, vLLM) and on-premise PostgreSQL/MinIO.
- **Strict Network Routing**: Host environment variables and internal network endpoints are protected by proxy perimeter rules.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
