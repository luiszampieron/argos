export type TaskStatus = "todo" | "in_progress" | "done" | "blocked";
export type TaskPriority = "low" | "medium" | "high";

export interface Team {
  id: number;
  name: string;
  created_at: string;
}

export interface Task {
  id: number;
  team_id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id: number | null;
  assignee_name: string | null;
  created_at: string;
  due_date: string | null;
}

export interface Member {
  id: number;
  name: string;
  email: string;
  cargo: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
