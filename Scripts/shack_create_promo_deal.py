import json, os
project_root = r'C:\Users\Bola\Documents\Shack_Project'
card = {
    "deal": "DEAL-PROMO01",
    "client": "Internal Shack Test",
    "summary": "90-second Brand Anthem video. Requires location scouting, B-roll of live shows, and interviews with artists. Purpose: stress-test the Film Director's integration and multi-deal concurrency.",
    "constraints": [
        "SHACK BRAND CARD",
        "REVENUE DOCTRINE v1 applies",
        "Visuals must reflect fringe-literacy, no corporate gloss"
    ],
    "status": {"current_stage": 0, "gates_passed": []},
    "stages": [
        {"stage": 1, "name": "triage_and_concept", "tasks": [
            {"agent": "cos", "action": "triage_and_plan", "params": {}},
            {"agent": "content", "action": "script_and_storyboard", "params": {}}
        ]},
        {"stage": 2, "name": "production_logistics", "tasks": [
            {"agent": "le", "action": "location_scouting", "params": {}},
            {"agent": "film", "action": "shot_list_and_gear", "params": {}}
        ]},
        {"stage": 3, "name": "post_and_review", "tasks": [
            {"agent": "film", "action": "edit_notes_and_grading", "params": {}},
            {"agent": "cos", "action": "final_deal_review", "params": {}}
        ]}
    ]
}
path = os.path.join(project_root, 'Data', 'deals', 'DEAL-PROMO01.json')
with open(path, 'w') as f: json.dump(card, f, indent=4)
print('Test deal DEAL-PROMO01 created.')