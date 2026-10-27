"use client";

import { useSearchParams } from "next/navigation";
import { useMemo } from "react";

import { useI18n } from "@/core/i18n/hooks";
import { cn } from "@/lib/utils";

import { AuroraText } from "../ui/aurora-text";
import { NkyelEmblem } from "../ui/nkyel-logo";

function WelcomeDescription({ children }: { children: string }) {
  return (
    <p className="max-w-full text-wrap break-words whitespace-pre-line">
      {children}
    </p>
  );
}

export function Welcome({
  className,
  mode,
}: {
  className?: string;
  mode?: "ultra" | "pro" | "thinking" | "flash";
}) {
  const { t } = useI18n();
  const searchParams = useSearchParams();
  const isUltra = useMemo(() => mode === "ultra", [mode]);
  const colors = useMemo(() => {
    if (isUltra) {
      return ["#efefbb", "#e9c665", "#e3a812"];
    }
    return ["var(--color-foreground)"];
  }, [isUltra]);
  return (
    <div
      className={cn(
        "mx-auto flex w-full max-w-full flex-col items-center justify-center gap-3 px-4 py-6 text-center sm:px-8",
        className,
      )}
    >
      <div className="relative flex items-center justify-center">
        <div className="absolute -inset-3 rounded-3xl bg-gradient-to-tr from-primary/25 via-primary/5 to-transparent blur-lg opacity-75" />
        <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-b from-card to-card/70 border border-border/60 shadow-lg ring-1 ring-white/5">
          <NkyelEmblem size={36} className="text-foreground" />
        </div>
      </div>

      <div className="max-w-full text-2xl font-bold tracking-tight">
        {searchParams.get("mode") === "skill" ? (
          `✨ ${t.welcome.createYourOwnSkill} ✨`
        ) : (
          <div className="flex max-w-full flex-wrap items-center justify-center gap-2">
            <AuroraText colors={colors}>{t.welcome.greeting}</AuroraText>
          </div>
        )}
      </div>
      {searchParams.get("mode") === "skill" ? (
        <div className="text-muted-foreground max-w-full text-sm">
          <WelcomeDescription>
            {t.welcome.createYourOwnSkillDescription}
          </WelcomeDescription>
        </div>
      ) : (
        <div className="text-muted-foreground max-w-full text-sm">
          <WelcomeDescription>{t.welcome.description}</WelcomeDescription>
        </div>
      )}
    </div>
  );
}
