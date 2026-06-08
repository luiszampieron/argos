"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { member, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !member) {
      router.push("/login");
    }
  }, [loading, member, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-7 h-7 border-[3px] border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!member) return null;

  const initials = member.name
    .split(" ")
    .slice(0, 2)
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 h-14 flex items-center justify-between sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <span className="text-white text-xs font-bold">A</span>
          </div>
          <span className="font-bold text-slate-800 tracking-tight">Argos</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
              <span className="text-indigo-700 text-xs font-bold">
                {initials}
              </span>
            </div>
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-slate-800 leading-none">
                {member.name}
              </p>
              <p className="text-xs text-slate-400 mt-0.5">{member.cargo}</p>
            </div>
          </div>
          <div className="w-px h-5 bg-slate-200" />
          <LogoutButton />
        </div>
      </header>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}

function LogoutButton() {
  const { logout } = useAuth();
  const router = useRouter();

  return (
    <button
      onClick={() => {
        logout();
        router.push("/login");
      }}
      className="text-sm text-slate-500 hover:text-red-500 font-medium transition-colors px-2 py-1 rounded-lg hover:bg-red-50"
    >
      Sair
    </button>
  );
}
