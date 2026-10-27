# Ñkyel — Plateforme Souveraine de Super-Agents Autonomes

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](./backend/pyproject.toml)
[![Next.js](https://img.shields.io/badge/Next.js-15%2B-000000?logo=next.js&logoColor=white)](./frontend/package.json)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF6F00?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![MCP](https://img.shields.io/badge/Protocole-MCP-8A2BE2)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Prêt-2496ED?logo=docker&logoColor=white)](./docker/)
[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](./LICENSE)

**Plateforme d'agents IA autonomes souveraine et open source combinant LangGraph, Next.js, FastAPI, des bacs à sable isolés et le Model Context Protocol (MCP).**

[English](./README.md) | [Français](./README_fr.md) | [Documentation](https://nkyel.smartandjai.com)

</div>

---

## 🌟 Qu'est-ce que Ñkyel ?

**Ñkyel** est une infrastructure de **Super-Agents** (SuperAgent Harness) conçue dès l'origine pour exécuter des missions autonomes complexes, des recherches approfondies, de l'exécution de code sécurisée et des opérations en environnement réel.

Contrairement aux simples surcouches de chat, Ñkyel coordonne des **sous-agents spécialisés**, conserve une **mémoire contextuelle à long terme**, exécute du code dans des **bacs à sable isolés (sandboxes)**, navigue visuellement sur le Web avec un véritable navigateur (**E2B Cloud Desktop & Tavily**), et s'interface avec vos outils d'entreprise grâce au standard **Model Context Protocol (MCP)**.

```
+-----------------------------------------------------------------------------------+
|                                INTERFACE UTILISATEUR                              |
|                      Next.js 15 (TailwindCSS, Radix, Streaming SSE)               |
+-----------------------------------------+-----------------------------------------+
                                          | :2026 (Reverse Proxy Nginx)
+-----------------------------------------v-----------------------------------------+
|                                    GATEWAY API                                    |
|                   FastAPI + Moteur d'Exécution d'Agents LangGraph                 |
+-------------------+---------------------+--------------------+--------------------+
|  Cœur des Agents  |  Bacs à sable (VM)  |  Connecteurs MCP   | Stockage & Checkpt |
|  - Planificateur  |  - E2B Desktop      |  - Google Drive    | - PostgreSQL       |
|  - Sous-agents    |  - Docker Sandbox   |  - Recherche Tavily| - SQLite           |
|  - Mémoire Context|  - Terminal Local   |  - Gmail / Slack   | - Cloudflare R2    |
+-------------------+---------------------+--------------------+--------------------+
```

---

## ✨ Fonctionnalités Clés

- 🧠 **Orchestration Multi-Agents LangGraph** : Graphes d'états avancés, sous-agents spécialisés, compactage dynamique du contexte, validation humaine dans la boucle (HITL) et persistance par checkpoints.
- 🔌 **Intégration Native Model Context Protocol (MCP)** : Connexion immédiate de serveurs MCP standards (Google Drive, Gmail, GitHub, Tavily, PostgreSQL, Slack, système de fichiers, etc.) en mode `stdio` ou `SSE/HTTP`.
- 🖥️ **Bacs à Sable Isolés & Navigation Visuelle (Computer Use)** : Navigation web Chrome réelle et exécution sécurisée en ligne de commande via **E2B Cloud Desktop** ou conteneurs Docker isolés.
- 📊 **Génération Automatique de Livrables d'Entreprise** : Compilation de rapports de synthèse en **PDF professionnels avec Typst 0.15**, documents Markdown et visualisations interactives.
- 🌐 **Routage Multi-LLM Souverain** : Aucun verrouillage fournisseur. Support natif de **RunPod** (Qwen3 / DeepSeek auto-hébergé), **Groq**, **Anthropic Claude**, **OpenAI**, **Ollama**, ou toute passerelle compatible OpenAI.
- 💾 **Persistance et Stockage Haute Disponibilité** : Persistance transactionnelle via **PostgreSQL (Neon)** ou SQLite, avec sauvegarde des artéfacts sur **Cloudflare R2** / Amazon S3.
- 💬 **Passerelle Omnicanale** : Déploiement direct de vos agents sur vos canaux de discussion : **Slack**, **Telegram**, **Lark/Feishu**, **DingTalk** et **WeCom**.

---

## 🏗️ Architecture des Services

Une pile complète Ñkyel orchestre quatre services complémentaires via un reverse proxy unifié :

| Service | Port | Rôle |
| :--- | :--- | :--- |
| **Nginx** | `2026` | Point d'entrée unique & Reverse proxy (UI Web, flux SSE, WebSockets) |
| **Frontend** | `3000` | Interface utilisateur Next.js 15 (Espace de travail, chat, artéfacts, terminaux) |
| **Gateway API** | `8001` | API REST FastAPI + moteur d'exécution d'agents LangGraph |
| **Provisioner** | `8002` | Gestionnaire de bacs à sable (*optionnel, pour environnements Kubernetes/dynamiques*) |

---

## 🚀 Démarrage Rapide

### Prérequis

- **Docker** & **Docker Compose v2** (Méthode recommandée)
- *Ou pour un développement local direct* :
  - **Python 3.12+** avec [`uv`](https://docs.astral.sh/uv/)
  - **Node.js 22+** avec [`pnpm`](https://pnpm.io/)
  - **Nginx**

---

### Option 1 : Docker (Recommandé)

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/smartandjai/nkyel-mcp.git
   cd nkyel-mcp
   ```

2. **Générer les fichiers de configuration par défaut** :
   ```bash
   make config
   ```
   *Cette commande crée `config.yaml` et `extensions_config.json` à partir des modèles d'exemples.*

3. **Définir vos variables d'environnement** :
   ```bash
   cp .env.example .env
   # Renseignez vos clés API LLM (RunPod, Groq, OpenAI, Anthropic...)
   ```

4. **Démarrer l'ensemble de la pile** :
   ```bash
   make up
   ```
   Accédez à l'application sur **[http://localhost:2026](http://localhost:2026)**.

---

### Option 2 : Développement Local

1. **Installer les dépendances et générer les configurations** :
   ```bash
   make config
   make install
   ```

2. **Lancer les services avec rechargement à chaud (Hot-Reload)** :
   ```bash
   make dev
   ```
   *Démarre l'API Gateway (`:8001`), le serveur Next.js (`:3000`) et le proxy Nginx (`:2026`).*

3. **Diagnostiquer l'environnement** :
   ```bash
   make doctor
   ```

---

## ⚙️ Configuration & Outils MCP

### 1. `config.yaml` (Moteurs LLM & Runtime)

Configurez vos fournisseurs d'inférence, modèles et bacs à sable :

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
  driver: "e2b"  # options : "e2b", "docker", "local"
  e2b_api_key: "${E2B_API_KEY}"
```

### 2. `extensions_config.json` (Serveurs MCP & Outils)

Déclarez vos serveurs Model Context Protocol :

```json
{
  "mcp_servers": {
    "tavily": {
      "type": "sse",
      "url": "https://mcp.tavily.com/mcp/",
      "headers": {
        "Authorization": "Bearer VOTRE_CLE_TAVILY"
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

## 📁 Structure du Projet

```
nkyel-mcp/
├── Makefile                     # Commandes d'orchestration principales
├── config.example.yaml          # Modèle de configuration du Gateway et des LLMs
├── extensions_config.example.json # Modèle de configuration des serveurs MCP
├── backend/                     # Backend Python 3.12
│   ├── app/                     # Gateway FastAPI, WebSockets et bots de messagerie
│   ├── packages/harness/        # nkyel-harness : Cœur multi-agents LangGraph
│   ├── packages/extension-api/  # nkyel-extension-api : Interfaces publiques d'extension
│   └── tests/                   # Suite de tests unitaires et d'intégration
├── frontend/                    # Frontend Next.js 15
│   ├── src/app/                 # Pages App Router (Espace de travail, Chat, Auth)
│   ├── src/components/          # Composants UI, visionneuse d'artéfacts et terminaux
│   └── src/core/                # Gestion d'état, streaming SSE et internationalisation
├── docker/                      # Fichiers Dockerfile, proxy Nginx et Docker Compose
├── skills/                      # Compétences d'agents intégrées et personnalisées
└── tests/                       # Scénarios de tests end-to-end multi-outils
```

---

## 🛠️ Commandes Utiles (Makefile)

| Commande | Action |
| :--- | :--- |
| `make dev` | Démarre la pile complète en mode développement avec rechargement automatique |
| `make up` | Lance la pile de production sous Docker |
| `make down` | Arrête et nettoie les conteneurs Docker |
| `make stop` | Arrête les services locaux en cours d'exécution |
| `make doctor` | Lance les vérifications système, réseaux et de dépendances |
| `make install` | Installe l'ensemble des dépendances (Frontend `pnpm` + Backend `uv`) |
| `make test` | Exécute la suite de tests automatisés (Backend et Frontend) |

---

## 📄 Licence

Ce projet est distribué sous licence open source [MIT](./LICENSE).
