"""
SHACK ENTERTAINMENT — shack_registry_mcp.py
Agent Registry: the Conductor's roster. Read-only.
"""
import os, json
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
REG = os.path.join(project_root, 'Data', 'agent_registry.json')

mcp = FastMCP('ShackRegistry')

def _load():
    with open(REG, encoding='utf-8') as f:
        return json.load(f)

@mcp.tool()
def list_agents() -> str:
    """List all registered agents and their names."""
    r = _load()
    return ' | '.join(f"{k}: {v['name']}" for k, v in r.items())

@mcp.tool()
def agent_capabilities(agent_id: str) -> str:
    """Return one agent's capabilities, tools and output folder."""
    a = _load().get(agent_id.strip().lower())
    return json.dumps(a) if a else f"No agent '{agent_id}' in registry."

@mcp.tool()
def find_agent_for(action: str) -> str:
    """Find which registered agent owns an action keyword."""
    r = _load()
    hits = [k for k, v in r.items()
            if any(c.replace('_', ' ') in action.lower()
                   or action.lower() in c for c in v['capabilities'])]
    return ', '.join(hits) if hits else 'No registered agent for that action.'

if __name__ == '__main__':
    mcp.run()