import ReactMarkdown from "react-markdown";
import Card from "./Card";

function isErrorMessage(text) {
    return (
        typeof text === "string" &&
        (text.includes("Unavailable") || text.includes("429") || text.includes("Quota exceeded"))
    );
}

function AISummaryCard({ title, content }) {
    const isError = isErrorMessage(content);

    return (
        <Card title={title}>
            {isError ? (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-700">
                    AI insight unavailable right now — the AI provider's usage limit has been reached.
                    The rest of the analysis is unaffected.
                </div>
            ) : (
                    <div className="prose prose-base prose-invert max-w-none prose-headings:text-[#e8eaf0] prose-headings:font-semibold prose-strong:text-[#e8eaf0] prose-li:text-[#c5cad6] prose-p:text-[#c5cad6] leading-relaxed">
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
            )}
        </Card>
    );
}

export default AISummaryCard;