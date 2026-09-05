import asyncio, os
import edge_tts

TEXT = ("Bola. Two decisions await your approval. The SpiritCo contract is compliant. "
        "The venue hold expires on Friday. I recommend we sign today. "
        "Nothing moves without your word.")

REEL = [
    ('en-GB-ThomasNeural',   'gb_thomas'),
    ('en-GB-RyanNeural',     'gb_ryan'),
    ('en-IE-ConnorNeural',   'ie_connor'),
    ('en-AU-WilliamNeural',  'au_william'),
    ('en-AU-DarrenNeural',   'au_darren'),
    ('en-NZ-MitchellNeural', 'nz_mitchell'),
    ('en-ZA-LukeNeural',     'za_luke'),
    ('en-CA-LiamNeural',     'ca_liam'),
    ('en-US-ChristopherNeural', 'us_christopher'),
    ('en-US-RogerNeural',    'us_roger'),
    ('en-US-GuyNeural',      'us_guy'),
    ('en-US-SteffanNeural',  'us_steffan'),
    ('en-IN-PrabhatNeural',  'in_prabhat'),
    ('en-SG-WayneNeural',    'sg_wayne'),
    ('en-IE-EmilyNeural',    'ie_emily'),
    ('en-AU-NatashaNeural',  'au_natasha'),
]

out = r'C:\Users\Bola\Documents\Shack_Project\Data'

async def main():
    for voice, name in REEL:
        try:
            await edge_tts.Communicate(TEXT, voice).save(
                os.path.join(out, f'cos_audition_{name}.mp3'))
            print('saved', name)
        except Exception as e:
            print('missed', name, '-', e)

asyncio.run(main())