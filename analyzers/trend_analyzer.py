from core.scan_history_store import get_history_for_repo

MIN_SCANS_FOR_TREND = 2
MIN_SCANS_FOR_PREDICTION = 3
CRITICAL_THRESHOLD = 40


class TrendAnalyzer:
    """
    Computes trend analysis and basic debt prediction from stored
    scan history for a given repo. Requires multiple historical
    scans of the same repo_url to produce meaningful output.
    """

    def __init__(self, repo_url):

        self.repo_url = repo_url
        self._cache = None

    def analyze(self):

        if self._cache is not None:
            return self._cache

        history = get_history_for_repo(self.repo_url, limit=20)

        history.sort(key=lambda x: x["scanned_at"])

        self._cache = history
        return self._cache

    def trend_summary(self):

        history = self.analyze()

        if len(history) < MIN_SCANS_FOR_TREND:

            return {
                "status": "Not Enough Scan History",
                "scans_recorded": len(history),
                "scans_needed": MIN_SCANS_FOR_TREND
            }

        scores = [
            h["health_score"] for h in history
            if h["health_score"] is not None
        ]

        if len(scores) < MIN_SCANS_FOR_TREND:

            return {
                "status": "Not Enough Valid Health Scores",
                "scans_recorded": len(history)
            }

        first_score = scores[0]
        latest_score = scores[-1]
        change = latest_score - first_score

        if change > 5:
            direction = "Improving"
        elif change < -5:
            direction = "Declining"
        else:
            direction = "Stable"

        return {
            "scans_recorded": len(history),
            "first_score": first_score,
            "latest_score": latest_score,
            "change": change,
            "direction": direction
        }

    def trend_timeline(self):

        history = self.analyze()

        return [
            {
                "scanned_at": h["scanned_at"],
                "health_score": h["health_score"],
                "status": h["health_status"],
                "security_high": h["security_high"],
                "duplicate_blocks": h["duplicate_blocks"]
            }
            for h in history
        ]

    def debt_prediction(self):

        history = self.analyze()

        scores = [
            h["health_score"] for h in history
            if h["health_score"] is not None
        ]

        if len(scores) < MIN_SCANS_FOR_PREDICTION:

            return {
                "status": "Not Enough Scan History For Prediction",
                "scans_recorded": len(scores),
                "scans_needed": MIN_SCANS_FOR_PREDICTION
            }

        recent_scores = scores[-MIN_SCANS_FOR_PREDICTION:]

        deltas = [
            recent_scores[i + 1] - recent_scores[i]
            for i in range(len(recent_scores) - 1)
        ]

        avg_delta_per_scan = sum(deltas) / len(deltas)

        current_score = recent_scores[-1]

        if avg_delta_per_scan >= 0:

            return {
                "trend": "Not Declining",
                "current_score": current_score,
                "average_change_per_scan": round(avg_delta_per_scan, 2),
                "note": "Health score is stable or improving based on recent scans."
            }

        scans_until_critical = (
            (current_score - CRITICAL_THRESHOLD) / abs(avg_delta_per_scan)
        )

        if scans_until_critical < 0:

            return {
                "trend": "Already Critical",
                "current_score": current_score,
                "average_change_per_scan": round(avg_delta_per_scan, 2)
            }

        return {
            "trend": "Declining",
            "current_score": current_score,
            "average_change_per_scan": round(avg_delta_per_scan, 2),
            "estimated_scans_until_critical": round(scans_until_critical, 1),
            "note": "Linear projection based on recent scan history - not a guarantee, just a trend signal."
        }