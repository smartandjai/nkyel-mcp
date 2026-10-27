"use client";

import { useClerk, useUser } from "@clerk/nextjs";
import { useRouter, usePathname } from "next/navigation";
import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";

import { useArtifactDraftOwner } from "@/core/artifacts/draft-context";

import { isStaticWebsiteOnly } from "../static-mode";

import { AuthQueryScopeContext } from "./query-scope";
import {
  ACCOUNT_DISABLED_LOGIN_URL,
  type User,
  buildLoginUrl,
  currentReturnPath,
  parseAuthError,
} from "./types";

// Re-export for consumers
export type { User };

/**
 * Authentication context provided to consuming components
 */
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  applyUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * True when the SSR auth verdict for this auth-page render was
 * `account_disabled`: the visitor holds a live session cookie for a
 * suspended account, so /login states the known reason immediately instead
 * of waiting for a login attempt the backend deliberately answers with the
 * generic invalid-credentials message (#4063 gap 3).
 */
export const AuthDisabledContext = createContext(false);

interface AuthProviderProps {
  children: ReactNode;
  initialUser: User | null;
  /** The Gateway could not determine authentication; null is not a confirmed logout. */
  initialAuthUnknown?: boolean;
}

export function AuthProvider({
  children,
  initialUser,
  initialAuthUnknown = false,
}: AuthProviderProps) {
  const { user: clerkUser, isLoaded: clerkLoaded } = useUser();
  const { signOut } = useClerk();

  const [user, setUser] = useState<User | null>(initialUser);
  const [authKnown, setAuthKnown] = useState(!initialAuthUnknown);
  const authQueryScope = authKnown ? (user?.id ?? null) : undefined;
  useArtifactDraftOwner(authQueryScope);
  const [isLoading, setIsLoading] = useState(false);
  const authRequestRef = React.useRef(0);
  const router = useRouter();
  const pathname = usePathname();
  const staticMode = isStaticWebsiteOnly();

  const isAuthenticated = user !== null || !!clerkUser;

  /**
   * Apply a user value supplied by a caller (e.g. banner probe) that has
   * already fetched it. Equivalent to setUser, exposed with a stable name
   * so consumers don't reach into React internals.
   */
  const applyUser = useCallback((next: User | null) => {
    authRequestRef.current++;
    setUser(next);
    setAuthKnown(true);
    setIsLoading(false);
  }, []);

  /**
   * Fetch current user from FastAPI
   * Used when initialUser might be stale (e.g., after tab was inactive)
   */
  const refreshUser = useCallback(async () => {
    if (staticMode) return;
    const requestId = ++authRequestRef.current;

    try {
      setIsLoading(true);
      const res = await fetch("/api/v1/auth/me", {
        credentials: "include",
      });
      if (requestId !== authRequestRef.current) return;

      if (res.ok) {
        const data = await res.json();
        if (requestId !== authRequestRef.current) return;
        setUser(data);
        setAuthKnown(true);
      } else if (res.status === 401) {
        setUser(null);
        setAuthKnown(true);
        const code = await res
          .json()
          .then((data) => parseAuthError(data).code)
          .catch(() => null);
        if (requestId !== authRequestRef.current) return;
        if (code === "account_disabled") {
          // Operator-disabled account (#4063 gap 3): the login page states
          // the reason. Unlike an expired session there is nothing to come
          // back to, so no `next` is preserved and the path gate does not
          // apply — every authenticated page is equally unreachable.
          router.push(ACCOUNT_DISABLED_LOGIN_URL);
        } else if (pathname?.startsWith("/workspace")) {
          // Session expired or invalid — redirect on protected routes
          router.push(buildLoginUrl(currentReturnPath()));
        }
      }
    } catch (err) {
      if (requestId !== authRequestRef.current) return;
      console.error("Failed to refresh user:", err);
      setUser(null);
      setAuthKnown(false);
    } finally {
      if (requestId === authRequestRef.current) setIsLoading(false);
    }
  }, [staticMode, pathname, router]);

  useEffect(() => {
    if (clerkLoaded && clerkUser) {
      const email =
        clerkUser.primaryEmailAddress?.emailAddress ??
        `${clerkUser.id}@clerk.smartandjai.com`;
      const fallbackUser: User = {
        id: clerkUser.id,
        email,
        system_role: "user",
        needs_setup: false,
      };
      setUser((current) => current ?? fallbackUser);
      setAuthKnown(true);
      void refreshUser();
    }
  }, [clerkLoaded, clerkUser, refreshUser]);

  /**
   * Logout - call Clerk signOut and FastAPI logout endpoint
   */
  const logout = useCallback(async () => {
    authRequestRef.current++;
    setUser(null);
    setAuthKnown(true);
    setIsLoading(false);

    try {
      await signOut();
    } catch (err) {
      console.error("Clerk signOut error:", err);
    }

    try {
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // Ignore network errors on logout
    }

    if (typeof window !== "undefined") {
      window.location.href = "/sign-in";
    }
  }, [signOut]);

  /**
   * Handle visibility change - refresh user when tab becomes visible again.
   * Throttled to at most once per 60 s to avoid spamming the backend on rapid tab switches.
   */
  const lastCheckRef = React.useRef(0);

  useEffect(() => {
    if (staticMode) return;

    const handleVisibilityChange = () => {
      if (document.visibilityState !== "visible" || user === null) return;
      const now = Date.now();
      if (now - lastCheckRef.current < 60_000) return;
      lastCheckRef.current = now;
      void refreshUser();
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [staticMode, user, refreshUser]);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    logout,
    refreshUser,
    applyUser,
  };

  return (
    <AuthContext.Provider value={value}>
      <AuthQueryScopeContext.Provider value={authQueryScope}>
        {children}
      </AuthQueryScopeContext.Provider>
    </AuthContext.Provider>
  );
}

/**
 * Hook to access authentication context
 * Throws if used outside AuthProvider - this is intentional for proper usage
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

/**
 * Hook to require authentication - redirects to login if not authenticated
 * Useful for client-side checks in addition to server-side guards
 */
export function useRequireAuth(): AuthContextType {
  const auth = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (isStaticWebsiteOnly()) return;

    // Only redirect if we're sure user is not authenticated (not just loading)
    if (!auth.isLoading && !auth.isAuthenticated) {
      router.push(buildLoginUrl(currentReturnPath()));
    }
  }, [auth.isAuthenticated, auth.isLoading, router, pathname]);

  return auth;
}
