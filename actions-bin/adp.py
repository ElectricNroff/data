import sys
import os
import json
import requests
import shutil

with open(sys.argv[2], 'r', encoding='utf-8') as f:
    filename = os.path.basename(sys.argv[2])
    ws = os.environ['GITHUB_WORKSPACE']
    original_path = ws + '/' + sys.argv[1] + '/' + filename
    rbp_path = ws + '/rbp/' + filename
    shutil.copyfile(original_path, rbp_path)

    all = f.readline()
    obj = json.loads(all)
    u = obj['URL']
    cve = obj['id']
    h = {}
    h['Content-type'] = 'application/json'
    h['CVE-API-ORG'] = 'secretariat-reference'
    h['CVE-API-USER'] = 'u@secretariat-reference.example.com'
    h['CVE-API-KEY'] = os.environ['A_API_KEY']

    print('Retrieving placeholder for ' + cve)
    s = 'https://a.vulnerability.info/api/cve/'

    # url_get = s + cve
    # for testing, map all references to one of 10 CVE Records
    fake_cve = 'CVE-2023-2001' + cve[-1]
    url_get = s + fake_cve
    
    r = requests.get(url_get)
    gr = r.json()
    gs = r.status_code
    print(cve + ': GET status ' + str(gs) + ' for ' + json.dumps(gr))
    if gs == 404:
        print(f'{cve} not found (may be RBP); cannot add ADP container')
        exit()
    elif gs != 200:
        print(f'{cve} published record was not successfully retrieved ({gs}); cannot add ADP container')
        exit()

    oldrefs = set()
    for oldref in gr['containers']['cna']['references']:
        ru = oldref['url']
        print(cve + ': from CNA: ' + ru)
        oldrefs.add(ru)

    has_adp_container = False
    # this is zero because there is only one ADP in the system today
    index = 0
    # this specific ADP is not expected to ever have an ADP container that lacks a references property
    if 'adp' in gr['containers'] and 'references' in gr['containers']['adp'][index]:
        has_adp_container = True
        for oldref in gr['containers']['adp'][index]['references']:
            ru = oldref['url']
            print(cve + ': from ADP: ' + ru)
            oldrefs.add(ru)
    else:
        print(cve + ' has no ADP container yet, or one without references')

    if u in oldrefs:
        print(cve + ': found reference ' + u + ' is a duplicate')
    else:
        print(cve + ': found reference ' + u + ' is new')        

        # url_put = s + cve + '/adp'
        # for testing, map all references to one of 10 CVE Records
        url_put = s + fake_cve + '/adp'

        j = '{"adpContainer": {"references": [{"url": "' + u + '"}]}}'
        if has_adp_container:
            current_adp_c = gr['containers']['adp'][index]
            s_jref = '{"url": "' + u + '"}'
            jref = json.loads(s_jref)
            current_adp_c['references'].append(jref)
            j = '{"adpContainer": {"references": ' + json.dumps(current_adp_c['references']) + '}}'            
        print(cve + ': Doing PUT of ADP container ' + j)
        r = requests.put(url_put, headers=h, data=j)
        pr = r.json()
        ps = r.status_code
        print(cve + ': PUT status ' + str(ps) + ' for ' + json.dumps(pr))
