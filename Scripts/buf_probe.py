import os, json, httpx
from dotenv import load_dotenv
load_dotenv(r'C:\Users\Bola\Documents\Shack_Project\configs\.env', override=True)
k = os.getenv('BUFFER_API_KEY', '')
H = {'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json'}

def gql(q):
    r = httpx.post('https://api.buffer.com', headers=H,
                   json={'query': q}, timeout=30)
    return r.status_code, r.text

oid = json.loads(gql('{ account { organizations { id } } }')[1])['data']['account']['organizations'][0]['id']
chs = json.loads(gql('{ channels(input: { organizationId: "%s" }) { id name service } }' % oid)[1])['data']['channels']
print('CHANNELS:', [(c['service'], c['name']) for c in chs])
cid = chs[0]['id']
text = json.dumps('Fringe test - ignore. #ShackEntertainment')

q1 = ('mutation { createPost(input: { text: ' + text + ', channelId: "' + cid +
      '", schedulingType: automatic, mode: addToQueue }) '
      '{ ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }')
print('TRY1 (full):', gql(q1))

q2 = ('mutation { createPost(input: { text: ' + text + ', channelId: "' + cid +
      '", mode: addToQueue }) '
      '{ ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }')
print('TRY2 (no sched):', gql(q2))