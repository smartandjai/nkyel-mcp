"use client";

import React, { useState, useRef, useEffect } from "react";
import { TerminalIcon, PlayIcon, Trash2Icon, Loader2Icon, CheckCircle2Icon, AlertCircleIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { runE2BTerminal } from "@/core/e2b/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface TerminalLine {
  id: string;
  command: string;
  stdout?: string;
  stderr?: string;
  exitCode?: number;
  timeMs?: number;
}

export function E2BTerminalViewer({ className }: { className?: string }) {
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState<TerminalLine[]>([
    {
      id: "initial-1",
      command: "uname -a && cat /etc/os-release | grep PRETTY_NAME",
      stdout: "Linux e2b-cloud-sandbox 6.6.137 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux\nPRETTY_NAME=\"Debian GNU/Linux 13 (trixie)\"",
      exitCode: 0,
      timeMs: 120,
    },
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleRun = async (cmdToRun = command) => {
    const cmd = cmdToRun.trim();
    if (!cmd || loading) return;

    setLoading(true);
    setCommand("");

    try {
      const res = await runE2BTerminal(cmd);
      setHistory((prev) => [
        ...prev,
        {
          id: `cmd-${Date.now()}`,
          command: cmd,
          stdout: res.stdout,
          stderr: res.stderr,
          exitCode: res.exit_code,
          timeMs: res.execution_time_ms,
        },
      ]);
    } catch (e: any) {
      toast.error(e.message || "Erreur d'exécution de la commande");
      setHistory((prev) => [
        ...prev,
        {
          id: `cmd-${Date.now()}`,
          command: cmd,
          stderr: e.message,
          exitCode: 1,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("flex flex-col h-full bg-neutral-950 font-mono text-xs text-neutral-200", className)}>
      {/* Terminal Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-neutral-800 bg-neutral-900/80 text-[11px]">
        <div className="flex items-center gap-2">
          <TerminalIcon className="size-3.5 text-emerald-400" />
          <span className="font-semibold text-neutral-200">Terminal Bash — E2B MicroVM</span>
          <span className="rounded bg-emerald-950/60 border border-emerald-500/40 text-[10px] px-1.5 py-0.2 text-emerald-300">
            root@e2b-sandbox
          </span>
        </div>

        <Button
          size="sm"
          variant="ghost"
          onClick={() => setHistory([])}
          className="h-6 px-2 text-[10px] text-neutral-400 hover:text-neutral-100"
          title="Effacer l'historique"
        >
          <Trash2Icon className="size-3 mr-1" />
          Effacer
        </Button>
      </div>

      {/* Preset Chips */}
      <div className="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-900/40 border-b border-neutral-800/80 text-[10px] overflow-x-auto select-none">
        <span className="text-neutral-500 font-sans">Commandes :</span>
        {["ls -la /home/user", "python3 --version", "df -h", "free -m", "ps aux"].map((cmd) => (
          <button
            key={cmd}
            onClick={() => handleRun(cmd)}
            disabled={loading}
            className="rounded bg-neutral-800/70 px-2 py-0.5 hover:bg-neutral-700 text-neutral-300 transition-colors whitespace-nowrap"
          >
            {cmd}
          </button>
        ))}
      </div>

      {/* Terminal Output Log */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 font-mono text-[11px] leading-relaxed select-text">
        {history.map((item) => (
          <div key={item.id} className="space-y-1">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold">
              <span className="text-neutral-500">user@e2b:~$</span>
              <span className="text-neutral-100">{item.command}</span>
              {item.timeMs !== undefined && (
                <span className="text-[9px] text-neutral-500 ml-auto font-sans">
                  {item.timeMs}ms
                </span>
              )}
            </div>

            {item.stdout && (
              <pre className="text-neutral-300 whitespace-pre-wrap break-all pl-2 border-l border-neutral-800">
                {item.stdout}
              </pre>
            )}

            {item.stderr && (
              <pre className="text-rose-400 whitespace-pre-wrap break-all pl-2 border-l border-rose-800/60">
                {item.stderr}
              </pre>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-neutral-400 italic">
            <Loader2Icon className="size-3 animate-spin text-emerald-400" />
            <span>Exécution en cours dans la microVM E2B...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Terminal Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleRun();
        }}
        className="flex items-center gap-2 p-2 border-t border-neutral-800 bg-neutral-900"
      >
        <span className="text-emerald-400 font-bold pl-1">$</span>
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Entrez une commande bash..."
          disabled={loading}
          className="flex-1 bg-transparent text-neutral-100 focus:outline-none text-[11px] font-mono"
        />
        <Button
          type="submit"
          size="sm"
          disabled={loading || !command.trim()}
          className="h-7 px-3 text-[11px] bg-emerald-600 hover:bg-emerald-500 text-white font-medium gap-1"
        >
          {loading ? <Loader2Icon className="size-3 animate-spin" /> : <PlayIcon className="size-3" />}
          Lancer
        </Button>
      </form>
    </div>
  );
}
