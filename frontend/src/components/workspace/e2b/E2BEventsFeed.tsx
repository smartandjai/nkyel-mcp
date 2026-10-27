"use client";

import React, { useState, useEffect } from "react";
import { ActivityIcon, CheckCircle2Icon, AlertCircleIcon, Loader2Icon, RefreshCwIcon } from "lucide-react";
import { getE2BEvents } from "@/core/e2b/api";
import { type E2BEvent } from "@/core/e2b/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function E2BEventsFeed({ className }: { className?: string }) {
  const [events, setEvents] = useState<E2BEvent[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchEvents = async () => {
    try {
      const data = await getE2BEvents();
      setEvents(data);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={cn("flex flex-col h-full bg-neutral-950 font-sans text-xs text-neutral-200", className)}>
      <div className="flex items-center justify-between px-3 py-2 border-b border-neutral-800 bg-neutral-900/80">
        <div className="flex items-center gap-2">
          <ActivityIcon className="size-3.5 text-emerald-400" />
          <span className="font-semibold text-neutral-200">Journal d'Activité en Direct — IA & E2B</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] text-emerald-400 font-medium">Flux temps réel</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {events.length === 0 ? (
          <div className="text-center p-8 text-neutral-500 text-xs">
            En attente des actions de l'agent...
          </div>
        ) : (
          events.map((evt) => (
            <div
              key={evt.id}
              className="p-2.5 rounded-lg border border-neutral-800/80 bg-neutral-900/40 space-y-1 hover:border-neutral-700 transition-all"
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-1.5 min-w-0">
                  {evt.status === "error" ? (
                    <AlertCircleIcon className="size-3.5 text-rose-500 shrink-0" />
                  ) : evt.status === "running" ? (
                    <Loader2Icon className="size-3.5 animate-spin text-primary shrink-0" />
                  ) : (
                    <CheckCircle2Icon className="size-3.5 text-emerald-500 shrink-0" />
                  )}
                  <span className="font-semibold text-neutral-200 text-[11px] truncate">
                    {evt.title}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <Badge
                    variant="outline"
                    className="text-[9px] px-1 py-0 uppercase tracking-wider border-neutral-700 text-neutral-400"
                  >
                    {evt.type}
                  </Badge>
                  <span className="text-[10px] text-neutral-500 font-mono">{evt.timestamp}</span>
                </div>
              </div>
              <p className="text-[11px] text-neutral-400 pl-5 font-mono break-all">{evt.details}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
