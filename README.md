nkyel
An AI agent you can watch, guide, and trust.

Un agent IA qui travaille devant vous, vous laisse le contrôle et livre des résultats concrets.

nkyel.smartandjai.com · SMARTANDJ AI Technologies

Project status: Competition demo and active development. This repository contains the independent nkyel MCP demo, built on ByteDance's open-source DeerFlow 2.0. It is not the commercial nkyel application. A configured integration or registered tool is not considered production-ready until its real end-to-end test passes.

What is nkyel?
nkyel is a general-purpose, visual AI-agent workspace. Instead of only answering questions, it coordinates tools, accesses authorized services, researches information, uses a cloud computer, creates professional deliverables, and asks for human approval before consequential actions.

The defining experience is simple: one conversation, one continuous mission, with the actual work visible to the user.

Example mission
“Find the report I saved in Google Drive months ago. Read it, research current developments from reliable sources, visit relevant websites, update the report, create a professional PDF, and prepare an email with the PDF attached. Ask for my approval before sending it.”

The intended workflow is:

Connect — Securely authorize the user's Google account when needed.
Discover — Locate and preview the real Drive file.
Research — Retrieve and cite sources with Tavily.
Browse — Visit relevant pages in a real E2B cloud browser, with visible navigation.
Create — Use DeerFlow skills and executable document tooling to produce an actual artifact.
Inspect — Preview rendered pages and apply justified, source-level corrections.
Approve — Show the Gmail draft, recipient, message, and real attachment for human review.
Execute — Send only after explicit approval and report the actual provider response.
Resume — Preserve authorized mission history and downloadable deliverables.
The visual workspace
The application is designed to keep every meaningful action connected to the conversation:

Surface	What the user sees
Chat & Mission	Instructions, agent progress, tool activity, and decisions
Connections	Google and other authorized accounts, scopes, and connection state
Research	Tavily queries, source cards, citations, and extracted findings
Computer	Real E2B browser/desktop stream, navigation, clicks, typing, and scrolling
Code & Console	Actual files, edits, executed commands, and sanitized output
Studio	Generated PDF, DOCX, PPTX, and XLSX artifacts and genuine previews
Approvals	Review, edit, reject, or approve consequential external actions
￼
No simulated tool success, fabricated website visits, or fake email-delivery claims. A service's response and an independently verified outcome are different forms of evidence.

Technology
Layer	Technology / approach
Agent runtime	ByteDance DeerFlow 2.0, LangGraph, native tools and skills
Agent model	DeepSeek for planning, tool use, and supported visual inspection
Simple chat	Qwen3 32B through a configured RunPod endpoint
External tools	Model Context Protocol (MCP) servers, clients, and adapters
Google Workspace	Gmail and Google Drive via authenticated, user-authorized integrations
Research	Tavily Search, Extract, Map, Crawl, and Research
Visual computer	E2B Desktop, with browser automation where appropriate
Real-time experience	Existing DeerFlow streaming, AG-UI integrations, A2UI and compatible MCP Apps
Document engine	DeerFlow skills with open-source PDF, Office, and rendering tools
Frontend	Next.js, TypeScript, responsive workspace UI
Identity	Clerk
Persistence	Neon PostgreSQL
Artifact storage	Cloudflare R2
Deployment	Docker / Docker Compose, reverse proxy, HTTPS
￼
The target is a catalog of 50 useful, verified MCP/native tool capabilities, not 50 nominal connections. Tools should be exposed to the model contextually and validated through real calls.

Architecture
User
nkyel Workspace · Next.js
Live activity · approvals ·previews
DeerFlow 2.0 · Agentorchestration
MCP tools · Gmail · Drive ·services
Tavily · Research
E2B Desktop · Browser ·Code
Artifact skills · Rendering ·QA
Neon · Mission state
Cloudflare R2 · Artifacts
Clerk · Identity
￼
￼
The interface reports real backend events, not animated substitutes for execution. Native app components can render tool results; MCP Apps are used when a connected MCP server actually exposes a compatible interactive UI resource.

Getting started
Requirements
Git and Docker with Docker Compose
A supported configuration of the DeerFlow backend and Next.js frontend
Credentials for whichever integrations you choose to enable
A dedicated environment for development and test data
Clone
Bash
￼
￼
git clone https://github.com/smartandjai/nkyel-mcp.git
cd nkyel-mcp
Configure
Use the example files present in the checked-out revision as the source of truth. Depending on the fork revision, configuration can include .env, backend/.env, config.yaml, and extensions_config.json.

Never commit real credentials. Store production secrets in protected deployment environment files or an appropriate secrets manager. Do not copy secrets into public configuration examples or terminal logs.

Run
Inspect the Compose manifests included in your revision before starting services:

Bash
￼
￼
find . -maxdepth 3 \( -name 'compose*.yaml' -o -name 'compose*.yml' -o -name 'docker-compose*.yaml' -o -name 'docker-compose*.yml' \)
Use the manifest, environment files, ports, and service names actually present in your revision. The competition deployment must run separately from the commercial nkyel stack. Never remove another project's containers, volumes, or databases to launch this demo.

Production verification
A green connection badge is not enough. An integration passes only with real evidence:

MCP: successful tools/list discovery and actual tools/call execution.
Drive: authenticated access to a real, authorized test file and correct retrieved content.
Tavily: genuine search/extraction results, with traceable source URLs.
E2B: actual browser session, real navigation, control actions, and a matching visible stream.
Artifacts: openable final files, validated previews, and accessible downloads.
Gmail: real draft, immutable approval of recipients/content/attachments, then provider-confirmed submission.
Persistence: reloadable mission state with correct per-user authorization.
The final acceptance scenario connects Drive → Research → E2B → Document → Approval → Gmail through the same visible agent mission. Until a step passes, it should be reported as not tested, partial, or blocked, rather than presented as complete.

Security and human control
User-specific OAuth authorization and least-privilege scopes.
No API keys, OAuth tokens, database credentials, or private files in this public repository.
Explicit human approval for sending emails and other consequential operations.
Per-user isolation of missions and artifacts.
Untrusted web pages, emails, and documents must not override user instructions.
Sensitive values are redacted from visible logs and agent activity feeds.
External actions are recorded with verifiable status and recoverable error handling.
Origins and acknowledgements
This demo builds upon ByteDance DeerFlow and integrates open-source and authorized external services. Upstream attribution and applicable third-party license notices must be preserved. Review the repository's actual license files and the licenses of dependencies before redistribution or deployment.

nkyel is developed by SMARTANDJ AI Technologies, with a vision of making capable AI agents transparent, useful, and responsive to human intent.

Website: smartandjai.com
