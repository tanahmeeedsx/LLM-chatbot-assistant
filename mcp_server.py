import logging
logging.basicConfig(level=logging.WARNING, stream=__import__("sys").stderr)
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Kleos")

PROJECT_DIR = Path(__file__).resolve().parent
IGNORED_DIRS = {".git", ".venv", "__pycache__"}


@mcp.tool()
def list_project_files() -> list[str]:
    """List files and folders in the Kleos project directory."""
    items = []

    for item in sorted(PROJECT_DIR.iterdir()):
        if item.name in IGNORED_DIRS:
            continue

        name = item.name + ("/" if item.is_dir() else "")
        items.append(name)

    return items


@mcp.tool()
def get_project_info() -> dict:
    """Get basic information about the Kleos project."""
    files = [
        item for item in PROJECT_DIR.iterdir()
        if item.name not in IGNORED_DIRS and item.is_file()
    ]

    folders = [
        item for item in PROJECT_DIR.iterdir()
        if item.name not in IGNORED_DIRS and item.is_dir()
    ]

    return {
        "project_name": "Kleos",
        "project_directory": str(PROJECT_DIR),
        "file_count": len(files),
        "folder_count": len(folders),
    }



@mcp.tool()
def get_github_workflow_runs(limit: int = 5) -> dict:
    """Read recent GitHub Actions workflow runs for the DevSecOps Agent repository."""
    import json
    import subprocess

    if not 1 <= limit <= 20:
        return {"error": "limit must be between 1 and 20"}

    command = [
        "gh", "run", "list",
        "-R", "tanahmeeedsx/devsecops-agent",
        "--workflow", "DevSecOps Agent CI/CD",
        "--limit", str(limit),
        "--json", "databaseId,displayTitle,status,conclusion,headBranch,event,createdAt,updatedAt,url",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"error": "GitHub CLI request timed out"}
    except OSError as error:
        return {"error": f"Could not run GitHub CLI: {error}"}

    if result.returncode != 0:
        return {
            "error": "GitHub CLI request failed",
            "details": result.stderr.strip()[:2000],
        }

    try:
        runs = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "GitHub CLI returned invalid JSON"}

    return {
        "repository": "tanahmeeedsx/devsecops-agent",
        "workflow": "DevSecOps Agent CI/CD",
        "count": len(runs),
        "runs": runs,
    }



@mcp.tool()
def get_github_run_jobs(run_id: int) -> dict:
    """Read job statuses and step results for a GitHub Actions run in the DevSecOps Agent repository."""
    import json
    import subprocess

    if run_id <= 0:
        return {"error": "run_id must be a positive integer"}

    command = [
        "gh", "api",
        f"repos/tanahmeeedsx/devsecops-agent/actions/runs/{run_id}/jobs",
        "--jq", "{total_count: .total_count, jobs: [.jobs[] | {id: .id, name: .name, status: .status, conclusion: .conclusion, steps: [.steps[]? | {name: .name, status: .status, conclusion: .conclusion, number: .number}]}]}",
    ]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=30, check=False
        )
    except subprocess.TimeoutExpired:
        return {"error": "GitHub CLI request timed out"}
    except OSError as error:
        return {"error": f"Could not run GitHub CLI: {error}"}

    if result.returncode != 0:
        return {
            "error": "GitHub API request failed",
            "details": result.stderr.strip()[:2000],
        }

    try:
        return {
            "repository": "tanahmeeedsx/devsecops-agent",
            "run_id": run_id,
            **json.loads(result.stdout),
        }
    except json.JSONDecodeError:
        return {"error": "GitHub API returned invalid JSON"}



