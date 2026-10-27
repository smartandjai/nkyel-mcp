"use client";

import React, { useState } from "react";
import { Code2Icon, PlayIcon, Loader2Icon, SparklesIcon, CheckCircle2Icon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { runE2BCode } from "@/core/e2b/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const SAMPLE_CODES: Record<string, string> = {
  stats: `# Synthèse statistique pour la mission
import math

donnees = [120, 145, 180, 210, 240, 310]
moyenne = sum(donnees) / len(donnees)
ecart_type = math.sqrt(sum((x - moyenne)**2 for x in donnees) / len(donnees))

print(f"Échantillon : {donnees}")
print(f"Moyenne calculée : {moyenne:.2f}")
print(f"Écart-type : {ecart_type:.2f}")
print("Validation souveraine E2B Cloud : Conforme.")
`,
  aninf: `# Analyse de données des téléservices ANINF Gabon
services = [
    {"nom": "DGDI e-Visa", "statut": "Opérationnel", "delai": "48h"},
    {"nom": "Guichet Unique Investissement", "statut": "Actif", "delai": "24h"},
    {"nom": "Portail CNAMGS", "statut": "Vérifié", "delai": "Immédiat"},
]

for s in services:
    print(f"✓ {s['nom']} - Statut: {s['statut']} (Délai moyen: {s['delai']})")
`,
};

export function E2BCodeViewer({ className }: { className?: string }) {
  const [code, setCode] = useState<string>(SAMPLE_CODES.stats || "");
  const [stdout, setStdout] = useState<string[]>([]);
  const [stderr, setStderr] = useState<string[]>([]);
  const [results, setResults] = useState<Array<{ type: string; data: string }>>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeMs, setTimeMs] = useState<number | null>(null);

  const handleRun = async () => {
    if (!code.trim() || loading) return;
    setLoading(true);
    setError(null);

    try {
      const res = await runE2BCode(code);
      setStdout(res.stdout || []);
      setStderr(res.stderr || []);
      setResults(res.results || []);
      setError(res.error || null);
      setTimeMs(res.execution_time_ms);
      if (res.error) {
        toast.error("Erreur durant l'exécution Python");
      } else {
        toast.success(`Code exécuté avec succès en ${res.execution_time_ms}ms !`);
      }
    } catch (e: any) {
      setError(e.message || "Erreur de connexion avec la microVM E2B");
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("flex flex-col h-full bg-neutral-950 font-mono text-xs text-neutral-200", className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-neutral-800 bg-neutral-900/80">
        <div className="flex items-center gap-2">
          <Code2Icon className="size-3.5 text-blue-400" />
          <span className="font-semibold text-neutral-200">E2B Code Interpreter (Python 3.12)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setCode(SAMPLE_CODES.stats || "")}
            className="rounded bg-neutral-800 px-2 py-0.5 text-[10px] text-neutral-300 hover:bg-neutral-700"
          >
            Statistiques
          </button>
          <button
            onClick={() => setCode(SAMPLE_CODES.aninf || "")}
            className="rounded bg-neutral-800 px-2 py-0.5 text-[10px] text-neutral-300 hover:bg-neutral-700"
          >
            ANINF Services
          </button>
        </div>
      </div>

      {/* Code Editor */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="p-2 bg-neutral-950/90 flex-1 flex flex-col min-h-[160px]">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            disabled={loading}
            placeholder="# Entrez du code Python à exécuter dans E2B Cloud..."
            className="w-full flex-1 bg-neutral-900/40 p-2.5 rounded-lg border border-neutral-800 text-neutral-100 font-mono text-[11px] focus:outline-none focus:border-blue-500/50 resize-none leading-relaxed"
          />
        </div>

        {/* Action Row */}
        <div className="flex items-center justify-between px-3 py-2 bg-neutral-900 border-y border-neutral-800">
          <div className="text-[10px] text-neutral-400 font-sans">
            {timeMs !== null ? (
              <span className="text-emerald-400 font-mono">Dernière exécution : {timeMs}ms</span>
            ) : (
              <span>Exécution isolée dans E2B Cloud MicroVM</span>
            )}
          </div>
          <Button
            size="sm"
            onClick={handleRun}
            disabled={loading || !code.trim()}
            className="h-7 px-3 text-[11px] bg-blue-600 hover:bg-blue-500 text-white font-medium gap-1.5"
          >
            {loading ? <Loader2Icon className="size-3 animate-spin" /> : <PlayIcon className="size-3" />}
            Exécuter le code
          </Button>
        </div>

        {/* Output Panel */}
        <div className="flex-1 overflow-y-auto p-3 bg-neutral-950 space-y-2 border-t border-neutral-800/80">
          <div className="text-[10px] font-semibold text-neutral-500 uppercase tracking-wider font-sans">
            Sortie standard & résultats :
          </div>

          {stdout.length > 0 && (
            <div className="rounded bg-neutral-900/60 p-2.5 border border-neutral-800 space-y-1">
              {stdout.map((line, idx) => (
                <div key={idx} className="text-neutral-200 text-[11px] whitespace-pre-wrap">
                  {line}
                </div>
              ))}
            </div>
          )}

          {results.map((res, idx) => (
            <div key={idx} className="rounded bg-neutral-900/60 p-2.5 border border-neutral-800">
              {res.type === "image/png" ? (
                <img
                  src={`data:image/png;base64,${res.data}`}
                  alt="E2B Generated Plot"
                  className="rounded max-h-60 mx-auto"
                />
              ) : (
                <pre className="text-emerald-400 text-[11px] whitespace-pre-wrap">{res.data}</pre>
              )}
            </div>
          ))}

          {error && (
            <div className="rounded bg-rose-950/40 p-2.5 border border-rose-800/60 text-rose-300 text-[11px] whitespace-pre-wrap">
              {error}
            </div>
          )}

          {stdout.length === 0 && results.length === 0 && !error && !loading && (
            <div className="text-neutral-600 italic text-[11px]">
              Aucun résultat pour le moment. Cliquez sur « Exécuter le code ».
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
