r"""
SHACK ENTERTAINMENT — voice_audit.py
Lists every SAPI voice on this machine and records a sample of each
candidate (Natural / David / Davis / Dave / George / Ryan / Thomas)
as voice_audit_*.wav files in your user folder, so you can pick by ear.
"""
import os
import re
import pyttsx3

OUT = os.path.expanduser('~')

eng = pyttsx3.init()
voices = eng.getProperty('voices')

print("ALL VOICES ON THIS MACHINE:")
for i, v in enumerate(voices):
    print(f"  {i}: {v.name}")
print()

made = 0
for v in voices:
    n = v.name.lower()
    if any(k in n for k in ['natural', 'david', 'davis', 'dave',
                            'george', 'ryan', 'thomas']):
        safe = re.sub(r'[^A-Za-z0-9]+', '_', v.name).strip('_')
        path = os.path.join(OUT, f'voice_audit_{safe}.wav')
        try:
            eng.setProperty('voice', v.id)
            eng.save_to_file(
                f"Hello Bola. I am {v.name}. This is how I sound.", path)
            eng.runAndWait()
            print("  made:", path)
            made += 1
        except Exception as e:
            print(f"  skipped {v.name}: {e}")

if not made:
    print("No candidate voices found. Paste the full list above.")
print("DONE")