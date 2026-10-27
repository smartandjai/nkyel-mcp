"use client";

import React from "react";
import { CheckCircle2Icon, CircleIcon, Loader2Icon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface NkyelTimelineStep {
  id: string;
  title: string;
  description?: string;
  status: "pending" | "running" | "completed";
  timestamp?: string;
}

export interface NkyelAgentTimelineProps {
  steps: NkyelTimelineStep[];
  className?: string;
}

export function NkyelAgentTimeline({ steps, className }: NkyelAgentTimelineProps) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className={cn("space-y-3 p-3 rounded-xl border border-border/70 bg-card/40 backdrop-blur-sm", className)}>
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Chronologie de la mission
      </h4>

      <div className="space-y-2.5">
        {steps.map((step, idx) => (
          <div key={step.id || idx} className="flex items-start gap-2.5 text-xs">
            <div className="shrink-0 mt-0.5">
              {step.status === "completed" ? (
                <CheckCircle2Icon className="size-4 text-emerald-500" />
              ) : step.status === "running" ? (
                <Loader2Icon className="size-4 animate-spin text-primary" />
              ) : (
                <CircleIcon className="size-4 text-muted-foreground/40" />
              )}
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <span
                  className={cn(
                    "font-medium",
                    step.status === "completed"
                      ? "text-foreground"
                      : step.status === "running"
                        ? "text-primary font-semibold"
                        : "text-muted-foreground"
                  )}
                >
                  {step.title}
                </span>
                {step.timestamp && (
                  <span className="text-[10px] text-muted-foreground">{step.timestamp}</span>
                )}
              </div>
              {step.description && (
                <p className="text-[11px] text-muted-foreground mt-0.5">{step.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
