"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { NkyelEmblem } from "@/components/ui/nkyel-logo";
import { cn } from "@/lib/utils";
import { GlobeIcon, SparklesIcon, CheckCircle2Icon, Loader2Icon } from "lucide-react";

export interface NkyelResearchHeaderProps {
  title?: string;
  query?: string;
  status: "idle" | "running" | "completed" | "error";
  mode?: "radi" | "pro" | "chui";
  sourceCount?: number;
  className?: string;
}

export function NkyelResearchHeader({
  title,
  query,
  status,
  mode = "pro",
  sourceCount = 0,
  className,
}: NkyelResearchHeaderProps) {
  const isRunning = status === "running";
  const displayTitle = title || query || "Mission de recherche approfondie";
  const modeLabel = mode === "chui" ? "nkyel chui" : mode === "radi" ? "nkyel radi" : "nkyel pro";

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-border/80 bg-gradient-to-r from-card via-card/90 to-card/60 p-4 shadow-sm backdrop-blur-md transition-all",
        isRunning && "border-primary/40 ring-1 ring-primary/20",
        className
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="relative flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <NkyelEmblem size={22} />
            {isRunning && (
              <span className="absolute -top-1 -right-1 flex size-3">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex size-3 rounded-full bg-emerald-500" />
              </span>
            )}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h2 className="truncate text-base font-semibold tracking-tight text-foreground">
                {displayTitle}
              </h2>
            </div>
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <GlobeIcon className="size-3 text-primary/70 shrink-0" />
              <span>Recherche web souveraine validée via Tavily API</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {sourceCount > 0 && (
            <Badge variant="secondary" className="gap-1 text-xs font-medium">
              <GlobeIcon className="size-3 text-muted-foreground" />
              {sourceCount} {sourceCount === 1 ? "source vérifiée" : "sources vérifiées"}
            </Badge>
          )}

          <Badge
            variant="outline"
            className="border-primary/30 bg-primary/5 text-primary text-xs font-semibold uppercase tracking-wider"
          >
            {modeLabel}
          </Badge>

          {isRunning ? (
            <Badge className="gap-1 bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 text-xs font-medium">
              <Loader2Icon className="size-3 animate-spin" />
              En direct
            </Badge>
          ) : status === "completed" ? (
            <Badge className="gap-1 bg-primary/10 text-primary border border-primary/20 text-xs font-medium">
              <CheckCircle2Icon className="size-3 text-emerald-500" />
              Synthétisé
            </Badge>
          ) : null}
        </div>
      </div>
    </div>
  );
}
