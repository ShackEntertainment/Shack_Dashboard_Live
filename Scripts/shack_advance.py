import json, sys
code = sys.argv[1] if len(sys.argv) > 1 else 'DEAL-SHOWCASE01'
p = rf'C:\Users\Bola\Documents\Shack_Project\Data\deals\{code}.json'
with open(p, encoding='utf-8') as f:
    card = json.load(f)
st = card['status']
nxt = st['current_stage'] + 1
st['gates_passed'].append(nxt)
st['current_stage'] = nxt
with open(p, 'w', encoding='utf-8') as f:
    json.dump(card, f, indent=2)
print(f'GATE S{nxt} PASSED — {code} now at stage {nxt}.')