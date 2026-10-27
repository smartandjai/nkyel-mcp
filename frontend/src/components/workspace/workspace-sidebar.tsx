"use client";

import { UserButton } from "@clerk/nextjs";

import {
  type Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import { useThreadActivity } from "@/core/threads/activity";

import { WorkspaceChannelsList } from "./channels/workspace-channels-list";
import { PluginNavigation } from "./plugin-navigation";
import { ProjectsSection } from "./projects-section";
import { RecentChatList } from "./recent-chat-list";
import { ThreadDeleteDialogProvider } from "./thread-delete-dialog";
import { WorkspaceHeader } from "./workspace-header";
import { WorkspaceNavChatList } from "./workspace-nav-chat-list";
import { WorkspaceNavMenu } from "./workspace-nav-menu";
import {
  WorkspaceSidebarFrame,
  useWorkspaceSidebarExpanded,
} from "./workspace-sidebar-frame";

export function WorkspaceSidebar({
  ...props
}: React.ComponentProps<typeof Sidebar>) {
  // One activity poll per workspace (off unless the Gateway offers it): new
  // and changed server-created threads reach the thread lists without a
  // reload, and a read on another device clears their dots here.
  useThreadActivity();
  return (
    <ThreadDeleteDialogProvider>
      <WorkspaceSidebarFrame variant="sidebar" collapsible="icon" {...props}>
        <WorkspaceSidebarContents />
      </WorkspaceSidebarFrame>
    </ThreadDeleteDialogProvider>
  );
}

function WorkspaceSidebarContents() {
  const isSidebarOpen = useWorkspaceSidebarExpanded();
  const { isMobile } = useSidebar();
  return (
    <>
      <SidebarHeader className="py-0">
        <WorkspaceHeader />
      </SidebarHeader>
      <SidebarContent>
        <WorkspaceNavChatList />
        <PluginNavigation />
        <WorkspaceChannelsList />
        {isSidebarOpen && (
          <>
            <ProjectsSection />
            <RecentChatList />
          </>
        )}
      </SidebarContent>
      <SidebarFooter className="gap-2">
        <div className="flex items-center gap-2 px-1 py-1">
          <UserButton
            showName={isSidebarOpen}
            appearance={{
              elements: {
                userButtonAvatarBox: "size-7",
                userButtonOuterIdentifier: "text-xs font-medium text-foreground truncate max-w-36",
                userButtonPopoverCard: "border border-border/60 bg-card/95 backdrop-blur-xl shadow-xl",
              },
            }}
          />
        </div>
        <WorkspaceNavMenu />
      </SidebarFooter>
      {!isMobile && <SidebarRail />}
    </>
  );
}
