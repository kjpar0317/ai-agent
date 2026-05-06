import type { Ref } from "react";

import type { AgentStep, AgentStepState } from "../types";

const stateLabel: Record<AgentStepState, string> = {
  pending: "대기",
  active: "진행 중",
  done: "완료",
  error: "오류",
};

function stepOrder(a: AgentStep, b: AgentStep): number {
  const order = ["analyze", "execute", "validate"];
  return order.indexOf(a.id) - order.indexOf(b.id);
}

export type AgentSteppersProps = {
  steps: AgentStep[];
  ref?: Ref<HTMLDivElement>;
};

export function AgentSteppers({ steps, ref }: AgentSteppersProps) {
  const ordered = [...steps].sort(stepOrder);

  return (
    <div ref={ref} className="steppers" role="list" aria-label="에이전트 단계">
      {ordered.map((s) => (
        <div key={s.id} className={`step step-${s.state}`} role="listitem">
          <span className="step-label">{s.label}</span>
          <span className="step-state">{stateLabel[s.state]}</span>
        </div>
      ))}
      <style>{`
        .steppers {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin: 1rem 0;
        }
        .step {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.6rem 0.75rem;
          border-radius: 8px;
          border: 1px solid #e2e8f0;
          background: #fff;
        }
        .step-pending { opacity: 0.65; }
        .step-active { border-color: #3b82f6; box-shadow: 0 0 0 1px #3b82f640; }
        .step-done { border-color: #22c55e; }
        .step-error { border-color: #ef4444; }
        .step-label { font-weight: 600; }
        .step-state { font-size: 0.85rem; color: #64748b; }
      `}</style>
    </div>
  );
}
