"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  createTask,
  getMembers,
  getTask,
  getTasksByTeam,
  getTeams,
  updateTaskAssignee,
  updateTaskStatus,
} from "@/lib/api";
import type { Member, Task, TaskPriority, TaskStatus, Team } from "@/types";

const COLUMNS: {
  key: TaskStatus;
  label: string;
  accent: string;
  bg: string;
  badge: string;
  dot: string;
}[] = [
  {
    key: "todo",
    label: "A fazer",
    accent: "border-t-slate-400",
    bg: "bg-slate-50",
    badge: "bg-slate-200 text-slate-600",
    dot: "bg-slate-400",
  },
  {
    key: "in_progress",
    label: "Em progresso",
    accent: "border-t-blue-500",
    bg: "bg-blue-50/60",
    badge: "bg-blue-100 text-blue-700",
    dot: "bg-blue-500",
  },
  {
    key: "blocked",
    label: "Bloqueado",
    accent: "border-t-rose-500",
    bg: "bg-rose-50/60",
    badge: "bg-rose-100 text-rose-700",
    dot: "bg-rose-500",
  },
  {
    key: "done",
    label: "Concluído",
    accent: "border-t-emerald-500",
    bg: "bg-emerald-50/60",
    badge: "bg-emerald-100 text-emerald-700",
    dot: "bg-emerald-500",
  },
];

const STATUS_BADGE: Record<TaskStatus, string> = {
  todo: "bg-slate-100 text-slate-600",
  in_progress: "bg-blue-100 text-blue-700",
  blocked: "bg-rose-100 text-rose-700",
  done: "bg-emerald-100 text-emerald-700",
};

const PRIORITY_CONFIG: Record<
  TaskPriority,
  { label: string; badge: string; dot: string }
> = {
  low: {
    label: "Baixa",
    badge: "bg-slate-100 text-slate-500",
    dot: "bg-slate-400",
  },
  medium: {
    label: "Média",
    badge: "bg-amber-100 text-amber-700",
    dot: "bg-amber-400",
  },
  high: {
    label: "Alta",
    badge: "bg-rose-100 text-rose-700",
    dot: "bg-rose-500",
  },
};

interface CreateTaskForm {
  title: string;
  description: string;
  priority: TaskPriority;
  assignee_id: number | null;
  due_date: string;
}

const EMPTY_FORM: CreateTaskForm = {
  title: "",
  description: "",
  priority: "medium",
  assignee_id: null,
  due_date: "",
};

