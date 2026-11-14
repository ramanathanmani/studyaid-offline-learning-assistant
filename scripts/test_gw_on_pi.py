import urllib.request, json, time

with open('/home/rock/studyaid/final/passages.json') as f:
    passages = json.load(f)

gw = passages[0]
print('Submitting passage:', gw['title_en'])

req = urllib.request.Request(
    'http://127.0.0.1:8080/api/run',
    data=json.dumps({'text': gw['text']}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    init_res = json.loads(resp.read().decode('utf-8'))

jid = init_res['job']
print('Job ID:', jid)

for _ in range(200):
    time.sleep(2)
    with urllib.request.urlopen(f'http://127.0.0.1:8080/api/job/{jid}') as resp:
        st = json.loads(resp.read().decode('utf-8'))
    stage = st.get('stage')
    print('Polling job:', stage, '...')
    if stage == 'done':
        result = st['result']
        with open('/home/rock/studyaid/final/gw_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print('Job completed successfully on Pi!')
        print('Elapsed:', st.get('elapsed_s'), 's, RSS:', st.get('rss_mb'), 'MB')
        break
    elif stage == 'error':
        print('Job failed with error:', st.get('error'))
        break
