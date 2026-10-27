"use client";

import {
  CheckCircle2Icon,
  CloudIcon,
  FileTextIcon,
  HardDriveIcon,
  MailIcon,
  RefreshCwIcon,
  SearchIcon,
  SendIcon,
  ShieldCheckIcon,
  SparklesIcon,
  XCircleIcon,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

export interface MCPToolItem {
  category: string;
  server: string;
  status: string;
  description: string;
}

export interface GmailDraft {
  approval_token: string;
  status: string;
  to: string;
  subject: string;
  body: string;
  attachments: Array<{
    filename: string;
    filepath: string;
    size_bytes: number;
    checksum: string;
  }>;
}

export function McpHubTab({
  threadId: _threadId,
  onNavigateToUrl: _onNavigateToUrl,
}: {
  threadId?: string;
  onNavigateToUrl?: (url: string) => void;
}) {
  const [tools, setTools] = useState<Record<string, MCPToolItem>>({});
  const [totalCount, setTotalCount] = useState<number>(50);
  const [drafts, setDrafts] = useState<GmailDraft[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [loading, setLoading] = useState(false);
  const [sendingToken, setSendingToken] = useState<string | null>(null);

  const fetchRegistry = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch("/api/nkyel/mcp/registry");
      if (res.ok) {
        const data = (await res.json()) as {
          tools?: Record<string, MCPToolItem>;
          total_tools?: number;
        };
        setTools(data.tools ?? {});
        setTotalCount(data.total_tools ?? 50);
      }
    } catch {
      // Offline fallback
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDrafts = useCallback(async () => {
    try {
      const res = await fetch("/api/nkyel/gmail/drafts");
      if (res.ok) {
        const data = (await res.json()) as GmailDraft[];
        setDrafts(data ?? []);
      }
    } catch {
      // Offline fallback
    }
  }, []);

  useEffect(() => {
    void fetchRegistry();
    void fetchDrafts();
  }, [fetchRegistry, fetchDrafts]);

  const handleApproval = async (token: string, approved: boolean) => {
    try {
      setSendingToken(token);
      const res = await fetch("/api/nkyel/gmail/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approval_token: token, approved }),
      });
      const data = (await res.json()) as { to?: string };
      if (approved) {
        toast.success(`Email certifié et envoyé : ${data.to ?? "destinataire"}`);
      } else {
        toast.info("Envoi de l'email annulé par l'utilisateur.");
      }
      void fetchDrafts();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      toast.error(`Erreur d'approbation : ${msg}`);
    } finally {
      setSendingToken(null);
    }
  };

  const filteredTools = Object.entries(tools).filter(([name, meta]) => {
    const matchesCat =
      selectedCategory === "all" || meta.category === selectedCategory;
    const matchesQuery =
      name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      Boolean(meta.description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCat && matchesQuery;
  });

  return (
    <div className="flex size-full flex-col bg-background text-foreground">
      {/* Top Bar */}
      <div className="flex shrink-0 items-center justify-between border-b px-4 py-2.5">
        <div className="flex items-center gap-2">
          <SparklesIcon className="size-4 text-primary" />
          <span className="font-semibold text-sm">
            Ñkyel MCP Studio & Live Ecosystem
          </span>
          <Badge variant="outline" className="text-xs">
            {totalCount} Outils Connectés
          </Badge>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            void fetchRegistry();
            void fetchDrafts();
          }}
          disabled={loading}
        >
          <RefreshCwIcon className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-6">
          {/* Section 1: Human Approvals & Outgoing Drafts (Manus Style) */}
          {drafts.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-medium text-amber-500">
                <ShieldCheckIcon className="size-4" />
                <span>Validation Humaine Requise avant Envoi</span>
              </div>
              {drafts.map((draft) => (
                <Card
                  key={draft.approval_token}
                  className="border-amber-500/30 bg-amber-500/5 shadow-sm"
                >
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MailIcon className="size-4 text-amber-500" />
                        <CardTitle className="text-sm font-semibold">
                          Brouillon Gmail Prêt : {draft.subject}
                        </CardTitle>
                      </div>
                      <Badge variant="secondary" className="bg-amber-500/20 text-amber-600 text-xs">
                        Jeton: {draft.approval_token}
                      </Badge>
                    </div>
                    <CardDescription className="text-xs">
                      Destinataire : <strong>{draft.to}</strong>
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3 p-4 pt-0">
                    <div className="rounded border bg-background/50 p-2.5 text-xs text-muted-foreground whitespace-pre-wrap">
                      {draft.body}
                    </div>

                    {/* Attachments */}
                    {draft.attachments && draft.attachments.length > 0 && (
                      <div className="space-y-1.5">
                        <span className="text-xs font-medium">
                          Pièce jointe certifiée :
                        </span>
                        {draft.attachments.map((att) => (
                          <div
                            key={att.filename}
                            className="flex items-center justify-between rounded border bg-card p-2 text-xs"
                          >
                            <div className="flex items-center gap-2">
                              <FileTextIcon className="size-3.5 text-primary" />
                              <span className="font-medium">{att.filename}</span>
                              <span className="text-muted-foreground">
                                ({(att.size_bytes / 1024).toFixed(1)} Ko)
                              </span>
                            </div>
                            <Badge variant="outline" className="font-mono text-[10px]">
                              SHA256: {att.checksum.slice(0, 10)}...
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Action buttons */}
                    <div className="flex items-center justify-end gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleApproval(draft.approval_token, false)}
                        disabled={sendingToken === draft.approval_token}
                      >
                        <XCircleIcon className="size-3.5 mr-1" />
                        Rejeter
                      </Button>
                      <Button
                        size="sm"
                        className="bg-primary text-primary-foreground"
                        onClick={() => handleApproval(draft.approval_token, true)}
                        disabled={sendingToken === draft.approval_token}
                      >
                        <SendIcon className="size-3.5 mr-1" />
                        Approuver & Envoyer
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Section 2: Core Sovereign Service Connections */}
          <div className="space-y-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Serveurs & Connecteurs Actifs
            </span>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Card className="p-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <HardDriveIcon className="size-4 text-blue-500" />
                    <div>
                      <div className="font-medium text-xs">Google Drive MCP</div>
                      <div className="text-[11px] text-muted-foreground">
                        drivemcp.googleapis.com
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-emerald-500 border-emerald-500/30 text-[10px]">
                    Connecté (8 Outils)
                  </Badge>
                </div>
              </Card>

              <Card className="p-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <MailIcon className="size-4 text-red-500" />
                    <div>
                      <div className="font-medium text-xs">Gmail MCP & Adapter</div>
                      <div className="text-[11px] text-muted-foreground">
                        gmailmcp.googleapis.com + REST
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-emerald-500 border-emerald-500/30 text-[10px]">
                    Connecté (19 Outils)
                  </Badge>
                </div>
              </Card>

              <Card className="p-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <SearchIcon className="size-4 text-purple-500" />
                    <div>
                      <div className="font-medium text-xs">Tavily Recherche MCP</div>
                      <div className="text-[11px] text-muted-foreground">
                        mcp.tavily.com/mcp/
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-emerald-500 border-emerald-500/30 text-[10px]">
                    Connecté (5 Outils)
                  </Badge>
                </div>
              </Card>

              <Card className="p-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <CloudIcon className="size-4 text-sky-500" />
                    <div>
                      <div className="font-medium text-xs">E2B Desktop Live Sandbox</div>
                      <div className="text-[11px] text-muted-foreground">
                        e2b-desktop SDK v2.7.2
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-emerald-500 border-emerald-500/30 text-[10px]">
                    Actif (7 Outils)
                  </Badge>
                </div>
              </Card>
            </div>
          </div>

          {/* Section 3: 50-Tool Registry Explorer */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Catalogue Unifié des 50 Outils MCP
              </span>
              <span className="text-xs text-muted-foreground">
                {filteredTools.length} sur {totalCount} affichés
              </span>
            </div>

            {/* Filter Pills & Search */}
            <div className="flex flex-wrap items-center gap-2">
              <Input
                placeholder="Filtrer un outil ou une action..."
                className="h-8 flex-1 text-xs"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {["all", "drive", "email", "research", "browser", "artifact", "knowledge"].map(
                (cat) => (
                  <Button
                    key={cat}
                    variant={selectedCategory === cat ? "default" : "outline"}
                    size="sm"
                    className="h-8 text-xs capitalize"
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </Button>
                ),
              )}
            </div>

            {/* Tool List */}
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {filteredTools.map(([name, meta]) => (
                <div
                  key={name}
                  className="flex flex-col justify-between rounded-lg border bg-card p-3 shadow-xs hover:border-primary/50 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-medium text-xs text-primary">
                        {name}
                      </span>
                      <Badge
                        variant="secondary"
                        className="text-[10px] uppercase font-mono"
                      >
                        {meta.category}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-muted-foreground line-clamp-2">
                      {meta.description}
                    </p>
                  </div>
                  <div className="mt-2 flex items-center justify-between border-t pt-2 text-[10px] text-muted-foreground">
                    <span>Serveur: {meta.server}</span>
                    <span className="flex items-center gap-1 text-emerald-500 font-medium">
                      <CheckCircle2Icon className="size-3" />
                      {meta.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
