"use client";
import { useEffect, useRef, useState } from "react";

export function usePoll<T>(fn: () => Promise<T>, intervalMs: number, enabled = true) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    const tick = async () => {
      try {
        const d = await fnRef.current();
        if (active) {
          setData(d);
          setError(null);
        }
      } catch (e) {
        if (active) setError((e as Error).message);
      }
    };
    tick();
    const id = setInterval(tick, intervalMs);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [intervalMs, enabled]);

  return { data, error };
}
