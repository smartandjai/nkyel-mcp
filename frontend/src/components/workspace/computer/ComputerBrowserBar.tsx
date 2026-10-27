"use client";

import React, { useState, useEffect } from "react";
import {
  ArrowLeftIcon,
  RotateCwIcon,
  GlobeIcon,
  SearchIcon,
  ExternalLinkIcon,
  ShieldCheckIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface ComputerBrowserBarProps {
  currentUrl: string;
  pageTitle?: string;
  onNavigate: (url: string) => void;
  onBack?: () => void;
  onRefresh?: () => void;
  isUserControlling: boolean;
  className?: string;
}

export function ComputerBrowserBar({
  currentUrl,
  pageTitle,
  onNavigate,
  onBack,
  onRefresh,
  isUserControlling,
  className,
}: ComputerBrowserBarProps) {
  const [inputUrl, setInputUrl] = useState(currentUrl || "https://example.com");

  useEffect(() => {
    if (currentUrl) {
      setInputUrl(currentUrl);
    }
  }, [currentUrl]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputUrl.trim()) {
      let target = inputUrl.trim();
      if (!target.startsWith("http://") && !target.startsWith("https://")) {
        target = `https://${target}`;
      }
      onNavigate(target);
    }
  };

  return (
    <div className="flex flex-col gap-1.5 border-b border-zinc-800 bg-zinc-900/90 px-3 py-2">
      <div className="flex items-center gap-2">
        <Button
          size="icon-sm"
          variant="ghost"
          onClick={onBack}
          className="h-7 w-7 text-zinc-400 hover:text-white"
          title="Précédent"
        >
          <ArrowLeftIcon className="h-3.5 w-3.5" />
        </Button>
        <Button
          size="icon-sm"
          variant="ghost"
          onClick={onRefresh}
          className="h-7 w-7 text-zinc-400 hover:text-white"
          title="Actualiser"
        >
          <RotateCwIcon className="h-3.5 w-3.5" />
        </Button>

        <form onSubmit={handleSubmit} className="relative flex-1">
          <div className="relative flex items-center">
            <span className="absolute left-2.5 flex items-center text-zinc-400">
              <ShieldCheckIcon className="h-3.5 w-3.5 text-emerald-500 mr-1" />
              <GlobeIcon className="h-3 w-3 text-zinc-500" />
            </span>
            <Input
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              disabled={!isUserControlling}
              placeholder="Entrer une URL (ex: https://example.com)..."
              className="h-7.5 w-full bg-zinc-950 pl-12 pr-16 text-xs text-zinc-200 border-zinc-800 focus-visible:ring-primary/40 font-mono"
            />
            {isUserControlling && (
              <Button
                type="submit"
                size="sm"
                variant="ghost"
                className="absolute right-1 h-6 px-2 text-[10px] text-primary hover:bg-primary/10"
              >
                Aller
              </Button>
            )}
          </div>
        </form>
      </div>

      {pageTitle && (
        <div className="flex items-center gap-2 px-1 text-[11px] text-zinc-400 truncate">
          <span className="font-semibold text-zinc-300">Titre :</span>
          <span className="truncate">{pageTitle}</span>
        </div>
      )}
    </div>
  );
}
