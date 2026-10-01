import os

from dotenv import load_dotenv
from groq import Groq

from agent.logging_config import get_logger
from agent.tools import TOOL_REGISTRY

logger = get_logger("llm")

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def function_tool(name, description, properties=None, required=None):
    # Build the JSON schema expected by Groq function calling.
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
            },
        },
    }


STRING = {"type": "string"}
tools = [
    function_tool(
        "calculate",
        "Calculate a basic arithmetic expression.",
        {"expression": {**STRING, "description": "Arithmetic expression."}},
        ["expression"],
    ),
    function_tool("get_current_time", "Get the local system time."),
    function_tool(
        "list_files",
        "List files and directories in a directory.",
        {"directory": {**STRING, "description": "Directory path."}},
    ),
    function_tool(
        "read_file",
        "Read a UTF-8 text file.",
        {"file_path": {**STRING, "description": "File path."}},
        ["file_path"],
    ),
    function_tool(
        "create_file",
        "Create an empty file.",
        {"file_path": {**STRING, "description": "File path."}},
        ["file_path"],
    ),
    function_tool(
        "write_file",
        "Write text to a file, replacing existing content.",
        {
            "file_path": {**STRING, "description": "File path."},
            "content": {**STRING, "description": "Text to write."},
        },
        ["file_path", "content"],
    ),
    function_tool(
        "append_file",
        "Append text to a file.",
        {
            "file_path": {**STRING, "description": "File path."},
            "content": {**STRING, "description": "Text to append."},
        },
        ["file_path", "content"],
    ),
    function_tool(
        "create_directory",
        "Create a directory.",
        {"directory": {**STRING, "description": "Directory path."}},
        ["directory"],
    ),
    function_tool(
        "delete_file",
        "Delete a file.",
        {"file_path": {**STRING, "description": "File path."}},
        ["file_path"],
    ),
    function_tool(
        "move_file",
        "Move a file or directory.",
        {
            "source": {**STRING, "description": "Current path."},
            "destination": {**STRING, "description": "Destination path."},
        },
        ["source", "destination"],
    ),
    function_tool(
        "copy_file",
        "Copy a file.",
        {
            "source": {**STRING, "description": "Source path."},
            "destination": {**STRING, "description": "Destination path."},
        },
        ["source", "destination"],
    ),
    function_tool(
        "file_exists",
        "Check whether a file or directory exists.",
        {"file_path": {**STRING, "description": "Path to check."}},
        ["file_path"],
    ),
    function_tool(
        "get_file_info",
        "Get metadata about a file or directory.",
        {"file_path": {**STRING, "description": "Path to inspect."}},
        ["file_path"],
    ),
    function_tool(
        "search_files",
        "Recursively find files by exact filename.",
        {
            "directory": {**STRING, "description": "Search root directory."},
            "filename": {**STRING, "description": "Exact filename."},
            "max_depth": {
                "type": "integer",
                "description": "Maximum directory depth; defaults to 5.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum matches; defaults to 100.",
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Maximum scan time; defaults to 10 seconds.",
            },
        },
        ["directory", "filename"],
    ),
    function_tool(
        "search_text",
        "Find matching lines in a UTF-8 text file.",
        {
            "file_path": {**STRING, "description": "File path."},
            "text": {**STRING, "description": "Text to find."},
            "case_sensitive": {
                "type": "boolean",
                "description": "Whether matching respects letter case.",
            },
        },
        ["file_path", "text"],
    ),
    function_tool(
        "get_directory_tree",
        "Show a bounded directory tree.",
        {
            "directory": {**STRING, "description": "Root directory."},
            "max_depth": {"type": "integer", "description": "Maximum depth."},
        },
    ),
    function_tool(
        "get_file_hash",
        "Calculate a file checksum.",
        {
            "file_path": {**STRING, "description": "File path."},
            "algorithm": {**STRING, "description": "Hash algorithm, such as sha256."},
        },
        ["file_path"],
    ),
    function_tool("get_working_directory", "Get the agent's current directory."),
    function_tool("get_environment_info", "Get basic runtime environment information."),
    function_tool(
        "check_port",
        "Check whether a local TCP port is in use.",
        {"port": {"type": "integer", "description": "TCP port number."}},
        ["port"],
    ),
    function_tool(
        "list_open_ports",
        "List open TCP ports on a host within a bounded port range.",
        {
            "start_port": {
                "type": "integer",
                "description": "First port, from 1 to 65535.",
            },
            "end_port": {
                "type": "integer",
                "description": "Last port, from 1 to 65535.",
            },
            "host": {**STRING, "description": "Host to scan, usually 127.0.0.1."},
        },
    ),
    function_tool(
        "run_command",
        "Execute a shell command after the permission policy allows it.",
        {"command": {**STRING, "description": "Shell command."}},
        ["command"],
    ),
]


def ask_llm(messages):
    logger.info("Sending Groq request; message_count=%d", len(messages))
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="qwen/qwen3.8-27b",
            tools=tools,
            tool_choice="auto",
        ).choices[0].message
        logger.info("Groq request completed; tool_call_count=%d", len(response.tool_calls or []))
        return response
    except Exception:
        logger.exception("Groq request failed")
        raise


if set(TOOL_REGISTRY) != {tool["function"]["name"] for tool in tools}:
    raise RuntimeError("Groq tools and TOOL_REGISTRY are out of sync.")