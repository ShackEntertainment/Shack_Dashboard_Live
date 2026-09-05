import json, os
project_root = r'C:\Users\Bola\Documents\Shack_Project'
card = {
    "deal": "DEAL-SHOWCASE01",
    "client": "Internal Shack Test",
    "summary": "Hybrid music and art showcase. 1 full band, 1 solo acoustic, 2 visual artists. Fictional 200-cap venue. Purpose: prove the orchestration pipeline, Rate Card v1, and Revenue Doctrine v1.",
    "constraints": [
        "SHACK BRAND CARD",
        "REVENUE DOCTRINE v1 applies",
        "RATE CARD v1 applies",
        "Event costing template must be filled and attached to reply"
    ],
    "status": {"current_stage": 1, "gates_passed": []},
    "stages": [
        {"stage": 1, "name": "triage_and_strategy", "tasks": [{"agent": "cos", "action": "triage_and_plan", "params": {}}]},
        {"stage": 2, "name": "logistics_and_talent", "tasks": [
            {"agent": "le", "action": "venue_logistics_and_security", "params": {"capacity": 200}},
            {"agent": "au", "action": "talent_booking_and_rider", "params": {"bands": 1, "solo": 1, "artists": 2}}
        ]},
        {"stage": 3, "name": "marketing_and_comms", "tasks": [
            {"agent": "marketing", "action": "exposure_map", "params": {}},
            {"agent": "content", "action": "promo_copy", "params": {}}
        ]},
        {"stage": 4, "name": "finance_and_review", "tasks": [
            {"agent": "ryan", "action": "full_event_costing_and_pnl", "params": {"use_template": True}},
            {"agent": "cos", "action": "final_deal_review", "params": {}}
        ]}
    ]
}
path = os.path.join(project_root, 'Data', 'deals', 'DEAL-SHOWCASE01.json')
with open(path, 'w') as f: json.dump(card, f, indent=4)
print('Test deal DEAL-SHOWCASE01 created.')
