"use client";

import React, { useMemo } from "react";
import { NkyelResearchHeader } from "./NkyelResearchHeader";
import { NkyelSourceCard, type NkyelSourceItem } from "./NkyelSourceCard";
import { NkyelFindingsPanel } from "./NkyelFindingsPanel";
import { NkyelArtifactActions } from "./NkyelArtifactActions";
import { NkyelMissionStatus } from "./NkyelMissionStatus";
import { NkyelToolActivityCard } from "./NkyelToolActivityCard";
import { cn } from "@/lib/utils";

export interface NkyelResearchSummaryProps {
  query?: string;
  title?: string;
  status?: "idle" | "running" | "completed" | "error";
  sources?: NkyelSourceItem[];
  findings?: string[];
  markdownContent?: string;
  toolCalls?: Array<{
    name: string;
    args: Record<string, unknown>;
    result?: unknown;
    status: "running" | "completed" | "error";
  }>;
  className?: string;
}

export function NkyelResearchSummary({
  query,
  title,
  status = "completed",
  sources = [],
  findings = [],
  markdownContent = "",
  toolCalls = [],
  className,
}: NkyelResearchSummaryProps) {
  const uniqueSources = useMemo(() => {
    const seen = new Set<string>();
    return sources.filter((s) => {
      if (!s.url || seen.has(s.url)) return false;
      seen.add(s.url);
      return true;
    });
  }, [sources]);

  return (
    <div className={cn("space-y-4 my-2", className)}>
      <NkyelResearchHeader
        title={title}
        query={query}
        status={status}
        sourceCount={uniqueSources.length}
      />

      {toolCalls.length > 0 && (
        <div className="space-y-2">
          {toolCalls.map((tc, idx) => (
            <NkyelToolActivityCard
              key={idx}
              toolName={tc.name}
              args={tc.args}
              result={tc.result}
              status={tc.status}
            />
          ))}
        </div>
      )}

      {uniqueSources.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-muted-foreground uppercase tracking-wider px-1">
            <span>Sources consultées ({uniqueSources.length})</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {uniqueSources.map((source, index) => (
              <NkyelSourceCard key={source.url || index} source={source} index={index} />
            ))}
          </div>
        </div>
      )}

      {findings.length > 0 && (
        <NkyelFindingsPanel findings={findings} />
      )}

      {markdownContent && (
        <NkyelArtifactActions content={markdownContent} title={title || query} />
      )}
    </div>
  );
}
