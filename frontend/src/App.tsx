import { useAtomValue } from "jotai";
import { useState } from "react";

import { currentRunIdAtom } from "./atoms/agentAtoms";
import { AgentStatusUsePanel } from "./components/AgentStatusUsePanel";
import { ReactUseRibbon } from "./components/ReactUseRibbon";
import { useAgentRunStream } from "./hooks/useAgent";

export default function App() {
  const runId = useAtomValue(currentRunIdAtom);
  const [message, setMessage] = useState("오늘 뉴스 요약해 줘.");
  const runMutation = useAgentRunStream();

  return (
    <main>
      <h1>자율 에이전트 (Small Loop)</h1>
      <p className="lead">
        FastAPI 백엔드의 <code>POST /agent/run</code> 스트림과 <code>GET /agent/status</code> 폴링을
        TanStack Query로 묶었습니다.
      </p>

      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          runMutation.mutateAsync(message).catch(() => {
            /* TanStack Query가 mutation.isError 로 표면화 */
          });
        }}
      >
        <label htmlFor="msg">요청</label>
        <textarea
          id="msg"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
          disabled={runMutation.isPending}
        />
        <button type="submit" disabled={runMutation.isPending || !message.trim()}>
          {runMutation.isPending ? "실행 중…" : "에이전트 실행"}
        </button>
      </form>

      {message.trim() ? <ReactUseRibbon label={message.trim().slice(0, 80)} /> : null}

      {runMutation.isError ? (
        <p className="error" role="alert">
          {(runMutation.error as Error).message}
        </p>
      ) : null}

      {runId ? (
        <AgentStatusUsePanel runId={runId} />
      ) : (
        <p className="muted">실행을 시작하면 run_id가 생성됩니다.</p>
      )}

      <style>{`
        .lead { color: #475569; }
        .form {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin-top: 1rem;
        }
        textarea {
          font: inherit;
          padding: 0.5rem 0.6rem;
          border-radius: 8px;
          border: 1px solid #cbd5e1;
        }
        button {
          align-self: flex-start;
          padding: 0.45rem 1rem;
          border-radius: 8px;
          border: none;
          background: #2563eb;
          color: #fff;
        }
        button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .error { color: #b91c1c; }
        .muted { color: #64748b; margin-top: 1rem; }
      `}</style>
    </main>
  );
}
