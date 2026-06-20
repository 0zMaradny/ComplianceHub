#!/usr/bin/env python3
"""chat.py — Unified ComplianceHub Chat
Usage:
  python chat.py                    # Interactive (auto-detect mode)
  python chat.py "your message"     # One-shot query
  python chat.py --mode audit       # Audit mode (Agent 1 default)
  python chat.py --mode general     # General chat mode
  python chat.py --agent 2          # Load Agent 2 (Lead Implementer)
  python chat.py --model opus       # Use Claude Opus Thinking
  python chat.py --resume           # Resume last session
  python chat.py --context file.pdf # Load file as context
"""

import os, sys, json, time, re, readline, argparse, textwrap
from datetime import datetime
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

CHAT_LOGS_DIR = HERE / "chat_logs"
CHAT_LOGS_DIR.mkdir(exist_ok=True)

KNOWLEDGE_FILES = {
    "AGENTS.md": HERE / "AGENTS.md",
    "AGENT_PROMPTS.md": HERE / "AGENT_PROMPTS.md",
    "MEMORY.md": HERE / "MEMORY.md",
    "HUMANIZE.md": HERE / "HUMANIZE.md",
}

AGENT_PROMPTS_FILE = HERE / "AGENT_PROMPTS.md"

DEFAULT_MODEL = "claude-sonnet-4-6"
OPUS_MODEL = "claude-opus-4-6-thinking"

LOCAL_API = "http://localhost:8000/v1/chat/completions"
GENERAL_SYSTEM = "You are a helpful, direct assistant. Be concise and accurate. Use the knowledge provided to understand the user's context."

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"

history_file = HERE / ".chat_history"
if not history_file.exists():
    history_file.write_text("")
try:
    readline.read_history_file(str(history_file))
except FileNotFoundError:
    pass
except OSError:
    pass
readline.set_history_length(500)


def eprint(*a, **kw):
    print(*a, file=sys.stderr, **kw)


def color(text, color_code, bold=False):
    return f"{BOLD if bold else ''}{color_code}{text}{RESET}"


def load_knowledge() -> str:
    parts = []
    for name, path in KNOWLEDGE_FILES.items():
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="replace")
            parts.append(f"=== {name} ===\n{content[:8000]}")
    return "\n\n".join(parts)


def load_agent_prompt(agent_num: int) -> Optional[str]:
    if not AGENT_PROMPTS_FILE.exists():
        return None
    text = AGENT_PROMPTS_FILE.read_text(encoding="utf-8")
    pattern = rf"## Agent {agent_num} — .*?(?=\n## Agent |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return None
    block = match.group(0)
    lines = block.split("\n")
    result = []
    in_prompt = False
    for line in lines:
        if "System Prompt" in line and "```" in line:
            in_prompt = True
            continue
        if in_prompt:
            if "```" in line:
                break
            result.append(line)
    return "\n".join(result).strip() if result else None


def list_agents() -> list[dict]:
    if not AGENT_PROMPTS_FILE.exists():
        return []
    text = AGENT_PROMPTS_FILE.read_text(encoding="utf-8")
    agents = []
    for match in re.finditer(r"## Agent (\d+) — (.+?)(?:\n|$)", text):
        agents.append({"num": int(match.group(1)), "name": match.group(2).strip()})
    return agents


def list_sessions() -> list[Path]:
    return sorted(CHAT_LOGS_DIR.glob("*.json"), reverse=True)


def save_session(messages: list, mode: str, agent: Optional[int], model: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = CHAT_LOGS_DIR / f"chat_{ts}.json"
    data = {
        "timestamp": ts,
        "mode": mode,
        "agent": agent,
        "model": model,
        "messages": messages[-100:],
    }
    if len(messages) > 100:
        logger.debug("Session save: truncating %d messages to last 100", len(messages))
    fname.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return fname


def load_session(fpath: Path) -> dict:
    return json.loads(fpath.read_text(encoding="utf-8"))


def detect_api_url() -> str:
    try:
        import urllib.request
        req = urllib.request.Request(LOCAL_API, method="POST",
            data=b'{"model":"test","messages":[{"role":"user","content":"ping"}]}',
            headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=3)
        if resp.status == 200:
            return LOCAL_API
    except Exception as e:
        logger.debug("Local API probe failed: %s", e)
    # Read tunnel URL from file with SSRF protection
    for tf in [HERE / ".tunnel-url", Path("/tmp/compliancehub-url.txt")]:
        if tf.exists():
            url = tf.read_text().strip()
            if url and _is_valid_tunnel_url(url):
                return f"{url}/v1/chat/completions"
    return LOCAL_API


def _is_valid_tunnel_url(url: str) -> bool:
    """Validate tunnel URL to prevent SSRF. Only allow known safe patterns."""
    from urllib.parse import urlparse
    import ipaddress
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname:
        return False
    # Block private/internal IPs
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            return False
    except ValueError:
        pass  # hostname, not IP — allow
    # Allow known tunnel domains
    allowed_suffixes = (".trycloudflare.com", ".ngrok.io", ".loca.lt", ".tunnel.app")
    if not any(parsed.hostname.endswith(s) for s in allowed_suffixes):
        return False
    return True


def call_api(api_url: str, model: str, messages: list,
             temperature: float = 0.3, max_tokens: int = 4096,
             stream: bool = False) -> dict:
    import urllib.request
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }).encode()
    req = urllib.request.Request(api_url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read().decode())
        return data
    except Exception as e:
        return {"error": str(e)}


