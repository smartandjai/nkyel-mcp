"use client";

import React from "react";
import { MonitorIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface E2BModeToggleProps {
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

export function E2BModeToggle({ isOpen, onToggle, className }: E2BModeToggleProps) {
  return (
    <Button
      variant={isOpen ? "secondary" : "outline"}
      size="sm"
      onClick={onToggle}
      className={cn(
        "h-8 gap-1.5 text-xs font-semibold rounded-lg transition-all",
        isOpen
          ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 hover:bg-emerald-500/30"
          : "border-border/80 hover:border-emerald-500/40 hover:text-emerald-400",
        className
      )}
      title="Activer ou masquer le panneau visuel E2B Cloud"
    >
      <span className="relative flex size-2">
        <span
          className={cn(
            "absolute inline-flex size-full rounded-full bg-emerald-400 opacity-75",
            isOpen && "animate-ping"
          )}
        />
        <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
      </span>
      <MonitorIcon className="size-3.5 text-emerald-400" />
      <span className="hidden sm:inline">Mode Visuel E2B</span>
    </Button>
  );
}
