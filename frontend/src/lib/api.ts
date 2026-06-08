import type {
  Member,
  Task,
  TaskPriority,
  TaskStatus,
  Team,
  TokenResponse,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001/api";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((e: { msg?: string }) => e.msg ?? String(e)).join("; ")
      : typeof detail === "string"
        ? detail
        : "Erro na requisição.";
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// Auth
export async function register(data: {
  name: string;
  email: string;
  cargo: string;
  password: string;
}): Promise<Member> {
  return request<Member>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function login(data: {
  email: string;
  password: string;
}): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getMe(): Promise<Member> {
  return request<Member>("/auth/me");
}

// Teams
export async function getTeams(): Promise<Team[]> {
  return request<Team[]>("/teams");
}

export async function createTeam(name: string): Promise<Team> {
  return request<Team>("/teams", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

// Tasks
export async function getTask(taskId: number): Promise<Task> {
  return request<Task>(`/tasks/${taskId}`);
}

export async function getTasksByTeam(teamId: number): Promise<Task[]> {
  return request<Task[]>(`/teams/${teamId}/tasks`);
}

export async function createTask(data: {
  team_id: number;
  title: string;
  description?: string;
  priority: TaskPriority;
  assignee_id: number;
  due_date: string; // ISO string, must be in the future
}): Promise<Task> {
  return request<Task>("/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTaskStatus(
  taskId: number,
  status: TaskStatus,
): Promise<Task> {
  return request<Task>(`/tasks/${taskId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function updateTaskAssignee(
  taskId: number,
  assigneeId: number,
): Promise<Task> {
  return request<Task>(`/tasks/${taskId}/assignee`, {
    method: "PATCH",
    body: JSON.stringify({ assignee_id: assigneeId }),
  });
}

// Members
export async function getMembers(): Promise<Member[]> {
  return request<Member[]>("/members");
}
