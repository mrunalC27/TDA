import streamlit as st
import pandas as pd
from utils.github_clone import clone_repository

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
from analyzers.javascript.npm_audit_analyzer import (
    NPMAuditAnalyzer
)
from analyzers.javascript.complexity_analyzer import (
    JSComplexityAnalyzer
)
from analyzers.javascript.maintainability_analyzer import (
    JSMaintainabilityAnalyzer
)
from analyzers.javascript.security_analyzer import (
    JSSecurityAnalyzer
)
from analyzers.javascript.dead_code_analyzer import (
    JSDeadCodeAnalyzer
)
from analyzers.universal_complexity_analyzer import (
    UniversalComplexityAnalyzer
)
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
from core.scan_history_store import save_scan, init_db
from analyzers.trend_analyzer import TrendAnalyzer
from ai.architecture_evaluator import ArchitectureEvaluator
st.title("Technical Debt Analyzer")

repo_url = st.text_input(
    "Enter GitHub Repository URL"
)

st.caption(
    "Large repositories (1000+ commits or files) may take 1-3 minutes to analyze. "
    "Please keep this tab open until analysis completes."
)

if st.button("Analyze Repository"):

    if not repo_url.strip():

        st.error(
            "Please enter a GitHub URL"
        )

        st.stop()

    try:

        with st.spinner(
            "Cloning Repository..."
        ):

            repo_path = clone_repository(
                repo_url
            )
        with st.spinner(
            "Fetching commit history for churn analysis..."
        ):

            history_available = fetch_full_history(repo_path)

        repo_analyzer = RepositoryAnalyzer(
            repo_path
        )
        profiler = RepositoryProfiler(
            repo_path
        )
        profile = profiler.analyze()

        coverage_engine = CoverageEngine()

        coverage = coverage_engine.evaluate(
            profile
        )

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

        try:

            architecture_evaluator = ArchitectureEvaluator(repo_path)

            architecture_evaluation = (
                architecture_evaluator.evaluate(profile)
            )

        except Exception as e:

            architecture_evaluation = (
                f"Architecture Evaluation Unavailable: {str(e)}"
            )

        repo_results = repo_analyzer.analyze()

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

        dependency_summary = dependency.summary()
        dependency_findings = dependency.top_findings()

        print("CHECKPOINT: dependency done")

        churn = CodeChurnAnalyzer(repo_path)
        churn_summary = churn.summary()
        churn_hotspots = churn.hotspots()

        print("CHECKPOINT: churn done")

        duplication = DuplicationAnalyzer(repo_path)
        duplication_summary = duplication.summary()
        duplication_findings = duplication.top_findings()

        print("CHECKPOINT: duplication done")

        test_presence = TestPresenceAnalyzer(repo_path)
        test_summary = test_presence.summary()
        untested_files = test_presence.untested_files()

        print("CHECKPOINT: test_presence done")

        dependency_rot = DependencyRotAnalyzer(repo_path, language)
        dependency_rot_summary = dependency_rot.summary()
        dependency_rot_findings = dependency_rot.top_findings()

        print("CHECKPOINT: dependency_rot done")

        loop_query = LoopAndQueryAnalyzer(repo_path)
        loop_query_summary = loop_query.summary()
        loop_findings = loop_query.loop_findings()
        query_findings = loop_query.query_findings()

        print("CHECKPOINT: loop_query done")

        secrets = SecretsAnalyzer(repo_path)
        secrets_summary = secrets.summary()
        secrets_findings = secrets.top_findings()

        print("CHECKPOINT: secrets done")

        backdoor = BackdoorPatternAnalyzer(repo_path)
        backdoor_summary = backdoor.summary()
        backdoor_findings = backdoor.top_findings()

        print("CHECKPOINT: backdoor done")

        endpoint_security = EndpointSecurityAnalyzer(repo_path)
        endpoint_summary = endpoint_security.summary()
        endpoint_findings = endpoint_security.top_findings()

        print("CHECKPOINT: endpoint_security done")

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

        print("CHECKPOINT: contributor done")

        pr_maturity = PRMaturityAnalyzer(repo_url)
        pr_maturity_summary = pr_maturity.summary()
        pr_maturity_findings = pr_maturity.top_findings()

        print("CHECKPOINT: pr_maturity done")

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
            
        report = {
            "health": health,
            "repository": repo_results,
            "complexity": complexity_summary,
            "maintainability": maint_summary,
            "dead_code": dead_summary,
            "security": security_summary,
            "dependency": dependency_summary
        }

        try:

            gemini = GeminiSummary()

            summary = gemini.generate(
                report
            )

        except Exception as e:

            summary = (
                f"AI Summary Unavailable: {str(e)}"
            )

        try:

            roadmap = (
                roadmap_generator.generate(
                    report
                )
            )

        except Exception as e:

            roadmap = (
                f"Roadmap Unavailable: {str(e)}"
            )
        try:

            save_scan(
                repo_url,
                profile,
                health,
                complexity_summary,
                maint_summary,
                dead_summary,
                security_summary,
                dependency_summary,
                duplication_summary,
                secrets_summary,
                backdoor_summary,
                endpoint_summary
            )

        except Exception as e:

            st.warning(f"Could not save scan history: {str(e)}")

        try:

            trend = TrendAnalyzer(repo_url)
            trend_summary = trend.trend_summary()
            trend_timeline = trend.trend_timeline()
            debt_prediction = trend.debt_prediction()

        except Exception as e:

            trend_summary = {"status": "Trend Analysis Unavailable", "reason": str(e)}
            trend_timeline = []
            debt_prediction = {"status": "Debt Prediction Unavailable", "reason": str(e)}


        st.success(
            "Analysis Complete"
        )
        st.subheader(
            "Overall Health Score"
        )

        st.json(
            health
        )

        st.subheader(
            "AI executive Summary"
        )
        st.markdown(
            summary
        )

        st.subheader(
            "AI Remediation Roadmap"
        )
        st.markdown(
            roadmap
        )

        st.subheader(
            "Repository Metadata"
        )

        st.json(repo_results)

        st.subheader(
            "Complexity Summary"
        )

        st.json(complexity_summary)

        st.subheader(
            "Maintainability Summary"
        )

        st.json(maint_summary)

        st.subheader(
            "Top Complexity Hotspots"
        )

        st.dataframe(pd.DataFrame(hotspots))

        st.subheader(
            "Lowest Maintainability Files"
        )

        st.dataframe(pd.DataFrame(worst_files))

        st.subheader(
            "Potential Dead Code Summary"
        )

        st.json(
            dead_summary
        )

        st.subheader(
            "Potential Dead Code Findings"
        )

        if dead_findings:

            st.dataframe(
                pd.DataFrame(dead_findings)
            )

        else:

            st.info(
                "Dead code analysis not available for this language yet."
            )

        st.subheader(
            "Security Summary"
        )

        st.json(
            security_summary
        )

        st.subheader(
            "Security Findings"
        )

        if security_findings:

            st.dataframe(
                pd.DataFrame(security_findings)
            )

        else:

            st.info(
                "Security analysis not available for this language yet."
            )

        st.subheader(
            "Dependency Summary"
        )

        st.json(
            dependency_summary
        )

        st.subheader(
            "Dependency Findings"
        )

        st.dataframe(pd.DataFrame(dependency_findings))

        st.subheader(
            "Repository Profile"
        )

        st.json(profile)

        st.subheader(
            "Analysis Coverage"
        )

        st.json(
            coverage
        )

        st.subheader(
            "Analysis Capability"
        )

        if language == "Python":

            capability = {

                "Complexity": True,
                "Maintainability": True,
                "Dead Code": True,
                "Security": True,
                "Dependencies": True
            }

        elif language == "JavaScript":

            capability = {

                "Complexity": True,
                "Maintainability": True,
                "Dead Code": False,
                "Security": True,
                "Dependencies": True
            }

        else:

            capability = {

                "Complexity": True,
                "Maintainability": False,
                "Dead Code": False,
                "Security": True,
                "Dependencies": False
            }

        st.json(capability)
        st.subheader("Code Churn Summary")
        st.json(churn_summary)

        st.subheader("Most Frequently Changed Files")
        st.dataframe(pd.DataFrame(churn_hotspots))

        st.subheader("Code Duplication Summary")
        st.json(duplication_summary)

        st.subheader("Duplicate Code Blocks")

        if duplication_findings and "status" not in duplication_findings[0]:
            st.dataframe(pd.DataFrame(duplication_findings))
        else:
            st.info("No duplication data available.")


        st.subheader("Test Coverage Estimate (Static)")
        st.json(test_summary)

        st.subheader("Source Files With No Matching Test Found")

        if untested_files:
            st.dataframe(pd.DataFrame(untested_files))
        else:
            st.info("Every source file appears to have a matching test file.")

        st.subheader("Dependency Staleness (Rot) Summary")
        st.json(dependency_rot_summary)

        st.subheader("Outdated Dependencies")

        if dependency_rot_findings:
            st.dataframe(pd.DataFrame(dependency_rot_findings))
        else:
            st.info("No dependency staleness data available.")


        st.subheader("Broken Loops & Unbounded Queries Summary")
        st.json(loop_query_summary)

        st.subheader("Risky Loop Findings")

        if loop_findings:
            st.dataframe(pd.DataFrame(loop_findings))
        else:
            st.info("No risky loop patterns found.")

        st.subheader("Unbounded Query Findings")

        if query_findings:
            st.dataframe(pd.DataFrame(query_findings))
        else:
            st.info("No unbounded query patterns found.")


        st.subheader("Leaked Secrets & Hardcoded Credentials Summary")
        st.json(secrets_summary)

        st.subheader("Secret/Credential Findings")

        if secrets_findings:
            st.dataframe(pd.DataFrame(secrets_findings))
        else:
            st.info("No leaked secrets or hardcoded credentials found.")


        st.subheader("Backdoor & Dangerous Pattern Summary")
        st.json(backdoor_summary)

        st.subheader("Backdoor & Dangerous Pattern Findings")

        if backdoor_findings:
            st.dataframe(pd.DataFrame(backdoor_findings))
        else:
            st.info("No backdoor or dangerous patterns found.")


        st.subheader("Open Endpoints & RBAC Summary")
        st.json(endpoint_summary)

        st.subheader("Endpoints Without Detected Auth")

        if endpoint_findings:
            st.dataframe(pd.DataFrame(endpoint_findings))
        else:
            st.info("No unprotected endpoints detected (or no routes found).")


        st.subheader("Contributor & Velocity Summary")
        st.json(contributor_summary)

        st.subheader("Developer Efficiency")

        if developer_efficiency:
            st.dataframe(pd.DataFrame(developer_efficiency))
        else:
            st.info("No contributor data available.")

        st.subheader("Debt Contribution Ratio")

        if debt_contribution:
            st.dataframe(pd.DataFrame(debt_contribution))
        else:
            st.info("No debt contribution data available.")

        st.subheader("Knowledge Silos (Files With Single Author)")

        if knowledge_silos:
            st.dataframe(pd.DataFrame(knowledge_silos))
        else:
            st.info("No knowledge silo files detected.")

        st.subheader("Large/High-Impact Commits")

        if large_commits:
            st.dataframe(pd.DataFrame(large_commits))
        else:
            st.info("No unusually large commits detected.")


        st.subheader("PR Maturity Index")
        st.json(pr_maturity_summary)

        st.subheader("Pull Request Review Findings")

        if pr_maturity_findings:
            st.dataframe(pd.DataFrame(pr_maturity_findings))
        else:
            st.info("No pull request data available.")


        st.subheader("Trend Analysis")
        st.json(trend_summary)

        if trend_timeline:
            st.dataframe(pd.DataFrame(trend_timeline))

        st.subheader("Debt Prediction")
        st.json(debt_prediction)

        st.subheader("AI Architecture Pattern Evaluation")
        st.markdown(architecture_evaluation)

    except Exception as e:

        st.error(
            f"Analysis Failed: {str(e)}"
        )
    finally:

        cleanup_repository(repo_path)