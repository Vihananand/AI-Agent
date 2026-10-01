
# Groq Tool Agent

A local Python tool-calling agent powered by Groq. The agent receives a user
request, lets the language model select an appropriate tool, executes that tool
locally, and sends the result back to the model for a final response.

The project is designed for local development workflows involving files,
directories, system information, basic calculations, and carefully controlled
shell commands.

## Features

- Groq function calling with the `qwen/qwen3.8-27b` model.
- 21 local tools for files, directories, system information, networking, and
  command execution.
- Safe arithmetic evaluation without executing arbitrary Python expressions.
- Command permissions with `ALLOW`, `APPROVAL`, and `DENY` classifications.
- Explicit user confirmation before approval-level shell commands run.
- Read-only helpers for text search, directory trees, and file checksums.
- Direct script execution for the included local test files.
- A schema consistency check that prevents Groq tools from drifting away from
  the Python tool registry.

## Requirements

- Windows, macOS, or Linux.
- Python 3.10 or newer.
- A Groq API key.
- Internet access when the agent sends requests to Groq.

## Installation

From the project directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

The dependencies are:

- `groq`: Groq Python client.
- `python-dotenv`: Loads environment variables from a local `.env` file.

## Configuration

Set `GROQ_API_KEY` before starting the agent.

For the current PowerShell session:

```powershell
$env:GROQ_API_KEY = "your-groq-api-key"
```

For a persistent Windows user environment variable:

```powershell
[Environment]::SetEnvironmentVariable(
    "GROQ_API_KEY",
    "your-groq-api-key",
    "User"
)
```

Alternatively, create a `.env` file in the project root:

```text
GROQ_API_KEY=your-groq-api-key
```

Do not commit `.env` files or API keys to source control.

## Running The Agent

Start the example entry point:

```powershell
python main.py
```

The example request is defined in `main.py`. Change the string passed to
`run_agent()` to try another request.

For example:

```python
from agent.agent import run_agent

response = run_agent("List the files in the current directory")
print(response)
```

The agent can use multiple tools during one request. It continues the Groq
conversation until the model returns a response without more tool calls.

## Conversation Context

The interactive application keeps one `AgentSession` for the entire chat, so
the model can refer to recent messages and tool results. To prevent the
conversation from exceeding the model context window, the session:

- Keeps the system prompt and newest complete turns.
- Removes the oldest complete turns when the context budget is exceeded.
- Truncates individual tool results before storing them in model context.
- Keeps the full chat log separately in the session log file.

The default context budget is approximately 24,000 characters. This is a
deliberately conservative budget because characters are only an estimate of
tokens. The budget can be changed by passing `max_context_chars` to
`AgentSession`.

## Run Logs

Each chat session creates one log file in `logs/`. Every user message is marked
inside that file with a message number:

```text
logs/run_YYYYMMDD_HHMMSS_microseconds.log
```

Logs include the chat lifecycle, message boundaries, model requests and responses, selected tools,
permission classifications, approval outcomes, tool completion status, and
exceptions. Logger output is written only to these files; it is not printed to
the terminal. The `logs/` directory is excluded from source control.

API keys are never written to the logs. Tool arguments are logged to make a
run reproducible, so avoid sending secrets as tool arguments.

## Architecture

```text
main.py
|
v
agent.agent.run_agent()
|                    \
|                     -> agent.permissions
v
agent.llm.ask_llm()    -> agent.tools.TOOL_REGISTRY
|
v
Groq chat completions
```

### `main.py`

Provides the runnable example. It passes a user request to `run_agent()` and
prints the final response.

### `agent/agent.py`

Owns the tool-calling loop:

1. Sends the system prompt and user request to Groq.
2. Reads any function calls returned by the model.
3. Parses each function's JSON arguments.
4. Applies the command permission policy when the tool is `run_command`.
5. Executes the selected Python tool.
6. Sends each tool result back to Groq.
7. Returns the final natural-language response.

### `agent/llm.py`

Creates the Groq client and defines the function schemas sent to the model.
The module checks that every Groq schema name also exists in
`TOOL_REGISTRY`. This catches incomplete tool registration during import.