def stream_chat(api_url: str, model: str, messages: list,
                temperature: float = 0.3, max_tokens: int = 4096):
    import urllib.request
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }).encode()
    req = urllib.request.Request(api_url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        buffer = ""
        while True:
            chunk = resp.read(4096).decode("utf-8", errors="replace")
            if not chunk:
                # Flush remaining buffer on stream end
                if buffer.strip():
                    for line in buffer.strip().split("\n"):
                        if line.startswith("data: "):
                            payload = line[6:]
                            if payload == "[DONE]":
                                return
                            try:
                                d = json.loads(payload)
                                if "choices" in d and len(d["choices"]) > 0:
                                    delta = d["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                pass
                break
            buffer += chunk
            while "\n\n" in buffer:
                event_text, buffer = buffer.split("\n\n", 1)
                for line in event_text.strip().split("\n"):
                    if line.startswith("data: "):
                        payload = line[6:]
                        if payload == "[DONE]":
                            return
                        try:
                            d = json.loads(payload)
                            if "choices" in d and len(d["choices"]) > 0:
                                delta = d["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        yield f"\n{color(f'[Error: {e}]', RED)}"


def build_prompt(mode: str, agent_num: Optional[int], knowledge: str,
                 user_msg: str, context_text: str = "") -> list:
    system_parts = []

    if mode == "audit" and agent_num:
        agent_prompt = load_agent_prompt(agent_num)
        if agent_prompt:
            system_parts.append(agent_prompt)
        else:
            agent_name = "Assistant"
            agents = list_agents()
            for a in agents:
                if a["num"] == agent_num:
                    agent_name = a["name"]
                    break
            system_parts.append(f"You are Agent {agent_num} ({agent_name}) at TÜV AUSTRIA GCC.")

    system_parts.append("\n=== KNOWLEDGE (reference for user context) ===\n" + knowledge[:12000])

    if context_text:
        system_parts.append(f"\n=== USER FILE CONTEXT ===\n{context_text[:8000]}")

    if mode == "audit":
        system_parts.append("\nRules: ISO clause references in English. Arabic MSA for deliverables. Client isolation. Findings only for audit work.")
    else:
        system_parts.append("\nThe user's files (AGENTS.md, MEMORY.md, etc.) describe their work. Use them for context when asked.")

    system = "\n\n".join(system_parts)

    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]
    return msgs


def print_header(mode: str, agent: Optional[int], model: str, session_label: str = ""):
    model_label = "Opus" if "opus" in model else "Sonnet"
    agent_label = f"Agent {agent}" if agent else ""
    mode_label = mode.upper()
    parts = [f"  {color('🤖 ComplianceHub Chat', CYAN, bold=True)}"]
    if session_label:
        parts.append(f"  {color(f'Session: {session_label}', DIM)}")
    parts.append(f"  {color(mode_label, GREEN)} {color(agent_label, YELLOW)} {color(f'[{model_label}]', MAGENTA)}")
    sep = "─" * 60
    print(f"\n{color(sep, DIM)}")
    for p in parts:
        print(p)
    print(f"{color(sep, DIM)}\n")


def print_help():
    help_text = f"""
{color('Commands:', BOLD)}
  {color('/mode general', CYAN)}         Switch to general chat mode
  {color('/mode audit', CYAN)}           Switch to audit mode (Agent 1 default)
  {color('/agent <1-9>', CYAN)}          Load agent prompt (e.g., /agent 2 for Lead Implementer)
  {color('/model sonnet', CYAN)}         Use Claude Sonnet 4.6 (default)
  {color('/model opus', CYAN)}           Use Claude Opus 4.6 Thinking
  {color('/model auto', CYAN)}           Auto-select best model for query
  {color('/load <file>', CYAN)}          Load file as context
  {color('/files', CYAN)}                List available files
  {color('/save', CYAN)}                 Save session to chat_logs/
  {color('/list', CYAN)}                 List saved sessions
  {color('/resume <n>', CYAN)}           Resume session by number
  {color('/export', CYAN)}               Export session as markdown
  {color('/clear', CYAN)}                Clear screen
  {color('/help', CYAN)}                 Show this help
  {color('/exit', CYAN)}                 Exit

{color('Quick tips:', DIM)}
  - General mode: free chat, no agent loaded
  - Audit mode: agent prompts + ISO knowledge active
  - Files are always loaded as background context (AGENTS.md, MEMORY.md, etc.)
  - Press Ctrl+D or type /exit to quit
"""
    print(help_text)


def print_agent_list():
    agents = list_agents()
    if not agents:
        print(f"{color('No agents found in AGENT_PROMPTS.md', RED)}")
        return
    print(f"\n{color('Available Agents:', BOLD)}")
    for a in agents:
        prompt_preview = load_agent_prompt(a["num"])
        desc = prompt_preview[:60].replace("\n", " ") + "..." if prompt_preview else ""
        print(f"  {color(f'Agent {a["num"]}:', YELLOW)} {color(a['name'], GREEN)}")
        if desc:
            print(f"         {color(desc, DIM)}")
    print()


def print_file_list():
    print(f"\n{color('Available files as context:', BOLD)}")
    for name, path in KNOWLEDGE_FILES.items():
        status = color("✓", GREEN) if path.exists() else color("✗", RED)
        size = path.stat().st_size if path.exists() else 0
        print(f"  {status} {name} ({size//1024} KB)")
    print(f"  {color('Use /load <path>', DIM)} to load additional files")
    print()


def load_file_as_text(fpath: str) -> Optional[str]:
    p = Path(fpath).expanduser().resolve()
    if not p.exists():
        return None
    # Path traversal protection: only allow files within workspace
    try:
        p.relative_to(HERE)
    except ValueError:
        return None  # File is outside workspace
    ext = p.suffix.lower()
    if ext == ".txt":
        return p.read_text(encoding="utf-8", errors="replace")
    if ext in (".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".conf", ".sh", ".bash", ".env"):
        return p.read_text(encoding="utf-8", errors="replace")
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(str(p))
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except ImportError:
            return f"[python-docx not installed, cannot parse {p.name}]"
        except Exception as e:
            return f"[Error parsing docx: {e}]"
    if ext == ".pdf":
        try:
            import subprocess
            result = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except Exception:
            pass
        return f"[Cannot extract text from {p.name} - try converting to .txt first]"
    return f"[Unsupported format: {ext}]"


def main():
    parser = argparse.ArgumentParser(description="ComplianceHub Chat")
    parser.add_argument("message", nargs="?", help="One-shot query (skips interactive mode)")
    parser.add_argument("--mode", choices=["general", "audit"], default=None,
                        help="Chat mode (default: auto-detect from message)")
    parser.add_argument("--agent", type=int, choices=range(1, 10), default=None,
                        help="Agent number (1-9, audit mode only)")
    parser.add_argument("--model", choices=["sonnet", "opus"], default=None,
                        help="Model (sonnet or opus)")
    parser.add_argument("--resume", nargs="?", const="latest", default=None,
                        help="Resume a session (name or 'latest')")
    parser.add_argument("--context", type=str, default=None,
                        help="File to load as context")
    parser.add_argument("--api-url", type=str, default=None,
                        help="API URL override")
    args = parser.parse_args()

    api_url = args.api_url or detect_api_url()
    mode = args.mode or "general"
    model = OPUS_MODEL if args.model == "opus" else DEFAULT_MODEL
    agent = args.agent
    knowledge = load_knowledge()
    context_text = ""
    messages = []
    session_path = None

    if args.context:
        ctx = load_file_as_text(args.context)
        if ctx:
            context_text = ctx
            print(f"{color('✓', GREEN)} Loaded: {args.context} ({len(ctx)//1024} KB)")
        else:
            print(f"{color('✗', RED)} Cannot load: {args.context}")

    if args.resume:
        sessions = list_sessions()
        if args.resume == "latest" and sessions:
            session_path = sessions[0]
        else:
            for s in sessions:
                if args.resume in s.stem:
                    session_path = s
                    break
        if session_path:
            data = load_session(session_path)
            messages = data.get("messages", [])
            mode = data.get("mode", mode)
            agent = data.get("agent", agent)
            model = data.get("model", model)

    if mode == "audit" and agent is None:
        agent = 1

    session_label = session_path.stem.replace("chat_", "") if session_path else datetime.now().strftime("%H%M%S")

    if args.message:
        msgs = build_prompt(mode, agent, knowledge, args.message, context_text)
        if messages:
            # Keep all non-system messages from history, replace system with new prompt
            existing = [m for m in messages if m.get("role") != "system"]
            msgs = msgs[:1] + existing + msgs[1:]  # new system + history + new user msg
        print_header(mode, agent, model)
        print(f"\n{color('You:', BLUE, bold=True)} {args.message}\n")
        print(f"{color('🤖:', GREEN, bold=True)} ", end="", flush=True)
        full = ""
        for token in stream_chat(api_url, model, msgs):
            print(token, end="", flush=True)
            full += token
        print(f"\n{color(f'[via: {model}]', DIM)}")
        readline.write_history_file(str(history_file))
        return

    print_header(mode, agent, model, session_label)
    print(f"{color('API:', DIM)} {api_url}")
    print(f"{color('Type /help for commands or start chatting.', DIM)}\n")

    if mode == "audit" and agent:
        agent_prompt = load_agent_prompt(agent) or "Agent loaded"
        print(f"{color(f'Agent {agent} active.', GREEN)} {agent_prompt[:80]}...")

    if args.resume and messages:
        last = messages[-3:]
        print(f"{color(f'Resumed session: {session_path.stem}', YELLOW)}")
        for m in last:
            role = m.get("role", "?")
            content = m.get("content", "")[:80]
            print(f"  {color(f'{role}:', DIM)} {content}...")

    while True:
        try:
            user_input = input(f"\n{color('>', CYAN, bold=True)} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{color('Bye!', GREEN)}")
            readline.write_history_file(str(history_file))
            sys.exit(0)

        if not user_input:
            continue

        readline.add_history(user_input)

        if user_input.startswith("/"):
            cmd = user_input[1:].lower().split()
            if not cmd:
                continue
            command = cmd[0]

            if command in ("exit", "quit", "q"):
                print(f"\n{color('Bye!', GREEN)}")
                readline.write_history_file(str(history_file))
                sys.exit(0)

            elif command == "help":
                print_help()

            elif command == "clear":
                print(CLEAR)
                print_header(mode, agent, model, session_label)

            elif command == "mode":
                if len(cmd) > 1 and cmd[1] in ("general", "audit"):
                    mode = cmd[1]
                    messages = []  # Clear history on mode switch to avoid conflicting system prompts
                    if mode == "audit" and agent is None:
                        agent = 1
                    print(f"{color(f'→ Switched to {mode.upper()} mode', GREEN)}")
                    if mode == "audit" and agent:
                        ap = load_agent_prompt(agent)
                        print(f"{color(f'  Agent {agent} loaded.', DIM)}")
                else:
                    print(f"{color('Usage: /mode general|audit', YELLOW)}")

            elif command == "agent":
                if mode != "audit":
                    mode = "audit"
                    messages = []  # Clear history on mode switch
                    print(f"{color('→ Auto-switched to AUDIT mode', GREEN)}")
                if len(cmd) > 1 and cmd[1].isdigit():
                    agent = int(cmd[1])
                    ap = load_agent_prompt(agent)
                    if ap:
                        print(f"{color(f'→ Agent {agent} loaded.', GREEN)}")
                        agent_name = ap.split("\n")[0][:60] if ap else ""
                        print(f"  {color(agent_name, DIM)}")
                    else:
                        print(f"{color(f'→ Agent {agent} selected (no prompt file)', YELLOW)}")
                else:
                    print_agent_list()

            elif command == "model":
                if len(cmd) > 1:
                    if cmd[1] == "sonnet":
                        model = DEFAULT_MODEL
                        print(f"{color('→ Model: Claude Sonnet 4.6', GREEN)}")
                    elif cmd[1] == "opus":
                        model = OPUS_MODEL
                        print(f"{color('→ Model: Claude Opus 4.6 Thinking', GREEN)}")
                    elif cmd[1] == "auto":
                        model = "auto"
                        print(f"{color('→ Model: Auto (will analyze query)', GREEN)}")
                    else:
                        print(f"{color('Usage: /model sonnet|opus|auto', YELLOW)}")
                else:
                    current = "Opus" if "opus" in model else "Sonnet" if "sonnet" in model else model
                    print(f"{color(f'Current model: {current}', CYAN)}")

            elif command == "load":
                if len(cmd) < 2:
                    print(f"{color('Usage: /load <filepath>', YELLOW)}")
                    continue
                fpath = " ".join(cmd[1:])
                ctx = load_file_as_text(fpath)
                if ctx:
                    if ctx.startswith("[") and ctx.endswith("]"):
                        print(f"{color(ctx, RED)}")
                    else:
                        context_text = ctx
                        print(f"{color(f'✓ Loaded: {fpath} ({len(ctx)//1024} KB)', GREEN)}")
                else:
                    print(f"{color(f'✗ File not found: {fpath}', RED)}")

            elif command == "files":
                print_file_list()

            elif command == "save":
                if messages:
                    fname = save_session(messages, mode, agent, model)
                    print(f"{color(f'✓ Session saved: {fname.name}', GREEN)}")
                else:
                    print(f"{color('Nothing to save.', YELLOW)}")

            elif command == "list":
                sessions = list_sessions()
                if not sessions:
                    print(f"{color('No saved sessions.', DIM)}")
                    continue
                print(f"\n{color('Saved Sessions:', BOLD)}")
                for i, s in enumerate(sessions[:20], 1):
                    data = load_session(s)
                    ts = data.get("timestamp", "?")
                    m = data.get("mode", "?")
                    a = data.get("agent", "")
                    cnt = len(data.get("messages", []))
                    label = f"  {i}. {color(ts, CYAN)} [{m.upper()}]"
                    if a:
                        label += f" Agent {a}"
                    label += f" ({cnt//2} exchanges)"
                    print(label)
                print()

            elif command == "resume":
                sessions = list_sessions()
                if not sessions:
                    print(f"{color('No saved sessions.', YELLOW)}")
                    continue
                idx = 0
                if len(cmd) > 1 and cmd[1].isdigit():
                    idx = int(cmd[1]) - 1
                if 0 <= idx < len(sessions):
                    session_path = sessions[idx]
                    data = load_session(session_path)
                    messages = data.get("messages", [])
                    mode = data.get("mode", mode)
                    agent = data.get("agent", agent)
                    model = data.get("model", model)
                    session_label = session_path.stem.replace("chat_", "")
                    print(f"{color(f'→ Resumed: {session_path.name}', GREEN)} ({len(messages)//2} exchanges)")
                else:
                    print(f"{color(f'Session #{idx+1} not found.', RED)}")

            elif command == "export":
                if not messages:
                    print(f"{color('Nothing to export.', YELLOW)}")
                    continue
                md_lines = [f"# ComplianceHub Chat Session", f"Date: {datetime.now().isoformat()}",
                            f"Mode: {mode}", f"Model: {model}"]
                if agent:
                    md_lines.append(f"Agent: {agent}")
                md_lines.append("")
                for m in messages:
                    role = m.get("role", "?")
                    content = m.get("content", "")
                    emoji = "🤖" if role == "assistant" else "👤" if role == "user" else "⚙️"
                    md_lines.append(f"### {emoji} {role.capitalize()}")
                    md_lines.append(content)
                    md_lines.append("")
                md = "\n".join(md_lines)
                fname = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                (HERE / fname).write_text(md, encoding="utf-8")
                print(f"{color(f'✓ Exported: {fname}', GREEN)}")

            elif command == "agent-list":
                print_agent_list()

            else:
                print(f"{color(f'Unknown command: /{command}', RED)} {color('Try /help', DIM)}")
            continue

        use_model = model
        if model == "auto":
            risk_keywords = ["risk", "evaluate", "analyze", "compare", "complex", "scenario", "trade-off", "factor",
                             "audit", "compliance", "iso", "nc", "clause", "non-conformity", "capa", "bcmd"]
            if any(kw in user_input.lower() for kw in risk_keywords):
                use_model = OPUS_MODEL
            else:
                use_model = DEFAULT_MODEL

        msgs = build_prompt(mode, agent, knowledge, user_input, context_text)
        if messages:
            full_msgs = messages[:] + msgs[-1:] if messages[-1].get("role") != "user" else messages + msgs[-1:]
        else:
            full_msgs = msgs

        print(f"{color('🤖:', GREEN, bold=True)} ", end="", flush=True)
        full_response = ""
        for token in stream_chat(api_url, use_model, full_msgs):
            print(token, end="", flush=True)
            full_response += token

        model_used = use_model
        print(f"\n{color(f'[via: {model_used}]', DIM)}")

        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": full_response})

        if len(messages) > 100:
            messages = messages[-100:]


if __name__ == "__main__":
    main()
