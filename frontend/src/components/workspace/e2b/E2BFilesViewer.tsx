"use client";

import React, { useState, useEffect } from "react";
import { FolderIcon, FileIcon, RefreshCwIcon, Loader2Icon, HardDriveIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { listE2BFiles } from "@/core/e2b/api";
import { type E2BFileItem } from "@/core/e2b/types";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function E2BFilesViewer({ className }: { className?: string }) {
  const [currentPath, setCurrentPath] = useState("/home/user");
  const [files, setFiles] = useState<E2BFileItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFiles = async (p = currentPath) => {
    setLoading(true);
    try {
      const items = await listE2BFiles(p);
      setFiles(items);
    } catch (e: any) {
      toast.error("Impossible de lister les fichiers");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <div className={cn("flex flex-col h-full bg-neutral-950 font-sans text-xs text-neutral-200", className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-neutral-800 bg-neutral-900/80">
        <div className="flex items-center gap-2">
          <HardDriveIcon className="size-3.5 text-amber-400" />
          <span className="font-semibold text-neutral-200">Explorateur MicroVM E2B</span>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => fetchFiles()}
          disabled={loading}
          className="h-6 w-6 p-0 text-neutral-400 hover:text-neutral-100"
          title="Actualiser"
        >
          <RefreshCwIcon className={cn("size-3.5", loading && "animate-spin")} />
        </Button>
      </div>

      {/* Path indicator */}
      <div className="px-3 py-1.5 bg-neutral-900/40 border-b border-neutral-800 text-[11px] font-mono text-neutral-400 flex items-center gap-2">
        <span>Répertoire :</span>
        <span className="text-neutral-200 font-semibold">{currentPath}</span>
      </div>

      {/* File List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {loading && (
          <div className="flex items-center justify-center p-6 text-neutral-500 gap-2">
            <Loader2Icon className="size-4 animate-spin text-amber-400" />
            <span>Lecture du système de fichiers E2B...</span>
          </div>
        )}

        {!loading && files.length === 0 && (
          <div className="text-center p-8 text-neutral-500 text-xs">
            Le répertoire est vide ou en cours d'initialisation par l'agent.
          </div>
        )}

        {!loading &&
          files.map((file, idx) => (
            <div
              key={file.path || idx}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-neutral-900/70 text-neutral-300 transition-colors border border-transparent hover:border-neutral-800"
            >
              {file.type === "dir" ? (
                <FolderIcon className="size-4 text-amber-400 shrink-0" />
              ) : (
                <FileIcon className="size-4 text-blue-400 shrink-0" />
              )}
              <span className="font-mono text-[11px] truncate flex-1">{file.name}</span>
              <span className="text-[10px] text-neutral-500 uppercase">{file.type}</span>
            </div>
          ))}
      </div>
    </div>
  );
}
