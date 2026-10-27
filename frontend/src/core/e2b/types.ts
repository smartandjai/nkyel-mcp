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
  type: "system" | "code" | "terminal" | "desktop" | "microvm" | "browser" | "control";
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

export interface ComputerSessionResponse {
  active: boolean;
  thread_id: string;
  sandbox_id?: string;
  status: "STARTING" | "LIVE" | "AGENT_CONTROLLING" | "USER_CONTROLLING" | "PAUSED" | "CLOSED" | "FAILED" | "NO_SESSION";
  stream_url: string;
  current_url: string;
  current_app: string;
  screenshot_base64?: string | null;
  terminal_logs?: Array<{
    id: string;
    command: string;
    stdout: string;
    stderr: string;
    exit_code: number;
    timestamp: string;
  }>;
  events?: Array<{
    id: string;
    type: string;
    action: string;
    details: string;
    status: string;
    timestamp: string;
  }>;
}

export interface ComputerActionParams {
  thread_id: string;
  action: "click" | "move" | "type" | "keypress" | "scroll" | "navigate" | "screenshot" | "takeover" | "release_control";
  x?: number;
  y?: number;
  button?: "left" | "right" | "double";
  text?: string;
  key?: string;
  url?: string;
  direction?: "up" | "down";
  amount?: number;
  press_enter?: boolean;
}
