"use client";

import React, { useState } from "react";
import { ExternalLinkIcon, GlobeIcon, CheckCircle2Icon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface NkyelSourceItem {
  title: string;
  url: string;
  domain?: string;
  snippet?: string;
  score?: number;
}

export interface NkyelSourceCardProps {
  source: NkyelSourceItem;
  index?: number;
  className?: string;
}

export function NkyelSourceCard({ source, index, className }: NkyelSourceCardProps) {
  const [imgError, setImgError] = useState(false);
  const domain = source.domain || extractDomain(source.url);
  const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "group relative flex flex-col justify-between overflow-hidden rounded-xl border border-border/80 bg-card p-3.5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/50 hover:shadow-md",
        className
      )}
    >
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <div className="flex size-5 shrink-0 items-center justify-center rounded-sm bg-muted overflow-hidden">
              {!imgError ? (
                <img
                  src={faviconUrl}
                  alt={domain}
                  className="size-4 object-contain"
                  onError={() => setImgError(true)}
                  loading="lazy"
                />
              ) : (
                <GlobeIcon className="size-3 text-muted-foreground" />
              )}
            </div>
            <span className="truncate text-xs font-medium text-muted-foreground group-hover:text-foreground transition-colors">
              {domain}
            </span>
          </div>

          <div className="flex items-center gap-1">
            {index !== undefined && (
              <span className="flex size-4 items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary">
                {index + 1}
              </span>
            )}
            <ExternalLinkIcon className="size-3 text-muted-foreground/60 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-primary" />
          </div>
        </div>

        <h4 className="line-clamp-2 text-xs font-semibold text-foreground group-hover:text-primary transition-colors leading-snug">
          {source.title}
        </h4>

        {source.snippet && (
          <p className="line-clamp-3 text-[11px] text-muted-foreground leading-relaxed">
            {source.snippet}
          </p>
        )}
      </div>

      <div className="mt-2.5 flex items-center gap-1 border-t border-border/40 pt-2 text-[10px] text-muted-foreground">
        <CheckCircle2Icon className="size-3 text-emerald-500" />
        <span>Source officielle vérifiée</span>
      </div>
    </a>
  );
}

function extractDomain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
