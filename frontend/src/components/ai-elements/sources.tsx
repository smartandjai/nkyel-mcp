"use client";

import React, { type ComponentProps, useState } from "react";
import { BookOpenIcon, ChevronDownIcon, ExternalLinkIcon, GlobeIcon } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type SourcesProps = ComponentProps<typeof Collapsible> & {
  count?: number;
};

export const Sources = ({ className, children, count, defaultOpen = false, ...props }: SourcesProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <Collapsible
      open={isOpen}
      onOpenChange={setIsOpen}
      className={cn("my-2.5 w-full", className)}
      {...props}
    >
      {children}
    </Collapsible>
  );
};

export type SourcesTriggerProps = ComponentProps<typeof Button> & {
  count?: number;
  label?: string;
};

export const SourcesTrigger = ({
  className,
  count,
  label,
  children,
  ...props
}: SourcesTriggerProps) => {
  return (
    <CollapsibleTrigger asChild>
      <Button
        variant="ghost"
        size="sm"
        className={cn(
          "h-7 gap-1.5 px-2.5 text-xs font-medium text-muted-foreground hover:text-foreground border border-border/60 bg-muted/30 hover:bg-muted/70 rounded-lg transition-colors group",
          className
        )}
        {...props}
      >
        <BookOpenIcon className="size-3.5 text-primary/80" />
        <span>{children ?? (label || `${count ?? 0} sources`)}</span>
        <ChevronDownIcon className="size-3 opacity-60 transition-transform duration-200 group-data-[state=open]:rotate-180" />
      </Button>
    </CollapsibleTrigger>
  );
};

export type SourcesContentProps = ComponentProps<typeof CollapsibleContent>;

export const SourcesContent = ({
  className,
  children,
  ...props
}: SourcesContentProps) => {
  return (
    <CollapsibleContent
      className={cn(
        "mt-2.5 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3 transition-all",
        className
      )}
      {...props}
    >
      {children}
    </CollapsibleContent>
  );
};

export type SourceItemProps = ComponentProps<"a"> & {
  title: string;
  url: string;
  domain?: string;
  snippet?: string;
  index?: number;
};

export const SourceItem = ({
  title,
  url,
  domain,
  snippet,
  index,
  className,
  ...props
}: SourceItemProps) => {
  const [imgError, setImgError] = useState(false);
  const resolvedDomain = domain || (() => {
    try {
      return new URL(url).hostname.replace(/^www\./, "");
    } catch {
      return "";
    }
  })();
  const faviconUrl = `https://www.google.com/s2/favicons?domain=${resolvedDomain}&sz=64`;

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "group relative flex flex-col justify-between overflow-hidden rounded-xl border border-border/70 bg-card/60 p-3 shadow-2xs backdrop-blur-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/50 hover:bg-card hover:shadow-xs",
        className
      )}
      {...props}
    >
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-1.5">
          <div className="flex items-center gap-1.5 min-w-0">
            <div className="flex size-4 shrink-0 items-center justify-center rounded-xs bg-muted overflow-hidden">
              {!imgError && resolvedDomain ? (
                <img
                  src={faviconUrl}
                  alt={resolvedDomain}
                  className="size-3.5 object-contain"
                  onError={() => setImgError(true)}
                  loading="lazy"
                />
              ) : (
                <GlobeIcon className="size-3 text-muted-foreground" />
              )}
            </div>
            <span className="truncate text-[11px] font-medium text-muted-foreground group-hover:text-foreground transition-colors">
              {resolvedDomain}
            </span>
          </div>

          <div className="flex items-center gap-1">
            {index !== undefined && (
              <span className="flex size-3.5 items-center justify-center rounded-full bg-primary/10 text-[9px] font-semibold text-primary">
                {index + 1}
              </span>
            )}
            <ExternalLinkIcon className="size-3 text-muted-foreground/60 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        <h4 className="line-clamp-2 text-xs font-medium text-foreground group-hover:text-primary transition-colors leading-snug">
          {title}
        </h4>

        {snippet && (
          <p className="line-clamp-2 text-[11px] text-muted-foreground/80 leading-relaxed">
            {snippet}
          </p>
        )}
      </div>
    </a>
  );
};
