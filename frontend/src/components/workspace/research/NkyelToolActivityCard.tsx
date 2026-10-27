"use client";

import React, { useState } from "react";
import { ChevronDownIcon, SearchIcon, FileTextIcon, NetworkIcon, CompassIcon, SparklesIcon, CheckCircle2Icon, AlertCircleIcon, Loader2Icon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface NkyelToolActivityCardProps {
  toolName: string;
  args: Record<string, unknown>;
  result?: unknown;
  status: "running" | "completed" | "error";
  className?: string;
}

export function NkyelToolActivityCard({
  toolName,
  args,
  result,
  status,
  className,
}: NkyelToolActivityCardProps) {
  const [expanded, setExpanded] = useState(false);

  const meta = getToolMeta(toolName, args);

  return (
    <div
      className={cn(
        "overflow-hidden rounded-xl border border-border/70 bg-card/60 backdrop-blur-sm transition-all",
        status === "running" && "border-primary/40 ring-1 ring-primary/20",
        className
      )}
    >
      <div
        className="flex cursor-pointer items-center justify-between gap-3 p-3 select-none hover:bg-muted/40 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-foreground/80 overflow-hidden">
            {meta.icon}
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-foreground truncate">
                {meta.title}
              </span>
              <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary uppercase">
                Tavily
              </span>
            </div>
            <p className="truncate text-[11px] text-muted-foreground">
              {meta.subtitle}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {status === "running" ? (
            <span className="flex items-center gap-1 text-[11px] text-amber-500 font-medium">
              <Loader2Icon className="size-3 animate-spin" />
              Recherche...
            </span>
          ) : status === "error" ? (
            <span className="flex items-center gap-1 text-[11px] text-destructive font-medium">
              <AlertCircleIcon className="size-3" />
              Erreur
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[11px] text-emerald-500 font-medium">
              <CheckCircle2Icon className="size-3" />
              Terminé
            </span>
          )}

          <ChevronDownIcon
            className={cn(
              "size-4 text-muted-foreground transition-transform duration-200",
              expanded && "rotate-180"
            )}
          />
        </div>
      </div>

      {expanded && (
        <div className="border-t border-border/50 bg-muted/20 p-3 space-y-2 text-xs">
          <div>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Paramètres :
            </span>
            <pre className="mt-1 max-h-32 overflow-auto rounded bg-background/80 p-2 text-[11px] font-mono break-all whitespace-pre-wrap border border-border/40">
              {JSON.stringify(args, null, 2)}
            </pre>
          </div>

          {result !== undefined && (
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                Résultat brut :
              </span>
              <pre className="mt-1 max-h-48 overflow-auto rounded bg-background/80 p-2 text-[11px] font-mono break-all whitespace-pre-wrap border border-border/40">
                {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function getToolMeta(name: string, args: Record<string, unknown>) {
  if (name.includes("search")) {
    return {
      title: "Tavily Web Search",
      subtitle: typeof args.query === "string" ? `« ${args.query} »` : "Recherche web ciblée",
      icon: <SearchIcon className="size-4 text-primary" />,
    };
  }
  if (name.includes("fetch") || name.includes("extract")) {
    return {
      title: "Tavily Extract",
      subtitle: typeof args.url === "string" ? args.url : "Extraction de page web",
      icon: <FileTextIcon className="size-4 text-indigo-500" />,
    };
  }
  if (name.includes("crawl")) {
    return {
      title: "Tavily Crawl",
      subtitle: typeof args.url === "string" ? args.url : "Exploration de domaine",
      icon: <NetworkIcon className="size-4 text-emerald-500" />,
    };
  }
  if (name.includes("map")) {
    return {
      title: "Tavily Sitemap",
      subtitle: typeof args.url === "string" ? args.url : "Cartographie du site",
      icon: <CompassIcon className="size-4 text-amber-500" />,
    };
  }
  return {
    title: "Tavily Research",
    subtitle: typeof args.query === "string" ? args.query : "Recherche approfondie",
    icon: <SparklesIcon className="size-4 text-primary" />,
  };
}
