import asyncio, os
import edge_tts

TEXT = ("Good morning, Bola. Stage four of Showcase One is approved. "
        "Ryan's costing shows Shack's share at eight hundred and fourteen pounds, eighty nine. "
        "Proudly on the fringe. The gate is yours.")

VOICES = {'sonia': 'en-GB-SoniaNeural',
          'libby': 'en-GB-LibbyNeural',
          'thomas': 'en-GB-ThomasNeural',
          'ryan': 'en-GB-RyanNeural'}

out = r'C:\Users\Bola\Documents\Shack_Project\Data'

async def main():
    for name, v in VOICES.items():
        await edge_tts.Communicate(TEXT, v).save(os.path.join(out, f'voice_sample_{name}.mp3'))
        print(name, 'saved')

asyncio.run(main())