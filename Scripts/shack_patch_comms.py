import os, re
p = r'C:\Users\Bola\Documents\Shack_Project\Scripts\shack_mail_bridge.py'
src = open(p, encoding='utf-8').read()

FUNC = '''def _comms_reply(fname, subject, body, kind):
    """[COMMSWIRE] 2026-08-15 — Communications workspace drafts the reply.
    Returns None on ANY failure; caller falls back to approved templates."""
    try:
        import requests
        akey = os.getenv('ANYTHINGLLM_API_KEY', '')
        aurl = os.getenv('ANYTHINGLLM_URL', 'http://localhost:3001')
        if not akey:
            return None
        r = requests.get(aurl + '/api/v1/workspaces',
                         headers={'Authorization': 'Bearer ' + akey},
                         timeout=15)
        slug = None
        for ws in r.json().get('workspaces', []):
            if 'communication' in ws['name'].lower():
                slug = ws['slug']
        if not slug:
            return None
        prompt = (
            "Draft a warm, professional reply email for Shack "
            f"Entertainment. Sender name: {fname}. Subject: {subject}. "
            f"Their message: {body[:1500]}\\n\\n"
            "Return ONLY the email body text. No subject line, no "
            "quotation marks around it, no sign-off or name at the end "
            "(the signature is added automatically).")
        r2 = requests.post(aurl + f'/api/v1/workspace/{slug}/chat',
                           headers={'Authorization': 'Bearer ' + akey,
                                    'Content-Type': 'application/json'},
                           json={'message': prompt, 'mode': 'chat'},
                           timeout=60)
        txt = (r2.json().get('textResponse') or '').strip()
        if len(txt) < 40:
            return None
        return txt[:2000]
    except Exception as e:
        print(f"comms draft fallback: {e}")
        return None


'''

i = src.find('def _comms_reply')
j = src.find('def check_mail')
if j == -1:
    print('FATAL: check_mail not found')
elif i == -1 or i > j:
    src = src[:j] + FUNC + src[j:]
    print('Function inserted fresh')
else:
    src = src[:i] + FUNC + src[j:]
    print('Mangled region replaced')

pat = re.compile(
    r"([ \t]*)f\.write\('TEMPLATE: ' \+ tpl \+ '\\n'\)\n"
    r"[ \t]*f\.write\('---BODY---\\n'\)\n"
    r"[ \t]*f\.write\(TEMPLATES\[tpl\]\.format\(name=fname\)\)")
if "comms = _comms_reply" in src:
    print('Edit2 already present')
else:
    m = pat.search(src)
    if m:
        ind = m.group(1)
        NEW = (ind + "comms = _comms_reply(fname, subject, body, cfg['kind'])\n"
               + ind + "f.write('TEMPLATE: ' + tpl + ('+comms' if comms else '') + '\\n')\n"
               + ind + "f.write('---BODY---\\n')\n"
               + ind + "if comms:\n"
               + ind + "    f.write(comms + '\\n')\n"
               + ind + "else:\n"
               + ind + "    f.write(TEMPLATES[tpl].format(name=fname))")
        src = src[:m.start()] + NEW + src[m.end():]
        print('Edit2 applied by patcher')
    else:
        print('WARNING: Edit2 block not found — check manually')

open(p, 'w', encoding='utf-8').write(src)
print('PATCHED OK')