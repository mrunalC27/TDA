class CoverageEngine:

    SUPPORTED_LANGUAGES = {
        "Python",
        "JavaScript"
    }

    def evaluate(
        self,
        profile
    ):

        language = profile.get(
            "primary_language",
            "Unknown"
        )

        if language in self.SUPPORTED_LANGUAGES:

            return {
                "coverage": "Full",
                "language": language,
                "supported": True
            }

        return {
            "coverage": "Partial",
            "language": language,
            "supported": False
        }