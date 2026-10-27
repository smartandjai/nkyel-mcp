import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

import { getServerSideUser } from "@/core/auth/server";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const { userId } = await auth();
  if (userId) {
    redirect("/workspace");
  }
  const result = await getServerSideUser();
  if (result.tag === "authenticated") {
    redirect("/workspace");
  }
  redirect("/sign-in");
}
