"use client";

import React, { useState } from "react";
import {
  MonitorIcon,
  TerminalIcon,
  Code2Icon,
  FolderIcon,
  ActivityIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CpuIcon,
  ShieldCheckIcon,
  SparklesIcon,
  XIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { NkyelEmblem } from "@/components/ui/nkyel-logo";
import { E2BDesktopViewer } from "./E2BDesktopViewer";
import { E2BTerminalViewer } from "./E2BTerminalViewer";
import { E2BCodeViewer } from "./E2BCodeViewer";
import { E2BFilesViewer } from "./E2BFilesViewer";
import { E2BEventsFeed } from "./E2BEventsFeed";
import { cn } from "@/lib/utils";

export interface E2BVisualPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

export function E2BVisualPanel({ isOpen, onToggle, className }: E2BVisualPanelProps) {
  const [activeTab, setActiveTab] = useState<"desktop" | "terminal" | "code" | "files" | "events">("desktop");

  if (!isOpen) {
    return (
      <div className="fixed left-2 top-20 z-40 hidden md:block">
        <Button
          onClick={onToggle}
          variant="outline"
          size="sm"
          className="h-9 px-3 gap-2 bg-neutral-950/90 border-emerald-500/40 text-emerald-400 hover:text-emerald-300 hover:bg-neutral-900 shadow-xl backdrop-blur-md rounded-full transition-all group"
        >
          <span className="relative flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
          </span>
          <MonitorIcon className="size-3.5" />
          <span className="text-xs font-semibold">Mode Visuel E2B</span>
          <ChevronRightIcon className="size-3 transition-transform group-hover:translate-x-0.5" />
        </Button>
      </div>
    );
  }

  return (
    <aside
      className={cn(
        "flex flex-col h-full w-[420px] lg:w-[480px] shrink-0 border-r border-neutral-800 bg-neutral-950/95 backdrop-blur-xl z-30 shadow-2xl transition-all duration-300 select-none overflow-hidden",
        className
      )}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between px-3 py-2.5 border-b border-neutral-800 bg-gradient-to-r from-neutral-900/90 via-neutral-900/60 to-neutral-900/90">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <NkyelEmblem size={16} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-bold text-neutral-100 truncate">
                E2B Cloud Desktop
              </span>
              <Badge
                variant="outline"
                className="text-[9px] px-1 py-0 border-emerald-500/40 bg-emerald-950/40 text-emerald-400 uppercase font-semibold"
              >
                Live
              </Badge>
            </div>
            <p className="text-[10px] text-neutral-400 flex items-center gap-1 truncate">
              <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
              <span>MicroVM isolée · Travail de l'IA visible</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={onToggle}
            className="h-7 w-7 p-0 text-neutral-400 hover:text-neutral-100"
            title="Masquer le panneau"
          >
            <ChevronLeftIcon className="size-4" />
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center border-b border-neutral-800 bg-neutral-900/40 px-1 py-1 gap-1 text-[11px] overflow-x-auto">
        <button
          onClick={() => setActiveTab("desktop")}
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md font-medium transition-all",
            activeTab === "desktop"
              ? "bg-neutral-800 text-neutral-100 shadow-sm"
              : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/40"
          )}
        >
          <MonitorIcon className="size-3.5 text-emerald-400" />
          <span>Bureau Chrome</span>
        </button>

        <button
          onClick={() => setActiveTab("terminal")}
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md font-medium transition-all",
            activeTab === "terminal"
              ? "bg-neutral-800 text-neutral-100 shadow-sm"
              : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/40"
          )}
        >
          <TerminalIcon className="size-3.5 text-emerald-400" />
          <span>Terminal</span>
        </button>

        <button
          onClick={() => setActiveTab("code")}
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md font-medium transition-all",
            activeTab === "code"
              ? "bg-neutral-800 text-neutral-100 shadow-sm"
              : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/40"
          )}
        >
          <Code2Icon className="size-3.5 text-blue-400" />
          <span>Python</span>
        </button>

        <button
          onClick={() => setActiveTab("files")}
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md font-medium transition-all",
            activeTab === "files"
              ? "bg-neutral-800 text-neutral-100 shadow-sm"
              : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/40"
          )}
        >
          <FolderIcon className="size-3.5 text-amber-400" />
          <span>Fichiers</span>
        </button>

        <button
          onClick={() => setActiveTab("events")}
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md font-medium transition-all",
            activeTab === "events"
              ? "bg-neutral-800 text-neutral-100 shadow-sm"
              : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/40"
          )}
        >
          <ActivityIcon className="size-3.5 text-purple-400" />
          <span>Flux IA</span>
        </button>
      </div>

      {/* Main Tab Content */}
      <div className="flex-1 min-h-0 overflow-hidden relative">
        {activeTab === "desktop" && <E2BDesktopViewer />}
        {activeTab === "terminal" && <E2BTerminalViewer />}
        {activeTab === "code" && <E2BCodeViewer />}
        {activeTab === "files" && <E2BFilesViewer />}
        {activeTab === "events" && <E2BEventsFeed />}
      </div>

      {/* Footer Metrics */}
      <div className="flex items-center justify-between px-3 py-2 bg-neutral-900/90 border-t border-neutral-800 text-[10px] text-neutral-400">
        <div className="flex items-center gap-2">
          <CpuIcon className="size-3 text-emerald-400" />
          <span>2 vCPU · 4 GB RAM · Debian 13</span>
        </div>
        <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
          <ShieldCheckIcon className="size-3" />
          <span>Souveraineté E2B</span>
        </div>
      </div>
    </aside>
  );
}
