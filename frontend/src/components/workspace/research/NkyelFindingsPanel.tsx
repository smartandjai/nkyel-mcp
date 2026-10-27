"use client";

import React from "react";
import { CheckCircleIcon, SparklesIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface NkyelFindingsPanelProps {
  findings: string[];
  title?: string;
  className?: string;
}

export function NkyelFindingsPanel({
  findings,
  title = "Points Clés & Résultats",
  className,
}: NkyelFindingsPanelProps) {
  if (!findings || findings.length === 0) return null;

  return (
    <div
      className={cn(
        "rounded-xl border border-primary/20 bg-primary/5 p-4 space-y-3",
        className
      )}
    >
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-primary">
        <SparklesIcon className="size-3.5" />
        <span>{title}</span>
      </div>

      <ul className="space-y-2">
        {findings.map((item, idx) => (
          <li key={idx} className="flex items-start gap-2.5 text-xs text-foreground/90 leading-relaxed">
            <CheckCircleIcon className="size-3.5 text-emerald-500 shrink-0 mt-0.5" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
