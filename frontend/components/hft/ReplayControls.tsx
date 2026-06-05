"use client";
import { Pause, Play, RotateCcw, Square } from "lucide-react";
import { ReplayState } from "@/lib/types";
import { Button } from "@/components/ui/primitives";

const SPEEDS = [1, 5, 10, 50, 100];

export function ReplayControls({
  state,
  onStart,
  onPause,
  onResume,
  onReset,
  onSpeed,
}: {
  state?: ReplayState;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onReset: () => void;
  onSpeed: (s: number) => void;
}) {
  const running = state?.running;
  const paused = state?.paused;
  return (
    <div className="flex flex-wrap items-center gap-2">
      {!running ? (
        <Button variant="gold" onClick={onStart}>
          <Play size={14} /> Start Demo Replay
        </Button>
      ) : paused ? (
        <Button variant="gold" onClick={onResume}>
          <Play size={14} /> Resume
        </Button>
      ) : (
        <Button onClick={onPause}>
          <Pause size={14} /> Pause
        </Button>
      )}
      <Button variant="ghost" onClick={onReset}>
        <RotateCcw size={14} /> Reset
      </Button>
      <div className="flex items-center gap-1 rounded-md border border-terminal-border bg-terminal-panel p-0.5">
        {SPEEDS.map((s) => (
          <button
            key={s}
            onClick={() => onSpeed(s)}
            className={`rounded px-2 py-1 text-xs font-medium transition-colors ${
              state?.speed === s ? "bg-gold/20 text-gold" : "text-terminal-muted hover:text-gray-200"
            }`}
          >
            {s}x
          </button>
        ))}
      </div>
      {state && state.total > 0 && (
        <div className="flex items-center gap-2 text-xs text-terminal-muted">
          <div className="h-1.5 w-28 overflow-hidden rounded-full bg-terminal-panel">
            <div className="h-full rounded-full bg-gold/70" style={{ width: `${state.progress}%` }} />
          </div>
          <span className="mono">{state.progress}%</span>
        </div>
      )}
    </div>
  );
}
