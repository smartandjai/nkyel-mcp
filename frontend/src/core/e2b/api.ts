import type {
  E2BStatusResponse,
  E2BEvent,
  E2BCodeRunResult,
  E2BTerminalResult,
  E2BFileItem,
  E2BDesktopActionResponse,
} from "./types";

const BASE_URL = "/api/nkyel/e2b";

export async function getE2BStatus(): Promise<E2BStatusResponse> {
  const res = await fetch(`${BASE_URL}/status`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch E2B status");
  return res.json();
}

export async function getE2BEvents(): Promise<E2BEvent[]> {
  const res = await fetch(`${BASE_URL}/events`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.events || [];
}

export async function runE2BCode(code: string, sandboxId?: string): Promise<E2BCodeRunResult> {
  const res = await fetch(`${BASE_URL}/run_code`, {
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
  const res = await fetch(`${BASE_URL}/terminal`, {
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
  const res = await fetch(`${BASE_URL}/files?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.items || [];
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
  const res = await fetch(`${BASE_URL}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sandbox_id: params.sandbox_id || "default",
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
