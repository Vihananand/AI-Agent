import ast
import hashlib
import math
import os
import shutil
import socket
import subprocess
import time
from datetime import datetime


def calculate(expression: str) -> str:
    # Calculate arithmetic without executing arbitrary Python code.
    operators = {
        ast.Add: lambda left, right: left + right,
        ast.Sub: lambda left, right: left - right,
        ast.Mult: lambda left, right: left * right,
        ast.Div: lambda left, right: left / right,
        ast.FloorDiv: lambda left, right: left // right,
        ast.Mod: lambda left, right: left % right,
        ast.Pow: lambda left, right: left ** right,
    }
    unary_operators = {ast.UAdd: lambda value: value, ast.USub: lambda value: -value}

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if not math.isfinite(node.value): 
                raise ValueError("Only finite numbers are supported.")
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large.")
            return operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_operators:
            return unary_operators[type(node.op)](evaluate(node.operand))
        raise ValueError("Only basic arithmetic expressions are supported.")

    try:
        tree = ast.parse(expression, mode="eval")
        return str(evaluate(tree))
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
        return f"Error: {error}"


def get_current_time() -> str:
    # Get the current local system time.
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def list_files(directory: str = ".") -> str:
    # List files and directories inside a directory.
    try:
        files = sorted(os.listdir(directory))
        return "\n".join(files) if files else "Directory is empty."
    except OSError as error:
        return f"Error: {error}"


def read_file(file_path: str) -> str:
    # Read the contents of a text file.
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as error:
        return f"Error: {error}"


def create_file(file_path: str) -> str:
    # Create an empty file.
    try:
        with open(file_path, "x", encoding="utf-8"):
            pass
        return f"File created successfully: {file_path}"
    except FileExistsError:
        return f"File already exists: {file_path}"
    except OSError as error:
        return f"Error: {error}"


def write_file(file_path: str, content: str) -> str:
    # Write content to a file, replacing existing content.
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Successfully wrote to {file_path}"
    except OSError as error:
        return f"Error: {error}"


def append_file(file_path: str, content: str) -> str:
    # Append content to an existing file.
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(content)
        return f"Successfully appended to {file_path}"
    except OSError as error:
        return f"Error: {error}"


def create_directory(directory: str) -> str:
    # Create a directory.
    try:
        os.makedirs(directory, exist_ok=False)
        return f"Directory created successfully: {directory}"
    except FileExistsError:
        return f"Directory already exists: {directory}"
    except OSError as error:
        return f"Error: {error}"


def delete_file(file_path: str) -> str:
    # Delete a file.
    try:
        os.remove(file_path)
        return f"File deleted successfully: {file_path}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except OSError as error:
        return f"Error: {error}"


def move_file(source: str, destination: str) -> str:
    # Move a file or directory.
    try:
        shutil.move(source, destination)
        return f"Moved {source} to {destination}"
    except OSError as error:
        return f"Error: {error}"


def copy_file(source: str, destination: str) -> str:
    # Copy a file.
    try:
        shutil.copy2(source, destination)
        return f"Copied {source} to {destination}"
    except OSError as error:
        return f"Error: {error}"


def file_exists(file_path: str) -> str:
    # Check whether a file or directory exists.
    return str(os.path.exists(file_path))


def get_file_info(file_path: str) -> str:
    # Get basic information about a file.
    try:
        stats = os.stat(file_path)
        info = {
            "path": file_path,
            "size_bytes": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "is_directory": os.path.isdir(file_path),
            "is_file": os.path.isfile(file_path),
        }
        return str(info)
    except OSError as error:
        return f"Error: {error}"


def search_files(
    directory: str,
    filename: str,
    max_depth: int = 5,
    max_results: int = 100,
    timeout_seconds: int = 10,
) -> str:
    # Search recursively with depth, result, and time limits.
    if max_depth < 0 or max_results < 1 or timeout_seconds < 1:
        return "Error: search limits must be positive, with max_depth at least zero."
    try:
        started_at = time.monotonic()
        matches = []
        for root, directories, files in os.walk(directory):
            depth = os.path.relpath(root, directory).count(os.sep)
            if depth >= max_depth:
                directories[:] = []
            if filename in files:
                matches.append(os.path.join(root, filename))
                if len(matches) >= max_results:
                    break
            if time.monotonic() - started_at >= timeout_seconds:
                break
        timed_out = time.monotonic() - started_at >= timeout_seconds
        if not matches:
            if timed_out:
                return f"Search timed out after {timeout_seconds} seconds."
            return f"No files named '{filename}' found."
        result = "\n".join(matches)
        if len(matches) >= max_results:
            result += f"\nSearch stopped after {max_results} results."
        elif timed_out:
            result += f"\nSearch timed out after {timeout_seconds} seconds."
        return result
    except OSError as error:
        return f"Error: {error}"