export default function TeamBoardPage() {
  const { id } = useParams<{ id: string }>();
  const teamId = Number(id);
  const router = useRouter();

  const [team, setTeam] = useState<Team | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterStatus, setFilterStatus] = useState<TaskStatus | "all">("all");
  const [filterPriority, setFilterPriority] = useState<TaskPriority | "all">(
    "all",
  );
  const [filterAssigneeId, setFilterAssigneeId] = useState<
    number | "all" | "none"
  >("all");

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [form, setForm] = useState<CreateTaskForm>(EMPTY_FORM);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const [detailTask, setDetailTask] = useState<Task | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [editingAssignee, setEditingAssignee] = useState(false);
  const [assigneeValue, setAssigneeValue] = useState<number | null>(null);
  const [savingAssignee, setSavingAssignee] = useState(false);

  async function handleSaveAssignee(e: React.FormEvent) {
    e.preventDefault();
    if (!detailTask || assigneeValue === null) return;
    setSavingAssignee(true);
    try {
      const updated = await updateTaskAssignee(detailTask.id, assigneeValue);
      setDetailTask(updated);
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
      setEditingAssignee(false);
    } finally {
      setSavingAssignee(false);
    }
  }

  const [searchId, setSearchId] = useState("");
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const id = Number(searchId.trim());
    if (!id || id <= 0) {
      setSearchError("Digite um ID válido.");
      return;
    }
    setSearchError(null);
    setSearching(true);
    try {
      const task = await getTask(id);
      setDetailTask(task);
      setSearchId("");
    } catch {
      setSearchError(`Nenhuma tarefa encontrada com ID #${id}.`);
    } finally {
      setSearching(false);
    }
  }

  async function openDetail(taskId: number) {
    setDetailLoading(true);
    setDetailTask(null);
    try {
      const task = await getTask(taskId);
      setDetailTask(task);
    } finally {
      setDetailLoading(false);
    }
  }

  useEffect(() => {
    async function load() {
      const [allTeams, teamTasks, allMembers] = await Promise.all([
        getTeams(),
        getTasksByTeam(teamId),
        getMembers(),
      ]);
      const found = allTeams.find((t) => t.id === teamId) ?? null;
      if (!found) {
        router.push("/dashboard");
        return;
      }
      setTeam(found);
      setTasks(teamTasks);
      setMembers(allMembers);
      setLoading(false);
    }
    load().catch(() => setLoading(false));
  }, [teamId, router]);

  async function handleStatusChange(task: Task, newStatus: TaskStatus) {
    try {
      const updated = await updateTaskStatus(task.id, newStatus);
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch {
      // silently ignore, UI reverts
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreateError(null);
    setCreating(true);
    try {
      const task = await createTask({
        team_id: teamId,
        title: form.title,
        description: form.description || undefined,
        priority: form.priority,
        assignee_id: form.assignee_id!,
        due_date: new Date(form.due_date).toISOString(),
      });
      setTasks((prev) => [task, ...prev]);
      setForm(EMPTY_FORM);
      setShowCreateModal(false);
    } catch (err: unknown) {
      setCreateError(
        err instanceof Error ? err.message : "Erro ao criar tarefa.",
      );
    } finally {
      setCreating(false);
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="w-7 h-7 border-[3px] border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const filteredTasks = tasks.filter((t) => {
    if (filterPriority !== "all" && t.priority !== filterPriority) return false;
    if (filterAssigneeId === "none" && t.assignee_id !== null) return false;
    if (
      filterAssigneeId !== "all" &&
      filterAssigneeId !== "none" &&
      t.assignee_id !== filterAssigneeId
    )
      return false;
    return true;
  });

  const tasksByStatus = (s: TaskStatus) =>
    filteredTasks.filter(
      (t) =>
        (filterStatus === "all" || t.status === filterStatus) && t.status === s,
    );

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2 text-sm">
          <Link
            href="/dashboard"
            className="text-slate-400 hover:text-indigo-600 transition-colors font-medium"
          >
            Times
          </Link>
          <span className="text-slate-300">/</span>
          <span className="font-semibold text-slate-800">{team?.name}</span>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-indigo-600 hover:bg-indigo-700 active:scale-[.98] text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all shadow-sm flex items-center gap-1.5"
        >
          <span className="text-base leading-none">+</span> Nova tarefa
        </button>
      </div>

      {/* Search by ID */}
      <form onSubmit={handleSearch} className="flex items-center gap-2 mb-2">
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-mono">
            #
          </span>
          <input
            type="number"
            min="1"
            value={searchId}
            onChange={(e) => {
              setSearchId(e.target.value);
              setSearchError(null);
            }}
            placeholder="Buscar por ID"
            className="pl-7 pr-3 py-2 text-sm bg-white border border-slate-200 rounded-xl w-44 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm placeholder:text-slate-400 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>
        <button
          type="submit"
          disabled={searching || !searchId.trim()}
          className="bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-40 text-slate-700 text-sm font-medium px-3 py-2 rounded-xl shadow-sm transition"
        >
          {searching ? "..." : "Buscar"}
        </button>
        {searchError && (
          <span className="text-xs text-rose-600 font-medium">
            {searchError}
          </span>
        )}
      </form>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-2 p-3 bg-white border border-slate-200 rounded-2xl shadow-sm">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          Filtros
        </span>

        {/* Status filter */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {(["all", ...COLUMNS.map((c) => c.key)] as const).map((s) => {
            const label =
              s === "all"
                ? "Todos"
                : (COLUMNS.find((c) => c.key === s)?.label ?? s);
            const active = filterStatus === s;
            return (
              <button
                key={s}
                onClick={() => setFilterStatus(s)}
                className={`text-xs font-semibold px-2.5 py-1 rounded-lg transition ${
                  active
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        <div className="h-4 w-px bg-slate-200 hidden sm:block" />

        {/* Priority filter */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-slate-500">Prioridade:</span>
          {(["all", "low", "medium", "high"] as const).map((p) => {
            const label = p === "all" ? "Todas" : PRIORITY_CONFIG[p].label;
            const active = filterPriority === p;
            const cfg = p !== "all" ? PRIORITY_CONFIG[p] : null;
            return (
              <button
                key={p}
                onClick={() => setFilterPriority(p)}
                className={`text-xs font-semibold px-2.5 py-1 rounded-lg transition flex items-center gap-1 ${
                  active && cfg
                    ? `${cfg.badge} shadow-sm`
                    : active
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {cfg && <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />}
                {label}
              </button>
            );
          })}
        </div>

        <div className="h-4 w-px bg-slate-200 hidden sm:block" />

        {/* Assignee filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Responsável:</span>
          <select
            value={filterAssigneeId === "all" ? "all" : String(filterAssigneeId)}
            onChange={(e) => {
              const v = e.target.value;
              if (v === "all") setFilterAssigneeId("all");
              else setFilterAssigneeId(Number(v));
            }}
            className="text-xs bg-slate-100 border-0 rounded-lg px-2.5 py-1 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="all">Todos</option>
            {members.map((m) => (
              <option key={m.id} value={String(m.id)}>
                {m.name}
              </option>
            ))}
          </select>
        </div>

        {(filterStatus !== "all" || filterPriority !== "all" || filterAssigneeId !== "all") && (
          <button
            onClick={() => {
              setFilterStatus("all");
              setFilterPriority("all");
              setFilterAssigneeId("all");
            }}
            className="ml-auto text-xs text-rose-600 hover:text-rose-700 font-medium"
          >
            Limpar filtros
          </button>
        )}
      </div>

      {/* Kanban board */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 flex-1 items-start">
        {COLUMNS.map((col) => (
          <div
            key={col.key}
            className={`rounded-2xl border border-slate-200 border-t-[3px] ${col.accent} ${col.bg} p-4 flex flex-col gap-3`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${col.dot}`} />
                <h2 className="text-sm font-semibold text-slate-700">
                  {col.label}
                </h2>
              </div>
              <span
                className={`text-xs font-semibold rounded-full px-2 py-0.5 ${col.badge}`}
              >
                {tasksByStatus(col.key).length}
              </span>
            </div>

            {tasksByStatus(col.key).length === 0 && (
              <div className="border-2 border-dashed border-slate-200 rounded-xl py-6 text-center">
                <p className="text-xs text-slate-400">Vazio</p>
              </div>
            )}

            {tasksByStatus(col.key).map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onStatusChange={handleStatusChange}
                onDetail={openDetail}
              />
            ))}
          </div>
        ))}
      </div>

      {/* Create task modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 border border-slate-100">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-slate-900">Nova tarefa</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setForm(EMPTY_FORM);
                  setCreateError(null);
                }}
                className="w-8 h-8 rounded-lg hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              {createError && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3 flex items-start gap-2">
                  <span>⚠</span>
                  <span>{createError}</span>
                </div>
              )}

              <FormField
                label="Título *"
                id="title"
                value={form.title}
                onChange={(v) => setForm((p) => ({ ...p, title: v }))}
                required
                maxLength={200}
                placeholder="Ex: Implementar autenticação"
              />
              <FormField
                label="Descrição"
                id="description"
                value={form.description}
                onChange={(v) => setForm((p) => ({ ...p, description: v }))}
                textarea
                placeholder="Detalhes opcionais..."
              />
              <MemberPicker
                label="Responsável *"
                members={members}
                value={form.assignee_id}
                onChange={(id) => setForm((p) => ({ ...p, assignee_id: id }))}
              />

              {/* Priority selector */}
              <div className="space-y-1.5">
                <p className="text-sm font-medium text-slate-700">
                  Prioridade *
                </p>
                <div className="flex gap-2">
                  {(["low", "medium", "high"] as TaskPriority[]).map((p) => {
                    const cfg = PRIORITY_CONFIG[p];
                    const active = form.priority === p;
                    return (
                      <button
                        key={p}
                        type="button"
                        onClick={() => setForm((f) => ({ ...f, priority: p }))}
                        className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold border transition ${
                          active
                            ? `${cfg.badge} border-current shadow-sm`
                            : "bg-slate-50 text-slate-400 border-slate-200 hover:border-slate-300"
                        }`}
                      >
                        <span
                          className={`w-2 h-2 rounded-full ${active ? cfg.dot : "bg-slate-300"}`}
                        />
                        {cfg.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              <FormField
                label="Prazo *"
                id="due_date"
                type="date"
                value={form.due_date}
                onChange={(v) => setForm((p) => ({ ...p, due_date: v }))}
                required
              />

              <div className="flex gap-3 pt-1">
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-xl text-sm transition-all"
                >
                  {creating ? "Criando..." : "Criar tarefa"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setForm(EMPTY_FORM);
                    setCreateError(null);
                  }}
                  className="flex-1 border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium py-2.5 rounded-xl text-sm transition"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Task detail modal */}
      {(detailLoading || detailTask) && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 border border-slate-100">
            {detailLoading ? (
              <div className="flex justify-center py-8">
                <div className="w-7 h-7 border-[3px] border-indigo-600 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : detailTask ? (
              <>
                <div className="flex items-start justify-between mb-4">
                  <h2 className="text-lg font-bold text-slate-900 pr-4 leading-snug">
                    {detailTask.title}
                  </h2>
                  <button
                    onClick={() => {
                      setDetailTask(null);
                      setEditingAssignee(false);
                    }}
                    className="w-8 h-8 rounded-lg hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition flex-shrink-0"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-3 text-sm">
                  {detailTask.description && (
                    <div className="bg-slate-50 rounded-xl p-3 text-slate-600 leading-relaxed">
                      {detailTask.description}
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-0.5">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                        Status
                      </p>
                      <span
                        className={`inline-block text-xs font-semibold rounded-lg px-2.5 py-1 ${STATUS_BADGE[detailTask.status]}`}
                      >
                        {
                          COLUMNS.find((c) => c.key === detailTask.status)
                            ?.label
                        }
                      </span>
                    </div>
                    <div className="space-y-0.5">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                        Prioridade
                      </p>
                      {(() => {
                        const cfg = PRIORITY_CONFIG[detailTask.priority];
                        return (
                          <span
                            className={`inline-flex items-center gap-1 text-xs font-semibold rounded-lg px-2.5 py-1 ${cfg.badge}`}
                          >
                            <span
                              className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`}
                            />
                            {cfg.label}
                          </span>
                        );
                      })()}
                    </div>
                    <div className="space-y-0.5">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                        ID
                      </p>
                      <p className="text-slate-700 font-mono">
                        #{detailTask.id}
                      </p>
                    </div>
                    {/* Assignee — editable */}
                    <div className="space-y-1 col-span-2">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                          Responsável
                        </p>
                        {!editingAssignee && (
                          <button
                            onClick={() => {
                              setAssigneeValue(detailTask.assignee_id);
                              setEditingAssignee(true);
                            }}
                            className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                          >
                            Editar
                          </button>
                        )}
                      </div>
                      {editingAssignee ? (
                        <form
                          onSubmit={handleSaveAssignee}
                          className="space-y-2"
                        >
                          <MemberPicker
                            members={members}
                            value={assigneeValue}
                            onChange={setAssigneeValue}
                          />
                          <div className="flex gap-2">
                            <button
                              type="submit"
                              disabled={savingAssignee}
                              className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold py-2 rounded-lg transition"
                            >
                              {savingAssignee ? "Salvando..." : "Salvar"}
                            </button>
                            <button
                              type="button"
                              onClick={() => setEditingAssignee(false)}
                              className="flex-1 border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-medium py-2 rounded-lg transition"
                            >
                              Cancelar
                            </button>
                          </div>
                        </form>
                      ) : (
                        <p className="text-slate-700">
                          {detailTask.assignee_name ?? (
                            <span className="text-slate-400 italic">
                              Ninguém atribuído
                            </span>
                          )}
                        </p>
                      )}
                    </div>
                    {detailTask.due_date && (
                      <div className="space-y-0.5">
                        <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                          Prazo
                        </p>
                        <p className="text-slate-700">
                          {new Date(detailTask.due_date).toLocaleDateString(
                            "pt-BR",
                            { day: "2-digit", month: "long", year: "numeric" },
                          )}
                        </p>
                      </div>
                    )}
                    <div className="space-y-0.5">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                        Criado em
                      </p>
                      <p className="text-slate-700">
                        {new Date(detailTask.created_at).toLocaleDateString(
                          "pt-BR",
                          { day: "2-digit", month: "short", year: "numeric" },
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

function TaskCard({
  task,
  onStatusChange,
  onDetail,
}: {
  task: Task;
  onStatusChange: (task: Task, status: TaskStatus) => void;
  onDetail: (taskId: number) => void;
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-3.5 shadow-sm hover:shadow-md transition-all space-y-2.5 group">
      <button
        onClick={() => onDetail(task.id)}
        className="text-sm font-semibold text-slate-800 leading-snug text-left hover:text-indigo-600 transition-colors w-full"
      >
        {task.title}
      </button>

      {task.description && (
        <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
          {task.description}
        </p>
      )}

      <div className="flex flex-wrap gap-1.5 text-xs">
        {/* Priority badge */}
        {(() => {
          const cfg = PRIORITY_CONFIG[task.priority];
          return (
            <span
              className={`${cfg.badge} rounded-full px-2.5 py-0.5 font-semibold flex items-center gap-1`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
              {cfg.label}
            </span>
          );
        })()}
        {task.assignee_name && (
          <span className="bg-violet-50 text-violet-700 border border-violet-100 rounded-full px-2.5 py-0.5 font-medium flex items-center gap-1">
            <span>👤</span>
            {task.assignee_name}
          </span>
        )}
        {task.due_date && (
          <span className="bg-amber-50 text-amber-700 border border-amber-100 rounded-full px-2.5 py-0.5 font-medium flex items-center gap-1">
            <span>📅</span>
            {new Date(task.due_date).toLocaleDateString("pt-BR")}
          </span>
        )}
      </div>

      {/* Status changer */}
      <div className="pt-0.5">
        <select
          value={task.status}
          onChange={(e) => onStatusChange(task, e.target.value as TaskStatus)}
          className={`text-xs font-semibold rounded-lg px-2.5 py-1 border-0 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-400 ${STATUS_BADGE[task.status]}`}
        >
          {COLUMNS.map((col) => (
            <option key={col.key} value={col.key}>
              {col.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

function initials(name: string) {
  return name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

function MemberPicker({
  members,
  value,
  onChange,
  label,
}: {
  members: Member[];
  value: number | null;
  onChange: (id: number | null) => void;
  label?: string;
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const selected = members.find((m) => m.id === value) ?? null;
  const filtered = query.trim()
    ? members.filter(
        (m) =>
          m.name.toLowerCase().includes(query.toLowerCase()) ||
          m.cargo.toLowerCase().includes(query.toLowerCase()),
      )
    : members;

  useEffect(() => {
    function onDown(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, []);

  function select(m: Member | null) {
    onChange(m?.id ?? null);
    setOpen(false);
    setQuery("");
  }

  return (
    <div className="space-y-1.5" ref={ref}>
      {label && <p className="text-sm font-medium text-slate-700">{label}</p>}
      <div className="relative">
        {/* Trigger button */}
        <button
          type="button"
          onClick={() => {
            setOpen((o) => !o);
            setQuery("");
          }}
          className="w-full flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-left hover:border-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
        >
          {selected ? (
            <>
              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">
                {initials(selected.name)}
              </span>
              <span className="flex-1 text-slate-900 font-medium">
                {selected.name}
              </span>
              <span className="text-xs text-slate-400">{selected.cargo}</span>
              <span
                role="button"
                tabIndex={0}
                onClick={(e) => {
                  e.stopPropagation();
                  select(null);
                }}
                onKeyDown={(e) =>
                  e.key === "Enter" && (e.stopPropagation(), select(null))
                }
                className="ml-1 text-slate-300 hover:text-rose-400 transition text-lg leading-none"
                aria-label="Remover responsável"
              >
                ×
              </span>
            </>
          ) : (
            <>
              <span className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0 text-slate-400 text-xs">
                ?
              </span>
              <span className="flex-1 text-slate-400">
                Selecionar responsável...
              </span>
              <svg
                className="w-4 h-4 text-slate-300 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </>
          )}
        </button>

        {/* Dropdown */}
        {open && (
          <div className="absolute z-50 top-full mt-1 w-full bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden">
            {/* Search input */}
            <div className="p-2 border-b border-slate-100">
              <div className="relative">
                <svg
                  className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-4.35-4.35m0 0A7 7 0 1116.65 16.65z"
                  />
                </svg>
                <input
                  autoFocus
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Buscar por nome ou cargo..."
                  className="w-full bg-slate-50 rounded-lg pl-8 pr-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <ul className="max-h-52 overflow-y-auto py-1">
              {/* None option */}
              <li>
                <button
                  type="button"
                  onClick={() => select(null)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-slate-50 transition ${
                    !value ? "bg-indigo-50" : ""
                  }`}
                >
                  <span className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 flex-shrink-0 text-base">
                    —
                  </span>
                  <span
                    className={`italic ${!value ? "text-indigo-700 font-medium" : "text-slate-400"}`}
                  >
                    Ninguém
                  </span>
                  {!value && (
                    <span className="ml-auto text-indigo-600 text-sm">✓</span>
                  )}
                </button>
              </li>

              {filtered.length === 0 ? (
                <li className="px-3 py-4 text-center text-xs text-slate-400">
                  Nenhum membro encontrado
                </li>
              ) : (
                filtered.map((m) => (
                  <li key={m.id}>
                    <button
                      type="button"
                      onClick={() => select(m)}
                      className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-slate-50 transition ${
                        value === m.id ? "bg-indigo-50" : ""
                      }`}
                    >
                      <span
                        className={`w-7 h-7 rounded-full text-xs font-bold flex items-center justify-center flex-shrink-0 ${
                          value === m.id
                            ? "bg-indigo-600 text-white"
                            : "bg-indigo-100 text-indigo-700"
                        }`}
                      >
                        {initials(m.name)}
                      </span>
                      <span className="flex-1 text-left">
                        <span
                          className={`block font-medium ${
                            value === m.id
                              ? "text-indigo-700"
                              : "text-slate-800"
                          }`}
                        >
                          {m.name}
                        </span>
                        <span className="block text-xs text-slate-400">
                          {m.cargo}
                        </span>
                      </span>
                      {value === m.id && (
                        <span className="text-indigo-600 text-sm">✓</span>
                      )}
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function FormField({
  label,
  id,
  value,
  onChange,
  required,
  textarea,
  type = "text",
  maxLength,
  placeholder,
}: {
  label: string;
  id: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  textarea?: boolean;
  type?: string;
  maxLength?: number;
  placeholder?: string;
}) {
  const cls =
    "w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition";
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="text-sm font-medium text-slate-700">
        {label}
      </label>
      {textarea ? (
        <textarea
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          placeholder={placeholder}
          className={cls}
        />
      ) : (
        <input
          id={id}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          maxLength={maxLength}
          placeholder={placeholder}
          className={cls}
        />
      )}
    </div>
  );
}
