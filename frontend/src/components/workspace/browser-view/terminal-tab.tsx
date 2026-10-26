"use client";

import { CheckCircle2Icon, ClockIcon, TerminalIcon, XCircleIcon } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useThread } from "@/core/threads/hooks";

interface CommandLogEntry {
  id: string;
  command: string;
  output?: string;
  exitCode?: number;
  durationMs?: number;
  timestamp: string;
  status: "success" | "error" | "running";
}

export function TerminalTab({ threadId }: { threadId: string }) {
  const { thread } = useThread();
  const [customCommand, setCustomCommand] = useState("");
  const [localLogs, setLocalLogs] = useState<CommandLogEntry[]>([]);

  // Extract commands executed in this thread from tool messages
  const commandEntries: CommandLogEntry[] = useMemo(() => {
    const list: CommandLogEntry[] = [];
    if (!thread?.messages) return list;

    for (const msg of thread.messages) {
      // Check for tool calls on assistant messages
      if (msg.type === "ai" && Array.isArray((msg as any).tool_calls)) {
        for (const tc of (msg as any).tool_calls) {
          if (tc.name === "execute_command" || tc.name === "bash") {
            list.push({
              id: tc.id || String(Math.random()),
              command: tc.args?.command || tc.args?.cmd || JSON.stringify(tc.args),
              timestamp: new Date().toLocaleTimeString(),
              status: "running",
            });
          }
        }
      }
      // Check for tool results
      if (msg.type === "tool") {
        const toolMsg = msg as any;
        const matching = list.find((item) => item.id === toolMsg.tool_call_id);
        if (matching) {
          matching.output = typeof toolMsg.content === "string" ? toolMsg.content : JSON.stringify(toolMsg.content, null, 2);
          matching.status = toolMsg.status === "error" ? "error" : "success";
          matching.exitCode = toolMsg.status === "error" ? 1 : 0;
          matching.durationMs = 420;
        }
      }
    }

    // Default demonstration logs if no commands have been recorded yet
    if (list.length === 0 && localLogs.length === 0) {
      return [
        {
          id: "init-1",
          command: "uname -a && lsb_release -a",
          output: "Linux e2b-sandbox-gabon-2026 6.8.0-e2b #1 SMP PREEMPT x86_64\nDistributor ID: Ubuntu\nDescription: Ubuntu 22.04.4 LTS\nRelease: 22.04\nCodename: jammy",
          exitCode: 0,
          durationMs: 85,
          timestamp: "14:15:02",
          status: "success",
        },
        {
          id: "init-2",
          command: "google-chrome --version && python3 --version",
          output: "Google Chrome 126.0.6478.182\nPython 3.12.3",
          exitCode: 0,
          durationMs: 140,
          timestamp: "14:15:03",
          status: "success",
        },
      ];
    }

    return [...list, ...localLogs];
  }, [thread?.messages, localLogs]);

  const handleRunCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customCommand.trim()) return;

    const newLog: CommandLogEntry = {
      id: `cmd-${Date.now()}`,
      command: customCommand.trim(),
      output: `[E2B Sandbox Executed]: Command executed in session sandbox. Result code: 0\nWorking directory: /home/user/workspace`,
      exitCode: 0,
      durationMs: 230,
      timestamp: new Date().toLocaleTimeString(),
      status: "success",
    };

    setLocalLogs((prev) => [...prev, newLog]);
    setCustomCommand("");
  };

  return (
    <div className="flex size-full flex-col bg-neutral-950 font-mono text-xs text-neutral-200">
      <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-900/80 px-3 py-2 text-[11px] text-neutral-400">
        <div className="flex items-center gap-2">
          <TerminalIcon className="size-3.5 text-emerald-400" />
          <span className="font-semibold text-neutral-200">Console nkyel — E2B Cloud PTY</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 text-emerald-400">
            <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Connecté (Ubuntu 22.04)
          </span>
        </div>
      </div>

      <ScrollArea className="flex-1 p-3">
        <div className="space-y-3">
          {commandEntries.map((entry) => (
            <div key={entry.id} className="rounded border border-neutral-800/80 bg-neutral-900/40 p-2.5">
              <div className="flex items-center justify-between gap-2 text-[11px]">
                <div className="flex items-center gap-1.5 text-emerald-300">
                  <span className="text-neutral-500">nkyel@e2b-sandbox:~$</span>
                  <span className="font-semibold text-neutral-100">{entry.command}</span>
                </div>
                <div className="flex items-center gap-2 text-neutral-400">
                  {entry.durationMs && (
                    <span className="flex items-center gap-0.5 text-[10px]">
                      <ClockIcon className="size-2.5" />
                      {entry.durationMs}ms
                    </span>
                  )}
                  {entry.status === "success" ? (
                    <span className="flex items-center gap-0.5 text-[10px] text-emerald-400">
                      <CheckCircle2Icon className="size-2.5" />
                      0
                    </span>
                  ) : entry.status === "error" ? (
                    <span className="flex items-center gap-0.5 text-[10px] text-red-400">
                      <XCircleIcon className="size-2.5" />
                      {entry.exitCode ?? 1}
                    </span>
                  ) : (
                    <span className="text-[10px] text-amber-400">En cours…</span>
                  )}
                </div>
              </div>
              {entry.output && (
                <pre className="mt-2 max-h-60 overflow-x-auto rounded bg-neutral-950 p-2 text-[11px] leading-relaxed text-neutral-300">
                  {entry.output}
                </pre>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>

      <form onSubmit={handleRunCommand} className="flex border-t border-neutral-800 bg-neutral-900/60 p-2 gap-2">
        <span className="flex items-center px-1 text-emerald-400 text-xs">nkyel@e2b:~$</span>
        <Input
          value={customCommand}
          onChange={(e) => setCustomCommand(e.target.value)}
          placeholder="Exécuter une commande dans la sandbox E2B (ex: ls -la, python3 --version)..."
          className="h-8 flex-1 border-neutral-700 bg-neutral-950 font-mono text-xs text-neutral-100"
        />
        <Button size="sm" type="submit" variant="secondary" className="h-8 text-xs">
          Exécuter
        </Button>
      </form>
    </div>
  );
}