@mcp.tool()
def get_github_job_log_findings(job_id: int) -> dict:
    """Return a limited, classified set of GitHub Actions log findings."""
    import re
    import subprocess

    if job_id <= 0:
        return {"error": "job_id must be a positive integer"}

    command = [
        "gh", "api",
        f"repos/tanahmeeedsx/devsecops-agent/actions/jobs/{job_id}/logs",
    ]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=45, check=False
        )
    except subprocess.TimeoutExpired:
        return {"error": "GitHub log request timed out"}
    except OSError as error:
        return {"error": f"Could not run GitHub CLI: {error}"}

    if result.returncode != 0:
        return {
            "error": "GitHub log request failed",
            "details": result.stderr.strip()[:1000],
        }

    sensitive = re.compile(
        r"(?i)\b(token|password|passwd|secret|authorization|api[_ -]?key|private[_ -]?key)\b(\s*[:=]\s*)\S+"
    )

    def redact(line: str) -> str:
        line = sensitive.sub(r"\1\2[REDACTED]", line)
        line = re.sub(r"(?i)Bearer\s+\S+", "Bearer [REDACTED]", line)
        line = re.sub(r"\bgh[pousr]_[A-Za-z0-9_]+\b", "[REDACTED_TOKEN]", line)
        return line[:500]

    findings = []
    seen = set()

    # Prefer explicit GitHub Actions annotations over keyword matching.
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        annotation = re.search(r"##\[(warning|error)\](.*)", line, re.I)
        if annotation:
            severity = annotation.group(1).lower()
            message = annotation.group(2).strip()
        elif re.search(r"\b(deprecated|deprecation warning)\b", line, re.I):
            severity = "warning"
            message = line
        elif re.search(
            r"\bWARNING:\s+Running pip as the ['\"]root['\"] user\b",
            line, re.I
        ):
            severity = "warning"
            message = line
        elif re.search(
            r"\b(fatal error|build failed|deployment failed|"
            r"missing repository variable|missing required (?:variable|secret)|"
            r"required variable .+ (?:not set|missing)|"
            r"access denied|permission denied|"
            r"validation failed|invalid configuration)\b",
            line, re.I
        ):
            severity = "error"
            message = line
        else:
            # Avoid treating substrings in package names such as
            # libgpg-error0 as actual error messages.
            continue

        # A generic exit-code annotation is a symptom, not the root cause.
        if re.fullmatch(
            r"Process completed with exit code \d+\.", message, re.I
        ):
            continue

        clean_message = redact(message)
        key = (severity, clean_message)
        if key in seen:
            continue
        seen.add(key)

        findings.append({
            "severity": severity,
            "message": clean_message,
            "source": "GitHub Actions annotation" if annotation else "log pattern",
        })

        if len(findings) >= 20:
            break

    return {
        "repository": "tanahmeeedsx/devsecops-agent",
        "job_id": job_id,
        "finding_count": len(findings),
        "findings": findings,
        "note": (
            "Findings are selected by explicit annotations or narrow log patterns. "
            "This is not a complete log review; verify context before deciding "
            "whether a finding is actionable. Secret redaction is best-effort."
        ),
    }


