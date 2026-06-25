function RadialScore({ value, label, sublabel, color = "#06f0c8", size = 140 }) {
    const radius = size / 2 - 10;
    const circumference = 2 * Math.PI * radius;
    const safeValue = Math.max(0, Math.min(100, value ?? 0));
    const offset = circumference - (safeValue / 100) * circumference;

    return (
        <div className="flex flex-col items-center justify-center">
            <div style={{ width: size, height: size }} className="relative">
                <svg width={size} height={size} className="-rotate-90">
                    <defs>
                        <filter id={`glow-${color.replace("#", "")}`} x="-50%" y="-50%" width="200%" height="200%">
                            <feGaussianBlur stdDeviation="4" result="blur" />
                            <feMerge>
                                <feMergeNode in="blur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="none"
                        stroke="#1a2030"
                        strokeWidth="10"
                    />
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="none"
                        stroke={color}
                        strokeWidth="8"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        filter={`url(#glow-${color.replace("#", "")})`}
                        style={{ transition: "stroke-dashoffset 0.6s ease" }}
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span
                        className="text-3xl font-bold"
                        style={{
                            fontFamily: "var(--font-display)",
                            color,
                            textShadow: `0 0 12px ${color}80`,
                        }}
                    >
                        {Math.round(safeValue)}
                    </span>
                    {sublabel && (
                        <span className="text-[10px] text-[#7b8395] uppercase tracking-wide mt-0.5">
                            {sublabel}
                        </span>
                    )}
                </div>
            </div>
            {label && <span className="text-sm text-[#7b8395] mt-2">{label}</span>}
        </div>
    );
}

export default RadialScore;