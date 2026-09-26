"use client";

import { useEffect, useState } from "react";

const STAGES = [
  "Collecting evidence",
  "Building context",
  "Checking contradictions",
  "Forming decision",
] as const;

export function AnalysisProgress({ active }: { active: boolean }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!active) {
      setIndex(0);
      return;
    }
    const timer = window.setInterval(() => {
      setIndex((current) => Math.min(current + 1, STAGES.length - 1));
    }, 450);
    return () => window.clearInterval(timer);
  }, [active]);

  if (!active) {
    return null;
  }

  return (
    <ol className="mt-8 border border-[#2F2D28] bg-[#0B0B0C] px-5 py-4" aria-live="polite">
      {STAGES.map((stage, stageIndex) => {
        const reached = stageIndex <= index;
        return (
          <li
            key={stage}
            className={`py-1 font-mono text-xs tracking-[0.08em] ${
              reached ? "text-[#F7F4EC]" : "text-[#A5A198]"
            }`}
          >
            {reached ? "→" : "·"} {stage}
          </li>
        );
      })}
    </ol>
  );
}
