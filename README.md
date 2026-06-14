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

## Running the Server

You can start the MCP server directly using Python:
```bash
python ousia_server.py
```

### Adding to Claude Desktop

To use Ousia with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ousia": {
      "command": "python",
      "args": [
        "C:/path/to/Ousia/ousia_server.py"
      ]
    }
  }
}
```
*(Make sure to replace `C:/path/to/Ousia` with the absolute path to your repository).*
