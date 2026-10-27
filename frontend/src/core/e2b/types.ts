export interface E2BStatusResponse {
  connected: boolean;
  api_key_configured: boolean;
  engine: string;
  capabilities: string[];
  active_desktop_sessions: string[];
  active_code_sessions: string[];
  total_active: number;
}

export interface E2BEvent {
  id: string;
  type: "system" | "code" | "terminal" | "desktop" | "microvm";
  title: string;
  details: string;
  status: "success" | "error" | "running";
  timestamp: string;
}

export interface E2BResultItem {
  type: string;
  data: string;
}

export interface E2BCodeRunResult {
  sandbox_id: string;
  stdout: string[];
  stderr: string[];
  results: E2BResultItem[];
  error?: string | null;
  execution_time_ms: number;
  status: "COMPLETED" | "ERROR";
}

export interface E2BTerminalResult {
  sandbox_id: string;
  command: string;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time_ms: number;
}

export interface E2BFileItem {
  name: string;
  type: "file" | "dir";
  path: string;
}

export interface E2BDesktopActionResponse {
  sandbox_id: string;
  current_url?: string;
  stream_url?: string;
  screenshot_base64?: string;
  status?: string;
  error?: string;
}
