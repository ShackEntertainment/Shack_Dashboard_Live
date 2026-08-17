r"""
SHACK ENTERTAINMENT — voice_shop.py
Records one audition sample per candidate en-GB neural voice into
your user folder as audition_<name>.mp3. Skips any voice that fails.
"""
import os
import asyncio
import edge_tts

OUT = os.path.expanduser('~')

VOICES = [
    'en-GB-ThomasNeural',
    'en-GB-RyanNeural',
    'en-GB-OliverNeural',
    'en-GB-NoelNeural',
    'en-GB-AlfieNeural',
    'en-GB-ElliotNeural',
    'en-GB-EthanNeural',
    'en-GB-KenNeural',
]

async def main():
    for v in VOICES:
        name = v.replace('en-GB-', '').replace('Neural', '')
        path = os.path.join(OUT, f'audition_{name}.mp3')
        try:
            await edge_tts.Communicate(
                f"Hello Bola. I am {name}. This is how I sound for the Shack.",
                v).save(path)
            print('made:', path)
        except Exception as e:
            print(f'skipped {v}: {type(e).__name__}')
        await asyncio.sleep(1)
    print('DONE — play the audition_*.mp3 files and pick your voice.')

asyncio.run(main())