"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  MonitorIcon,
  RefreshCwIcon,
  Maximize2Icon,
  Minimize2Icon,
  CameraIcon,
  UserCheckIcon,
  BotIcon,
  Loader2Icon,
  AlertCircleIcon,
  ExternalLinkIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface ComputerDesktopStreamProps {
  streamUrl: string;
  sandboxId?: string;
  status: string;
  currentUrl?: string;
  screenshotBase64?: string | null;
  isUserControlling: boolean;
  onTakeControlToggle: () => void;
  onCaptureScreenshot?: () => void;
  className?: string;
}

export function ComputerDesktopStream({
  streamUrl,
  sandboxId,
  status,
  currentUrl,
  screenshotBase64,
  isUserControlling,
  onTakeControlToggle,
  onCaptureScreenshot,
  className,
}: ComputerDesktopStreamProps) {
  const [iframeLoaded, setIframeLoaded] = useState(false);
  const [streamError, setStreamError] = useState(false);
  const [useFallbackScreenshot, setUseFallbackScreenshot] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    setIframeLoaded(false);
    setStreamError(false);
    setUseFallbackScreenshot(false);
  }, [streamUrl]);

  return (
    <div className={cn("relative flex size-full flex-col overflow-hidden bg-zinc-950 select-none", className)}>
      {/* Top stream banner overlay */}
      <div className="absolute top-2 left-3 right-3 z-20 flex items-center justify-between rounded-lg bg-zinc-900/80 px-3 py-1.5 backdrop-blur-md border border-zinc-800/80 shadow-md">
        <div className="flex items-center gap-2 text-xs">
          <span className="relative flex h-2 w-2">
            {status === "LIVE" || status === "AGENT_CONTROLLING" || status === "USER_CONTROLLING" ? (
              <>
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </>
            ) : (
              <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-500" />
            )}
          </span>
          <span className="font-semibold text-zinc-200">
            {isUserControlling ? "Contrôle Humain Actif" : "Agent Ñkyel en action"}
          </span>
          {sandboxId && (
            <span className="text-[10px] text-zinc-400 font-mono hidden sm:inline">
              ({sandboxId.slice(0, 10)}…)
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <Button
            size="sm"
            variant={isUserControlling ? "default" : "outline"}
            onClick={onTakeControlToggle}
            className={cn(
              "h-7 text-xs gap-1.5 px-2.5 transition-all",
              isUserControlling
                ? "bg-amber-600 hover:bg-amber-500 text-white border-amber-500"
                : "border-zinc-700 bg-zinc-800/80 text-zinc-300 hover:bg-zinc-700"
            )}
          >
            {isUserControlling ? (
              <>
                <BotIcon className="h-3.5 w-3.5" />
                Rendre à l'Agent
              </>
            ) : (
              <>
                <UserCheckIcon className="h-3.5 w-3.5" />
                Prendre le Contrôle
              </>
            )}
          </Button>

          {onCaptureScreenshot && (
            <Button
              size="icon-sm"
              variant="ghost"
              onClick={onCaptureScreenshot}
              className="h-7 w-7 text-zinc-400 hover:text-white"
              title="Prendre une capture"
            >
              <CameraIcon className="h-3.5 w-3.5" />
            </Button>
          )}

          {streamUrl && (
            <Button
              size="icon-sm"
              variant="ghost"
              onClick={() => window.open(streamUrl, "_blank")}
              className="h-7 w-7 text-zinc-400 hover:text-white"
              title="Ouvrir dans un nouvel onglet"
            >
              <ExternalLinkIcon className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
      </div>

      {/* Main Screen Stream Container */}
      <div className="relative flex size-full items-center justify-center p-2 pt-12">
        {streamUrl && !useFallbackScreenshot ? (
          <div className="relative size-full rounded-lg overflow-hidden border border-zinc-800/60 shadow-2xl bg-black">
            {!iframeLoaded && !streamError && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-zinc-950/90 z-10 text-zinc-400">
                <Loader2Icon className="h-7 w-7 animate-spin text-primary" />
                <span className="text-xs font-mono">Connexion au flux vidéo VNC E2B...</span>
              </div>
            )}

            <iframe
              ref={iframeRef}
              src={streamUrl}
              onLoad={() => setIframeLoaded(true)}
              onError={() => {
                setStreamError(true);
                setUseFallbackScreenshot(true);
              }}
              className="size-full border-0 select-auto"
              allow="clipboard-read; clipboard-write; autoplay"
              title="Ñkyel Cloud Computer Desktop"
            />
          </div>
        ) : screenshotBase64 ? (
          <div className="relative size-full flex flex-col items-center justify-center rounded-lg overflow-hidden border border-zinc-800 bg-black">
            <img
              src={`data:image/png;base64,${screenshotBase64}`}
              alt="Live Screen Capture"
              className="max-h-full max-w-full object-contain"
            />
            <div className="absolute bottom-3 left-3 bg-zinc-900/90 px-2 py-1 rounded text-[11px] text-zinc-400 border border-zinc-800">
              Capture écran instantanée (Fallback)
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 text-zinc-500">
            <MonitorIcon className="h-10 w-10 text-zinc-600 stroke-[1.5]" />
            <div className="text-center">
              <p className="text-sm font-medium text-zinc-300">Ordinateur Cloud en attente</p>
              <p className="text-xs text-zinc-500 mt-1">
                Le flux vidéo de l'écran apparaîtra dès que l'agent démarrera une tâche.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
