"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createTeam, getTeams } from "@/lib/api";
import type { Team } from "@/types";

export default function DashboardPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTeamName, setNewTeamName] = useState("");
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    getTeams()
      .then(setTeams)
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newTeamName.trim()) return;
    setCreating(true);
    try {
      const team = await createTeam(newTeamName.trim());
      setTeams((prev) => [team, ...prev]);
      setNewTeamName("");
      setShowForm(false);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Meus Times</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Selecione um time para ver o board
          </p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-indigo-600 hover:bg-indigo-700 active:scale-[.98] text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all shadow-sm flex items-center gap-1.5"
        >
          <span className="text-base leading-none">+</span> Novo time
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 flex gap-3 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm"
        >
          <input
            autoFocus
            type="text"
            value={newTeamName}
            onChange={(e) => setNewTeamName(e.target.value)}
            placeholder="Ex: Squad Frontend"
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            minLength={2}
            maxLength={120}
            required
          />
          <button
            type="submit"
            disabled={creating}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all"
          >
            {creating ? "Criando..." : "Criar"}
          </button>
          <button
            type="button"
            onClick={() => setShowForm(false)}
            className="text-sm text-slate-500 hover:text-slate-700 px-3 rounded-xl hover:bg-slate-100 transition"
          >
            Cancelar
          </button>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-7 h-7 border-[3px] border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : teams.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-slate-200 border-dashed">
          <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">👥</span>
          </div>
          <p className="font-semibold text-slate-700">Nenhum time ainda</p>
          <p className="text-sm text-slate-400 mt-1">
            Clique em &quot;Novo time&quot; para começar.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {teams.map((team, i) => {
            const colors = [
              "from-violet-500 to-indigo-500",
              "from-blue-500 to-cyan-500",
              "from-emerald-500 to-teal-500",
              "from-orange-400 to-pink-500",
              "from-rose-500 to-pink-500",
              "from-amber-400 to-orange-500",
            ];
            const gradient = colors[i % colors.length];
            return (
              <Link
                key={team.id}
                href={`/dashboard/teams/${team.id}`}
                className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-lg hover:-translate-y-0.5 transition-all group overflow-hidden relative"
              >
                <div
                  className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${gradient}`}
                />
                <div className="flex items-start justify-between mt-1">
                  <div>
                    <h2 className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors text-base">
                      {team.name}
                    </h2>
                    <p className="text-xs text-slate-400 mt-1.5 flex items-center gap-1">
                      <span>📅</span>
                      {new Date(team.created_at).toLocaleDateString("pt-BR", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                      })}
                    </p>
                  </div>
                  <span className="w-8 h-8 bg-slate-100 group-hover:bg-indigo-100 rounded-lg flex items-center justify-center text-slate-400 group-hover:text-indigo-600 transition-all text-sm font-bold">
                    →
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
