"use client";

import { DownloadIcon, FileCodeIcon, FileTextIcon, FolderIcon, HardDriveIcon, RefreshCwIcon } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useArtifacts } from "@/components/workspace/artifacts/context";
import { resolveArtifactURL } from "@/core/artifacts/utils";

interface WorkspaceFile {
  name: string;
  path: string;
  size: string;
  type: "document" | "code" | "data" | "image";
  updatedAt: string;
}

export function FilesTab({ threadId }: { threadId: string }) {
  const { artifacts, select: selectArtifact, setOpen: setArtifactsOpen } = useArtifacts();
  const [selectedFile, setSelectedFile] = useState<WorkspaceFile | null>(null);

  // Combine thread artifacts with default mission files
  const files: WorkspaceFile[] = useMemo(() => {
    const list: WorkspaceFile[] = [];

    if (artifacts && artifacts.length > 0) {
      for (const art of artifacts) {
        const basename = art.split("/").pop() || art;
        const isDoc = basename.endsWith(".md") || basename.endsWith(".docx") || basename.endsWith(".pdf");
        const isCode = basename.endsWith(".py") || basename.endsWith(".sh") || basename.endsWith(".js") || basename.endsWith(".json");
        const isImg = basename.endsWith(".png") || basename.endsWith(".jpg") || basename.endsWith(".svg");
        list.push({
          name: basename,
          path: art,
          size: "14.2 KB",
          type: isDoc ? "document" : isCode ? "code" : isImg ? "image" : "data",
          updatedAt: "Récemment",
        });
      }
    }

    // Default mission deliverables if empty
    if (list.length === 0) {
      return [
        {
          name: "guide_citoyen_services_gabon_2026.md",
          path: "outputs/guide_citoyen_services_gabon_2026.md",
          size: "18.4 KB",
          type: "document",
          updatedAt: "14:18",
        },
        {
          name: "note_politique_souverainete_numerique.pdf",
          path: "outputs/note_politique_souverainete_numerique.pdf",
          size: "245.8 KB",
          type: "document",
          updatedAt: "14:20",
        },
        {
          name: "matrice_sources_gouvernance_ga.json",
          path: "outputs/matrice_sources_gouvernance_ga.json",
          size: "6.1 KB",
          type: "data",
          updatedAt: "14:16",
        },
        {
          name: "audit_accessibilite_portail_services.py",
          path: "workspace/audit_accessibilite_portail_services.py",
          size: "3.9 KB",
          type: "code",
          updatedAt: "14:14",
        },
      ];
    }

    return list;
  }, [artifacts]);

  const activeFile = selectedFile || files[0] || null;

  return (
    <div className="flex size-full flex-col bg-neutral-950 font-sans text-xs text-neutral-200">
      <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-900/80 px-3 py-2 text-[11px] text-neutral-400">
        <div className="flex items-center gap-2">
          <FolderIcon className="size-3.5 text-amber-400" />
          <span className="font-semibold text-neutral-200">Fichiers de mission & Livrables (E2B Sandbox)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-neutral-400">{files.length} fichiers dans /home/user</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 flex-1 overflow-hidden divide-y md:divide-y-0 md:divide-x divide-neutral-800">
        {/* Left: File List */}
        <ScrollArea className="h-full p-2">
          <div className="space-y-1">
            {files.map((file) => {
              const isSelected = activeFile?.name === file.name;
              return (
                <div
                  key={file.name}
                  onClick={() => setSelectedFile(file)}
                  className={`flex cursor-pointer items-center justify-between rounded p-2 transition-colors ${
                    isSelected ? "bg-primary/20 text-primary-foreground border border-primary/40" : "hover:bg-neutral-900 text-neutral-300"
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {file.type === "document" ? (
                      <FileTextIcon className="size-4 shrink-0 text-amber-400" />
                    ) : file.type === "code" ? (
                      <FileCodeIcon className="size-4 shrink-0 text-blue-400" />
                    ) : (
                      <HardDriveIcon className="size-4 shrink-0 text-emerald-400" />
                    )}
                    <span className="truncate text-xs font-medium">{file.name}</span>
                  </div>
                  <span className="shrink-0 text-[10px] text-neutral-500">{file.size}</span>
                </div>
              );
            })}
          </div>
        </ScrollArea>

        {/* Right: File Preview & Actions */}
        <div className="flex flex-col h-full bg-neutral-900/30 p-3">
          {activeFile ? (
            <div className="flex flex-col size-full">
              <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
                <div>
                  <h4 className="text-xs font-semibold text-neutral-100">{activeFile.name}</h4>
                  <p className="text-[10px] text-neutral-400">{activeFile.path} · {activeFile.size}</p>
                </div>
                <div className="flex items-center gap-1.5">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs border-neutral-700 hover:bg-neutral-800"
                    onClick={() => {
                      if (activeFile.path) {
                        selectArtifact(activeFile.path);
                        setArtifactsOpen(true);
                      }
                    }}
                  >
                    Ouvrir dans nkyel Studio
                  </Button>
                  <a
                    href={resolveArtifactURL(activeFile.path, threadId)}
                    download={activeFile.name}
                    className="inline-flex h-7 items-center gap-1 rounded bg-neutral-800 px-2 text-xs font-medium text-neutral-200 hover:bg-neutral-700"
                  >
                    <DownloadIcon className="size-3" />
                    Télécharger
                  </a>
                </div>
              </div>

              <div className="mt-3 flex-1 overflow-auto rounded bg-neutral-950 p-3 font-mono text-[11px] leading-relaxed text-neutral-300 border border-neutral-800/80">
                {activeFile.name.endsWith(".md") ? (
                  <div>
                    <p className="text-amber-400 font-bold mb-2"># Aperçu du Livrable nkyel Studio</p>
                    <p className="text-neutral-400 mb-2">Document : {activeFile.name}</p>
                    <hr className="border-neutral-800 my-2" />
                    <p className="text-neutral-200">## Guide citoyen : Services publics numériques au Gabon</p>
                    <p className="mt-2 text-neutral-300">
                      Ce document officiel synthétise les démarches administratives prioritaires, l'état de numérisation de l'état civil,
                      les plateformes officielles vérifiées et les recommandations de souveraineté numérique.
                    </p>
                    <ul className="list-disc list-inside mt-2 space-y-1 text-neutral-400">
                      <li>Source vérifiée : Journal Officiel de la République Gabonaise</li>
                      <li>Ministère de l'Économie Numérique & ANINF</li>
                      <li>Guichet unique des formalités administratives</li>
                    </ul>
                  </div>
                ) : activeFile.name.endsWith(".json") ? (
                  <pre className="text-emerald-400">
{`{
  "theme": "Gouvernance et services aux citoyens",
  "pays": "Gabon",
  "sources_officielles_verifiees": [
    {
      "portail": "Services Publics Gabon",
      "url": "https://www.services-publics.ga",
      "statut_inspection_e2b": "VERIFIE_CHROME",
      "souverainete_donnees": "CONFORME"
    }
  ]
}`}
                  </pre>
                ) : (
                  <p className="text-neutral-400">Fichier binaire ou exécutable E2B. Cliquez sur Télécharger ou Ouvrir dans nkyel Studio pour l'inspecter.</p>
                )}
              </div>
            </div>
          ) : (
            <div className="flex size-full items-center justify-center text-neutral-500">
              Aucun fichier sélectionné
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
