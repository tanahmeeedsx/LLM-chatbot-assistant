<div align="center">

# ⚡ Kleos — AI DevOps Assistant

### Investigate CI/CD failures. Understand logs. Find the evidence.

An MCP-powered AI DevOps assistant that connects a local LLM to GitHub Actions data to help investigate failed workflows, inspect job logs, and understand deployment issues.

<br/>

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge&logo=ollama&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Tool_Integration-6C5CE7?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active_Development-orange?style=for-the-badge)

**Local AI · Model-powered reasoning · MCP tools · Read-only investigation**

</div>

---

## 📌 Overview

Kleos is a local AI DevOps assistant designed to make GitHub Actions troubleshooting easier. It combines an Ollama-hosted language model with a Model Context Protocol (MCP) server that retrieves workflow information and analyzes selected job-log findings.

Instead of relying only on generic AI explanations, Kleos can use actual GitHub Actions data to investigate failures and distinguish confirmed evidence from warnings or possible causes.

> **Project status:** The command-line agent and GitHub Actions investigation tools are under active development. A dedicated chatbot interface and additional features are planned.

## ✨ Features

- **Workflow inspection** — Retrieve recent GitHub Actions workflow runs.
- **Job and step analysis** — Inspect job status, conclusions, and individual steps.
- **Log findings** — Extract selected error and warning messages from job logs.
- **AI-assisted investigation** — Use a local LLM to interpret tool results and explain what the evidence shows.
- **Root-cause investigation** — Combine run metadata, failed steps, and selected log findings to help identify likely causes.
- **Local model execution** — Use Ollama with `qwen2.5:1.5b`.
- **MCP integration** — Expose GitHub investigation capabilities as tools the agent can call.
- **Read-only by design** — No workflow reruns, repository writes, deployments, or cloud resource changes.

## 🧰 Tech Stack

<div align="center">

<a href="https://www.python.org/"><img src="https://skillicons.dev/icons?i=python" height="48" alt="Python"/></a>
<a href="https://github.com/ollama/ollama"><img src="https://img.shields.io/badge/Ollama-Local_Model-black?style=flat-square&logo=ollama" height="28" alt="Ollama"/></a>
<a href="https://github.com/modelcontextprotocol/python-sdk"><img src="https://img.shields.io/badge/Model_Context_Protocol-MCP-6C5CE7?style=flat-square" height="28" alt="MCP"/></a>
<a href="https://cli.github.com/"><img src="https://img.shields.io/badge/GitHub_CLI-181717?style=flat-square&logo=github" height="28" alt="GitHub CLI"/></a>
<a href="https://docs.github.com/en/actions"><img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" height="28" alt="GitHub Actions"/></a>

</div>

| Technology | Purpose |
|---|---|
| Python | Agent logic and investigation tools |
| Ollama | Runs the local language model |
| Qwen 2.5 1.5B | Natural-language reasoning and tool selection |
| MCP Python SDK | Connects the agent to external tools |
| GitHub CLI (`gh`) | Authenticated access to GitHub Actions data |
| Requests | Sends requests to the Ollama API |

## 🏗️ Architecture

```mermaid
flowchart TD
    U["User"] --> A["Kleos Agent<br/>Python"]
    A <--> L["Ollama API<br/>Qwen 2.5 1.5B"]
    A <--> M["MCP Client"]
    M <--> S["MCP Server<br/>Python"]
    S --> G["GitHub CLI"]
    G --> R["GitHub Actions API"]
    R --> D["Runs, Jobs, Steps<br/>and Job Logs"]
    D --> S
    S --> M
    M --> A
    A --> O["Evidence-based<br/>Investigation Results"]
