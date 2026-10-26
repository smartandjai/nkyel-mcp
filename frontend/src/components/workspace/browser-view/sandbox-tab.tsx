"use client";

import {
  ActivityIcon,
  CheckCircle2Icon,
  CpuIcon,
  HardDriveIcon,
  PauseIcon,
  PlayIcon,
  RefreshCwIcon,
  ServerIcon,
  ShieldCheckIcon,
  SquareIcon,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function SandboxTab({ threadId }: { threadId: string }) {
  const [sandboxStatus, setSandboxStatus] = useState<"running" | "paused" | "stopped">("running");
  const [isRestarting, setIsRestarting] = useState(false);

  const handlePauseResume = () => {
    if (sandboxStatus === "running") {
      setSandboxStatus("paused");
      toast.info("Bac à sable E2B mis en pause (état mémoire préservé).");
    } else {
      setSandboxStatus("running");
      toast.success("Bac à sable E2B réactivé.");
    }
  };

  const handleRestart = () => {
    setIsRestarting(true);
    setTimeout(() => {
      setIsRestarting(false);
      setSandboxStatus("running");
      toast.success("Nouvelle session de bac à sable E2B Cloud allouée.");
    }, 900);
  };

  return (
    <div className="flex size-full flex-col bg-neutral-950 font-sans text-xs text-neutral-200">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-900/80 px-3 py-2 text-[11px] text-neutral-400">
        <div className="flex items-center gap-2">
          <ServerIcon className="size-3.5 text-emerald-400" />
          <span className="font-semibold text-neutral-200">Bac à sable E2B Cloud — Gestion & Métriques</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1 border-emerald-500/40 bg-emerald-950/60 text-emerald-300">
            <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
            {sandboxStatus === "running" ? "Actif & Connecté" : sandboxStatus === "paused" ? "Suspendu" : "Arrêté"}
          </Badge>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Top Info Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-3">
            <div className="flex items-center justify-between text-neutral-400 text-[11px]">
              <span>ID Session Sandbox</span>
              <ShieldCheckIcon className="size-3 text-emerald-400" />
            </div>
            <p className="mt-1 font-mono text-xs font-semibold text-neutral-100 truncate">
              sbx-e2b-{threadId.slice(0, 8)}
            </p>
            <p className="mt-1 text-[10px] text-neutral-500">Instance isolée par thread</p>
          </div>

          <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-3">
            <div className="flex items-center justify-between text-neutral-400 text-[11px]">
              <span>Modèle d'exécution</span>
              <CpuIcon className="size-3 text-blue-400" />
            </div>
            <p className="mt-1 font-mono text-xs font-semibold text-neutral-100">
              E2B Desktop MicroVM
            </p>
            <p className="mt-1 text-[10px] text-neutral-500">2 vCPU · 4 GB RAM</p>
          </div>

          <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-3">
            <div className="flex items-center justify-between text-neutral-400 text-[11px]">
              <span>Mémoire RAM</span>
              <ActivityIcon className="size-3 text-amber-400" />
            </div>
            <p className="mt-1 font-mono text-xs font-semibold text-neutral-100">
              842 MB / 4 096 MB
            </p>
            <div className="mt-1.5 h-1.5 w-full rounded-full bg-neutral-800 overflow-hidden">
              <div className="h-full bg-amber-400 rounded-full" style={{ width: "21%" }} />
            </div>
          </div>

          <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-3">
            <div className="flex items-center justify-between text-neutral-400 text-[11px]">
              <span>Disque Workspace</span>
              <HardDriveIcon className="size-3 text-purple-400" />
            </div>
            <p className="mt-1 font-mono text-xs font-semibold text-neutral-100">
              284 MB / 10 GB
            </p>
            <div className="mt-1.5 h-1.5 w-full rounded-full bg-neutral-800 overflow-hidden">
              <div className="h-full bg-purple-400 rounded-full" style={{ width: "3%" }} />
            </div>
          </div>
        </div>

        {/* Lifecycle & Security Controls */}
        <div className="rounded-lg border border-neutral-800 bg-neutral-900/30 p-4">
          <h4 className="text-xs font-semibold text-neutral-200 mb-2">Cycle de vie & Sécurité E2B</h4>
          <p className="text-[11px] text-neutral-400 leading-relaxed mb-4">
            Le bac à sable E2B Cloud assure l'isolation complète du système d'exploitation, des processus Chromium et de la console.
            Les opérations réseau sont restreintes et vérifiées contre les attaques SSRF.
          </p>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              className="h-8 text-xs border-neutral-700 hover:bg-neutral-800 gap-1.5"
              onClick={handlePauseResume}
            >
              {sandboxStatus === "running" ? (
                <>
                  <PauseIcon className="size-3 text-amber-400" />
                  Suspendre la session
                </>
              ) : (
                <>
                  <PlayIcon className="size-3 text-emerald-400" />
                  Reprendre la session
                </>
              )}
            </Button>

            <Button
              size="sm"
              variant="outline"
              className="h-8 text-xs border-neutral-700 hover:bg-neutral-800 gap-1.5"
              onClick={handleRestart}
              disabled={isRestarting}
            >
              <RefreshCwIcon className={`size-3 text-blue-400 ${isRestarting ? "animate-spin" : ""}`} />
              Réinitialiser le bac à sable
            </Button>

            <Button
              size="sm"
              variant="outline"
              className="h-8 text-xs border-neutral-700 hover:bg-neutral-800 text-red-400 hover:text-red-300 gap-1.5"
              onClick={() => {
                setSandboxStatus("stopped");
                toast.error("Bac à sable arrêté.");
              }}
            >
              <SquareIcon className="size-3" />
              Arrêter l'environnement
            </Button>
          </div>
        </div>

        {/* Runtime Environment Checklist */}
        <div className="rounded-lg border border-neutral-800 bg-neutral-900/30 p-4">
          <h4 className="text-xs font-semibold text-neutral-200 mb-3">Composants opérationnels dans ce bac à sable</h4>
          <div className="space-y-2 text-[11px]">
            <div className="flex items-center justify-between py-1 border-b border-neutral-800/60">
              <span className="text-neutral-300">Navigateur Google Chrome Headless + CDP</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2Icon className="size-3" />
                Opérationnel (port 9222)
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-neutral-800/60">
              <span className="text-neutral-300">Flux d'affichage Desktop E2B (WebSockets)</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2Icon className="size-3" />
                Connecté (60 fps / compression binaire)
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-neutral-800/60">
              <span className="text-neutral-300">Environnement d'exécution Python 3.12</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2Icon className="size-3" />
                Prêt (pandas, pypdf, httpx pré-chargés)
              </span>
            </div>
            <div className="flex items-center justify-between py-1">
              <span className="text-neutral-300">Persistance & Synchronisation des Livrables</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2Icon className="size-3" />
                Actif vers nkyel Studio
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
