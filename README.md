# Groq Tool Agent

A local Python tool-calling agent powered by Groq. The agent receives user prompts, lets the model choose tools, executes those tools locally, and returns a final response.

## What is in this repository

- Interactive CLI chat entry point in `main.py`.
- Core agent loop and conversation/session management in `agent/agent.py`.
- Groq tool schemas and model call configuration in `agent/llm.py`.
- Local tool implementations and registry in `agent/tools.py`.
- Command/tool approval policy in `agent/permissions.py`.
- File-based logging setup in `agent/logging_config.py`.
- Lightweight script-style checks in `agent/test_tools.py` and `agent/test_permissions.py`.

## Features

- Groq function calling with model `qwen/qwen3.8-27b`.
- 22 local tools for file operations, environment/system info, networking checks, and controlled shell command execution.
- Safe arithmetic evaluation using Python AST (no arbitrary expression execution).
- Command classification with `ALLOW`, `APPROVAL`, and `DENY` outcomes for `run_command`.
- Additional approval gate for the `list_open_ports` tool.
- Conversation context compaction and tool-result truncation to stay within context budget.
- Session log files written under `logs/`.
- Schema/registry consistency checks between `agent/llm.py` and `agent/tools.py`.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux
- A Groq API key (`GROQ_API_KEY`)
- Internet access for Groq API calls

## Setup

From the project root:

```bash
python -m venv .venv
```

Activate the environment:

- PowerShell:

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- Bash/zsh:

  ```bash
  source .venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
pip install python-dotenv
```

> `agent/llm.py` imports `python-dotenv`. At the moment, `requirements.txt` includes `groq` only, so install `python-dotenv` as shown above.

## Configuration

Set your Groq key in the environment:

- PowerShell:

  ```powershell
  $env:GROQ_API_KEY = "your-groq-api-key"
  ```

- Bash/zsh:

  ```bash
  export GROQ_API_KEY="your-groq-api-key"
  ```

Or create a local `.env` file:

```text
GROQ_API_KEY=your-groq-api-key
```

Do not commit API keys or `.env` files.

## Running the agent

Start the interactive chat:

```bash
python main.py
```

Behavior:

- Prompts with `You:` for each message.
- Type `-1` to end the chat session.
- Reuses one `AgentSession` across turns so the model can use recent context.

## Conversation context behavior

`AgentSession` keeps a message history beginning with a system prompt and then:

- Adds each user/tool/model message to history.
- Compacts older complete turns when the context estimate exceeds `MAX_CONTEXT_CHARS` (default `24000`).
- Truncates individual tool results in model context above `MAX_TOOL_CONTEXT_CHARS` (default `6000`).

## Logging

Each run writes to:

```text
logs/run_YYYYMMDD_HHMMSS_microseconds.log
```

The logger is file-based (`agent/logging_config.py`) and logs lifecycle events, tool calls, permission outcomes, and errors.

## Architecture

```text
main.py (interactive loop)
  -> agent.agent.run_agent(...)
     -> agent.llm.ask_llm(...)
     -> agent.tools.TOOL_REGISTRY[tool_name](**args)
     -> agent.permissions (command/tool approval)
```

## Tool registry (22 tools)

### Calculations and system/runtime information

| Tool | Purpose |
| --- | --- |
| `calculate` | Evaluate arithmetic expressions safely. |
| `get_current_time` | Return local system time. |
| `get_working_directory` | Return current working directory. |
| `get_environment_info` | Return OS/platform/Python/current directory details. |
| `check_port` | Check whether a local TCP port is in use. |
| `list_open_ports` | Scan a bounded local port range for open TCP ports (approval required). |

### File and directory operations

| Tool | Purpose |
| --- | --- |
| `list_files` | List directory entries. |
| `read_file` | Read a UTF-8 text file. |
| `create_file` | Create an empty file (fails if it already exists). |
| `write_file` | Replace file content with text. |
| `append_file` | Append text to a file. |
| `create_directory` | Create a directory (fails if it already exists). |
| `delete_file` | Delete a file. |
| `move_file` | Move a file or directory. |
| `copy_file` | Copy a file. |
| `file_exists` | Check whether a path exists. |
| `get_file_info` | Return file/path metadata. |
| `search_files` | Recursively find exact filename matches with depth/result/time bounds. |
| `search_text` | Find matching lines in a UTF-8 text file. |
| `get_directory_tree` | Return a bounded directory tree. |
| `get_file_hash` | Compute a file hash (default `sha256`). |

### Command execution

| Tool | Purpose |
| --- | --- |
| `run_command` | Execute a shell command after policy classification/approval. |

## Command security policy

`run_command` first classifies commands via `agent/permissions.py`:

| Classification | Behavior |
| --- | --- |
| `ALLOW` | Runs immediately. |
| `APPROVAL` | Prompts the user (`yes`/`y`) before running. |
| `DENY` | Does not run. |

Current allow-list examples:

- `git status`, `git branch`, `git log`, `git diff`
- `pip list`
- `python --version`
- `dir`, `ls`

Current approval examples:

- `git commit`, `git checkout`, `git switch`, `git merge`
- `pip install`, `pip uninstall`
- `python script`

Current deny-list executables include:

- `rm`, `rmdir`, `del`, `format`, `shutdown`, `reboot`

## Testing and checks

Run compile checks:

```bash
python -m py_compile main.py agent/agent.py agent/llm.py agent/logging_config.py agent/permissions.py agent/test_permissions.py agent/test_tools.py agent/tools.py
```

Run permission behavior script:

```bash
python agent/test_permissions.py
```

Run tool behavior script:

```bash
python agent/test_tools.py
```

Notes:

- These are script-based checks using plain assertions (not `pytest`).
- `agent/test_tools.py` verifies tool behavior and schema/registry name alignment.
- These checks do not call the Groq API, but `agent/llm.py` initializes a Groq client at import time. Set `GROQ_API_KEY` (a dummy value is enough for these local checks).

## Project structure

```text
AI-Agent/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── llm.py
│   ├── logging_config.py
│   ├── permissions.py
│   ├── test_permissions.py
│   ├── test_tools.py
│   └── tools.py
└── logs/                  (created at runtime)
```

## Limitations

- No sandboxing of filesystem paths: tool paths are local filesystem paths.
- `run_command` still executes local shell commands; safety depends on policy configuration.
- Tool I/O is text-oriented unless explicitly binary (e.g., hashing).
- Groq API access is required for normal agent responses.
- Validation scripts are lightweight and do not replace a full test framework.
