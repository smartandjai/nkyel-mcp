"use client";

import { SignUp } from "@clerk/nextjs";
import { useTheme } from "next-themes";

import { FlickeringGrid } from "@/components/ui/flickering-grid";
import { NkyelEmblem } from "@/components/ui/nkyel-logo";

export default function SignUpPage() {
  const { theme, resolvedTheme } = useTheme();
  const currentTheme = theme === "system" ? resolvedTheme : theme;
  const isDark = currentTheme === "dark";

  return (
    <div className="bg-background relative flex min-h-screen items-center justify-center overflow-x-hidden overflow-y-auto px-4 py-8">
      <FlickeringGrid
        className="absolute inset-0 z-0 mask-[url(/images/nkyel.svg)] mask-size-[100vw] mask-center mask-no-repeat md:mask-size-[72vh]"
        squareSize={4}
        gridGap={4}
        color={isDark ? "white" : "black"}
        maxOpacity={0.25}
        flickerChance={0.2}
      />
      <div className="relative z-10 flex flex-col items-center">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-b from-primary/15 via-primary/5 to-transparent p-3 ring-1 ring-border/50 shadow-inner">
            <NkyelEmblem size={44} className="text-foreground" />
          </div>
          <h1 className="text-foreground text-2xl font-bold tracking-tight">
            nkyel
          </h1>
          <p className="text-muted-foreground mt-1 text-xs sm:text-sm">
            Rejoignez la plateforme souveraine d&apos;agents IA
          </p>
        </div>
        <SignUp
          routing="path"
          path="/sign-up"
          signInUrl="/sign-in"
          fallbackRedirectUrl="/workspace"
          appearance={{
            elements: {
              card: "border border-border/40 bg-card/75 shadow-2xl backdrop-blur-xl rounded-3xl ring-1 ring-white/5",
              headerTitle: "text-foreground font-bold tracking-tight",
              headerSubtitle: "text-muted-foreground text-sm",
              socialButtonsBlockButton: "rounded-xl border border-border/70 hover:bg-muted/60 transition-all font-medium py-2.5",
              formButtonPrimary: "rounded-xl bg-primary text-primary-foreground font-medium py-2.5 hover:bg-primary/90 transition-all shadow-sm",
              formFieldInput: "rounded-xl border border-border/60 bg-background/50 focus:border-primary text-foreground text-sm",
              footerActionLink: "text-primary hover:underline font-medium",
            },
          }}
        />
      </div>
    </div>
  );
}
