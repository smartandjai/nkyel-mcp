"use client";

import { MessageSquarePlus } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { NkyelEmblem } from "@/components/ui/nkyel-logo";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { useI18n } from "@/core/i18n/hooks";
import { cn } from "@/lib/utils";

import { useWorkspaceSidebarExpanded } from "./workspace-sidebar-frame";
import { WorkspaceSidebarTrigger } from "./workspace-sidebar-trigger";

export function WorkspaceHeader({ className }: { className?: string }) {
  const { t } = useI18n();
  const { isMobile } = useSidebar();
  const isSidebarOpen = useWorkspaceSidebarExpanded();
  const pathname = usePathname();
  return (
    <>
      <div
        className={cn(
          "group/workspace-header flex h-12 flex-col justify-center",
          className,
        )}
      >
        {!isSidebarOpen ? (
          <div className="group-has-data-[collapsible=icon]/sidebar-wrapper:-translate-y flex w-full cursor-pointer items-center justify-center">
            <div
              className={cn(
                "block pt-1 group-hover/workspace-header:hidden transition-transform hover:scale-105",
                isMobile && "hidden",
              )}
            >
              <NkyelEmblem size={22} className="text-foreground" />
            </div>
            <WorkspaceSidebarTrigger
              className={cn(
                "pl-2",
                !isMobile && "hidden group-hover/workspace-header:block",
              )}
            />
          </div>
        ) : (
          <div className="flex items-center justify-between gap-2">
            <Link
              href="/workspace"
              className="flex items-center gap-2.5 ml-1.5 select-none rounded-lg p-1 transition-colors hover:bg-muted/40"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 p-1 ring-1 ring-border/50">
                <NkyelEmblem size={18} className="text-foreground" />
              </div>
              <div className="font-bold tracking-tight text-foreground text-sm">
                nkyel
              </div>
            </Link>
            <WorkspaceSidebarTrigger />
          </div>
        )}
      </div>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton
            isActive={pathname === "/workspace/chats/new"}
            asChild
          >
            <Link className="text-muted-foreground" href="/workspace/chats/new">
              <MessageSquarePlus size={16} />
              <span>{t.sidebar.newChat}</span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </>
  );
}
