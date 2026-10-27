import type { Locale } from "./locale";
import { enUS } from "./locales/en-US";
import { frFR } from "./locales/fr-FR";
import type { Translations } from "./locales/types";
import { zhCN } from "./locales/zh-CN";

// Translation dictionaries contain formatter functions, so they must be
// selected inside a Client Component rather than serialized through an RSC
// boundary.
export const clientTranslations: Record<Locale, Translations> = {
  "en-US": enUS,
  "fr-FR": frFR,
  "zh-CN": zhCN,
};
