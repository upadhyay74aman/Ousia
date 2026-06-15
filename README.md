# Ousia MCP Server

Ousia is a high-performance **Model Context Protocol (MCP)** server built to optimize LLM context window token usage by generating structural code skeletons from source files.

It strips out execution details (function and method bodies) while retaining structural elements (class definitions, function signatures, docstrings, interfaces, and nested structures). This allows LLMs to understand the architecture of large codebases with minimal token consumption.

## Features

- **Python AST Parser:** Uses Python's native Abstract Syntax Tree (AST) to remove function/method bodies while preserving docstrings, signature types, and nested definitions (inner functions/classes).
- **C-Family/Generic State-Machine Parser:** Utilizes a custom single-pass scanner to parse JS, TS, Go, Rust, Java, C++, and C. It ignores comments and string contents when tracking block boundaries, preventing issues with curly braces in text.
- **Structural Integrity:** Retains container blocks (`class`, `struct`, `interface`, `enum`, `impl`, `type`, etc.) while stripping method bodies.
- **Token Efficiency:** Drops overall context consumption by up to 90% for typical source codebases.

## Exposed MCP Tools

1. **`get_code_skeleton(file_path: str) -> str`**: Returns the structural skeleton of the target file.
2. **`get_full_file(file_path: str) -> str`**: Returns the raw, unmodified source code (use when editing or debugging a file).

## Token Savings Benchmark

Using `get_code_skeleton` drastically lowers token consumption for LLMs during context initialization. Here is a benchmark using `ousia_server.py` as an example:

| File Mode | File Size (Chars) | Estimated Tokens | Token Cost |
| :--- | :--- | :--- | :--- |
| **Full Source File** | 8,544 | ~2,136 tokens | 100% |
| **Ousia Skeleton** | 1,008 | ~252 tokens | **11.8%** |
| **Total Savings** | **-7,536 chars** | **-1,884 tokens** | **88.2% reduction** |

For larger files containing long, verbose function/method bodies, Ousia often reaches **90% to 95%+ token reductions**.


---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/Ousia.git
   cd Ousia
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Integrating with Claude Desktop App

Since most users interact with Claude via the desktop GUI application rather than a command line, you need to register Ousia as an MCP server in Claude Desktop's configuration file.

### 1. Locate your Claude Desktop Config File
Open your file manager or terminal and find the **`claude_desktop_config.json`** file at the following path:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json` (e.g. `C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json`)
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### 2. Configure Ousia
Open the file in a text editor and add the following server config to the `mcpServers` object:

#### Windows Configuration
```json
{
  "mcpServers": {
    "ousia": {
      "command": "C:\\path\\to\\Ousia\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\Ousia\\ousia_server.py"
      ]
    }
  }
}
```

#### macOS / Linux Configuration
```json
{
  "mcpServers": {
    "ousia": {
      "command": "/path/to/Ousia/.venv/bin/python",
      "args": [
        "/path/to/Ousia/ousia_server.py"
      ]
    }
  }
}
```

> [!IMPORTANT]
> **Why use the `.venv` path?** 
> If you configure the command simply as `"python"`, Claude Desktop will call your system's global Python environment, which does not have the `fastmcp` dependency installed, causing Ousia to fail to start. Explicitly pointing the command to the `.venv` folder's Python executable ensures it runs with all required dependencies out-of-the-box.

### 3. Restart Claude
1. Fully close Claude Desktop (ensure it is quit from your system tray or menu bar).
2. Open Claude Desktop.
3. You will see a small plug icon in the bottom-right of the chat box showing that Ousia is connected!

