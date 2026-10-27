"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { FlickeringGrid } from "@/components/ui/flickering-grid";
import { NkyelEmblem } from "@/components/ui/nkyel-logo";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const next = searchParams.get("next") || "/workspace";
    router.replace(`/sign-in?redirect_url=${encodeURIComponent(next)}`);
  }, [router, searchParams]);

  return (
    <div className="bg-background relative flex min-h-screen items-center justify-center px-4">
      <FlickeringGrid
        className="absolute inset-0 z-0 mask-[url(/images/nkyel.svg)] mask-size-[100vw] mask-center mask-no-repeat md:mask-size-[72vh]"
        squareSize={4}
        gridGap={4}
        color="currentColor"
        maxOpacity={0.2}
      />
      <div className="relative z-10 flex flex-col items-center">
        <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-b from-primary/15 via-primary/5 to-transparent p-3 ring-1 ring-border/50 shadow-inner">
          <NkyelEmblem size={44} className="text-foreground animate-pulse" />
        </div>
        <p className="text-muted-foreground text-sm">Redirection vers l&apos;authentification souveraine...</p>
      </div>
    </div>
  );
}
