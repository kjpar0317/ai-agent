import { Suspense } from "react";

import { useAgentStatusSuspense } from "../hooks/useAgent";
import type { AgentStatus } from "../types";

import { AgentSteppers } from "./AgentSteppers";

function orderSteps(steps: AgentStatus["steps"]): AgentStatus["steps"] {
  const order = ["analyze", "execute", "validate"];
  const map = new Map(steps.map((s) => [s.id, s]));
  return order.flatMap((id) => (map.has(id) ? [map.get(id)!] : []));
}

function StatusInner({ runId }: { runId: string }) {
  const { data } = useAgentStatusSuspense(runId);
  return (
    <>
      <p className="meta">
        run_id: <code>{runId}</code> · 상태: {data.status} · 재시도: {data.retry_count}
      </p>
      <AgentSteppers steps={orderSteps(data.steps)} />
      {data.final_output ? (
        <article className="final-output">
          <h3>최종 출력</h3>
          <pre>{data.final_output}</pre>
        </article>
      ) : null}
      {data.error_message ? (
        <p className="error" role="alert">
          {data.error_message}
        </p>
      ) : null}
    </>
  );
}

export type AgentStatusUsePanelProps = {
  runId: string;
};

/** TanStack Query `useSuspenseQuery` + React `<Suspense>` (폴링은 쿼리 옵션). */
export function AgentStatusUsePanel({ runId }: AgentStatusUsePanelProps) {
  return (
    <section className="status-panel">
      <h2>에이전트 상태</h2>
      <Suspense fallback={<p className="muted">상태를 불러오는 중…</p>}>
        <StatusInner runId={runId} />
      </Suspense>
      <style>{`
        .status-panel {
          margin-top: 1.25rem;
          padding: 1rem;
          border-radius: 12px;
          background: #fff;
          border: 1px solid #e2e8f0;
        }
        .meta { font-size: 0.9rem; color: #475569; }
        .muted { color: #64748b; }
        .final-output pre {
          white-space: pre-wrap;
          word-break: break-word;
          background: #0f172a08;
          padding: 0.75rem;
          border-radius: 8px;
        }
        .error { color: #b91c1c; }
      `}</style>
    </section>
  );
}
