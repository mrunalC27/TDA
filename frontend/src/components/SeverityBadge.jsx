const SEVERITY_STYLES = {
    HIGH: "bg-[#ff5c7a]/15 text-[#ff5c7a]",
    MEDIUM: "bg-[#ffb454]/15 text-[#ffb454]",
    LOW: "bg-[#7b8395]/15 text-[#7b8395]",
};

function SeverityBadge({ severity }) {
    const normalized = (severity || "").toUpperCase();
    const style = SEVERITY_STYLES[normalized] || "bg-[#7b8395]/15 text-[#7b8395]";

    return (
        <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${style}`}>
            {severity || "Unknown"}
        </span>
    );
}

export default SeverityBadge;