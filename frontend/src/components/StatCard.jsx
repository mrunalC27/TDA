function StatCard({ label, value, subtext, tone = "neutral" }) {
    const toneStyles = {
        neutral: "text-[#e8eaf0]",
        good: "text-[#3fd68c]",
        warning: "text-[#ffb454]",
        bad: "text-[#ff5c7a]",
    };

    return (
        <div className="bg-[#11151f] border border-[#1f2533] rounded-xl p-5 hover:border-[#2a3144] transition-colors">
            <p className="text-sm text-[#7b8395] mb-1">{label}</p>
            <p className={`text-3xl font-bold ${toneStyles[tone]}`} style={{ fontFamily: "var(--font-display)" }}>
                {value}
            </p>
            {subtext && <p className="text-xs text-[#7b8395] mt-1">{subtext}</p>}
        </div>
    );
}

export default StatCard;