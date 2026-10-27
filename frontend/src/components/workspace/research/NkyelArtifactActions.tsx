"use client";

import React, { useState } from "react";
import { CopyIcon, CheckIcon, DownloadIcon, PrinterIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { writeTextToClipboard } from "@/core/clipboard";
import { cn } from "@/lib/utils";

export interface NkyelArtifactActionsProps {
  content: string;
  title?: string;
  className?: string;
}

export function NkyelArtifactActions({
  content,
  title = "Synthese-Recherche-Nkyel",
  className,
}: NkyelArtifactActionsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await writeTextToClipboard(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  const handleDownloadMarkdown = () => {
    try {
      const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${title.toLowerCase().replace(/\s+/g, "-")}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      // ignore
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className={cn("flex flex-wrap items-center gap-2 pt-2 border-t border-border/50", className)}>
      <Button
        variant="outline"
        size="sm"
        onClick={handleCopy}
        className="h-8 gap-1.5 text-xs font-medium"
      >
        {copied ? (
          <>
            <CheckIcon className="size-3.5 text-emerald-500" />
            <span>Copié !</span>
          </>
        ) : (
          <>
            <CopyIcon className="size-3.5 text-muted-foreground" />
            <span>Copier la synthèse</span>
          </>
        )}
      </Button>

      <Button
        variant="outline"
        size="sm"
        onClick={handleDownloadMarkdown}
        className="h-8 gap-1.5 text-xs font-medium"
      >
        <DownloadIcon className="size-3.5 text-muted-foreground" />
        <span>Télécharger (.md)</span>
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={handlePrint}
        className="h-8 gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground"
      >
        <PrinterIcon className="size-3.5" />
        <span>Imprimer</span>
      </Button>
    </div>
  );
}
