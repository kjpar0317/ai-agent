export type RunStatus = "pending" | "running" | "completed" | "failed";

export type AgentStepState = "pending" | "active" | "done" | "error";

export type AgentStep = {
  id: string;
  label: string;
  state: AgentStepState;
};

export type AgentEvent = {
  seq: number;
  kind: string;
  payload: Record<string, unknown>;
};

export type AgentStatus = {
  run_id: string;
  status: RunStatus;
  user_message: string;
  retry_count: number;
  final_output: string | null;
  error_message: string | null;
  steps: AgentStep[];
  events: AgentEvent[];
};

export type SseEnvelope = {
  kind: string;
  payload?: Record<string, unknown>;
};
