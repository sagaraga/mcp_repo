from fastmcp import FastMCP

mcp = FastMCP(name="Arithmetic MCP Server")

@mcp.tool
async def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.tool
async def subtract(a: int, b: int) -> int:
    """Subtract two integers."""
    return a - b

@mcp.tool
async def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

@mcp.tool
async def divide(a: int, b: int) -> float:
    """Divide two integers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b        

if __name__ == "__main__":
    mcp.run()



    # "Arithmetic MCP Server": {
    #   "command": "/Library/Frameworks/Python.framework/Versions/3.12/bin/uv",
    #   "args": [
    #     "run",
    #     "--with",
    #     "fastmcp",
    #     "fastmcp",
    #     "run",
    #     "/Users/sivasagar/WorkSpace/math-local-mcp-server/main.py"
    #   ],
    #   "env": {},
    #   "transport": "stdio",
    #   "type": null,
    #   "cwd": null,
    #   "timeout": null,
    #   "description": null,
    #   "icon": null,
    #   "authentication": null
    # }