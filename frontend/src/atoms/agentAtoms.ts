import { atom } from "jotai";

/** 현재 폴링·SSE와 연동할 실행 ID */
export const currentRunIdAtom = atom<string | null>(null);
