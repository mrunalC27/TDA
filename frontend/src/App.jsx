import { useState } from "react";
import { useAnalysis } from "./useAnalysis";
import Dashboard from "./Dashboard";
import PillarCard from "./components/PillarCard";
import RecentScans from "./components/RecentScans";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const { status, currentStep, result, error, runAnalysis, reset } = useAnalysis();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (repoUrl.trim()) {
      runAnalysis(repoUrl.trim());
    }
  };

  return (
    <div className={status === "complete" ? "" : "min-h-screen bg-[#0a0e17] flex flex-col"}>
      {status !== "complete" && (
        <header className="w-full flex items-center justify-between px-8 py-5">
          <div className="flex items-center gap-2">
            <img src="/refactr-logo.png" alt="Refactr" className="w-7 h-7" />            
            <span
              className="text-sm font-medium text-[#7b8395] tracking-wide"
              style={{ fontFamily: "var(--font-display)" }}
            >
              REFACTR
            </span>
          </div>
          {status === "idle" && (
            <RecentScans onSelectRepo={(url) => runAnalysis(url)} />
          )}
        </header>
      )}

      <div className="flex-1 flex flex-col items-center justify-center p-6">
        {status === "idle" && (
          <div className="max-w-5xl w-full text-center px-6">
            <h1
              className="text-7xl font-bold mb-4 tracking-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Refactr
            </h1>
            <p className="text-[#06f0c8] text-xl mb-4 font-medium">
              Debt doesn't ship. We find it before you do.
            </p>

            <p className="text-[#7b8395] mb-12 max-w-2xl mx-auto text-lg">
              A comprehensive code audit platform built to uncover risks, debt, and
              hidden bottlenecks.
            </p>

            <form onSubmit={handleSubmit} className="flex gap-2 max-w-xl mx-auto mb-3">
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/owner/repo"
                className="flex-1 bg-[#11151f] border border-[#1f2533] rounded-lg px-4 py-3 text-[#e8eaf0] placeholder-[#7b8395] focus:outline-none focus:ring-2 focus:ring-[#06f0c8]/50 focus:border-[#06f0c8]/50"
              />
              <button
                type="submit"
                className="bg-[#06f0c8] text-[#0a0e17] px-6 py-3 rounded-lg font-semibold hover:bg-[#06f0c8]/90 transition"
              >
                Analyze
              </button>
            </form>
            <p className="text-xs text-[#7b8395] mb-12">
              Large repositories (1000+ commits or files) may take 1-3 minutes to analyze.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-left mt-16">
              <PillarCard
                number="01"
                title="Structural Code Intelligence"
                description="Complexity, dead code, duplication, churn, and dependency rot across any language."
              />
              <PillarCard
                number="02"
                title="Security & Vulnerability Fortification"
                description="Leaked secrets, backdoor patterns, dangerous code, and unprotected endpoints."
              />
              <PillarCard
                number="03"
                title="Contributor & Velocity Metrics"
                description="Developer efficiency, knowledge silos, debt contribution, and PR review health."
              />
              <PillarCard
                number="04"
                title="AI-Synthesized Insight"
                description="Executive summaries, remediation roadmaps, and architecture evaluation."
              />
            </div>
          </div>
        )}

        {status === "running" && (
          <div className="max-w-xl w-full text-center">
            <div
              className="animate-spin h-12 w-12 border-4 border-t-transparent rounded-full mx-auto mb-6"
              style={{
                borderColor: "#06f0c8",
                borderTopColor: "transparent",
                boxShadow: "0 0 20px #06f0c850",
              }}
            />
            <p className="text-[#e8eaf0] font-lg">{currentStep || "Starting..."}</p>
          </div>
        )}

        {status === "failed" && (
          <div className="max-w-xl w-full text-center">
            <p className="text-red-600 font-medium mb-4">Analysis failed</p>
            <p className="text-slate-500 text-sm mb-6">{error}</p>
            <button
              onClick={reset}
              className="bg-slate-200 px-4 py-2 rounded-lg hover:bg-slate-300"
            >
              Try again
            </button>
          </div>
        )}

        {status === "complete" && result && (
          <Dashboard result={result} onReset={reset} />
        )}
      </div>
    </div>
  );
}

export default App;