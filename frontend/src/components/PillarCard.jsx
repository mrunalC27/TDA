function PillarCard({ number, title, description }) {
    return (
        <div className="bg-[#11151f] border border-[#1f2533] rounded-xl p-5 hover:border-[#06f0c8]/40 transition-colors">
            <div className="text-[#06f0c8] font-mono text-xs mb-2">PILLAR {number}</div>
            <h3 className="text-[#e8eaf0] font-semibold mb-2" style={{ fontFamily: "var(--font-display)" }}>
                {title}
            </h3>
            <p className="text-[#7b8395] text-sm leading-relaxed">{description}</p>
        </div>
    );
}

export default PillarCard;