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


st.title("Technical Debt Analyzer")

repo_url = st.text_input(
    "Enter GitHub Repository URL"
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

            complexity_summary = {"status": "Not Supported"}
            maint_summary = {"status": "Not Supported"}
            hotspots = []
            worst_files = []
            dead_summary = {"status": "Not Supported Yet"}
            dead_findings = []
            security_summary = {"status": "Not Supported"}
            security_findings = []

        dependency_summary = dependency.summary()
        dependency_findings = dependency.top_findings()

        calculator = HealthScoreCalculator()

        health = calculator.calculate(
            complexity_summary,
            maint_summary,
            dead_summary,
            security_summary,
            dependency_summary,
            coverage
        )

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

                "Complexity": False,
                "Maintainability": False,
                "Dead Code": False,
                "Security": True,
                "Dependencies": False
            }

        st.json(capability)

    except Exception as e:

        st.error(
            f"Analysis Failed: {str(e)}"
        )