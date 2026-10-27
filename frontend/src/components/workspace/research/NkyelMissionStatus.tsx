"use client";

import React from "react";
import { Progress } from "@/components/ui/progress";
import { Loader2Icon, CheckCircle2Icon, AlertTriangleIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface NkyelMissionStatusProps {
  status: "idle" | "running" | "completed" | "error";
  progressPercent?: number;
  message?: string;
  sourceCount?: number;
  className?: string;
}

export function NkyelMissionStatus({
  status,
  progressPercent = 100,
  message,
  sourceCount = 0,
  className,
}: NkyelMissionStatusProps) {
  const isRunning = status === "running";

  return (
    <div
      className={cn(
        "rounded-xl border border-border/70 bg-card/50 p-3.5 space-y-2.5 backdrop-blur-sm",
        isRunning && "border-primary/30",
        className
      )}
    >
      <div className="flex items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2 font-medium">
          {isRunning ? (
            <>
              <Loader2Icon className="size-3.5 animate-spin text-primary" />
              <span className="text-foreground">Recherche & Analyse en cours...</span>
            </>
          ) : status === "completed" ? (
            <>
              <CheckCircle2Icon className="size-3.5 text-emerald-500" />
              <span className="text-foreground">Synthèse validée</span>
            </>
          ) : (
            <>
              <AlertTriangleIcon className="size-3.5 text-amber-500" />
              <span className="text-foreground">Échec partiel</span>
            </>
          )}
        </div>

        {sourceCount > 0 && (
          <span className="text-[11px] text-muted-foreground">
            {sourceCount} {sourceCount === 1 ? "source analysée" : "sources analysées"}
          </span>
        )}
      </div>

      {isRunning && (
        <Progress value={progressPercent} className="h-1.5 w-full bg-primary/10" />
      )}

      {message && (
        <p className="text-[11px] text-muted-foreground">{message}</p>
      )}
    </div>
  );
}
