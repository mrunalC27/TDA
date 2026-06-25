from analyzers.repo_analyzer import RepositoryAnalyzer
from analyzers.complexity_analyzer import ComplexityAnalyzer
from analyzers.maintainability_analyzer import MaintainabilityAnalyzer
from analyzers.dead_code_analyzer import DeadCodeAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer
from analyzers.dependency_analyzer import DependencyAnalyzer
from scoring.health_score import HealthScoreCalculator
from ai.gemini_summary import GeminiSummary
from ai.remediation_roadmap import RemediationRoadmap
from core.repository_profiler import RepositoryProfiler
from core.coverage_engine import CoverageEngine
from analyzers.javascript.npm_audit_analyzer import NPMAuditAnalyzer
from analyzers.javascript.complexity_analyzer import JSComplexityAnalyzer
from analyzers.javascript.maintainability_analyzer import JSMaintainabilityAnalyzer
from analyzers.javascript.security_analyzer import JSSecurityAnalyzer
from analyzers.javascript.dead_code_analyzer import JSDeadCodeAnalyzer
from analyzers.universal_complexity_analyzer import UniversalComplexityAnalyzer
from analyzers.code_churn_analyzer import CodeChurnAnalyzer
from utils.github_clone import clone_repository, cleanup_repository, fetch_full_history
from analyzers.duplication_analyzer import DuplicationAnalyzer
from analyzers.test_presence_analyzer import TestPresenceAnalyzer
from analyzers.dependency_rot_analyzer import DependencyRotAnalyzer
from analyzers.loop_and_query_analyzer import LoopAndQueryAnalyzer
from analyzers.secrets_analyzer import SecretsAnalyzer
from analyzers.backdoor_pattern_analyzer import BackdoorPatternAnalyzer
from analyzers.endpoint_security_analyzer import EndpointSecurityAnalyzer
from analyzers.contributor_analyzer import ContributorAnalyzer
from analyzers.pr_maturity_analyzer import PRMaturityAnalyzer
from core.scan_history_store import save_scan
from analyzers.trend_analyzer import TrendAnalyzer
from ai.architecture_evaluator import ArchitectureEvaluator


