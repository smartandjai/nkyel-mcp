"use client";

import { NkyelEmblem } from "@/components/ui/nkyel-logo";
import { type Agent } from "@/core/agents";
import { cn } from "@/lib/utils";

export function AgentWelcome({
  className,
  agent,
  agentName,
}: {
  className?: string;
  agent: Agent | null | undefined;
  agentName: string;
}) {
  const displayName = agent?.display_name?.length
    ? agent.display_name
    : (agent?.name ?? agentName);
  const description = agent?.description;

  return (
    <div
      className={cn(
        "mx-auto flex w-full flex-col items-center justify-center gap-3 px-8 py-6 text-center",
        className,
      )}
    >
      <div className="relative flex items-center justify-center">
        <div className="absolute -inset-2 rounded-2xl bg-gradient-to-tr from-primary/20 via-primary/5 to-transparent blur-md opacity-75" />
        <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-card border border-border/60 shadow-md ring-1 ring-white/5">
          <NkyelEmblem size={28} className="text-foreground" />
        </div>
      </div>
      <div className="text-2xl font-bold tracking-tight">{displayName}</div>
      {description && (
        <p className="text-muted-foreground max-w-sm text-sm">{description}</p>
      )}
    </div>
  );
}
