import { redirect } from "next/navigation";

import { getServerSideUser } from "@/core/auth/server";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const result = await getServerSideUser();
  if (result.tag === "authenticated") {
    redirect("/workspace");
  }
  redirect("/login");
}
