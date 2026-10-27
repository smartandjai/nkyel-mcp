# Ñkyel 2.0 — Local Sovereign Agent Platform

> **SuperAgent Harness — Stack Locale & Souveraine**

**Ñkyel** est une plateforme d'agents autonomes orchestrée avec LangGraph, Next.js et des environnements isolés.
Elle intègre directement :

* **Authentification & Sessions** : Clerk (`clerk.smartandjai.com`)
* **Persistance des Missions & Checkpoints** : Neon PostgreSQL (`neondb`)
* **Stockage Sécurisé des Livrables** : Cloudflare R2 (`nkyel-artifacts-prod`)
* **Moteur Agent Principal** : Qwen3 32B AWQ sur RunPod
* **Moteur Rapide Conversationnel** : Qwen 27B sur Groq Free
* **Recherche & Exploration Web** : Tavily API (Search, Extract, Map, Crawl)
* **Exécution & Navigation Réelle** : Bac à sable E2B Cloud Desktop

---

## 💻 Architecture de l'Application Locale

* **Gateway API & Runtime** : FastAPI + Embedded LangGraph (`localhost:8001`)
* **Interface Web** : Next.js App Router (`localhost:3000`)
* **Reverse Proxy Unifié** : Nginx (`localhost:2026`)


## 📜 License

nkyel is proudly open source and distributed under the **MIT License**.

---

## 🙌 Acknowledgments

We extend our heartfelt gratitude to the open source projects and contributors who have made nkyel a reality. We truly stand on the shoulders of giants.

### Core Frameworks

- **[LangChain](https://github.com/langchain-ai/langchain)**: A phenomenal framework that powers our LLM interactions and chains.
- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Enabling sophisticated multi-agent orchestration.
- **[Next.js](https://nextjs.org/)**: A cutting-edge framework for building web applications.

### UI Libraries

- **[Shadcn](https://ui.shadcn.com/)**: Minimalistic components that power our UI.
- **[SToneX](https://github.com/stonexer)**: For his invaluable contribution to token-by-token visual effects.

These outstanding projects form the backbone of nkyel and exemplify the transformative power of open source collaboration.

### Special Thanks

Finally, we want to express our heartfelt gratitude to the core authors of nkyel 1.0 and 2.0:

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

Without their vision, passion and dedication, `nkyel` would not be what it is today.
