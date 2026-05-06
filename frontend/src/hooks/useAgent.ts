import { useMutation, useQuery, useQueryClient, useSuspenseQuery } from "@tanstack/react-query";
import { useSetAtom } from "jotai";
import { useCallback } from "react";

import { currentRunIdAtom } from "../atoms/agentAtoms";
import { apiUrl } from "../lib/api";
import type { AgentStatus, SseEnvelope } from "../types";

export const agentStatusQueryKey = (runId: string) => ["agent", "status", runId] as const;

export async function fetchAgentStatus(runId: string): Promise<AgentStatus> {
  const res = await fetch(apiUrl(`/agent/status/${runId}`));
  if (!res.ok) {
    throw new Error(`status ${res.status}`);
  }
  return (await res.json()) as AgentStatus;
}

export function useAgentStatus(runId: string | null) {
  return useQuery({
    queryKey: runId ? agentStatusQueryKey(runId) : ["agent", "status", "none"],
    queryFn: () => fetchAgentStatus(runId!),
    enabled: Boolean(runId),
    refetchInterval: (q) => {
      const st = q.state.data?.status;
      if (st === "running" || st === "pending") {
        return 1_500;
      }
      return false;
    },
  });
}

export function useAgentStatusSuspense(runId: string) {
  return useSuspenseQuery({
    queryKey: agentStatusQueryKey(runId),
    queryFn: () => fetchAgentStatus(runId),
    refetchInterval: (q) => {
      const st = q.state.data?.status;
      if (st === "running" || st === "pending") {
        return 1_500;
      }
      return false;
    },
  });
}

export async function* parseSseJsonLines(
  body: ReadableStream<Uint8Array> | null,
): AsyncGenerator<SseEnvelope> {
  if (!body) {
    return;
  }
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      for (const line of chunk.split("\n")) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data:")) {
          continue;
        }
        const json = trimmed.slice("data:".length).trim();
        if (!json) {
          continue;
        }
        yield JSON.parse(json) as SseEnvelope;
      }
    }
  }
}

export function useAgentRunStream() {
  const qc = useQueryClient();
  const setRunId = useSetAtom(currentRunIdAtom);

  return useMutation({
    mutationFn: async (message: string) => {
      const res = await fetch(apiUrl("/agent/run"), {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok || !res.body) {
        throw new Error(`run failed: ${res.status}`);
      }

      let activeRunId: string | null = null;

      for await (const msg of parseSseJsonLines(res.body)) {
        if (msg.kind === "lifecycle" && msg.payload?.phase === "run_started" && msg.payload.run_id != null) {
          const rid = msg.payload.run_id;
          activeRunId = typeof rid === "string" ? rid : String(rid);
          setRunId(activeRunId);
        }
        if (activeRunId) {
          qc.setQueryData<AgentStatus>(agentStatusQueryKey(activeRunId), (prev) => {
            const base: AgentStatus =
              prev ??
              ({
                run_id: activeRunId!,
                status: "running",
                user_message: message,
                retry_count: 0,
                final_output: null,
                error_message: null,
                steps: [],
                events: [],
              } satisfies AgentStatus);

            const events = [...base.events];
            const last = events[events.length - 1];
            const seq = last ? last.seq + 1 : 1;
            events.push({ seq, kind: msg.kind, payload: (msg.payload ?? {}) as Record<string, unknown> });

            let steps = base.steps;
            if (msg.kind === "ui_step" && msg.payload && typeof msg.payload === "object") {
              const p = msg.payload as AgentStepPayload;
              if ("id" in p && "label" in p && "state" in p) {
                const others = steps.filter((s) => s.id !== p.id);
                steps = [...others, { id: p.id, label: p.label, state: p.state }];
              }
            }

            let status = base.status;
            let error_message = base.error_message;

            if (msg.kind === "lifecycle" && msg.payload?.phase === "run_completed") {
              const st = msg.payload.status;
              if (st === "completed" || st === "failed" || st === "running" || st === "pending") {
                status = st;
              }
            }
            if (msg.kind === "done" && msg.payload?.status) {
              const st = msg.payload.status;
              if (st === "completed" || st === "failed" || st === "running" || st === "pending") {
                status = st;
              }
            }
            if (msg.kind === "error" && msg.payload?.message != null) {
              const m = msg.payload.message;
              error_message = typeof m === "string" ? m : JSON.stringify(m);
              status = "failed";
            }

            return {
              ...base,
              status,
              steps,
              events,
              error_message,
            };
          });
        }
      }

      if (activeRunId) {
        await qc.invalidateQueries({ queryKey: agentStatusQueryKey(activeRunId) });
      }
      return activeRunId;
    },
  });
}

type AgentStepPayload = { id: string; label: string; state: AgentStatus["steps"][number]["state"] };

export function useAgentController() {
  const setRunId = useSetAtom(currentRunIdAtom);
  const clearRun = useCallback(() => setRunId(null), [setRunId]);
  return { setRunId, clearRun };
}
