import type {
  E2BStatusResponse,
  E2BEvent,
  E2BCodeRunResult,
  E2BTerminalResult,
  E2BFileItem,
  E2BDesktopActionResponse,
  ComputerSessionResponse,
  ComputerActionParams,
} from "./types";

const E2B_BASE_URL = "/api/nkyel/e2b";
const COMPUTER_BASE_URL = "/api/nkyel/computer";

// ─── Unified Cloud Computer API (Thread-Bound) ───────────────────────────────

export async function getComputerSession(threadId: string): Promise<ComputerSessionResponse> {
  const res = await fetch(`${COMPUTER_BASE_URL}/session?thread_id=${encodeURIComponent(threadId)}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    return {
      active: false,
      thread_id: threadId,
      status: "NO_SESSION",
      stream_url: "",
      current_url: "",
      current_app: "Desktop",
    };
  }
  return res.json();
}

export async function startComputerSession(
  threadId: string,
  initialUrl = "https://example.com"
): Promise<ComputerSessionResponse> {
  const res = await fetch(`${COMPUTER_BASE_URL}/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId, initial_url: initialUrl }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Failed to start cloud computer");
  }
  return res.json();
}

export async function stopComputerSession(threadId: string): Promise<{ success: boolean }> {
  const res = await fetch(`${COMPUTER_BASE_URL}/stop?thread_id=${encodeURIComponent(threadId)}`, {
    method: "POST",
  });
  if (!res.ok) return { success: false };
  return res.json();
}

export async function executeComputerAction(params: ComputerActionParams): Promise<Record<string, unknown>> {
  const res = await fetch(`${COMPUTER_BASE_URL}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Failed to execute action ${params.action}`);
  }
  return res.json();
}

export async function executeComputerShell(
  threadId: string,
  command: string,
  workdir?: string
): Promise<E2BTerminalResult> {
  const res = await fetch(`${COMPUTER_BASE_URL}/shell`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId, command, workdir }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Failed to execute shell command");
  }
  return res.json();
}

export async function executeComputerPython(
  threadId: string,
  code: string,
  filename = "script.py"
): Promise<{ stdout: string; stderr: string; exit_code: number; duration_ms: number; filepath: string }> {
  const res = await fetch(`${COMPUTER_BASE_URL}/python`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId, code, filename }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Failed to execute Python script in computer");
  }
  return res.json();
}

export async function listComputerFiles(
  threadId: string,
  path = "/home/user"
): Promise<E2BFileItem[]> {
  const params = new URLSearchParams({ thread_id: threadId, path });
  const res = await fetch(`${COMPUTER_BASE_URL}/files?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.items ?? [];
}

export async function readComputerFile(
  threadId: string,
  path: string
): Promise<{ path: string; content: string }> {
  const params = new URLSearchParams({ thread_id: threadId, path });
  const res = await fetch(`${COMPUTER_BASE_URL}/read_file?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Could not read file");
  return res.json();
}

// ─── Legacy / Compatibility E2B Endpoints ────────────────────────────────────

export async function getE2BStatus(): Promise<E2BStatusResponse> {
  const res = await fetch(`${E2B_BASE_URL}/status`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch E2B status");
  return res.json();
}

export async function getE2BEvents(): Promise<E2BEvent[]> {
  const res = await fetch(`${E2B_BASE_URL}/events`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.events ?? [];
}

export async function runE2BCode(code: string, sandboxId?: string): Promise<E2BCodeRunResult> {
  const res = await fetch(`${E2B_BASE_URL}/run_code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, sandbox_id: sandboxId }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Failed to execute code in E2B microVM");
  }
  return res.json();
}

export async function runE2BTerminal(command: string, sandboxId?: string): Promise<E2BTerminalResult> {
  const res = await fetch(`${E2B_BASE_URL}/terminal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command, sandbox_id: sandboxId }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Failed to execute command in E2B microVM");
  }
  return res.json();
}

export async function listE2BFiles(path = "/home/user", sandboxId?: string): Promise<E2BFileItem[]> {
  const params = new URLSearchParams({ path });
  if (sandboxId) params.append("sandbox_id", sandboxId);
  const res = await fetch(`${E2B_BASE_URL}/files?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.items ?? [];
}

export async function executeE2BDesktopAction(
  action: "launch" | "navigate" | "click" | "scroll" | "type" | "screenshot" | "close",
  params: {
    sandbox_id?: string;
    url?: string;
    x?: number;
    y?: number;
    button?: string;
    direction?: string;
    amount?: number;
    text?: string;
    press_enter?: boolean;
  } = {}
): Promise<E2BDesktopActionResponse> {
  const res = await fetch(`${E2B_BASE_URL}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sandbox_id: params.sandbox_id ?? "default",
      action,
      ...params,
    }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Failed to execute desktop action in E2B");
  }
  return res.json();
}