def run_analysis(repo_url, progress_callback=None):

    def report(step_message):

        if progress_callback:
            progress_callback(step_message)

    from utils.github_clone import get_latest_commit_hash
    from core.scan_history_store import get_full_result_cache, save_full_result_cache

    report("Checking for cached results...")

    commit_hash = get_latest_commit_hash(repo_url)

    if commit_hash:

        cached = get_full_result_cache(repo_url, commit_hash)

        if cached:

            report("Found cached result for this commit - returning instantly.")
            cached["_from_cache"] = True
            return cached

    repo_path = None

    try:

        report("Cloning repository...")
        repo_path = clone_repository(repo_url)

        report("Fetching commit history...")
        fetch_full_history(repo_path)

        repo_analyzer = RepositoryAnalyzer(repo_path)
        profiler = RepositoryProfiler(repo_path)
        profile = profiler.analyze()

        coverage_engine = CoverageEngine()
        coverage = coverage_engine.evaluate(profile)

        language = profile["primary_language"]

        if language == "JavaScript":
            dead_code = JSDeadCodeAnalyzer(repo_path)
            security = JSSecurityAnalyzer(repo_path)
            dependency = NPMAuditAnalyzer(repo_path)
        else:
            dead_code = DeadCodeAnalyzer(repo_path)
            security = SecurityAnalyzer(repo_path)
            dependency = DependencyAnalyzer(repo_path)

        roadmap_generator = RemediationRoadmap()

        report("Evaluating architecture pattern...")

        try:
            architecture_evaluator = ArchitectureEvaluator(repo_path)
            architecture_evaluation = architecture_evaluator.evaluate(profile)
        except Exception as e:
            architecture_evaluation = f"Architecture Evaluation Unavailable: {str(e)}"

        repo_results = repo_analyzer.analyze()

        report("Analyzing code complexity and maintainability...")

        if language == "Python":

            complexity = ComplexityAnalyzer(repo_path)
            maintainability = MaintainabilityAnalyzer(repo_path)

            complexity_summary = complexity.summary()
            hotspots = complexity.hotspots()
            maint_summary = maintainability.summary()
            worst_files = maintainability.worst_files()

            dead_summary = dead_code.summary()
            dead_findings = dead_code.top_findings()
            security_summary = security.summary()
            security_findings = security.top_findings()

        elif language == "JavaScript":

            complexity = JSComplexityAnalyzer(repo_path)
            maintainability = JSMaintainabilityAnalyzer(repo_path)

            complexity_summary = complexity.summary()
            hotspots = complexity.hotspots()
            maint_summary = maintainability.summary()
            worst_files = maintainability.worst_files()

            dead_summary = {"status": "Not Supported Yet"}
            dead_findings = []
            security_summary = security.summary()
            security_findings = security.top_findings()

        else:

            complexity = UniversalComplexityAnalyzer(repo_path)
            complexity_summary = complexity.summary()
            hotspots = complexity.hotspots()

            if not complexity_summary:
                complexity_summary = {"status": "No Analyzable Code Found"}

            maint_summary = {"status": "Not Supported"}
            worst_files = []
            dead_summary = {"status": "Not Supported Yet"}
            dead_findings = []
            security_summary = {"status": "Not Supported"}
            security_findings = []

        report("Checking dependencies...")
        dependency_summary = dependency.summary()
        dependency_findings = dependency.top_findings()

        report("Analyzing code churn...")
        churn = CodeChurnAnalyzer(repo_path)
        churn_summary = churn.summary()
        churn_hotspots = churn.hotspots()

        report("Detecting code duplication...")
        duplication = DuplicationAnalyzer(repo_path)
        duplication_summary = duplication.summary()
        duplication_findings = duplication.top_findings()

        report("Estimating test coverage...")
        test_presence = TestPresenceAnalyzer(repo_path)
        test_summary = test_presence.summary()
        untested_files = test_presence.untested_files()

        report("Checking dependency staleness...")
        dependency_rot = DependencyRotAnalyzer(repo_path, language)
        dependency_rot_summary = dependency_rot.summary()
        dependency_rot_findings = dependency_rot.top_findings()

        report("Scanning for risky loops and queries...")
        loop_query = LoopAndQueryAnalyzer(repo_path)
        loop_query_summary = loop_query.summary()
        loop_findings = loop_query.loop_findings()
        query_findings = loop_query.query_findings()

        report("Scanning for leaked secrets...")
        secrets = SecretsAnalyzer(repo_path)
        secrets_summary = secrets.summary()
        secrets_findings = secrets.top_findings()

        report("Scanning for backdoor patterns...")
        backdoor = BackdoorPatternAnalyzer(repo_path)
        backdoor_summary = backdoor.summary()
        backdoor_findings = backdoor.top_findings()

        report("Checking endpoint security...")
        endpoint_security = EndpointSecurityAnalyzer(repo_path)
        endpoint_summary = endpoint_security.summary()
        endpoint_findings = endpoint_security.top_findings()

        report("Analyzing contributors...")
        contributor = ContributorAnalyzer(repo_path)
        contributor_summary = contributor.summary()
        developer_efficiency = contributor.developer_efficiency()
        knowledge_silos = contributor.knowledge_silos()
        large_commits = contributor.large_commits()

        high_risk_files = list({
            h.get("file", "") for h in hotspots
        } | {
            h.get("file", "") for h in churn_hotspots
        })

        debt_contribution = contributor.cross_reference_debt(high_risk_files)

        report("Checking pull request history...")
        pr_maturity = PRMaturityAnalyzer(repo_url)
        pr_maturity_summary = pr_maturity.summary()
        pr_maturity_findings = pr_maturity.top_findings()

        report("Calculating health score...")
        calculator = HealthScoreCalculator()

        try:

            health = calculator.calculate(
                complexity_summary,
                maint_summary,
                dead_summary,
                security_summary,
                dependency_summary,
                coverage
            )

        except Exception as e:

            health = {
                "health_score": "N/A",
                "status": "Calculation Error",
                "confidence": "Low",
                "reason": str(e)
            }

        report_data = {
            "health": health,
            "repository": repo_results,
            "complexity": complexity_summary,
            "maintainability": maint_summary,
            "dead_code": dead_summary,
            "security": security_summary,
            "dependency": dependency_summary
        }

        report("Generating AI summary...")

        try:
            gemini = GeminiSummary()
            summary = gemini.generate(report_data)
        except Exception as e:
            summary = f"AI Summary Unavailable: {str(e)}"

        report("Generating remediation roadmap...")

        try:
            roadmap = roadmap_generator.generate(report_data)
        except Exception as e:
            roadmap = f"Roadmap Unavailable: {str(e)}"

        report("Saving scan history...")

        try:

            save_scan(
                repo_url, profile, health, complexity_summary, maint_summary,
                dead_summary, security_summary, dependency_summary,
                duplication_summary, secrets_summary, backdoor_summary,
                endpoint_summary, commit_hash=commit_hash
            )

        except Exception:
            pass

        try:

            trend = TrendAnalyzer(repo_url)
            trend_summary = trend.trend_summary()
            trend_timeline = trend.trend_timeline()
            debt_prediction = trend.debt_prediction()

        except Exception as e:

            trend_summary = {"status": "Trend Analysis Unavailable", "reason": str(e)}
            trend_timeline = []
            debt_prediction = {"status": "Debt Prediction Unavailable", "reason": str(e)}

        if language == "Python":
            capability = {"Complexity": True, "Maintainability": True, "Dead Code": True, "Security": True, "Dependencies": True}
        elif language == "JavaScript":
            capability = {"Complexity": True, "Maintainability": True, "Dead Code": False, "Security": True, "Dependencies": True}
        else:
            capability = {"Complexity": True, "Maintainability": False, "Dead Code": False, "Security": True, "Dependencies": False}

        final_result = {
            "health": health,
            "ai_summary": summary,
            "ai_roadmap": roadmap,
            "architecture_evaluation": architecture_evaluation,
            "repository": repo_results,
            "profile": profile,
            "coverage": coverage,
            "capability": capability,
            "complexity": {"summary": complexity_summary, "hotspots": hotspots},
            "maintainability": {"summary": maint_summary, "worst_files": worst_files},
            "dead_code": {"summary": dead_summary, "findings": dead_findings},
            "security": {"summary": security_summary, "findings": security_findings},
            "dependency": {"summary": dependency_summary, "findings": dependency_findings},
            "churn": {"summary": churn_summary, "hotspots": churn_hotspots},
            "duplication": {"summary": duplication_summary, "findings": duplication_findings},
            "test_presence": {"summary": test_summary, "untested_files": untested_files},
            "dependency_rot": {"summary": dependency_rot_summary, "findings": dependency_rot_findings},
            "loop_query": {"summary": loop_query_summary, "loops": loop_findings, "queries": query_findings},
            "secrets": {"summary": secrets_summary, "findings": secrets_findings},
            "backdoor": {"summary": backdoor_summary, "findings": backdoor_findings},
            "endpoint_security": {"summary": endpoint_summary, "findings": endpoint_findings},
            "contributor": {
                "summary": contributor_summary,
                "developer_efficiency": developer_efficiency,
                "knowledge_silos": knowledge_silos,
                "large_commits": large_commits,
                "debt_contribution": debt_contribution
            },
            "pr_maturity": {"summary": pr_maturity_summary, "findings": pr_maturity_findings},
            "trend": {"summary": trend_summary, "timeline": trend_timeline, "prediction": debt_prediction}
        }

        try:

            save_full_result_cache(repo_url, commit_hash, final_result)
            print(f"CACHE SAVE: repo_url={repo_url} commit_hash={commit_hash}")

        except Exception as e:
            print(f"CACHE SAVE FAILED: {e}")

        return final_result

    finally:

        cleanup_repository(repo_path)