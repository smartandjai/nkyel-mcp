"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  MonitorIcon,
  GlobeIcon,
  TerminalIcon,
  FileCodeIcon,
  FolderIcon,
  ActivityIcon,
  Maximize2Icon,
  Minimize2Icon,
  XIcon,
  CameraIcon,
  RefreshCwIcon,
  UserCheckIcon,
  BotIcon,
  Loader2Icon,
  PowerIcon,
  SparklesIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

import {
  getComputerSession,
  startComputerSession,
  stopComputerSession,
  executeComputerAction,
} from "@/core/e2b/api";
import type { ComputerSessionResponse } from "@/core/e2b/types";

import { ComputerDesktopStream } from "./ComputerDesktopStream";
import { ComputerBrowserBar } from "./ComputerBrowserBar";
import { ComputerTerminalView } from "./ComputerTerminalView";
import { ComputerCodeView } from "./ComputerCodeView";
import { ComputerFilesView } from "./ComputerFilesView";
import { ComputerActivityFeed } from "./ComputerActivityFeed";

export interface NkyelComputerPanelProps {
  threadId: string;
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

export function NkyelComputerPanel({
  threadId,
  isOpen,
  onClose,
  className,
}: NkyelComputerPanelProps) {
  const [session, setSession] = useState<ComputerSessionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"desktop" | "browser" | "terminal" | "code" | "files" | "activity">("desktop");
  const [isExpanded, setIsExpanded] = useState(false);
  const [isUserControlling, setIsUserControlling] = useState(false);

  const fetchSession = useCallback(async () => {
    try {
      const data = await getComputerSession(threadId);
      setSession(data);
      if (data.status === "USER_CONTROLLING") {
        setIsUserControlling(true);
      }
    } catch (e) {
      // Quiet fail if not yet initialized
    }
  }, [threadId]);

  useEffect(() => {
    if (isOpen) {
      fetchSession();
      const interval = setInterval(fetchSession, 3000);
      return () => clearInterval(interval);
    }
  }, [isOpen, fetchSession]);

  const handleStartComputer = async () => {
    setLoading(true);
    try {
      const newSession = await startComputerSession(threadId, "https://example.com");
      setSession(newSession);
      toast.success("Ordinateur Cloud Ñkyel démarré avec succès !");
    } catch (e: any) {
      toast.error(e.message || "Erreur de démarrage de l'ordinateur");
    } finally {
      setLoading(false);
    }
  };

  const handleStopComputer = async () => {
    if (!confirm("Voulez-vous vraiment éteindre cet ordinateur cloud ?")) return;
    try {
      await stopComputerSession(threadId);
      setSession(null);
      toast.info("Ordinateur cloud éteint.");
    } catch (e: any) {
      toast.error("Erreur lors de l'arrêt");
    }
  };

  const handleTakeControlToggle = async () => {
    const nextState = !isUserControlling;
    try {
      const action = nextState ? "takeover" : "release_control";
      await executeComputerAction({ thread_id: threadId, action });
      setIsUserControlling(nextState);
      toast.info(nextState ? "Contrôle manuel activé" : "Contrôle rendu à l'agent Ñkyel");
      fetchSession();
    } catch (e: any) {
      toast.error("Impossible de modifier le contrôle");
    }
  };

  const handleBrowserNavigate = async (url: string) => {
    try {
      await executeComputerAction({ thread_id: threadId, action: "navigate", url });
      toast.success(`Navigation vers ${url}`);
      fetchSession();
    } catch (e: any) {
      toast.error("Erreur de navigation");
    }
  };

  const handleCaptureScreenshot = async () => {
    try {
      const res = await executeComputerAction({ thread_id: threadId, action: "screenshot" });
      if (res.screenshot_base64) {
        setSession((prev) => prev ? { ...prev, screenshot_base64: res.screenshot_base64 as string } : prev);
        toast.success("Capture d'écran enregistrée");
      }
    } catch (e) {
      toast.error("Échec de la capture d'écran");
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className={cn(
        "flex flex-col bg-zinc-950 border-l border-zinc-800 transition-all duration-300 z-30 shadow-2xl overflow-hidden",
        isExpanded ? "fixed inset-0 z-50 w-screen h-screen" : "size-full",
        className
      )}
    >
      {/* ─── 10. PREMIUM HEADER ────────────────────────────────────────────── */}
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-zinc-800/80 bg-zinc-900/90 px-3 backdrop-blur-md">
        {/* Left identity & status */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 rounded-md bg-gradient-to-r from-blue-600/20 to-indigo-600/20 px-2 py-1 border border-blue-500/30">
            <MonitorIcon className="h-4 w-4 text-blue-400" />
            <span className="text-xs font-bold tracking-wider text-blue-200">ÑKYEL COMPUTER</span>
          </div>

          <Badge
            variant="outline"
            className={cn(
              "text-[10px] uppercase font-mono px-2 py-0.5",
              session?.status === "LIVE" || session?.status === "AGENT_CONTROLLING"
                ? "bg-emerald-950/80 text-emerald-400 border-emerald-700/60"
                : session?.status === "USER_CONTROLLING"
                ? "bg-amber-950/80 text-amber-400 border-amber-700/60"
                : "bg-zinc-800 text-zinc-400 border-zinc-700"
            )}
          >
            <span className="relative flex h-1.5 w-1.5 mr-1.5">
              {session?.active && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />}
              <span className={cn("relative inline-flex h-1.5 w-1.5 rounded-full", session?.active ? "bg-emerald-500" : "bg-zinc-500")} />
            </span>
            {session?.status || "INACTIF"}
          </Badge>

          {session?.current_app && (
            <span className="text-xs text-zinc-400 hidden md:inline truncate font-mono">
              · {session.current_app}
            </span>
          )}
        </div>

        {/* Center active URL or mission */}
        <div className="hidden lg:flex items-center gap-1.5 max-w-sm truncate text-xs text-zinc-400 font-mono">
          {session?.current_url && (
            <>
              <GlobeIcon className="h-3.5 w-3.5 text-zinc-500 shrink-0" />
              <span className="truncate">{session.current_url}</span>
            </>
          )}
        </div>

        {/* Right Action buttons */}
        <div className="flex items-center gap-1">
          {!session?.active ? (
            <Button
              size="sm"
              onClick={handleStartComputer}
              disabled={loading}
              className="h-7 text-xs gap-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium"
            >
              {loading ? <Loader2Icon className="h-3.5 w-3.5 animate-spin" /> : <PowerIcon className="h-3.5 w-3.5" />}
              Allumer Ordinateur
            </Button>
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={handleTakeControlToggle}
              className={cn(
                "h-7 text-xs gap-1.5 px-2.5 transition-all",
                isUserControlling
                  ? "bg-amber-600 hover:bg-amber-500 text-white border-amber-500"
                  : "border-zinc-700 bg-zinc-850 text-zinc-200 hover:bg-zinc-700"
              )}
            >
              {isUserControlling ? (
                <>
                  <BotIcon className="h-3.5 w-3.5" />
                  Rendre Contrôle
                </>
              ) : (
                <>
                  <UserCheckIcon className="h-3.5 w-3.5" />
                  Prendre la Main
                </>
              )}
            </Button>
          )}

          <Button
            size="icon-sm"
            variant="ghost"
            onClick={() => setIsExpanded(!isExpanded)}
            className="h-7 w-7 text-zinc-400 hover:text-white"
            title={isExpanded ? "Réduire" : "Plein écran"}
          >
            {isExpanded ? <Minimize2Icon className="h-3.5 w-3.5" /> : <Maximize2Icon className="h-3.5 w-3.5" />}
          </Button>

          {session?.active && (
            <Button
              size="icon-sm"
              variant="ghost"
              onClick={handleStopComputer}
              className="h-7 w-7 text-rose-400 hover:text-rose-300 hover:bg-rose-950/40"
              title="Éteindre l'ordinateur"
            >
              <PowerIcon className="h-3.5 w-3.5" />
            </Button>
          )}

          <Button
            size="icon-sm"
            variant="ghost"
            onClick={onClose}
            className="h-7 w-7 text-zinc-400 hover:text-white"
            title="Masquer le panneau"
          >
            <XIcon className="h-3.5 w-3.5" />
          </Button>
        </div>
      </header>

      {/* ─── 11. TABS NAVIGATION ───────────────────────────────────────────── */}
      <Tabs
        value={activeTab}
        onValueChange={(val: any) => setActiveTab(val)}
        className="flex size-full flex-col overflow-hidden"
      >
        <div className="border-b border-zinc-800 bg-zinc-900/50 px-2 shrink-0">
          <TabsList className="h-9 bg-transparent p-0 gap-1 text-zinc-400">
            <TabsTrigger
              value="desktop"
              className="h-8 gap-1.5 px-3 text-xs data-[state=active]:bg-zinc-800 data-[state=active]:text-white font-medium"
            >
              <MonitorIcon className="h-3.5 w-3.5 text-blue-400" />
              BUREAU DIRECT
            </TabsTrigger>
            <TabsTrigger
              value="browser"
              className="h-8 gap-1.5 px-3 text-xs data-[state=active]:bg-zinc-800 data-[state=active]:text-white font-medium"
            >
              <GlobeIcon className="h-3.5 w-3.5 text-emerald-400" />
              CHROME
            </TabsTrigger>
            <TabsTrigger
              value="terminal"
              className="h-8 gap-1.5 px-3 text-xs data-[state=active]:bg-zinc-800 data-[state=active]:text-white font-medium"
            >
              <TerminalIcon className="h-3.5 w-3.5 text-amber-400" />
              TERMINAL
            </TabsTrigger>
            <TabsTrigger
              value="code"
              className="h-8 gap-1.5 px-3 text-xs data-[state=active]:bg-zinc-800 data-[state=active]:text-white font-medium"
            >
              <FileCodeIcon className="h-3.5 w-3.5 text-indigo-400" />
              PYTHON & CODE
            </TabsTrigger>
            <TabsTrigger
              value="files"
              className="h-8 gap-1.5 px-3 text-xs data-[state=active]:bg-zinc-800 data-[state=active]:text-white font-medium"
            >
              <FolderIcon className="h-3.5 w-3.5 text-purple-400" />
              FICHIERS
            </TabsTrigger>
            <TabsTrigger
              value="activity"
              className="h-8 gap-1.5 px-3 text-xs data-[state=active]:bg-zinc-800 data-[state=active]:text-white font-medium"
            >
              <ActivityIcon className="h-3.5 w-3.5 text-rose-400" />
              ACTIVITÉ
            </TabsTrigger>
          </TabsList>
        </div>

        {/* ─── TAB CONTENT VIEWS ───────────────────────────────────────────── */}
        <div className="flex-1 min-h-0 overflow-hidden relative">
          {/* TAB: DESKTOP STREAM */}
          <TabsContent value="desktop" className="m-0 size-full p-0">
            <ComputerDesktopStream
              streamUrl={session?.stream_url || ""}
              sandboxId={session?.sandbox_id}
              status={session?.status || "INACTIF"}
              currentUrl={session?.current_url}
              screenshotBase64={session?.screenshot_base64}
              isUserControlling={isUserControlling}
              onTakeControlToggle={handleTakeControlToggle}
              onCaptureScreenshot={handleCaptureScreenshot}
            />
          </TabsContent>

          {/* TAB: BROWSER VIEW */}
          <TabsContent value="browser" className="m-0 size-full flex flex-col p-0">
            <ComputerBrowserBar
              currentUrl={session?.current_url || "https://example.com"}
              pageTitle={session?.current_app}
              onNavigate={handleBrowserNavigate}
              isUserControlling={isUserControlling}
            />
            <div className="flex-1 min-h-0">
              <ComputerDesktopStream
                streamUrl={session?.stream_url || ""}
                sandboxId={session?.sandbox_id}
                status={session?.status || "INACTIF"}
                currentUrl={session?.current_url}
                screenshotBase64={session?.screenshot_base64}
                isUserControlling={isUserControlling}
                onTakeControlToggle={handleTakeControlToggle}
                onCaptureScreenshot={handleCaptureScreenshot}
              />
            </div>
          </TabsContent>

          {/* TAB: TERMINAL */}
          <TabsContent value="terminal" className="m-0 size-full p-0">
            <ComputerTerminalView
              threadId={threadId}
              logs={session?.terminal_logs || []}
            />
          </TabsContent>

          {/* TAB: CODE */}
          <TabsContent value="code" className="m-0 size-full p-0">
            <ComputerCodeView threadId={threadId} />
          </TabsContent>

          {/* TAB: FILES */}
          <TabsContent value="files" className="m-0 size-full p-0">
            <ComputerFilesView threadId={threadId} />
          </TabsContent>

          {/* TAB: ACTIVITY */}
          <TabsContent value="activity" className="m-0 size-full p-0">
            <ComputerActivityFeed events={session?.events || []} />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
