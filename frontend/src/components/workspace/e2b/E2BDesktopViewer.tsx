"use client";

import React, { useState } from "react";
import {
  GlobeIcon,
  PlayIcon,
  RefreshCwIcon,
  XIcon,
  ExternalLinkIcon,
  Loader2Icon,
  MousePointerClickIcon,
  ShieldCheckIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { executeE2BDesktopAction } from "@/core/e2b/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export interface E2BDesktopViewerProps {
  sandboxId?: string;
  className?: string;
}

export function E2BDesktopViewer({ sandboxId, className }: E2BDesktopViewerProps) {
  const [activeSessionId, setActiveSessionId] = useState<string>(sandboxId || "");
  const [url, setUrl] = useState("https://aninf.ga");
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>("Prêt");

  const handleLaunch = async (targetUrl = url) => {
    setLoading(true);
    setStatus("Démarrage de la microVM Chrome...");
    try {
      const res = await executeE2BDesktopAction("launch", { url: targetUrl });
      if (res.sandbox_id) {
        setActiveSessionId(res.sandbox_id);
      }
      if (res.screenshot_base64) {
        setScreenshot(`data:image/png;base64,${res.screenshot_base64}`);
      }
      setStatus("Chrome actif");
      toast.success("Session E2B Cloud Desktop initialisée avec succès !");
    } catch (e: any) {
      toast.error(e.message || "Erreur de démarrage E2B Desktop");
      setStatus("Erreur");
    } finally {
      setLoading(false);
    }
  };

  const handleNavigate = async () => {
    if (!activeSessionId) {
      await handleLaunch(url);
      return;
    }
    setLoading(true);
    setStatus(`Navigation vers ${url}...`);
    try {
      const res = await executeE2BDesktopAction("navigate", {
        sandbox_id: activeSessionId,
        url,
      });
      if (res.screenshot_base64) {
        setScreenshot(`data:image/png;base64,${res.screenshot_base64}`);
      }
      setStatus("Page chargée");
    } catch (e: any) {
      toast.error(e.message || "Erreur de navigation");
      setStatus("Erreur navigation");
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshScreenshot = async () => {
    if (!activeSessionId) {
      toast.info("Lancez d'abord une session Chrome.");
      return;
    }
    setLoading(true);
    try {
      const res = await executeE2BDesktopAction("screenshot", {
        sandbox_id: activeSessionId,
      });
      if (res.screenshot_base64) {
        setScreenshot(`data:image/png;base64,${res.screenshot_base64}`);
        toast.success("Capture d'écran actualisée.");
      }
    } catch (e: any) {
      toast.error("Échec de la capture d'écran");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = async () => {
    if (!activeSessionId) return;
    setLoading(true);
    try {
      await executeE2BDesktopAction("close", { sandbox_id: activeSessionId });
      setActiveSessionId("");
      setScreenshot(null);
      setStatus("Fermé");
      toast.info("Session E2B Cloud Desktop libérée.");
    } catch (e: any) {
      toast.error("Erreur lors de la fermeture");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("flex flex-col h-full bg-neutral-950 font-sans text-xs text-neutral-200 select-none", className)}>
      {/* Top Browser Bar */}
      <div className="flex items-center gap-2 p-2 border-b border-neutral-800 bg-neutral-900/90">
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="size-2.5 rounded-full bg-red-500/80 inline-block" />
          <span className="size-2.5 rounded-full bg-amber-500/80 inline-block" />
          <span className="size-2.5 rounded-full bg-emerald-500/80 inline-block" />
        </div>

        <div className="flex-1 flex items-center gap-1.5 bg-neutral-950 border border-neutral-800 rounded-md px-2 py-1">
          <GlobeIcon className="size-3.5 text-primary shrink-0" />
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleNavigate()}
            placeholder="https://..."
            className="flex-1 bg-transparent text-neutral-100 text-[11px] focus:outline-none font-mono"
          />
        </div>

        <Button
          size="sm"
          variant="secondary"
          onClick={handleNavigate}
          disabled={loading}
          className="h-7 px-2.5 text-[11px] font-medium gap-1"
        >
          {loading ? <Loader2Icon className="size-3 animate-spin" /> : <PlayIcon className="size-3" />}
          Naviguer
        </Button>

        <Button
          size="sm"
          variant="ghost"
          onClick={handleRefreshScreenshot}
          disabled={loading || !activeSessionId}
          className="h-7 w-7 p-0"
          title="Actualiser l'écran"
        >
          <RefreshCwIcon className={cn("size-3.5", loading && "animate-spin")} />
        </Button>

        {activeSessionId && (
          <Button
            size="sm"
            variant="ghost"
            onClick={handleClose}
            className="h-7 w-7 p-0 text-destructive hover:bg-destructive/10"
            title="Fermer la session"
          >
            <XIcon className="size-3.5" />
          </Button>
        )}
      </div>

      {/* Preset Quick Links */}
      <div className="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-900/40 border-b border-neutral-800/80 text-[10px] text-neutral-400 overflow-x-auto">
        <span className="shrink-0 font-medium text-neutral-500">Cibles :</span>
        <button
          onClick={() => { setUrl("https://aninf.ga"); handleLaunch("https://aninf.ga"); }}
          className="rounded bg-neutral-800/60 px-1.5 py-0.5 hover:bg-neutral-800 text-neutral-300 transition-colors"
        >
          🇬🇦 ANINF Gabon
        </button>
        <button
          onClick={() => { setUrl("https://service-public.ga"); handleLaunch("https://service-public.ga"); }}
          className="rounded bg-neutral-800/60 px-1.5 py-0.5 hover:bg-neutral-800 text-neutral-300 transition-colors"
        >
          🏛️ Téléservices
        </button>
        <button
          onClick={() => { setUrl("https://google.com"); handleLaunch("https://google.com"); }}
          className="rounded bg-neutral-800/60 px-1.5 py-0.5 hover:bg-neutral-800 text-neutral-300 transition-colors"
        >
          🔍 Google Chrome
        </button>
      </div>

      {/* Viewport Surface */}
      <div className="flex-1 relative flex items-center justify-center bg-neutral-950 overflow-hidden">
        {screenshot ? (
          <div className="relative size-full flex items-center justify-center p-2">
            <img
              src={screenshot}
              alt="E2B Desktop Screen"
              className="max-h-full max-w-full rounded shadow-2xl border border-neutral-800 object-contain"
            />
            <div className="absolute top-4 right-4 bg-black/80 backdrop-blur-md border border-neutral-800 px-2.5 py-1 rounded text-[10px] text-neutral-300 flex items-center gap-1.5">
              <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>E2B Cloud Desktop 1080p</span>
            </div>
          </div>
        ) : (
          <div className="text-center p-6 space-y-3 max-w-sm">
            <div className="size-12 rounded-xl bg-primary/10 border border-primary/20 text-primary mx-auto flex items-center justify-center">
              <GlobeIcon className="size-6" />
            </div>
            <div>
              <h4 className="font-semibold text-neutral-100 text-sm">Mode Visuel E2B Cloud</h4>
              <p className="text-[11px] text-neutral-400 mt-1">
                Visualisez la navigation web et les actions de l'agent en direct dans un bac à sable Debian isolé.
              </p>
            </div>
            <Button
              onClick={() => handleLaunch()}
              disabled={loading}
              className="w-full gap-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white"
            >
              {loading ? <Loader2Icon className="size-3.5 animate-spin" /> : <PlayIcon className="size-3.5" />}
              Démarrer l'ordinateur E2B Cloud
            </Button>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-neutral-900 border-t border-neutral-800 text-[10px] text-neutral-400">
        <div className="flex items-center gap-1.5">
          <ShieldCheckIcon className="size-3 text-emerald-400" />
          <span>{status}</span>
        </div>
        {activeSessionId && (
          <span className="font-mono text-neutral-500 truncate max-w-[150px]">
            {activeSessionId}
          </span>
        )}
      </div>
    </div>
  );
}
