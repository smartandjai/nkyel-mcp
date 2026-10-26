"use client";

import {
  ArrowLeftIcon,
  ArrowRightIcon,
  CompassIcon,
  FolderIcon,
  GlobeIcon,
  Loader2Icon,
  MonitorIcon,
  RadioIcon,
  ServerIcon,
  TerminalIcon,
  XIcon,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { ConversationEmptyState } from "@/components/ai-elements/conversation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { resolveArtifactURL } from "@/core/artifacts/utils";
import { useI18n } from "@/core/i18n/hooks";
import { isIMEComposing } from "@/lib/ime";
import { cn } from "@/lib/utils";

import { navigateBrowser } from "./api";
import { useMaybeBrowserView } from "./context";
import { FilesTab } from "./files-tab";
import { decideBrowserKeyInput } from "./keyboard";
import { SandboxTab } from "./sandbox-tab";
import { TavilyTab } from "./tavily-tab";
import { TerminalTab } from "./terminal-tab";
import { type BrowserInputEvent, useBrowserStream } from "./use-browser-stream";

export function BrowserViewPanel({
  threadId,
  className,
}: {
  threadId: string;
  className?: string;
}) {
  const { t } = useI18n();
  const browserView = useMaybeBrowserView();
  const frame = browserView?.latestFrame ?? null;
  const imageUrl = frame
    ? resolveArtifactURL(frame.screenshot, threadId)
    : null;

  const [activeTab, setActiveTab] = useState<
    "desktop" | "terminal" | "files" | "tavily" | "sandbox"
  >("desktop");
  const [urlInput, setUrlInput] = useState("");
  const [navigating, setNavigating] = useState(false);
  const [live, setLive] = useState(true);
  const [lastLiveUrl, setLastLiveUrl] = useState<string | null>(null);
  const [liveFallback, setLiveFallback] = useState<{
    frameUrl: string;
    url?: string;
  } | null>(null);

  const streamSeedUrl = lastLiveUrl ?? liveFallback?.url ?? frame?.url;
  const handleNavRejected = useCallback(
    (url: string | undefined, message: string | undefined) => {
      setNavigating(false);
      toast.error(
        message?.replace(/^Error:\s*/i, "") ??
          `Cannot open ${url ?? "that URL"}`,
      );
    },
    [],
  );
  const { status, closedReason, frameUrl, liveUrl, sendInput } =
    useBrowserStream(threadId, live, streamSeedUrl, handleNavRejected);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const surfaceRef = useRef<HTMLImageElement | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const staticScreenshotRef = useRef<string | null>(null);
  // True while the user is actively editing the URL bar, so background live-URL
  // reports do not clobber a half-typed address the user has not submitted yet.
  const urlEditingRef = useRef(false);
  // Handle for the live-navigate spinner timeout so it can be cleared on
  // unmount / re-navigation instead of firing setState after teardown.
  const navSpinnerTimerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (navSpinnerTimerRef.current !== null) {
        window.clearTimeout(navSpinnerTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    setLastLiveUrl(null);
  }, [threadId]);

  useEffect(() => {
    if (frame?.url && !urlInput && !liveUrl) {
      setUrlInput(frame.url);
    }
  }, [frame?.url, liveUrl, urlInput]);

  // Keep the URL bar in sync with the latest visible browser state while not
  // live. If the user leaves Live mode, the last streamed frame becomes the
  // static baseline instead of falling back to an older artifact screenshot.
  useEffect(() => {
    if (!live) {
      const url = liveFallback?.url ?? frame?.url;
      if (url) {
        setUrlInput(url);
      }
    }
  }, [frame?.url, live, liveFallback?.url]);

  useEffect(() => {
    const screenshot = frame?.screenshot ?? null;
    if (screenshot && screenshot !== staticScreenshotRef.current) {
      staticScreenshotRef.current = screenshot;
      setLiveFallback(null);
    }
  }, [frame?.screenshot]);

  useEffect(() => {
    if (frameUrl) {
      setLiveFallback((prev) => ({
        frameUrl,
        url: liveUrl ?? prev?.url ?? (urlInput || frame?.url),
      }));
    }
  }, [frame?.url, frameUrl, liveUrl, urlInput]);

  // In live mode the server reports the page's real URL (after redirects and
  // history moves). Reconcile the address bar + device-shell label + persisted
  // frame so the top URL never goes stale after navigation.
  useEffect(() => {
    if (live && liveUrl) {
      setLastLiveUrl(liveUrl);
      if (!urlEditingRef.current) {
        setUrlInput(liveUrl === "about:blank" ? "" : liveUrl);
      }
      setNavigating(false);
      setLiveFallback((prev) => (prev ? { ...prev, url: liveUrl } : prev));
    }
  }, [liveUrl, live]);

  const handleNavigate = async (targetOverride?: string) => {
    const target = (targetOverride ?? urlInput).trim();
    if (!target) {
      return;
    }
    const normalized = /^https?:\/\//i.test(target)
      ? target
      : `https://${target}`;

    // In live mode, steer the streamed page directly over the socket. The
    // screencast streams continuously, so there is no single "done" frame to
    // key off — show the reload spinner for a brief window so the user gets
    // clear feedback that the navigation actually took. Also sync the URL
    // everywhere immediately (URL bar, device-shell label, persisted frame).
    if (live) {
      sendInput({ type: "navigate", url: normalized });
      setUrlInput(normalized);
      urlEditingRef.current = false;
      setLiveFallback((prev) => (prev ? { ...prev, url: normalized } : prev));
      setNavigating(true);
      if (navSpinnerTimerRef.current !== null) {
        window.clearTimeout(navSpinnerTimerRef.current);
      }
      navSpinnerTimerRef.current = window.setTimeout(() => {
        navSpinnerTimerRef.current = null;
        setNavigating(false);
      }, 1200);
      return;
    }

    if (navigating) {
      return;
    }
    setNavigating(true);
    try {
      const result = await navigateBrowser(threadId, normalized);
      if (result.screenshot) {
        setLiveFallback(null);
        browserView?.pushFrame({
          screenshot: result.screenshot,
          url: result.url,
          title: result.title,
        });
      } else {
        setUrlInput(result.url);
        toast.warning("Navigated, but no screenshot could be captured.");
      }
      browserView?.openPanel();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : String(error));
    } finally {
      setNavigating(false);
    }
  };

  const normalizedPoint = useCallback(
    (
      clientX: number,
      clientY: number,
      options?: { fallbackToCenter?: boolean },
    ): { nx: number; ny: number } | null => {
      const el = surfaceRef.current;
      if (!el) {
        return null;
      }
      const rect = el.getBoundingClientRect();
      const natW = el.naturalWidth;
      const natH = el.naturalHeight;
      if (!rect.width || !rect.height || !natW || !natH) {
        return null;
      }
      // The frame is drawn with object-contain: scaled to fit and centered, so
      // there are letterbox bars whenever the panel and remote viewport differ
      // in aspect. Map the pointer against the actual content box.
      const scale = Math.min(rect.width / natW, rect.height / natH);
      const contentW = natW * scale;
      const contentH = natH * scale;
      const offX = (rect.width - contentW) / 2;
      const offY = (rect.height - contentH) / 2;
      const px = clientX - rect.left - offX;
      const py = clientY - rect.top - offY;
      if (px < 0 || py < 0 || px > contentW || py > contentH) {
        if (options?.fallbackToCenter) {
          return { nx: 0.5, ny: 0.5 };
        }
        return null;
      }
      return { nx: px / contentW, ny: py / contentH };
    },
    [],
  );

  const forwardMouse = (
    type: Extract<BrowserInputEvent, { nx: number }>["type"],
    event: React.MouseEvent<HTMLImageElement>,
  ) => {
    if (!live) {
      return;
    }
    const point = normalizedPoint(event.clientX, event.clientY);
    if (point) {
      sendInput({ type, ...point });
    }
  };

  const liveFailureMessage =
    live && closedReason
      ? closedReason === "handshake_timeout"
        ? t.browserStream.handshakeTimeout
        : t.browserStream.connectionFailed
      : null;
  const liveActive = live && status === "open";
  const liveConnecting = live && status === "connecting";
  const displayUrl = live
    ? (frameUrl ?? liveFallback?.frameUrl ?? imageUrl)
    : (liveFallback?.frameUrl ?? imageUrl);

  // React registers onWheel as a passive listener, so preventDefault() there is
  // ignored and the wheel scrolls the host chat page. Bind a native, non-passive
  // listener on the always-mounted stage (the <img> may not exist yet when live
  // first opens) so scrolling stays captured inside the remote page.
  useEffect(() => {
    const el = stageRef.current;
    if (!el || !liveActive) {
      return;
    }
    let wheelFrame: number | null = null;
    let pendingDx = 0;
    let pendingDy = 0;
    let pendingPoint: { nx: number; ny: number } | null = null;

    const browserWheelDelta = (pixels: number) => {
      return Math.abs(pixels) < 0.25 ? 0 : pixels * 2;
    };

    const flushWheel = () => {
      wheelFrame = null;
      const dx = browserWheelDelta(pendingDx);
      const dy = browserWheelDelta(pendingDy);
      const point = pendingPoint;
      pendingDx = 0;
      pendingDy = 0;
      pendingPoint = null;
      if (dx || dy) {
        sendInput({ type: "wheel", dx, dy, ...(point ?? {}) });
      }
    };

    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      event.stopPropagation();
      // Normalize deltaMode (line/page → pixels), then batch one animation
      // frame of deltas. A small 2x gain keeps touchpad gestures responsive
      // without returning to the jumpy large-step behavior.
      const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? 800 : 1;
      pendingDx += event.deltaX * unit;
      pendingDy += event.deltaY * unit;
      const point = normalizedPoint(event.clientX, event.clientY, {
        fallbackToCenter: true,
      });
      if (point) {
        pendingPoint = point;
      }
      wheelFrame ??= window.requestAnimationFrame(flushWheel);
    };
    el.addEventListener("wheel", onWheel, {
      capture: true,
      passive: false,
    });
    return () => {
      el.removeEventListener("wheel", onWheel, { capture: true });
      if (wheelFrame !== null) {
        window.cancelAnimationFrame(wheelFrame);
      }
    };
  }, [liveActive, normalizedPoint, sendInput]);

  return (
    <div
      ref={panelRef}
      className={cn(
        "bg-background relative flex flex-col",
        "size-full",
        className,
      )}
      tabIndex={live ? 0 : undefined}
      onKeyDown={(event) => {
        const target = event.target;
        const editableTarget =
          target instanceof HTMLInputElement ||
          target instanceof HTMLTextAreaElement ||
          (target instanceof HTMLElement && target.isContentEditable);
        const input = decideBrowserKeyInput({
          live,
          editableTarget,
          composing: isIMEComposing(event),
          key: event.key,
          metaKey: event.metaKey,
          ctrlKey: event.ctrlKey,
          shiftKey: event.shiftKey,
          altKey: event.altKey,
        });
        if (!input) {
          return;
        }
        sendInput(input);
        event.preventDefault();
        event.stopPropagation();
      }}
    >
      {/* Ordinateur nkyel - Unified Workspace Tabs */}
      <div className="flex shrink-0 items-center justify-between border-b bg-muted/40 px-2 py-1.5">
        <div className="flex items-center gap-1 overflow-x-auto">
          <Button
            size="sm"
            variant={activeTab === "desktop" ? "secondary" : "ghost"}
            className={cn(
              "h-7 gap-1.5 px-2.5 text-xs font-medium",
              activeTab === "desktop" &&
                "bg-background text-foreground shadow-xs font-semibold",
            )}
            onClick={() => setActiveTab("desktop")}
          >
            <MonitorIcon className="size-3.5 text-blue-500" />
            <span>Bureau distant</span>
          </Button>

          <Button
            size="sm"
            variant={activeTab === "tavily" ? "secondary" : "ghost"}
            className={cn(
              "h-7 gap-1.5 px-2.5 text-xs font-medium",
              activeTab === "tavily" &&
                "bg-background text-foreground shadow-xs font-semibold",
            )}
            onClick={() => setActiveTab("tavily")}
          >
            <CompassIcon className="size-3.5 text-emerald-500" />
            <span>Recherche Tavily</span>
          </Button>

          <Button
            size="sm"
            variant={activeTab === "terminal" ? "secondary" : "ghost"}
            className={cn(
              "h-7 gap-1.5 px-2.5 text-xs font-medium",
              activeTab === "terminal" &&
                "bg-background text-foreground shadow-xs font-semibold",
            )}
            onClick={() => setActiveTab("terminal")}
          >
            <TerminalIcon className="size-3.5 text-amber-500" />
            <span>Console</span>
          </Button>

          <Button
            size="sm"
            variant={activeTab === "files" ? "secondary" : "ghost"}
            className={cn(
              "h-7 gap-1.5 px-2.5 text-xs font-medium",
              activeTab === "files" &&
                "bg-background text-foreground shadow-xs font-semibold",
            )}
            onClick={() => setActiveTab("files")}
          >
            <FolderIcon className="size-3.5 text-indigo-500" />
            <span>Fichiers de mission</span>
          </Button>

          <Button
            size="sm"
            variant={activeTab === "sandbox" ? "secondary" : "ghost"}
            className={cn(
              "h-7 gap-1.5 px-2.5 text-xs font-medium",
              activeTab === "sandbox" &&
                "bg-background text-foreground shadow-xs font-semibold",
            )}
            onClick={() => setActiveTab("sandbox")}
          >
            <ServerIcon className="size-3.5 text-purple-500" />
            <span>Bac à sable E2B</span>
          </Button>
        </div>

        <Button
          size="icon-sm"
          variant="ghost"
          className="size-7 shrink-0"
          onClick={() => {
            setLive(false);
            browserView?.close();
          }}
          title="Fermer le panneau"
        >
          <XIcon className="size-3.5" />
        </Button>
      </div>

      {/* Desktop View Navigation Bar (Shown when desktop tab is active) */}
      {activeTab === "desktop" && (
        <header className="flex shrink-0 items-center gap-2 border-b px-3 py-1.5">
          <div className="flex shrink-0 items-center">
            <Button
              size="icon-sm"
              variant="ghost"
              className="size-7 shrink-0"
              disabled={!live}
              onClick={() => sendInput({ type: "back" })}
              title="Précédent"
            >
              <ArrowLeftIcon className="size-3.5" />
            </Button>
            <Button
              size="icon-sm"
              variant="ghost"
              className="size-7 shrink-0"
              disabled={!live}
              onClick={() => sendInput({ type: "forward" })}
              title="Suivant"
            >
              <ArrowRightIcon className="size-3.5" />
            </Button>
          </div>
          <form
            className="relative flex min-w-0 flex-1 items-center"
            onSubmit={(event) => {
              event.preventDefault();
              void handleNavigate();
            }}
          >
            <GlobeIcon className="text-muted-foreground pointer-events-none absolute left-2 size-3.5" />
            <Input
              value={urlInput}
              onChange={(event) => {
                urlEditingRef.current = true;
                setUrlInput(event.target.value);
              }}
              onFocus={(event) => {
                urlEditingRef.current = true;
                event.currentTarget.select();
              }}
              onBlur={() => {
                urlEditingRef.current = false;
              }}
              onKeyDown={(event) => {
                event.stopPropagation();
              }}
              placeholder="Saisissez une URL et appuyez sur Entrée"
              spellCheck={false}
              autoComplete="off"
              className="h-7 pl-7 text-xs"
            />
            {navigating && (
              <Loader2Icon className="text-muted-foreground absolute right-2 size-3.5 animate-spin" />
            )}
          </form>
          <Button
            size="sm"
            variant={live ? "default" : "ghost"}
            className="h-7 shrink-0 gap-1 px-2 text-xs"
            onClick={() => setLive((prev) => !prev)}
            title={live ? "Arrêter le direct" : "Prendre le contrôle en direct"}
          >
            <RadioIcon className="size-3" />
            {live && status !== "open"
              ? status === "closed"
                ? t.browserStream.disconnected
                : t.browserStream.connecting
              : "Direct"}
          </Button>
        </header>
      )}

      {/* Main Container */}
      <main className="relative flex min-h-0 grow flex-col overflow-hidden bg-neutral-950">
        {/* Desktop Browser Screencast (Always kept mounted to preserve stream connection) */}
        <div
          ref={stageRef}
          className={cn(
            "relative min-h-0 grow bg-neutral-900",
            activeTab !== "desktop" && "hidden",
          )}
          onMouseDown={() => {
            panelRef.current?.focus({ preventScroll: true });
          }}
        >
          {liveFailureMessage && (
            <p
              role="status"
              className="bg-background shrink-0 border-b px-3 py-2 text-xs"
            >
              {liveFailureMessage}
            </p>
          )}
          {displayUrl ? (
            <img
              ref={surfaceRef}
              className="absolute inset-0 h-full w-full cursor-default object-contain object-center"
              src={displayUrl}
              alt={frame?.title ?? "Browser view"}
              draggable={false}
              onClick={(event) => forwardMouse("click", event)}
            />
          ) : (
            <ConversationEmptyState
              className="absolute inset-0 m-auto h-fit"
              icon={<MonitorIcon />}
              title={
                liveFailureMessage
                  ? t.browserStream.disconnected
                  : live
                    ? "Connexion au navigateur en direct…"
                    : "Aucune activité de navigation pour l'instant"
              }
              description={
                liveFailureMessage
                  ? ""
                  : live
                    ? "En attente de la première image transmise par E2B."
                    : "Saisissez une URL ci-dessus ou lancez une mission : le flux en direct apparaîtra ici."
              }
            />
          )}
          {(navigating || liveConnecting) && displayUrl && (
            <div className="absolute inset-0 flex items-center justify-center bg-white/40 backdrop-blur-[1px]">
              <Loader2Icon className="text-muted-foreground size-8 animate-spin" />
            </div>
          )}
        </div>

        {/* Tab: Recherche Tavily */}
        {activeTab === "tavily" && (
          <div className="flex size-full flex-col overflow-hidden">
            <TavilyTab
              threadId={threadId}
              onNavigateToUrl={(url) => {
                setUrlInput(url);
                void handleNavigate(url);
                setActiveTab("desktop");
              }}
            />
          </div>
        )}

        {/* Tab: Console / Terminal */}
        {activeTab === "terminal" && (
          <div className="flex size-full flex-col overflow-hidden">
            <TerminalTab threadId={threadId} />
          </div>
        )}

        {/* Tab: Fichiers de mission */}
        {activeTab === "files" && (
          <div className="flex size-full flex-col overflow-hidden">
            <FilesTab threadId={threadId} />
          </div>
        )}

        {/* Tab: Bac à sable E2B Cloud */}
        {activeTab === "sandbox" && (
          <div className="flex size-full flex-col overflow-hidden">
            <SandboxTab threadId={threadId} />
          </div>
        )}
      </main>
    </div>
  );
}
