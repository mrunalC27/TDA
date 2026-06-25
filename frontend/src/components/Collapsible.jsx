import { useState } from "react";

function Collapsible({ title, defaultOpen = false, children }) {
    const [open, setOpen] = useState(defaultOpen);

    return (
        <div className="bg-[#11151f] border border-[#1f2533] rounded-xl overflow-hidden">
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between px-5 py-4 text-left"
            >
                <span className="text-sm font-medium text-[#e8eaf0]" style={{ fontFamily: "var(--font-display)" }}>
                    {title}
                </span>
                <span className="text-[#7b8395] text-sm">{open ? "−" : "+"}</span>
            </button>
            {open && <div className="px-5 pb-5">{children}</div>}
        </div>
    );
}

export default Collapsible;