def search_text(file_path: str, text: str, case_sensitive: bool = False) -> str:
    # Find matching lines in a text file.
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        needle = text if case_sensitive else text.lower()
        matches = [
            f"{line_number}: {line.rstrip()}"
            for line_number, line in enumerate(lines, 1)
            if needle in (line if case_sensitive else line.lower())
        ]
        return "\n".join(matches) if matches else "No matches found."
    except OSError as error:
        return f"Error: {error}"


def get_directory_tree(directory: str = ".", max_depth: int = 2) -> str:
    # Return a bounded, readable directory tree.
    if max_depth < 0:
        return "Error: max_depth must be zero or greater."
    try:
        root = os.path.abspath(directory)
        lines = [root]
        for current_root, directories, files in os.walk(root):
            depth = os.path.relpath(current_root, root).count(os.sep)
            if depth >= max_depth:
                directories[:] = []
            indent = "  " * (depth + 1)
            lines.extend(
                f"{indent}{name}" for name in sorted(directories) + sorted(files)
            )
        return "\n".join(lines)
    except OSError as error:
        return f"Error: {error}"


def get_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    # Calculate a file checksum using a hashlib algorithm.
    try:
        digest = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return f"{algorithm}: {digest.hexdigest()}"
    except (FileNotFoundError, ValueError, OSError) as error:
        return f"Error: {error}"


def get_working_directory() -> str:
    # Get the current working directory of the agent.
    return os.getcwd()


def get_environment_info() -> str:
    # Get basic information about the environment running the agent.
    return (
        f"Operating system: {os.name}\n"
        f"Platform: {os.sys.platform}\n"
        f"Python version: {os.sys.version}\n"
        f"Current directory: {os.getcwd()}"
    )


def check_port(port: int) -> str:
    # Check whether a local TCP port is available.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("127.0.0.1", port))
        if result == 0:
            return f"Port {port} is currently in use."
        return f"Port {port} is available."
    except OSError as error:
        return f"Error: {error}"


def list_open_ports(
    start_port: int = 1, end_port: int = 1024, host: str = "127.0.0.1"
) -> str:
    # List open TCP ports on a host within a bounded range.
    if not 1 <= start_port <= end_port <= 65535:
        return "Error: ports must be between 1 and 65535, with start_port first."
    if end_port - start_port > 2048:
        return "Error: port range cannot exceed 2048 ports."

    open_ports = []
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.05)
                if sock.connect_ex((host, port)) == 0:
                    open_ports.append(str(port))
        except OSError:
            continue

    if not open_ports:
        return f"No open TCP ports found on {host} in range {start_port}-{end_port}."
    return f"Open TCP ports on {host}: {', '.join(open_ports)}"


def run_command(command: str) -> str:
    # Execute an approved shell command and return its output.
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return f"{output}\nExit code: {result.returncode}".strip()
    except subprocess.TimeoutExpired:
        return "Error: command timed out."
    except OSError as error:
        return f"Error: {error}"


TOOL_REGISTRY = {
    "calculate": calculate,
    "get_current_time": get_current_time,
    "list_files": list_files,
    "read_file": read_file,
    "create_file": create_file,
    "write_file": write_file,
    "append_file": append_file,
    "create_directory": create_directory,
    "delete_file": delete_file,
    "move_file": move_file,
    "copy_file": copy_file,
    "file_exists": file_exists,
    "get_file_info": get_file_info,
    "search_files": search_files,
    "search_text": search_text,
    "get_directory_tree": get_directory_tree,
    "get_file_hash": get_file_hash,
    "get_working_directory": get_working_directory,
    "get_environment_info": get_environment_info,
    "check_port": check_port,
    "list_open_ports": list_open_ports,
    "run_command": run_command,
}