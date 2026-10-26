import type { Translations } from "@/core/i18n/locales/types";

import type { LoadedContribution } from "./registry";

// Discovery metadata only: catalog entries never enter the runtime module loader.
export const extensionCatalog = [
  {
    key: "agentTeams",
    package: "nkyel-extension-agent-teams",
    namespace: "community.agent-teams",
  },
  {
    key: "bookmarks",
    package: "nkyel-extension-bookmarks",
    namespace: "community.bookmarks",
    icon: "bookmark",
  },
  {
    key: "context",
    package: "nkyel-extension-jev-context",
    namespace: "community.jev-context",
  },
  {
    key: "classify",
    package: "nkyel-extension-jev-classify",
    namespace: "community.jev-classify",
  },
  {
    key: "screening",
    package: "nkyel-extension-jev-screening",
    namespace: null,
  },
  {
    key: "workflows",
    package: "nkyel-extension-workflows",
    namespace: "community.workflows",
  },
  {
    key: "reportSections",
    package: "nkyel-extension-report-sections",
    namespace: "community.report-sections",
  },
  {
    key: "retrieval",
    package: "nkyel-extension-retrieval",
    namespace: "example.retrieval",
  },
  {
    key: "knowledge",
    package: "nkyel-extension-knowledge",
    namespace: null,
  },
  {
    key: "knowledgeManagement",
    package: "nkyel-extension-knowledge-management",
    namespace: "knowledge-management",
  },
  {
    key: "knowledgePlatform",
    package: "nkyel-extension-knowledge-platform",
    namespace: "knowledge-platform",
  },
  { key: "lightrag", package: "nkyel-extension-lightrag", namespace: null },
  { key: "weknora", package: "nkyel-extension-weknora", namespace: null },
  { key: "example", package: "nkyel-extension-example", namespace: null },
] as const;

export interface ExtensionCatalogEntry {
  id: string;
  title: string;
  description: string;
  package?: string;
  guide?: string;
  icon?: string;
  loaded?: LoadedContribution;
}

export function extensionDirectory(
  loaded: LoadedContribution[],
  copy: Translations["extensions"]["catalog"],
): ExtensionCatalogEntry[] {
  const entries: ExtensionCatalogEntry[] = extensionCatalog.map((item) => ({
    id: item.namespace ?? `catalog/${item.key}`,
    ...copy[item.key],
    package: item.package,
    guide: `https://github.com/bytedance/deer-flow/tree/main/examples/${item.package}#readme`,
    icon: "icon" in item ? item.icon : undefined,
    loaded: loaded.find((entry) => entry.namespace === item.namespace),
  }));
  const known = new Set<string | null>(
    extensionCatalog.map((item) => item.namespace),
  );
  for (const entry of loaded) {
    if (known.has(entry.namespace)) continue;
    entries.push({
      id: entry.namespace,
      title: entry.title,
      description: entry.description,
      loaded: entry,
    });
  }
  return entries;
}
