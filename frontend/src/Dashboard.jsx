import { useState } from "react";
import StatCard from "./components/StatCard";
import Card from "./components/Card";
import HealthBreakdown from "./components/HealthBreakdown";
import AISummaryCard from "./components/AISummaryCard";
import DataTable from "./components/DataTable";
import Collapsible from "./components/Collapsible";
import SeverityBadge from "./components/SeverityBadge";
import RadialScore from "./components/RadialScore";
const TABS = ["Overview", "Structural", "Security", "Contributors", "AI Insights"];

function healthTone(status) {
    if (status === "Healthy") return "good";
    if (status === "Moderate Debt") return "warning";
    return "bad";
}

function Dashboard({ result, onReset }) {
    const [activeTab, setActiveTab] = useState("Overview");

    const health = result.health || {};
    const profile = result.profile || {};
    const contributorSummary = result.contributor?.summary || {};

    return (
        <div className="min-h-screen bg-[#0a0e17] p-6">
            <div className="max-w-6xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <h1
                        className="text-2xl font-bold text-[#e8eaf0]"
                        style={{ fontFamily: "var(--font-display)" }}
                    >
                        {result.repository?.repository_name?.replace(/_[a-f0-9]{8}$/, "") || "Analysis Results"}
                    </h1>
                    <button
                        onClick={onReset}
                        className="bg-[#06f0c8] text-[#0a0e17] px-5 py-2 rounded-lg font-semibold text-sm hover:bg-[#06f0c8]/90 transition"
                    >
                        Analyze another repo
                    </button>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-[#11151f] border border-[#1f2533] rounded-xl p-4 flex items-center justify-center">
                        <RadialScore
                            value={typeof health.health_score === "number" ? health.health_score : 0}
                            sublabel={health.status}
                            color={
                                health.status === "Healthy"
                                    ? "#00ffaa"
                                    : health.status === "Moderate Debt"
                                        ? "#ffc94d"
                                        : "#ff3366"
                            }
                        />
                    </div>
                    <StatCard
                        label="Primary Language"
                        value={profile.primary_language || "Unknown"}
                        subtext={profile.framework !== "Unknown" ? profile.framework : null}
                    />
                    <StatCard
                        label="Contributors"
                        value={contributorSummary.total_contributors ?? "N/A"}
                        subtext={
                            contributorSummary.active_contributors != null
                                ? `${contributorSummary.active_contributors} active`
                                : null
                        }
                    />
                    <StatCard
                        label="Total Files"
                        value={result.repository?.total_files ?? "N/A"}
                        subtext={
                            result.repository?.total_lines
                                ? `${result.repository.total_lines.toLocaleString()} lines`
                                : null
                        }
                    />
                </div>

                <div className="flex gap-1 border-b border-[#1f2533] mb-6">
                    {TABS.map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${activeTab === tab
                                    ? "bg-[#11151f] border border-[#1f2533] border-b-[#11151f] text-[#06f0c8] -mb-px"
                                    : "text-[#7b8395] hover:text-[#e8eaf0]"
                                }`}
                        >
                            {tab}
                        </button>
                    ))}
                </div>

                <div>
                    {activeTab === "Overview" && (
                        <div className="space-y-6">
                            <Card title="Health Score Breakdown">
                                <HealthBreakdown breakdown={health.breakdown} />
                            </Card>

                            <AISummaryCard title="AI Executive Summary" content={result.ai_summary} />

                            <Card title="Trend">
                                {result.trend?.summary?.status === "Not Enough Scan History" ? (
                                    <p className="text-sm text-slate-500">
                                        Run this analysis {result.trend.summary.scans_needed - result.trend.summary.scans_recorded} more time(s)
                                        on this repository to enable trend tracking.
                                    </p>
                                ) : (
                                    <p className="text-sm text-slate-500">
                                        {result.trend?.summary?.direction
                                            ? `Health score is ${result.trend.summary.direction.toLowerCase()} (${result.trend.summary.change > 0 ? "+" : ""}${result.trend.summary.change} since first scan).`
                                            : "No trend data available."}
                                    </p>
                                )}
                            </Card>
                        </div>
                    )}
                    {activeTab === "Structural" && (
                        <div className="space-y-6">
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                <StatCard
                                    label="Avg Complexity"
                                    value={result.complexity?.summary?.average_complexity ?? "N/A"}
                                    subtext={
                                        result.complexity?.summary?.high_risk_functions != null
                                            ? `${result.complexity.summary.high_risk_functions} high-risk functions`
                                            : null
                                    }
                                />
                                <StatCard
                                    label="Maintainability"
                                    value={result.maintainability?.summary?.average_maintainability ?? "N/A"}
                                    subtext={result.maintainability?.summary?.status}
                                    tone={
                                        result.maintainability?.summary?.status === "Excellent" ||
                                            result.maintainability?.summary?.status === "Good"
                                            ? "good"
                                            : result.maintainability?.summary?.status === "Poor"
                                                ? "bad"
                                                : "neutral"
                                    }
                                />
                                <StatCard
                                    label="Dead Code"
                                    value={result.dead_code?.summary?.total_dead_code ?? "N/A"}
                                    subtext={
                                        result.dead_code?.summary?.status === "Not Supported Yet"
                                            ? "Not supported for this language"
                                            : "findings"
                                    }
                                />
                                <StatCard
                                    label="Duplicate Blocks"
                                    value={result.duplication?.summary?.duplicate_blocks ?? "N/A"}
                                    subtext={
                                        result.duplication?.summary?.total_lines_duplicated != null
                                            ? `${result.duplication.summary.total_lines_duplicated} lines`
                                            : null
                                    }
                                    tone={result.duplication?.summary?.high_duplication ? "warning" : "neutral"}
                                />
                                <StatCard
                                    label="High-Churn Files"
                                    value={result.churn?.summary?.high_churn_files ?? "N/A"}
                                    subtext={
                                        result.churn?.summary?.files_tracked != null
                                            ? `of ${result.churn.summary.files_tracked} tracked`
                                            : null
                                    }
                                />
                                <StatCard
                                    label="Outdated Dependencies"
                                    value={
                                        (result.dependency_rot?.summary?.major_behind ?? 0) +
                                        (result.dependency_rot?.summary?.minor_behind ?? 0)
                                    }
                                    subtext={
                                        result.dependency_rot?.summary?.packages_checked != null
                                            ? `of ${result.dependency_rot.summary.packages_checked} checked`
                                            : null
                                    }
                                />
                            </div>

                            <Collapsible title="Top Complexity Hotspots" defaultOpen>
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "function", label: "Function" },
                                        { key: "complexity", label: "Complexity" },
                                    ]}
                                    rows={result.complexity?.hotspots}
                                    emptyMessage="No complexity data available."
                                />
                            </Collapsible>

                            <Collapsible title="Lowest Maintainability Files">
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "score", label: "Score" },
                                        { key: "status", label: "Status" },
                                    ]}
                                    rows={result.maintainability?.worst_files}
                                />
                            </Collapsible>

                            <Collapsible title="Most Frequently Changed Files">
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "changes", label: "Changes" },
                                    ]}
                                    rows={result.churn?.hotspots}
                                />
                            </Collapsible>

                            <Collapsible title="Code Duplication">
                                <DataTable
                                    columns={[
                                        { key: "file_a", label: "File A" },
                                        { key: "file_b", label: "File B" },
                                        { key: "lines_duplicated", label: "Lines" },
                                        {
                                            key: "same_file",
                                            label: "Same File",
                                            render: (val) => (val ? "Yes" : "No"),
                                        },
                                    ]}
                                    rows={result.duplication?.findings}
                                />
                            </Collapsible>

                            <Collapsible title="Outdated Dependencies">
                                <DataTable
                                    columns={[
                                        { key: "package", label: "Package" },
                                        { key: "current_version", label: "Current" },
                                        { key: "latest_version", label: "Latest" },
                                        {
                                            key: "status",
                                            label: "Status",
                                            render: (val) => (
                                                <span
                                                    className={
                                                        val === "major_behind"
                                                            ? "text-red-600"
                                                            : val === "minor_behind"
                                                                ? "text-amber-600"
                                                                : "text-slate-500"
                                                    }
                                                >
                                                    {val?.replace("_", " ")}
                                                </span>
                                            ),
                                        },
                                    ]}
                                    rows={result.dependency_rot?.findings}
                                />
                            </Collapsible>

                            <Collapsible title="Untested Source Files">
                                <DataTable
                                    columns={[{ key: "file", label: "File" }]}
                                    rows={result.test_presence?.untested_files}
                                    emptyMessage="Every source file has a matching test file."
                                />
                            </Collapsible>
                        </div>
                    )}
                    {activeTab === "Security" && (
                        <div className="space-y-6">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <StatCard
                                    label="Dangerous Patterns"
                                    value={result.security?.summary?.total_issues ?? "N/A"}
                                    subtext={
                                        result.security?.summary?.high != null
                                            ? `${result.security.summary.high} high severity`
                                            : null
                                    }
                                    tone={result.security?.summary?.high > 0 ? "bad" : "neutral"}
                                />
                                <StatCard
                                    label="Leaked Secrets"
                                    value={result.secrets?.summary?.total_findings ?? "N/A"}
                                    subtext={
                                        result.secrets?.summary?.high_severity != null
                                            ? `${result.secrets.summary.high_severity} high severity`
                                            : null
                                    }
                                    tone={result.secrets?.summary?.high_severity > 0 ? "bad" : "neutral"}
                                />
                                <StatCard
                                    label="Backdoor Patterns"
                                    value={result.backdoor?.summary?.backdoor_findings ?? "N/A"}
                                    subtext={
                                        result.backdoor?.summary?.dangerous_pattern_findings != null
                                            ? `+${result.backdoor.summary.dangerous_pattern_findings} dangerous patterns`
                                            : null
                                    }
                                    tone={result.backdoor?.summary?.high_severity_total > 0 ? "bad" : "neutral"}
                                />
                                <StatCard
                                    label="Unprotected Endpoints"
                                    value={result.endpoint_security?.summary?.open_endpoints_found ?? "N/A"}
                                    subtext={
                                        result.endpoint_security?.summary?.sensitive_endpoints_without_auth != null
                                            ? `${result.endpoint_security.summary.sensitive_endpoints_without_auth} sensitive`
                                            : null
                                    }
                                    tone={
                                        result.endpoint_security?.summary?.sensitive_endpoints_without_auth > 0
                                            ? "warning"
                                            : "neutral"
                                    }
                                />
                            </div>

                            <Collapsible title="Dangerous Code Patterns" defaultOpen>
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "line", label: "Line" },
                                        { key: "issue", label: "Issue" },
                                        {
                                            key: "severity",
                                            label: "Severity",
                                            render: (val) => <SeverityBadge severity={val} />,
                                        },
                                    ]}
                                    rows={result.security?.findings}
                                    emptyMessage="No dangerous code patterns found."
                                />
                            </Collapsible>

                            <Collapsible title="Leaked Secrets & Hardcoded Credentials">
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "line", label: "Line" },
                                        { key: "type", label: "Type" },
                                        {
                                            key: "severity",
                                            label: "Severity",
                                            render: (val) => <SeverityBadge severity={val} />,
                                        },
                                    ]}
                                    rows={result.secrets?.findings}
                                    emptyMessage="No leaked secrets or hardcoded credentials found."
                                />
                            </Collapsible>

                            <Collapsible title="Backdoor & Suspicious Patterns">
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "line", label: "Line" },
                                        { key: "category", label: "Category" },
                                        { key: "issue", label: "Issue" },
                                        {
                                            key: "severity",
                                            label: "Severity",
                                            render: (val) => <SeverityBadge severity={val} />,
                                        },
                                    ]}
                                    rows={result.backdoor?.findings}
                                    emptyMessage="No backdoor or suspicious patterns found."
                                />
                            </Collapsible>

                            <Collapsible title="Endpoints Without Detected Auth">
                                <div className="mb-3 text-xs text-slate-400">
                                    {result.endpoint_security?.summary?.note}
                                </div>
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "method", label: "Method" },
                                        { key: "path", label: "Path" },
                                        {
                                            key: "sensitive_path",
                                            label: "Sensitive",
                                            render: (val) => (val ? "Yes" : "No"),
                                        },
                                        {
                                            key: "risk",
                                            label: "Risk",
                                            render: (val) => <SeverityBadge severity={val} />,
                                        },
                                    ]}
                                    rows={result.endpoint_security?.findings}
                                    emptyMessage="No unprotected endpoints detected (or no routes found)."
                                />
                            </Collapsible>
                        </div>
                    )}
                    {activeTab === "Contributors" && (
                        <div className="space-y-6">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <StatCard
                                    label="Total Contributors"
                                    value={result.contributor?.summary?.total_contributors ?? "N/A"}
                                    subtext={
                                        result.contributor?.summary?.active_contributors != null
                                            ? `${result.contributor.summary.active_contributors} active`
                                            : null
                                    }
                                />
                                <StatCard
                                    label="Knowledge Silos"
                                    value={result.contributor?.summary?.knowledge_silo_files ?? "N/A"}
                                    subtext="files with a single author"
                                    tone={result.contributor?.summary?.knowledge_silo_files > 10 ? "warning" : "neutral"}
                                />
                                <StatCard
                                    label="Large Commits"
                                    value={result.contributor?.summary?.large_commits_found ?? "N/A"}
                                    subtext="unusually large changes"
                                />
                                <StatCard
                                    label="PR Review Coverage"
                                    value={
                                        result.pr_maturity?.summary?.review_coverage_pct != null
                                            ? `${result.pr_maturity.summary.review_coverage_pct}%`
                                            : "N/A"
                                    }
                                    subtext={
                                        result.pr_maturity?.summary?.merged_prs_analyzed != null
                                            ? `of ${result.pr_maturity.summary.merged_prs_analyzed} merged PRs`
                                            : result.pr_maturity?.summary?.status
                                    }
                                    tone={
                                        result.pr_maturity?.summary?.review_coverage_pct == null
                                            ? "neutral"
                                            : result.pr_maturity.summary.review_coverage_pct < 70
                                                ? "warning"
                                                : "good"
                                      }
                                />
                            </div>

                            <Collapsible title="Developer Efficiency" defaultOpen>
                                <DataTable
                                    columns={[
                                        { key: "author", label: "Author" },
                                        { key: "commits", label: "Commits" },
                                        { key: "lines_changed", label: "Lines Changed" },
                                        { key: "commits_per_week", label: "Commits/Week" },
                                        { key: "last_active", label: "Last Active" },
                                    ]}
                                    rows={result.contributor?.developer_efficiency}
                                    emptyMessage="No contributor data available."
                                />
                            </Collapsible>

                            <Collapsible title="Debt Contribution Ratio">
                                <DataTable
                                    columns={[
                                        { key: "author", label: "Author" },
                                        { key: "files_touched", label: "Files Touched" },
                                        { key: "high_risk_files_touched", label: "High-Risk Files" },
                                        {
                                            key: "debt_contribution_ratio",
                                            label: "Debt Ratio",
                                            render: (val) => (
                                                <span className={val >= 0.5 ? "text-amber-600 font-medium" : "text-slate-600"}>
                                                    {val}
                                                </span>
                                            ),
                                        },
                                    ]}
                                    rows={result.contributor?.debt_contribution}
                                    emptyMessage="No debt contribution data available."
                                />
                            </Collapsible>

                            <Collapsible title="Knowledge Silos (Files With Single Author)">
                                <DataTable
                                    columns={[
                                        { key: "file", label: "File" },
                                        { key: "sole_author", label: "Sole Author" },
                                    ]}
                                    rows={result.contributor?.knowledge_silos}
                                    emptyMessage="No knowledge silo files detected."
                                />
                            </Collapsible>

                            <Collapsible title="Large / High-Impact Commits">
                                <DataTable
                                    columns={[
                                        { key: "commit", label: "Commit" },
                                        { key: "author", label: "Author" },
                                        { key: "date", label: "Date" },
                                        { key: "files_changed", label: "Files" },
                                        { key: "lines_changed", label: "Lines" },
                                    ]}
                                    rows={result.contributor?.large_commits}
                                    emptyMessage="No unusually large commits detected."
                                />
                            </Collapsible>

                            <Collapsible title="Pull Request Review Findings">
                                <DataTable
                                    columns={[
                                        { key: "pr_number", label: "PR #" },
                                        { key: "title", label: "Title" },
                                        { key: "review_count", label: "Reviews" },
                                        {
                                            key: "merged_without_review",
                                            label: "Merged Without Review",
                                            render: (val) =>
                                                val ? (
                                                    <span className="text-red-600 font-medium">Yes</span>
                                                ) : (
                                                    "No"
                                                ),
                                        },
                                    ]}
                                    rows={result.pr_maturity?.findings}
                                    emptyMessage="No pull request data available."
                                />
                            </Collapsible>
                        </div>
                    )}
                    {activeTab === "AI Insights" && (
                        <div className="space-y-6">
                            <AISummaryCard title="Remediation Roadmap" content={result.ai_roadmap} />

                            <AISummaryCard
                                title="Architecture Pattern Evaluation"
                                content={result.architecture_evaluation}
                            />

                            <Card title="Debt Prediction">
                                {result.trend?.prediction?.status === "Not Enough Scan History For Prediction" ? (
                                    <p className="text-sm text-slate-500">
                                        Run this analysis {result.trend.prediction.scans_needed - result.trend.prediction.scans_recorded} more
                                        time(s) on this repository to enable debt prediction.
                                    </p>
                                ) : result.trend?.prediction?.trend === "Declining" ? (
                                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-700">
                                        Health score is declining at {result.trend.prediction.average_change_per_scan} points
                                        per scan. At this rate, this repo may reach critical status in
                                        approximately {result.trend.prediction.estimated_scans_until_critical} more scans.
                                    </div>
                                ) : result.trend?.prediction?.trend === "Already Critical" ? (
                                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
                                        This repository is already at a critical health level.
                                    </div>
                                ) : result.trend?.prediction?.trend === "Not Declining" ? (
                                    <p className="text-sm text-emerald-600">
                                        Health score is stable or improving — no debt acceleration detected.
                                    </p>
                                ) : (
                                    <p className="text-sm text-slate-400">No prediction data available.</p>
                                )}
                            </Card>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;