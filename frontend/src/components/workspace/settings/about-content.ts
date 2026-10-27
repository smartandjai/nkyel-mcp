/**
 * About nkyel markdown content. Inlined to avoid raw-loader dependency
 * (Turbopack cannot resolve raw-loader for .md imports).
 */
import { APP_VERSION } from "@/version";

export const aboutMarkdown = `# [About Ñkyel AI ${APP_VERSION}](https://nkyel.smartandjai.com)

> **Sovereign Agent Harness & Super Intelligence Platform**

Ñkyel AI is an advanced **super agent harness** that orchestrates **sub-agents**, **memory**, and **cloud sandboxes** to solve complex real-world tasks — powered by **extensible sovereign skills**.

---

## 🚀 Core Features

* **Skills & Tools**: Built-in and extensible skills (Tavily search & crawl, E2B cloud browser, document generation).
* **Sub-Agents**: Sub-Agents help the main agent to execute tasks with isolated context.
* **Sandbox & File System**: Safely execute code, control real browsers, and manipulate files in E2B sandboxes.
* **Context Engineering**: Sharp context windows through streaming compaction and summarization.
* **Sovereign Persistence**: Mission history and checkpoints persisted securely in Neon PostgreSQL and Cloudflare R2.

---

## 🌐 Official Platform

Explore Ñkyel AI: [nkyel.smartandjai.com](https://nkyel.smartandjai.com)


## 🌐 Official Platform

Visit the official platform of Ñkyel AI: [nkyel.smartandjai.com](https://nkyel.smartandjai.com)

## 📧 Support

Contact the engineering team at [contact@smartandjai.com](mailto:contact@smartandjai.com).

---

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

Without their vision, passion and dedication, \`nkyel\` would not be what it is today.
`;
