const CATEGORY_LABELS = {
    complexity: "Complexity",
    maintainability: "Maintainability",
    dead_code: "Dead Code",
    security: "Security",
    dependency: "Dependencies",
};

const CATEGORY_COLORS = {
    complexity: "bg-[#ffb454]",
    maintainability: "bg-[#7c5cff]",
    dead_code: "bg-[#06f0c8]",
    security: "bg-[#ff5c7a]",
    dependency: "bg-[#06b6d4]",
};

function HealthBreakdown({ breakdown }) {
    if (!breakdown) {
        return <p className="text-sm text-[#7b8395]">No breakdown data available.</p>;
    }

    const categories = Object.keys(CATEGORY_LABELS).filter(
        (key) => breakdown[key] > 0
    );

    const totalPenalty = categories.reduce((sum, key) => sum + breakdown[key], 0);

    if (categories.length === 0) {
        return (
            <p className="text-sm text-[#3fd68c]">
                No penalties applied — this category contributed no debt.
            </p>
        );
    }

    return (
        <div>
            <div className="flex w-full h-3 rounded-full overflow-hidden bg-[#1f2533] mb-3">
                {categories.map((key) => (
                    <div
                        key={key}
                        className={CATEGORY_COLORS[key]}
                        style={{ width: `${(breakdown[key] / totalPenalty) * 100}%` }}
                        title={`${CATEGORY_LABELS[key]}: -${breakdown[key]} points`}
                    />
                ))}
            </div>
            <div className="flex flex-wrap gap-3">
                {categories.map((key) => (
                    <div key={key} className="flex items-center gap-1.5 text-xs text-[#c5cad6]">
                        <span className={`w-2.5 h-2.5 rounded-full ${CATEGORY_COLORS[key]}`} />
                        {CATEGORY_LABELS[key]}: -{breakdown[key]}
                    </div>
                ))}
            </div>
            {breakdown.capped_overflow > 0 && (
                <p className="text-xs text-[#7b8395] mt-3">
                    Note: total penalty was capped at 75 points. Without the cap, this score
                    would have been {breakdown.capped_overflow} points lower.
                </p>
            )}
        </div>
    );
}

export default HealthBreakdown;