### `agent/tools.py`

Contains the local Python implementations and the `TOOL_REGISTRY` mapping.
The registry is the source used by the agent when resolving a model-generated
tool name.

### `agent/permissions.py`

Parses shell commands and classifies them before execution. The policy is
deliberately restrictive because `run_command` executes on the local machine.

## Available Tools

### Calculations and system information

| Tool | Purpose |
| --- | --- |
| `calculate` | Evaluates basic arithmetic such as `2 + 3 * 4`. |
| `get_current_time` | Returns the local system time. |
| `get_working_directory` | Returns the current working directory. |
| `get_environment_info` | Returns operating system, platform, Python, and directory details. |
| `check_port` | Checks whether a local TCP port is in use. |
| `list_open_ports` | Lists open TCP ports in a bounded local range. |

### File and directory operations

| Tool | Purpose |
| --- | --- |
| `list_files` | Lists entries in a directory. |
| `read_file` | Reads a UTF-8 text file. |
| `create_file` | Creates an empty file without overwriting an existing file. |
| `write_file` | Replaces a file's contents. |
| `append_file` | Appends text to a file. |
| `create_directory` | Creates a directory. |
| `delete_file` | Deletes a file. |
| `move_file` | Moves a file or directory. |
| `copy_file` | Copies a file. |
| `file_exists` | Checks whether a path exists. |
| `get_file_info` | Returns file metadata. |
| `search_files` | Recursively searches for an exact filename with depth, result, and time limits. |
| `search_text` | Finds matching lines in a text file. |
| `get_directory_tree` | Displays a bounded directory tree. |
| `get_file_hash` | Calculates a checksum such as SHA-256. |

### Command execution

| Tool | Purpose |
| --- | --- |
| `run_command` | Executes a shell command only after permission checks. |

## Command Security

Commands are classified before execution:

| Classification | Behavior |
| --- | --- |
| `ALLOW` | Executes immediately. |
| `APPROVAL` | Prompts the user for `yes` or `no`. |
| `DENY` | Never executes. |

Currently allowed command families include:

- `git status`
- `git branch`
- `git log`
- `git diff`
- `pip list`
- `python --version`
- `dir`
- `ls`

Approval is required for commands such as:

- `git commit`
- `git checkout`
- `git switch`
- `git merge`
- `pip install`
- `pip uninstall`

The policy denies destructive commands including `rm`, `rmdir`, `del`,
`format`, `shutdown`, and `reboot`.

This policy is a project-level safeguard, not a complete shell sandbox. Review
and extend it before using the agent in a sensitive environment.

## Testing

Compile every Python module:

```powershell
python -m py_compile main.py agent\agent.py agent\llm.py agent\permissions.py agent\test_permissions.py agent\test_tools.py agent\tools.py
```

Run permission checks:

```powershell
python agent\test_permissions.py
```

Run the network-free tool checks:

```powershell
python agent\test_tools.py
```

The tool checks verify safe arithmetic, text search, file hashing, and the
alignment between the Groq schema list and `TOOL_REGISTRY`. They do not call
the Groq API and do not require an API key.

## Adding A Tool

1. Add the Python implementation to `agent/tools.py`.
2. Add the function to `TOOL_REGISTRY`.
3. Add a matching `function_tool(...)` schema in `agent/llm.py`.
4. Make the schema name exactly match the registry key.
5. Add a focused assertion to `agent/test_tools.py`.
6. Run both test scripts and the compile command.

The schema consistency check will raise an error if a tool exists in only one
of the two registries.

## Project Structure

```text
ai-agent/
|-- main.py
|-- README.md
|-- requirements.txt
`-- agent/
    |-- __init__.py
    |-- agent.py
    |-- llm.py
    |-- permissions.py
    |-- test_permissions.py
    |-- test_tools.py
    `-- tools.py
```

## Limitations

- The agent requires a working Groq API key for normal operation.
- Tool paths are local paths and are not restricted to the project directory.
- File tools currently read and write UTF-8 text unless explicitly operating on
  binary content for hashing.
- Shell command safety depends on the permission policy in `permissions.py`.
- The included tests are lightweight scripts rather than a full test framework.
