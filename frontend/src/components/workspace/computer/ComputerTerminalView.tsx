"use client";

import React, { useState, useRef, useEffect } from "react";
import { TerminalIcon, PlayIcon, Trash2Icon, CopyIcon, CheckIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { executeComputerShell } from "@/core/e2b/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface TerminalLog {
  id: string;
  command: string;
  stdout: string;
  stderr: string;
  exit_code: number;
  timestamp: string;
}

interface ComputerTerminalViewProps {
  threadId: string;
  logs?: TerminalLog[];
  className?: string;
}

export function ComputerTerminalView({ threadId, logs = [], className }: ComputerTerminalViewProps) {
  const [command, setCommand] = useState("");
  const [running, setRunning] = useState(false);
  const [localLogs, setLocalLogs] = useState<TerminalLog[]>(logs);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logs && logs.length > 0) {
      setLocalLogs(logs);
    }
  }, [logs]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [localLogs]);

  const handleRun = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!command.trim() || running) return;

    const cmd = command.trim();
    setRunning(true);
    try {
      const res = await executeComputerShell(threadId, cmd);
      const newEntry: TerminalLog = {
        id: `local-${Date.now()}`,
        command: cmd,
        stdout: res.stdout || "",
        stderr: res.stderr || "",
        exit_code: res.exit_code,
        timestamp: new Date().toLocaleTimeString(),
      };
      setLocalLogs((prev) => [...prev, newEntry]);
      setCommand("");
    } catch (err: any) {
      toast.error(err.message || "Erreur d'exécution de la commande");
    } finally {
      setRunning(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  return (
    <div className={cn("flex size-full flex-col bg-zinc-950 text-zinc-100 font-mono text-xs", className)}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900/70 px-3 py-1.5 text-zinc-400">
        <div className="flex items-center gap-2">
          <TerminalIcon className="h-3.5 w-3.5 text-emerald-400" />
          <span className="font-semibold text-zinc-200">Terminal Bash — E2B Sandbox (/home/user)</span>
        </div>
        <Button
          size="icon-sm"
          variant="ghost"
          onClick={() => setLocalLogs([])}
          className="h-6 w-6 text-zinc-400 hover:text-white"
          title="Effacer le terminal"
        >
          <Trash2Icon className="h-3 w-3" />
        </Button>
      </div>

      {/* Terminal Output Logs */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
        {localLogs.length === 0 ? (
          <div className="text-zinc-500 italic py-4">
            # Prêt. Les commandes exécutées par l'agent ou par vous apparaîtront ici.
          </div>
        ) : (
          localLogs.map((log) => (
            <div key={log.id} className="rounded border border-zinc-800/80 bg-zinc-900/50 p-2.5">
              <div className="flex items-center justify-between text-[11px] text-zinc-400 pb-1 border-b border-zinc-800/50">
                <span className="text-emerald-400 font-bold">$ {log.command}</span>
                <div className="flex items-center gap-2">
                  <span className={cn("text-[10px] px-1.5 py-0.2 rounded font-semibold", log.exit_code === 0 ? "bg-emerald-950/80 text-emerald-400 border border-emerald-800/60" : "bg-rose-950/80 text-rose-400 border border-rose-800/60")}>
                    code {log.exit_code}
                  </span>
                  <span className="text-[10px] text-zinc-500">{log.timestamp}</span>
                  <button
                    onClick={() => handleCopy(log.id, `${log.stdout}\n${log.stderr}`)}
                    className="hover:text-white"
                  >
                    {copiedId === log.id ? <CheckIcon className="h-3 w-3 text-emerald-400" /> : <CopyIcon className="h-3 w-3" />}
                  </button>
                </div>
              </div>

              {log.stdout && (
                <pre className="mt-1.5 whitespace-pre-wrap break-all text-zinc-300 leading-relaxed font-mono">
                  {log.stdout}
                </pre>
              )}

              {log.stderr && (
                <pre className="mt-1.5 whitespace-pre-wrap break-all text-rose-400 leading-relaxed font-mono">
                  {log.stderr}
                </pre>
              )}
            </div>
          ))
        )}
      </div>

      {/* Command prompt input */}
      <form onSubmit={handleRun} className="flex items-center gap-2 border-t border-zinc-800 bg-zinc-900/90 p-2">
        <span className="text-emerald-400 font-bold pl-1">$</span>
        <Input
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Exécuter une commande bash dans le même ordinateur..."
          disabled={running}
          className="h-8 flex-1 bg-zinc-950 font-mono text-xs text-zinc-200 border-zinc-800 focus-visible:ring-emerald-500/30"
        />
        <Button
          type="submit"
          size="sm"
          disabled={running || !command.trim()}
          className="h-8 gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs px-3"
        >
          <PlayIcon className="h-3 w-3 fill-current" />
          Exécuter
        </Button>
      </form>
    </div>
  );
}
