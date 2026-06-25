function Card({ title, children, className = "" }) {
    return (
        <div className={`bg-[#11151f] border border-[#1f2533] rounded-xl p-5 hover:border-[#2a3144] transition-colors ${className}`}>
            {title && (
                <h3 className="text-base font-medium text-[#7b8395] mb-3" style={{ fontFamily: "var(--font-display)" }}>                    {title}
                </h3>
            )}
            {children}
        </div>
    );
}

export default Card;