import { useState, useEffect } from "react";
import { getRecentScans } from "../api";

function statusColor(status) {
    if (status === "Healthy") return "#00ffaa";
    if (status === "Moderate Debt") return "#ffc94d";
    return "#ff3366";
}

function repoDisplayName(repoUrl) {
    if (!repoUrl) return "Unknown";
    const parts = repoUrl.replace(/\/$/, "").split("/");
    return parts.slice(-2).join("/");
}

function timeAgo(isoString) {
    const diffMs = Date.now() - new Date(isoString).getTime();
    const minutes = Math.floor(diffMs / 60000);

    if (minutes < 1) return "just now";
    if (minutes < 60) return `${minutes}m ago`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;

    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

function RecentScans({ onSelectRepo }) {
    const [open, setOpen] = useState(false);
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!open) return;

        setLoading(true);
        getRecentScans()
            .then((data) => setScans(data))
            .catch(() => setScans([]))
            .finally(() => setLoading(false));
    }, [open]);

    const uniqueScans = [];
    const seenUrls = new Set();

    for (const scan of scans) {
        if (!seenUrls.has(scan.repo_url)) {
            seenUrls.add(scan.repo_url);
            uniqueScans.push(scan);
        }
    }

    return (
        <>
            <button
                onClick={() => setOpen(true)}
                className="bg-[#11151f]/80 border border-[#1f2533] backdrop-blur-md text-[#e8eaf0] text-sm font-medium px-4 py-2 rounded-lg hover:border-[#06f0c8]/40 transition-colors"
            >
                Recent Scans
            </button>

            {open && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex justify-end"
                    onClick={() => setOpen(false)}
                >
                    <div
                        className="w-full max-w-sm h-full bg-[#0d1119]/90 backdrop-blur-xl border-l border-[#1f2533] p-6 overflow-y-auto"
                        onClick={(e) => e.stopPropagation()}
                        style={{
                            boxShadow: "-20px 0 60px rgba(0,0,0,0.5)",
                        }}
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-base font-medium text-[#e8eaf0]" style={{ fontFamily: "var(--font-display)" }}>
                                Recent Scans
                            </h2>
                            <button
                                onClick={() => setOpen(false)}
                                className="text-[#7b8395] hover:text-[#e8eaf0] text-xl leading-none"
                            >
                                ×
                            </button>
                        </div>

                        {loading && <p className="text-sm text-[#7b8395]">Loading...</p>}

                        {!loading && uniqueScans.length === 0 && (
                            <p className="text-sm text-[#7b8395]">No scans yet.</p>
                        )}

                        <div className="space-y-2">
                            {uniqueScans.map((scan) => (
                                <button
                                    key={scan.id}
                                    onClick={() => {
                                        setOpen(false);
                                        onSelectRepo(scan.repo_url);
                                    }}
                                    className="w-full flex items-center justify-between bg-[#11151f]/60 border border-[#1f2533] rounded-lg px-4 py-3 hover:border-[#06f0c8]/40 hover:bg-[#11151f] transition-colors text-left"
                                >
                                    <div>
                                        <p className="text-[#e8eaf0] text-sm font-medium">
                                            {repoDisplayName(scan.repo_url)}
                                        </p>
                                        <p className="text-[#7b8395] text-xs mt-0.5">
                                            {scan.primary_language || "Unknown"} · {timeAgo(scan.scanned_at)}
                                        </p>
                                    </div>
                                    <span
                                        className="text-lg font-bold"
                                        style={{ fontFamily: "var(--font-display)", color: statusColor(scan.health_status) }}
                                    >
                                        {scan.health_score ?? "N/A"}
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

export default RecentScans;