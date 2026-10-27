"use client";

import React, { useState, useEffect } from "react";
import { FolderIcon, FileTextIcon, RefreshCwIcon, DownloadIcon, EyeIcon, Loader2Icon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { listComputerFiles, readComputerFile } from "@/core/e2b/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import type { E2BFileItem } from "@/core/e2b/types";

interface ComputerFilesViewProps {
  threadId: string;
  className?: string;
}

export function ComputerFilesView({ threadId, className }: ComputerFilesViewProps) {
  const [currentPath, setCurrentPath] = useState("/home/user");
  const [files, setFiles] = useState<E2BFileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<{ path: string; content: string } | null>(null);

  const fetchFiles = async (dir = currentPath) => {
    setLoading(true);
    try {
      const items = await listComputerFiles(threadId, dir);
      setFiles(items);
      setCurrentPath(dir);
    } catch (e: any) {
      toast.error(e.message || "Erreur de chargement des fichiers");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles("/home/user");
  }, [threadId]);

  const handleInspect = async (file: E2BFileItem) => {
    if (file.type === "dir") {
      fetchFiles(file.path);
      return;
    }
    try {
      const data = await readComputerFile(threadId, file.path);
      setSelectedFile(data);
    } catch (e: any) {
      toast.error(`Impossible de lire ${file.name}`);
    }
  };

  const handleDownload = (file: E2BFileItem) => {
    toast.info(`Téléchargement de ${file.name} initié.`);
  };

  return (
    <div className={cn("flex size-full flex-col bg-zinc-950 text-zinc-100 font-mono text-xs", className)}>
      {/* Path header & reload */}
      <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900/80 px-3 py-2">
        <div className="flex items-center gap-2 truncate">
          <FolderIcon className="h-4 w-4 text-primary shrink-0" />
          <span className="text-zinc-400">Répertoire :</span>
          <span className="font-semibold text-zinc-200 truncate">{currentPath}</span>
        </div>
        <Button
          size="icon-sm"
          variant="ghost"
          onClick={() => fetchFiles(currentPath)}
          disabled={loading}
          className="h-7 w-7 text-zinc-400 hover:text-white"
        >
          <RefreshCwIcon className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
        </Button>
      </div>

      {/* File List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {loading ? (
          <div className="flex items-center justify-center py-8 text-zinc-500 gap-2">
            <Loader2Icon className="h-4 w-4 animate-spin text-primary" />
            <span>Lecture du système de fichiers E2B...</span>
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-8 text-zinc-500 italic">
            Aucun fichier généré dans ce répertoire pour l'instant.
          </div>
        ) : (
          files.map((f) => (
            <div
              key={f.path}
              onClick={() => handleInspect(f)}
              className="flex items-center justify-between p-2 rounded-lg hover:bg-zinc-900/80 border border-transparent hover:border-zinc-800 transition cursor-pointer"
            >
              <div className="flex items-center gap-2.5 truncate">
                {f.type === "dir" ? (
                  <FolderIcon className="h-4 w-4 text-amber-400 shrink-0" />
                ) : (
                  <FileTextIcon className="h-4 w-4 text-zinc-400 shrink-0" />
                )}
                <span className={cn("truncate font-mono", f.type === "dir" ? "font-bold text-zinc-200" : "text-zinc-300")}>
                  {f.name}
                </span>
              </div>

              <div className="flex items-center gap-1 shrink-0">
                {f.type !== "dir" && (
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(f);
                    }}
                    className="h-6 w-6 text-zinc-400 hover:text-white"
                  >
                    <DownloadIcon className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* File Content Preview Modal / Drawer */}
      {selectedFile && (
        <div className="h-56 border-t border-zinc-800 bg-zinc-900/95 p-3 flex flex-col">
          <div className="flex items-center justify-between pb-1.5 border-b border-zinc-800">
            <span className="font-semibold text-zinc-200 truncate">{selectedFile.path}</span>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setSelectedFile(null)}
              className="h-6 text-[10px] text-zinc-400 hover:text-white"
            >
              Fermer
            </Button>
          </div>
          <pre className="flex-1 mt-2 overflow-y-auto font-mono text-zinc-300 whitespace-pre-wrap text-[11px] leading-relaxed p-2 bg-black/40 rounded border border-zinc-800/60">
            {selectedFile.content}
          </pre>
        </div>
      )}
    </div>
  );
}
