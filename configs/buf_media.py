import json, httpx, os
from dotenv import load_dotenv
load_dotenv(r'C:\Users\Bola\Documents\Shack_Project\configs\.env', override=True)
k = os.getenv('BUFFER_API_KEY', '')
H = {'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json'}
url = open(r'C:\Users\Bola\Documents\Shack_Project\configs\brand_media_url.txt').read().strip()
print('MEDIA URL:', url)

def gql(q):
    r = httpx.post('https://api.buffer.com', headers=H,
                   json={'query': q}, timeout=30)
    return r.status_code, r.text

oid = json.loads(gql('{ account { organizations { id } } }')[1])['data']['account']['organizations'][0]['id']
chs = json.loads(gql('{ channels(input: { organizationId: "%s" }) { id name service } }' % oid)[1])['data']['channels']
print('CHANNEL:', chs[0]['service'], chs[0]['name'])
text = json.dumps('Media wire test - ignore. #ShackEntertainment')
U = json.dumps(url)

cands = [
    ('mediaUrls',   'mediaUrls: [' + U + ']'),
    ('media_objs',  'media: [{ url: ' + U + ' }]'),
    ('media_strs',  'media: [' + U + ']'),
    ('attachments', 'attachments: [{ url: ' + U + ' }]'),
    ('images',      'images: [' + U + ']'),
]
for name, frag in cands:
    q = ('mutation { createPost(input: { text: ' + text + ', channelId: "' + chs[0]['id'] +
         '", schedulingType: automatic, mode: addToQueue, ' + frag + '}) '
         '{ ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }')
    sc, body = gql(q)
    print(name, '=>', body[:260])
    print('---')
    if '"post":{' in body.replace(' ', ''):
        print('WINNER:', name)
        break