"use client";

import React from "react";
import {
  ActivityIcon,
  CheckCircle2Icon,
  XCircleIcon,
  Loader2Icon,
  TerminalIcon,
  GlobeIcon,
  MonitorIcon,
  FileCodeIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ActionEvent {
  id: string;
  type: string;
  action: string;
  details: string;
  status: string;
  timestamp: string;
}

interface ComputerActivityFeedProps {
  events?: ActionEvent[];
  className?: string;
}

export function ComputerActivityFeed({ events = [], className }: ComputerActivityFeedProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case "browser":
        return <GlobeIcon className="h-3.5 w-3.5 text-blue-400" />;
      case "terminal":
        return <TerminalIcon className="h-3.5 w-3.5 text-emerald-400" />;
      case "code":
        return <FileCodeIcon className="h-3.5 w-3.5 text-amber-400" />;
      case "desktop":
        return <MonitorIcon className="h-3.5 w-3.5 text-purple-400" />;
      default:
        return <ActivityIcon className="h-3.5 w-3.5 text-primary" />;
    }
  };

  return (
    <div className={cn("flex size-full flex-col bg-zinc-950 text-zinc-100 font-mono text-xs overflow-y-auto p-3 space-y-2", className)}>
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800 text-zinc-400">
        <ActivityIcon className="h-4 w-4 text-primary" />
        <span className="font-semibold text-zinc-200">Journal d'Activité de l'Agent</span>
      </div>

      {events.length === 0 ? (
        <div className="text-zinc-500 italic py-6 text-center">
          Aucun événement d'exécution enregistré pour le moment.
        </div>
      ) : (
        events.map((evt) => (
          <div
            key={evt.id}
            className="flex items-start gap-2.5 rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-2.5 transition hover:bg-zinc-900/70"
          >
            <div className="mt-0.5 shrink-0">{getIcon(evt.type)}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-semibold text-zinc-200">{evt.action}</span>
                <span className="text-[10px] text-zinc-500">{evt.timestamp}</span>
              </div>
              <p className="mt-0.5 text-zinc-400 text-xs break-words">{evt.details}</p>
            </div>
            <div className="shrink-0 mt-0.5">
              {evt.status === "success" ? (
                <CheckCircle2Icon className="h-3.5 w-3.5 text-emerald-400" />
              ) : evt.status === "error" ? (
                <XCircleIcon className="h-3.5 w-3.5 text-rose-400" />
              ) : (
                <Loader2Icon className="h-3.5 w-3.5 animate-spin text-amber-400" />
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
