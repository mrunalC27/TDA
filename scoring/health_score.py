class HealthScoreCalculator:

    def calculate(
        self,
        complexity,
        maintainability,
        dead_code,
        security,
        dependency,
        coverage


    ):
        # confidence = "High"
        # if not coverage["supported"]:

        #     return {

        #         "health_score": "N/A",

        #         "status": "Incomplete Analysis",

        #         "confidence": "Low"
        #     }
        confidence = "High"

        if not coverage["supported"]:

            confidence = "Low"

        elif (
            "average_maintainability"
            not in maintainability
        ):

            confidence = "Medium"

        score = 100

        avg_complexity = complexity.get(
            "average_complexity",
            0
        )
        high_risk = complexity.get(
            "high_risk_files",
            0
        )
        if high_risk > 10:

            score -= 30

        elif high_risk > 5:

            score -= 20

        elif high_risk > 2:

            score -= 10

        elif avg_complexity > 10:
            score -= 20

        elif avg_complexity > 5:
            score -= 10

        maint_score = maintainability.get(
            "average_maintainability",
            100
        )

        if maint_score < 40:
            score -= 30

        elif maint_score < 65:
            score -= 20

        elif maint_score < 85:
            score -= 10


        dead_items = dead_code.get(
            "total_dead_code",
            0
        )

        if dead_items > 30:
            score -= 15

        elif dead_items > 15:
            score -= 10

        elif dead_items > 5:
            score -= 5


        score -= (
            security.get("high", 0) * 15
        )

        score -= (
            security.get("medium", 0) * 7
        )

        score -= (
            security.get("low", 0) * 3
        )


        dep_penalty = min(
            dependency.get(
                "vulnerabilities",
                0
            ) * 3,
            15
        )

        if dependency.get("status") == "Audit Failed":
            score -= 10

        score -= dep_penalty

        score = max(score, 0)

        if score >= 80:

            status = "Healthy"

        elif score >= 60:

            status = "Moderate Debt"

        elif score >= 40:

            status = "High Debt"

        else:

            status = "Critical"

        return {
            "health_score": score,
            "status": status,
            "confidence": confidence
        }