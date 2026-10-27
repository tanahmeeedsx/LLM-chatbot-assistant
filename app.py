import asyncio
import json
import sys
from pathlib import Path

import streamlit as st
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from kleos_agent import (
    API_URL,
    MODEL,
    MAX_ROUNDS,
    SYSTEM_PROMPT,
    ask_ollama,
    convert_mcp_tools,
    format_tool_result,
)

APP_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Kleos | AI DevOps Chatbot Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.hero-heading {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #192b4d;
    --muted: #71809b;
    --blue: #4777f5;
    --purple: #8159ed;
    --line: #e6ebf5;
    --surface: #ffffff;
    --canvas: #f7f9fe;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}
.stApp {
    background: var(--canvas);
}
header[data-testid="stHeader"] {
    background: rgba(247,249,254,.94);
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.4rem;
}
.brand {
    display:flex;
    align-items:center;
    gap:12px;
    padding: 7px 4px 24px;
}
.brand-mark {
    width:48px;
    height:48px;
    border-radius:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-family:'Manrope',sans-serif;
    font-size:29px;
    font-weight:800;
    background:linear-gradient(140deg,#3988ff,#7652e9);
    box-shadow:0 7px 18px rgba(90,104,232,.2);
}
.brand-name {
    font:800 25px 'Manrope',sans-serif;
    letter-spacing:-1px;
    color:#192b4d;
    line-height:1.1;
}
.brand-sub {
    font-size:11px;
    color:#7a89a5;
    margin-top:4px;
}
.topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:13px 17px;
    margin-bottom:22px;
    border:1px solid var(--line);
    border-radius:16px;
    background:rgba(255,255,255,.9);
}
.topbar-label {
    font-size:12px;
    color:#71809b;
}
.pill {
    display:inline-flex;
    align-items:center;
    gap:7px;
    border:1px solid #e7ecf6;
    border-radius:999px;
    padding:7px 11px;
    background:#fff;
    color:#526482;
    font-size:11px;
    font-weight:600;
}
.dot {
    height:7px;width:7px;border-radius:50%;
    background:#20b981;display:inline-block;
}
.hero {
    padding:18px 2px 14px;
}
.hero h1 {
    font:800 clamp(27px,3vw,38px) 'Manrope',sans-serif;
    letter-spacing:-1.3px;
    line-height:1.2;
    margin:0 0 10px;
    color:#192b4d;
}
.gradient-text {
    background:linear-gradient(100deg,#397ef5,#8055e9);
    -webkit-background-clip:text;
    background-clip:text;
    color:transparent;
}
.hero p {
    color:#71809b;
    font-size:14px;
    line-height:1.75;
    max-width:680px;
    margin:0;
}
.section-label {
    color:#7b89a2;
    font-size:10px;
    text-transform:uppercase;
    letter-spacing:1.4px;
    font-weight:700;
    margin:14px 0 10px;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color:var(--line)!important;
    border-radius:16px!important;
    background:#fff;
}
/* Improve readability in the light theme */
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] span {
    color: #24395d;
}
div[data-testid="stSpinner"] p {
    color: #24395d !important;
    font-weight: 600;
}
.stButton button,
.stButton button p,
.stButton button span {
    color: #24395d !important;
    opacity: 1 !important;
}
div[data-testid="stChatMessage"] {
    background:#fff;
    border:1px solid var(--line);
    border-radius:16px;
    padding:15px 17px;
    margin-bottom:12px;
    box-shadow:0 3px 14px rgba(31,55,100,.025);
}
div[data-testid="stChatInput"] {
    border-color:#dce5f5!important;
    border-radius:16px!important;
    background:#fff!important;
}
div[data-testid="stChatInput"] textarea {
    font-size:14px!important;
}
.stButton button {
    border-radius:11px;
    border:1px solid #e2e9f7;
    color:#344c76;
    background:#fff;
    min-height:43px;
    font-weight:600;
    transition:all .18s ease;
}
.stButton button:hover {
    border-color:#a9bafa;
    color:#426cf0;
    background:#f7f8ff;
}
div[data-testid="stMetric"] {
    background:#fff;
    border:1px solid var(--line);
    padding:12px 14px;
    border-radius:14px;
}
div[data-testid="stMetricLabel"] {
    color:#71809b;
    font-size:11px;
}
div[data-testid="stMetricValue"] {
    color:#24395d;
    font-size:24px;
}
.info-card {
    background:#fff;
    border:1px solid var(--line);
    border-radius:15px;
    padding:16px;
    margin-bottom:12px;
}
.info-title {
    font-size:13px;
    font-weight:700;
    color:#23385d;
    margin-bottom:12px;
}
.tool-row {
    display:flex;
    gap:10px;
    align-items:flex-start;
    padding:10px 0;
    border-bottom:1px solid #f0f3f9;
}
.tool-row:last-child {border-bottom:0;padding-bottom:0}
.tool-icon {
    display:flex;align-items:center;justify-content:center;
    min-width:33px;height:33px;border-radius:10px;
    background:#edf3ff;color:#4777f5;font-size:15px;
}
.tool-name {font-size:11px;font-weight:700;color:#334a70;overflow-wrap:anywhere}
.tool-desc {font-size:10px;color:#8591a8;line-height:1.5;margin-top:3px}
.small-muted {font-size:11px;color:#8591a8;line-height:1.65}
.ready-card {
    border:1px solid #cdeee1;
    background:linear-gradient(135deg,#f0fbf6,#fff);
    border-radius:15px;
    padding:16px;
}
.ready-title {font-size:13px;font-weight:700;color:#188567;margin-bottom:5px}
.footer-note {
    text-align:center;
    color:#9aa5b8;
    font-size:10px;
    padding:12px 0 0;
}
[data-testid="stStatusWidget"] {
    border-radius:12px;
}
@media (max-width: 900px) {
    .topbar {flex-wrap:wrap}
    .hero h1 {font-size:28px}
}

/* Readable inline code and code blocks */
div[data-testid="stMarkdownContainer"] code {
    color: #145b87 !important;
    background: #eaf4ff !important;
    border: 1px solid #c9e2f8 !important;
    border-radius: 6px;
    padding: 0.12rem 0.32rem;
}
div[data-testid="stMarkdownContainer"] pre {
    background: #101a27 !important;
    border: 1px solid #29435a !important;
    border-radius: 10px;
    padding: 14px 16px !important;
}
div[data-testid="stMarkdownContainer"] pre code {
    color: #e2edf8 !important;
    background: transparent !important;
    border: 0 !important;
    padding: 0 !important;
}
div[data-testid="stCodeBlock"] {
    border: 1px solid #29435a !important;
    border-radius: 10px !important;
}
div[data-testid="stCodeBlock"] pre,
div[data-testid="stCodeBlock"] code {
    color: #e2edf8 !important;
    background: #101a27 !important;
}
.ready-card .small-muted,
.info-card .small-muted {
    color: #79bfff !important;
}


/* Kleos chat input: light blue with a gradient-matched focus state */
div[data-testid="stChatInput"] {
    background: #edf7ff !important;
    border: 1.5px solid #a9d9ff !important;
    border-radius: 16px !important;
    box-shadow: 0 3px 14px rgba(81, 160, 255, 0.10) !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #6c9fff !important;
    box-shadow: 0 0 0 3px rgba(108, 159, 255, 0.18) !important;
}
div[data-testid="stChatInput"] textarea {
    color: #193b60 !important;
    background: transparent !important;
    caret-color: #4777f5 !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #6489b3 !important;
    opacity: 1 !important;
}
div[data-testid="stChatInput"] button {
    color: #4777f5 !important;
}

</style>
""", unsafe_allow_html=True)


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "tool_activity" not in st.session_state:
        st.session_state.tool_activity = []
    if "quick_prompt" not in st.session_state:
        st.session_state.quick_prompt = ""


def reset_chat():
    st.session_state.messages = []
    st.session_state.tool_activity = []
    st.session_state.quick_prompt = ""


def logo():
    st.markdown("""
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">
        <span style="font-size:34px;line-height:1;color:white;">∞</span>
      </div>
      <div>
        <div class="brand-name">Kleos</div>
        <div class="brand-sub">AI DevOps Chatbot Assistant</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


async def run_kleos(user_text, previous_messages):
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(APP_DIR / "mcp_server.py")],
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(previous_messages)
    messages.append({"role": "user", "content": user_text})
    activities = []

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            tools = convert_mcp_tools(mcp_tools)

            for round_number in range(1, MAX_ROUNDS + 1):
                assistant_message = await asyncio.to_thread(
                    ask_ollama, messages, tools
                )
                messages.append(assistant_message)
                tool_calls = assistant_message.get("tool_calls", [])

                if not tool_calls:
                    answer = assistant_message.get("content", "")
                    history = messages[1:]
                    return answer, history, activities, len(activities)

                for call in tool_calls:
                    function = call.get("function", {})
                    name = function.get("name", "")
                    arguments = function.get("arguments", {})

                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            arguments = {}

                    try:
                        result = await session.call_tool(name, arguments)
                        output = format_tool_result(result)
                        activities.append({
                            "name": name,
                            "ok": not result.isError,
                            "details": str(arguments),
                        })
                    except Exception as error:
                        output = json.dumps({"error": str(error)})
                        activities.append({
                            "name": name,
                            "ok": False,
                            "details": str(error),
                        })

                    messages.append({"role": "tool", "content": output})

    return (
        "I reached the tool-call limit before completing the response. "
        "Please try a more specific question.",
        messages[1:],
        activities,
        0,
    )


init_state()

# Sidebar
with st.sidebar:
    logo()
    st.markdown('<div class="section-label">WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown("💬  **Chat**")
    st.markdown("◈  GitHub Actions")
    st.markdown("▣  Project insights")
    st.markdown("⚙️  Settings")
    st.markdown("---")
    st.markdown('<div class="section-label">YOUR ASSISTANT</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ready-card">
      <div class="ready-title">● &nbsp; Kleos is ready</div>
      <div class="small-muted">Ask about DevOps, troubleshoot CI/CD failures, review logs, and investigate deployments.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    if st.button("＋  New conversation", use_container_width=True):
        reset_chat()
        st.rerun()
    st.markdown('<div class="footer-note">Kleos · AI DevOps Chatbot Assistant<br>Powered by Ollama + MCP</div>', unsafe_allow_html=True)

main_col, side_col = st.columns([2.15, 1], gap="large")

with main_col:
    if not st.session_state.messages:
        st.markdown("""
        <div class="hero">
          <h1 class="hero-heading" style="display:flex;align-items:center;flex-wrap:wrap;column-gap:0;">
          Hello, I'm <span class="gradient-text">Kleos</span>
          <span aria-hidden="true" style="display:inline-flex;align-items:center;justify-content:center;font-size:60px;line-height:1;height:1em;transform:translateY(5px);margin-left:5px;flex-shrink:0;background:linear-gradient(90deg,#51D8FF,#6C9FFF,#B19AFF);-webkit-background-clip:text;background-clip:text;color:transparent;">∞</span>
        </h1>
          <p>Your AI DevOps Chatbot Assistant. Ask about GitHub Actions workflows,
          investigate failures, analyze logs, and get practical next steps.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">TRY ASKING</div>', unsafe_allow_html=True)
        quick_cols = st.columns(2)
        prompts = [
            ("↗", "Check workflow status", "Show me the latest GitHub Actions workflow runs."),
            ("⌕", "Investigate a failed run", "Investigate failed workflow run 40247918295 and explain the root cause."),
            ("▤", "Analyze job logs", "Analyze job logs for job ID 121340363051 and identify the real errors."),
            ("✧", "Explain a warning", "Explain the difference between a real deployment error and a deprecation warning."),
        ]
        for i, (symbol, label, prompt) in enumerate(prompts):
            with quick_cols[i % 2]:
                if st.button(f"{symbol}  {label}", key=f"quick_{i}", use_container_width=True):
                    st.session_state.quick_prompt = prompt
                    st.rerun()

        st.markdown("")
        st.markdown("""
        <div class="info-card">
          <div class="info-title">✦ &nbsp; What Kleos can help with</div>
          <div class="small-muted">
          • Inspect workflow run history and job status<br>
          • Review job logs and identify useful error evidence<br>
          • Separate actionable errors from unrelated warnings<br>
          • Answer general DevOps questions clearly
          </div>
        </div>
        """, unsafe_allow_html=True)

    for item in st.session_state.messages:
        if item["role"] not in ("user", "assistant"):
            continue
        with st.chat_message(item["role"]):
            st.markdown(item.get("content", ""))

    prompt = st.chat_input("Ask about DevOps, CI/CD, GitHub Actions, or deployment logs…")
    if st.session_state.quick_prompt:
        prompt = st.session_state.quick_prompt
        st.session_state.quick_prompt = ""

    if prompt:
        previous = list(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Kleos is thinking and checking available tools…"):
                    answer, history, activities, tool_count = asyncio.run(
                        run_kleos(prompt, previous)
                    )
                st.markdown(answer or "I couldn't produce a text response.")
                st.session_state.messages = history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer or "I couldn't produce a text response.",
                })
                st.session_state.tool_activity = activities
                st.session_state.mcp_tool_count = tool_count
            except Exception as error:
                friendly_error = (
                    f"**I couldn't complete the request.**\n\n"
                    f"Check that Ollama is running at `{API_URL}` and that "
                    f"the `{MODEL}` model is available.\n\n"
                    f"Details: `{error}`"
                )
                st.error(friendly_error)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": friendly_error,
                })

with side_col:
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
      <div class="info-title">⚙️ &nbsp; Assistant status</div>
      <div class="tool-row">
        <div class="tool-icon">✦</div>
        <div><div class="tool-name">Local LLM</div>
        <div class="tool-desc">Qwen 2.5 · 1.5B via Ollama</div></div>
      </div>
      <div class="tool-row">
        <div class="tool-icon">⌘</div>
        <div><div class="tool-name">MCP tools</div>
        <div class="tool-desc">GitHub Actions and project investigation</div></div>
      </div>
      <div class="tool-row">
        <div class="tool-icon">♧</div>
        <div><div class="tool-name">Access mode</div>
        <div class="tool-desc">Read-only investigation</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    activities = st.session_state.tool_activity
    st.markdown(f"""
    <div class="info-card">
      <div class="info-title">◷ &nbsp; Recent tool activity</div>
      <div class="small-muted">{len(activities)} tool call(s) in the latest response</div>
    """, unsafe_allow_html=True)
    if activities:
        for activity in reversed(activities[-6:]):
            status = "✓" if activity["ok"] else "!"
            color = "#159b73" if activity["ok"] else "#d97735"
            st.markdown(
                f'<div class="tool-row"><div class="tool-icon" style="color:{color}">{status}</div>'
                f'<div><div class="tool-name">{activity["name"]}</div>'
                f'<div class="tool-desc">{"Completed" if activity["ok"] else "Needs attention"}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="small-muted">Your tool calls will appear here when Kleos investigates a request.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
      <div class="info-title">⌘ &nbsp; Connected repository</div>
      <div style="font-size:12px;font-weight:700;color:#344d76">tanahmeeedsx/devsecops-agent</div>
      <div class="small-muted" style="margin-top:7px">GitHub Actions · Workflow history · Job logs</div>
    </div>
    <div class="ready-card">
      <div class="ready-title">✓ &nbsp; Ready when you are</div>
      <div class="small-muted">Start with a suggested prompt or ask your own DevOps question.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    '<div class="footer-note">Kleos · AI DevOps Chatbot Assistant · Built with Python, Streamlit, Ollama and MCP</div>',
    unsafe_allow_html=True,
)
