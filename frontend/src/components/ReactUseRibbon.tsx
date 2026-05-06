import { Suspense, use, useMemo } from "react";

function RibbonInner({ textPromise }: { textPromise: Promise<string> }) {
  const text = use(textPromise);
  return <aside className="ribbon">{text}</aside>;
}

export type ReactUseRibbonProps = {
  /** Suspense + `use()` 샘플용 짧은 라벨 (예: 마지막 사용자 메시지) */
  label: string;
};

/**
 * React 19 `use()` + Suspense 최소 예시.
 * 마이크로태스크로 이행하는 Promise라도 경계 안에서 `use()`로 읽습니다.
 */
export function ReactUseRibbon({ label }: ReactUseRibbonProps) {
  const textPromise = useMemo(
    () =>
      new Promise<string>((resolve) => {
        queueMicrotask(() => resolve(`use() 리본 · ${label}`));
      }),
    [label],
  );

  return (
    <Suspense fallback={<aside className="ribbon muted">리본 준비 중…</aside>}>
      <RibbonInner textPromise={textPromise} />
      <style>{`
        .ribbon {
          margin-top: 0.75rem;
          padding: 0.5rem 0.75rem;
          border-radius: 999px;
          background: #e0f2fe;
          color: #075985;
          font-size: 0.85rem;
        }
        .ribbon.muted { background: #f1f5f9; color: #64748b; }
      `}</style>
    </Suspense>
  );
}
