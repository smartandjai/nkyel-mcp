"use client";

import React, { useState } from "react";
import { Code2Icon, PlayIcon, CopyIcon, CheckIcon, Loader2Icon, FileCodeIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { executeComputerPython } from "@/core/e2b/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface ComputerCodeViewProps {
  threadId: string;
  initialCode?: string;
  className?: string;
}

const DEFAULT_PYTHON_SNIPPET = `# Script Python exécuté directement dans la microVM E2B
import datetime
import sys

print("Machine:", sys.platform)
print("Date & Heure:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("Cloud Sandbox: Connecté et synchronisé")
`;

export function ComputerCodeView({ threadId, initialCode, className }: ComputerCodeViewProps) {
  const [code, setCode] = useState(initialCode || DEFAULT_PYTHON_SNIPPET);
  const [filename, setFilename] = useState("script.py");
  const [executing, setExecuting] = useState(false);
  const [output, setOutput] = useState<{ stdout: string; stderr: string; exit_code: number; duration_ms: number } | null>(null);
  const [copied, setCopied] = useState(false);

  const handleRun = async () => {
    if (!code.trim() || executing) return;
    setExecuting(true);
    try {
      const res = await executeComputerPython(threadId, code, filename);
      setOutput(res);
      toast.success(`Exécution terminée (${res.duration_ms}ms)`);
    } catch (e: any) {
      toast.error(e.message || "Erreur d'exécution Python");
    } finally {
      setExecuting(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className={cn("flex size-full flex-col bg-zinc-950 text-zinc-100 font-mono text-xs", className)}>
      {/* Top toolbar */}
      <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900/80 px-3 py-2">
        <div className="flex items-center gap-2">
          <FileCodeIcon className="h-4 w-4 text-amber-400" />
          <span className="font-semibold text-zinc-200">Éditeur & Interpréteur Python 3</span>
          <span className="text-[11px] text-zinc-500 font-mono">(/home/user/{filename})</span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleCopy}
            className="h-7 text-xs text-zinc-400 hover:text-white gap-1"
          >
            {copied ? <CheckIcon className="h-3.5 w-3.5 text-emerald-400" /> : <CopyIcon className="h-3.5 w-3.5" />}
            Copier
          </Button>

          <Button
            size="sm"
            onClick={handleRun}
            disabled={executing || !code.trim()}
            className="h-7 gap-1.5 bg-amber-600 hover:bg-amber-500 text-white font-mono text-xs px-3"
          >
            {executing ? <Loader2Icon className="h-3.5 w-3.5 animate-spin" /> : <PlayIcon className="h-3.5 w-3.5 fill-current" />}
            Exécuter Script
          </Button>
        </div>
      </div>

      {/* Code Editor */}
      <div className="flex-1 p-2 overflow-hidden flex flex-col">
        <Textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="# Écrivez votre code Python ici..."
          className="size-full resize-none bg-zinc-900/60 font-mono text-xs leading-relaxed text-zinc-200 border-zinc-800/80 focus-visible:ring-amber-500/30 p-3"
          spellCheck={false}
        />
      </div>

      {/* Execution Output Panel */}
      {output && (
        <div className="h-44 border-t border-zinc-800 bg-zinc-950 p-3 overflow-y-auto">
          <div className="flex items-center justify-between text-[11px] pb-1 border-b border-zinc-800 text-zinc-400">
            <span className="font-bold text-zinc-300">Sortie de la MicroVM ({output.duration_ms}ms)</span>
            <span className={cn("px-1.5 py-0.5 rounded text-[10px] font-semibold", output.exit_code === 0 ? "bg-emerald-950 text-emerald-400 border border-emerald-800/60" : "bg-rose-950 text-rose-400 border border-rose-800/60")}>
              Exit Code: {output.exit_code}
            </span>
          </div>

          {output.stdout && (
            <pre className="mt-2 text-emerald-300 whitespace-pre-wrap break-all leading-relaxed font-mono">
              {output.stdout}
            </pre>
          )}

          {output.stderr && (
            <pre className="mt-2 text-rose-400 whitespace-pre-wrap break-all leading-relaxed font-mono">
              {output.stderr}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
