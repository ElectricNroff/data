import sys
import os
import json
import requests

g_api_key = os.environ['G_WRITE_API_KEY']
filename = sys.argv[1]
contributor = sys.argv[2]
basename = os.path.basename(filename)
content = ''
with open(filename) as input_f:
    content = input_f.read()

primary_repo = 'ElectricNroff/data'
u = 'https://api.github.com/repos/' + primary_repo + '/contents/references/' + contributor + '-' + basename
h = {}
h['Accept'] = 'application/vnd.github+json'
h['X-GitHub-Api-Version'] = '2022-11-28'
h['Authorization'] = 'Bearer ' + g_api_key
j = {}
j['message'] = 'a contributed reference'
with open('.not-encoded', 'w') as not_f:
    not_f.write(content + '\n')
cmd = 'openssl base64 -in .not-encoded -out .base64-encoded'
os.system(cmd)
base64_original = ''
with open('.base64-encoded') as b64_f:
    base64_original = b64_f.read()
print('Original:\n' + base64_original)
base64_lines = base64_original.split('\n')
k = 0
base64_data = ''
for line in base64_lines:
    k = k + 1
    print(str(k) + ': ' + '"' + line + '"')
    base64_data += line
print('all on one line: "' + base64_data + '"')
j['content'] = base64_data
data = json.dumps(j)
r = requests.put(u, headers=h, data=data)
s = r.status_code
if s != 201:
    print('failed to add ' + u + ' via API: ' + str(s))
    exit()
print(filename + ' added: ' + content)