@mcp.tool()
def investigate_github_actions_run(run_id: int) -> dict:
    """Investigate a GitHub Actions run using read-only API calls and filtered job logs."""
    import json
    import subprocess

    repository = "tanahmeeedsx/devsecops-agent"

    if run_id <= 0:
        return {"error": "run_id must be a positive integer"}

    def run_gh(command: list[str], timeout: int = 30) -> dict:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True,
                timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired:
            return {"error": "GitHub CLI request timed out"}
        except OSError as error:
            return {"error": f"Could not run GitHub CLI: {error}"}

        if result.returncode != 0:
            return {
                "error": "GitHub CLI request failed",
                "details": result.stderr.strip()[:1000],
            }

        try:
            return {"data": json.loads(result.stdout)}
        except json.JSONDecodeError:
            return {"error": "GitHub CLI returned invalid JSON"}

    run_result = run_gh([
        "gh", "api", f"repos/{repository}/actions/runs/{run_id}",
        "--jq",
        "{id: .id, name: .name, display_title: .display_title, "
        "status: .status, conclusion: .conclusion, head_branch: .head_branch, "
        "event: .event, html_url: .html_url}"
    ])
    if "error" in run_result:
        return {"stage": "run_metadata", **run_result}

    jobs_result = run_gh([
        "gh", "api", f"repos/{repository}/actions/runs/{run_id}/jobs",
        "--jq",
        "{total_count: .total_count, jobs: [.jobs[] | "
        "{id: .id, name: .name, status: .status, conclusion: .conclusion, "
        "steps: [.steps[]? | {name: .name, status: .status, "
        "conclusion: .conclusion, number: .number}]}]}"
    ])
    if "error" in jobs_result:
        return {"stage": "jobs", **jobs_result}

    run_data = run_result["data"]
    jobs_data = jobs_result["data"]
    jobs = jobs_data.get("jobs", [])

    failed_jobs = [
        job for job in jobs
        if job.get("conclusion") in {"failure", "timed_out", "action_required"}
        or any(
            step.get("conclusion") in {"failure", "timed_out", "action_required"}
            for step in job.get("steps", [])
        )
    ]

    log_reports = []
    # Analyze only failed jobs; reuse the existing filtered log findings tool.
    for job in failed_jobs[:10]:
        report = get_github_job_log_findings(job["id"])
        log_reports.append({
            "job_id": job["id"],
            "job_name": job["name"],
            "finding_count": report.get("finding_count", 0),
            "findings": report.get("findings", []),
            **(
                {"error": report["error"], "details": report.get("details", "")}
                if "error" in report else {}
            ),
            "note": report.get("note", ""),
        })

    failed_steps = [
        {
            "job_id": job.get("id"),
            "job_name": job.get("name"),
            "step_name": step.get("name"),
            "conclusion": step.get("conclusion"),
        }
        for job in jobs
        for step in job.get("steps", [])
        if step.get("conclusion") in {"failure", "timed_out", "action_required"}
    ]

    all_findings = [
        finding
        for report in log_reports
        for finding in report.get("findings", [])
    ]
    error_findings = [
        finding for finding in all_findings
        if finding.get("severity") == "error"
    ]
    warning_findings = [
        finding for finding in all_findings
        if finding.get("severity") == "warning"
    ]

    if run_data.get("conclusion") == "failure" and not jobs:
        summary = (
            "The workflow run failed before any jobs were created. "
            "This is consistent with a workflow-level configuration or validation "
            "issue, but the exact cause is not confirmed by the available job data. "
            "No job logs are available; inspect the workflow file and run-level details."
        )
    elif error_findings:
        summary = (
            "Error-pattern findings were detected in failed-job logs. "
            "Use the listed messages as evidence; confirm their surrounding "
            "context before treating them as the root cause."
        )
    elif failed_steps and not all_findings:
        summary = (
            "Failed steps were found, but no matching error or warning patterns "
            "were extracted. The root cause remains undetermined from these findings."
        )
    elif run_data.get("conclusion") == "success" and not failed_steps:
        summary = (
            "The run completed successfully and no failed steps were reported. "
            "No failure root cause can be established from the run status."
        )
    elif failed_steps:
        summary = (
            "Failed steps were found. Review the listed step names and job log "
            "reports; this result does not assert a root cause unless log evidence "
            "has been successfully retrieved and analyzed."
        )
    else:
        summary = (
            "The run has no reported failed steps, but its status is not a confirmed "
            "success. Check the run status and any log retrieval errors."
        )

    return {
        "repository": repository,
        "run": run_data,
        "job_count": len(jobs),
        "jobs": jobs,
        "failed_steps": failed_steps,
        "log_reports": log_reports,
        "finding_summary": {
            "error_count": len(error_findings),
            "warning_count": len(warning_findings),
            "errors": error_findings,
            "warnings": warning_findings,
        },
        "summary": summary,
        "read_only": True,
        "limitations": [
            "This version reports run metadata and failed steps.",
            "Log findings use selected annotations and patterns; they are not a complete log review.",
            "No workflow reruns, repository writes, deployments, or cloud changes are performed.",
        ],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
