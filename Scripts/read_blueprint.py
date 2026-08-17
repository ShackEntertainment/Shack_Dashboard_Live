import os

# Read the blueprint file
blueprint_path = 'MASTER_AGENT_BLUEPRINT.md'
if os.path.exists(blueprint_path):
    with open(blueprint_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("=== MASTER AGENT BLUEPRINT ===\n")
        print(content[:3000])  # First 3000 chars
else:
    print("Blueprint file not found")

# Read the main agent script
agent_path = 'shack_main_agent.py'
if os.path.exists(agent_path):
    with open(agent_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("\n\n=== SHACK MAIN AGENT ===\n")
        print(content[:2000])  # First 2000 chars
else:
    print("\nMain agent script not found")