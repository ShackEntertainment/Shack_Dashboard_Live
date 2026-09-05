import asyncio, os
import edge_tts

TEXT = ("Bola. Two decisions await your approval. The SpiritCo contract is compliant. "
        "The venue hold expires on Friday. I recommend we sign today. "
        "Nothing moves without your word.")

out = r'C:\Users\Bola\Documents\Shack_Project\Data'

async def main():
    voices = await edge_tts.list_voices()
    gb = [v for v in voices if v['Locale'] == 'en-GB']
    print('en-GB company:')
    for v in gb:
        print('  ', v['ShortName'], '-', v['Gender'])
    for v in gb:
        name = v['ShortName'].split('-')[-1].replace('Neural', '').lower()
        await edge_tts.Communicate(TEXT, v['ShortName']).save(
            os.path.join(out, f'cos_audition_{name}.mp3'))
        print('saved', name)

asyncio.run(main())