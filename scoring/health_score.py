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

        confidence = "High"

        if not coverage["supported"]:

            confidence = "Low"

        elif (
            "average_maintainability"
            not in maintainability
        ):

            confidence = "Medium"

        score = 100

        breakdown = {}

        avg_complexity = complexity.get(
            "average_complexity",
            0
        )
        high_risk = complexity.get(
            "high_risk_functions",
            complexity.get("high_risk_files", 0)
        )

        complexity_penalty = 0

        if high_risk > 10:

            complexity_penalty = 30

        elif high_risk > 5:

            complexity_penalty = 20

        elif high_risk > 2:

            complexity_penalty = 10

        elif avg_complexity > 10:
            complexity_penalty = 20

        elif avg_complexity > 5:
            complexity_penalty = 10

        score -= complexity_penalty
        breakdown["complexity"] = complexity_penalty

        maint_score = maintainability.get(
            "average_maintainability",
            100
        )

        maintainability_penalty = 0

        if maint_score < 40:
            maintainability_penalty = 30

        elif maint_score < 65:
            maintainability_penalty = 20

        elif maint_score < 85:
            maintainability_penalty = 10

        score -= maintainability_penalty
        breakdown["maintainability"] = maintainability_penalty

        dead_items = dead_code.get(
            "total_dead_code",
            0
        )

        dead_code_penalty = 0

        if dead_items > 30:
            dead_code_penalty = 15

        elif dead_items > 15:
            dead_code_penalty = 10

        elif dead_items > 5:
            dead_code_penalty = 5

        score -= dead_code_penalty
        breakdown["dead_code"] = dead_code_penalty

        security_penalty = (
            security.get("high", 0) * 15
            + security.get("medium", 0) * 4
        )

        security_penalty = min(security_penalty, 40)

        score -= security_penalty
        breakdown["security"] = security_penalty

        dep_penalty = min(
            dependency.get(
                "vulnerabilities",
                0
            ) * 3,
            15
        )

        if dependency.get("status") == "Audit Failed":
            dep_penalty += 10

        score -= dep_penalty
        breakdown["dependency"] = dep_penalty

        total_penalty = 100 - score

        capped_penalty = min(total_penalty, 75)

        breakdown["capped_overflow"] = total_penalty - capped_penalty

        score = 100 - capped_penalty

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
            "confidence": confidence,
            "breakdown": breakdown
        }