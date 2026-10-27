"use client";

import React, { type ComponentProps, useState } from "react";
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  ChevronDownIcon,
  Code2Icon,
  FileTextIcon,
  Loader2Icon,
  SearchIcon,
  TerminalIcon,
  WrenchIcon,
} from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

export type ToolStatus = "running" | "completed" | "error";

export type ToolProps = ComponentProps<typeof Collapsible> & {
  status?: ToolStatus;
};

export const Tool = ({
  className,
  children,
  status = "completed",
  defaultOpen = false,
  ...props
}: ToolProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <Collapsible
      open={isOpen}
      onOpenChange={setIsOpen}
      className={cn(
        "my-2.5 overflow-hidden rounded-xl border border-border/70 bg-card/50 backdrop-blur-xs transition-all",
        status === "running" && "border-primary/40 ring-1 ring-primary/20",
        status === "error" && "border-destructive/40 bg-destructive/5",
        className
      )}
      {...props}
    >
      {children}
    </Collapsible>
  );
};

export type ToolHeaderProps = ComponentProps<typeof CollapsibleTrigger> & {
  toolName: string;
  status?: ToolStatus;
  summary?: string;
  durationMs?: number;
};

export function getToolIcon(name: string) {
  const lower = name.toLowerCase();
  if (lower.includes("search") || lower.includes("tavily")) {
    return <SearchIcon className="size-3.5 text-blue-500" />;
  }
  if (lower.includes("terminal") || lower.includes("bash") || lower.includes("shell")) {
    return <TerminalIcon className="size-3.5 text-emerald-500" />;
  }
  if (lower.includes("python") || lower.includes("code")) {
    return <Code2Icon className="size-3.5 text-amber-500" />;
  }
  if (lower.includes("file") || lower.includes("read") || lower.includes("write")) {
    return <FileTextIcon className="size-3.5 text-violet-500" />;
  }
  return <WrenchIcon className="size-3.5 text-primary" />;
}

export const ToolHeader = ({
  className,
  toolName,
  status = "completed",
  summary,
  durationMs,
  children,
  ...props
}: ToolHeaderProps) => {
  return (
    <CollapsibleTrigger
      className={cn(
        "flex w-full cursor-pointer items-center justify-between gap-3 p-3 text-left select-none hover:bg-muted/30 transition-colors group",
        className
      )}
      {...props}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <div className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-muted/80 text-foreground overflow-hidden">
          {getToolIcon(toolName)}
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-foreground truncate font-mono">
              {toolName}
            </span>
            <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground uppercase">
              Tool
            </span>
          </div>
          {summary && (
            <p className="truncate text-[11px] text-muted-foreground mt-0.5">
              {summary}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        {durationMs !== undefined && (
          <span className="text-[10px] font-mono text-muted-foreground">
            {durationMs > 1000 ? `${(durationMs / 1000).toFixed(1)}s` : `${durationMs}ms`}
          </span>
        )}

        {status === "running" && (
          <span className="flex items-center gap-1 text-[11px] text-amber-500 font-medium">
            <Loader2Icon className="size-3 animate-spin" />
            <span className="hidden sm:inline">Exécution...</span>
          </span>
        )}

        {status === "completed" && (
          <CheckCircle2Icon className="size-3.5 text-emerald-500" />
        )}

        {status === "error" && (
          <AlertCircleIcon className="size-3.5 text-destructive" />
        )}

        <ChevronDownIcon className="size-3.5 text-muted-foreground opacity-60 transition-transform duration-200 group-data-[state=open]:rotate-180" />
      </div>
    </CollapsibleTrigger>
  );
};

export type ToolContentProps = ComponentProps<typeof CollapsibleContent>;

export const ToolContent = ({
  className,
  children,
  ...props
}: ToolContentProps) => {
  return (
    <CollapsibleContent
      className={cn(
        "border-t border-border/50 bg-muted/15 p-3 text-xs space-y-2.5 transition-all font-mono",
        className
      )}
      {...props}
    >
      {children}
    </CollapsibleContent>
  );
};

export type ToolOutputProps = ComponentProps<"div"> & {
  output?: unknown;
};

export const ToolOutput = ({
  className,
  output,
  children,
  ...props
}: ToolOutputProps) => {
  if (!output && !children) return null;

  const content =
    children ??
    (typeof output === "string"
      ? output
      : JSON.stringify(output, null, 2));

  return (
    <div
      className={cn(
        "relative rounded-lg border border-border/60 bg-muted/40 p-2.5 overflow-x-auto text-[11px] text-muted-foreground font-mono leading-relaxed max-h-60",
        className
      )}
      {...props}
    >
      <pre className="whitespace-pre-wrap break-words">{content}</pre>
    </div>
  );
};
