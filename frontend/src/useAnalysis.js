import { useState, useRef, useCallback } from "react";
import { startAnalysis, getAnalysisStatus } from "./api";

export function useAnalysis() {
    const [status, setStatus] = useState("idle");
    const [currentStep, setCurrentStep] = useState("");
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const pollRef = useRef(null);

    const reset = useCallback(() => {
        if (pollRef.current) clearInterval(pollRef.current);
        setStatus("idle");
        setCurrentStep("");
        setResult(null);
        setError(null);
    }, []);

    const runAnalysis = useCallback(async (repoUrl) => {
        reset();
        setStatus("running");

        try {
            const jobId = await startAnalysis(repoUrl);

            pollRef.current = setInterval(async () => {
                try {
                    const data = await getAnalysisStatus(jobId);
                    setCurrentStep(data.current_step || "");

                    if (data.status === "complete") {
                        clearInterval(pollRef.current);
                        setResult(data.result);
                        setStatus("complete");
                    } else if (data.status === "failed") {
                        clearInterval(pollRef.current);
                        setError(data.error || "Analysis failed");
                        setStatus("failed");
                    }
                } catch (err) {
                    clearInterval(pollRef.current);
                    setError(err.message);
                    setStatus("failed");
                }
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setStatus("failed");
        }
    }, [reset]);

    return { status, currentStep, result, error, runAnalysis, reset };
}