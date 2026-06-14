import os
import ast
import re
from fastmcp import FastMCP

# Initialize the Ousia Core Server
mcp = FastMCP("Ousia")

def is_container_signature(sig: str) -> bool:
    """Checks if the signature indicates a container block (class, struct, interface, etc.)."""
    sig = sig.strip()
    if "=>" in sig:
        return False
    if re.search(r'\b(function|fn|func|constructor)\b', sig):
        return False
    if re.search(r'\b(class|struct|interface|enum|namespace|impl|type|extern|union|protocol|extension|module)\b', sig):
        return True
    return False

def shred_generic(content: str) -> str:
    """A high-speed structural block optimizer for JS, TS, Go, and Rust."""
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_line_comment = False
    in_block_comment = False
    escaped = False
    
    signature_buffer = []
    state_stack = []  # True for shredded block, False for container
    output = []
    
    i = 0
    n = len(content)
    
    while i < n:
        char = content[i]
        
        # 1. Handle active comments
        if in_line_comment:
            if char == '\n':
                in_line_comment = False
                if not any(state_stack):
                    output.append(char)
            else:
                if not any(state_stack):
                    output.append(char)
            i += 1
            continue
            
        if in_block_comment:
            if char == '*' and i + 1 < n and content[i+1] == '/':
                in_block_comment = False
                if not any(state_stack):
                    output.append("*/")
                i += 2
                continue
            else:
                if not any(state_stack):
                    output.append(char)
            i += 1
            continue
            
        # 2. Handle active strings
        if in_single_quote:
            if not any(state_stack):
                output.append(char)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '\'':
                in_single_quote = False
            i += 1
            continue
            
        if in_double_quote:
            if not any(state_stack):
                output.append(char)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                in_double_quote = False
            i += 1
            continue
            
        if in_backtick:
            if not any(state_stack):
                output.append(char)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '`':
                in_backtick = False
            i += 1
            continue
            
        # 3. Detect start of comments and strings
        if char == '/' and i + 1 < n and content[i+1] == '/':
            in_line_comment = True
            if not any(state_stack):
                output.append("//")
            i += 2
            continue
            
        if char == '/' and i + 1 < n and content[i+1] == '*':
            in_block_comment = True
            if not any(state_stack):
                output.append("/*")
            i += 2
            continue
            
        if char == '\'':
            in_single_quote = True
            escaped = False
            if not any(state_stack):
                output.append(char)
            i += 1
            continue
            
        if char == '"':
            in_double_quote = True
            escaped = False
            if not any(state_stack):
                output.append(char)
            i += 1
            continue
            
        if char == '`':
            in_backtick = True
            escaped = False
            if not any(state_stack):
                output.append(char)
            i += 1
            continue
            
        # 4. Handle braces and code logic (outside comments/strings)
        if char == '{':
            sig = "".join(signature_buffer)
            signature_buffer = []
            
            if any(state_stack):
                state_stack.append(True)
            else:
                if is_container_signature(sig):
                    state_stack.append(False)
                    output.append(char)
                else:
                    output.append(" { /* ... [Ousia: Implementation details hidden to save context tokens] ... */ }")
                    state_stack.append(True)
                    
        elif char == '}':
            signature_buffer = []
            if state_stack:
                was_shredded = state_stack.pop()
                if not was_shredded and not any(state_stack):
                    output.append(char)
            else:
                if not any(state_stack):
                    output.append(char)
                    
        elif char in (';', ','):
            signature_buffer = []
            if not any(state_stack):
                output.append(char)
                
        else:
            if not any(state_stack):
                signature_buffer.append(char)
                output.append(char)
                
        i += 1
        
    return "".join(output)

def shred_python(content: str) -> str:
    """Uses Python's native Abstract Syntax Tree (AST) to cleanly strip out method bodies."""
    try:
        tree = ast.parse(content)
        class ASTShredder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                self.generic_visit(node)
                docstring = ast.get_docstring(node)
                new_body = []
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        new_body.append(child)
                has_structure = any(isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for c in new_body)
                if not has_structure:
                    if docstring:
                        new_body = [ast.Expr(value=ast.Constant(value=docstring)), ast.Pass()]
                    else:
                        new_body = [ast.Pass()]
                else:
                    if docstring:
                        new_body.insert(0, ast.Expr(value=ast.Constant(value=docstring)))
                node.body = new_body
                return node
                
            def visit_AsyncFunctionDef(self, node):
                return self.visit_FunctionDef(node)
                
        tree = ASTShredder().visit(tree)
        return ast.unparse(tree)
    except Exception as e:
        return f"# [Ousia Parsing Error]: {e}\n{content}"

@mcp.tool()
def get_code_skeleton(file_path: str) -> str:
    """
    Parses a local source file and strips out its function and method bodies.
    Returns only structural interfaces and signatures to cut token consumption.
    """
    normalized_path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.exists(normalized_path):
        return f"Error: Target file not found at {normalized_path}"
        
    if os.path.getsize(normalized_path) > 5 * 1024 * 1024:
        return f"/* [Ousia Notice]: File too large ({os.path.getsize(normalized_path)} bytes). Use get_full_file. */"
        
    with open(normalized_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    ext = os.path.splitext(normalized_path)[1].lower()
    
    if ext == ".py":
        return shred_python(content)
    elif ext in [".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cpp", ".c"]:
        return shred_generic(content)
    else:
        if len(content.splitlines()) < 80:
            return content
        return f"/* [Ousia Notice]: {ext} file hidden to preserve token budget. Use get_full_file to inspect raw source. */"

@mcp.tool()
def get_full_file(file_path: str) -> str:
    """
    Retrieves the raw, full, un-shredded source code of a file.
    Use this ONLY when you are actively modifying, debugging, or updating logic inside this specific file.
    """
    normalized_path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.exists(normalized_path):
        return f"Error: Target file not found at {normalized_path}"
        
    with open(normalized_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()