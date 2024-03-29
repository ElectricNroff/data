import sys
import os
import json
import requests

g_api_key = os.environ['G_READ_API_KEY']

repo = sys.argv[1]
filename = sys.argv[2]
path_ending = 'last_run_shas/' + repo + '/' + filename
u = 'https://api.github.com/repos/ElectricNroff/data/contents/' + path_ending
h = {}
h['Accept'] = 'application/vnd.github+json'
h['X-GitHub-Api-Version'] = '2022-11-28'
h['Authorization'] = 'Bearer ' + g_api_key
r = requests.get(u, headers=h)
s = r.status_code
if s != 200:
    sys.atderr.write('failed to retrieve ' + path_ending + ' via API: ' + str(s))
    exit()
j = r.json()
c = j['content']
with open('.base64-encoded', 'w') as b64_f:
    b64_f.write(c + '\n')
cmd = 'openssl base64 -d -in .base64-encoded -out .not-encoded'
os.system(cmd)
sha = ''
with open('.not-encoded') as not_f:
    sha = not_f.readline().strip()
print(sha)
