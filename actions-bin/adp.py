import sys
import os
import json
import requests
import shutil

subdirectory = sys.argv[1]
ref_directory = sys.argv[2]
pathname = sys.argv[3]

with open(pathname, 'r', encoding='utf-8') as f:
    all = f.readline()
    obj = json.loads(all)
    u = obj['URL']
    cve = obj['id']

    # This prod_s 404 code is unrelated to the objective of adding data
    # to ADP containers. However, when a new reference is found, and
    # apparently identifies an RBP, then that information is stored in
    # the rbp directory of the primary repo. When this script is later run in
    # production, the code block here will partially duplicate the
    # functionality of the below requests.get(url_get) code block, and the
    # two should be combined at that point.
    prod_url = 'https://cveawg.mitre.org/api/cve/' + cve
    prod_r = requests.get(prod_url)
    prod_s = prod_r.status_code
    if prod_s == 404:
        filename = os.path.basename(pathname)
        work_dir = os.environ['GITHUB_WORKSPACE'] + '/' + subdirectory
        original_path = work_dir + '/' + ref_directory + '/' + filename
        rbp_path = work_dir + '/rbp/' + filename
        shutil.copyfile(original_path, rbp_path)
        with open('.rbp', 'a') as rbp_f:
            rbp_f.write(filename + '\n')
    
    h = {}
    h['Content-type'] = 'application/json'
    h['CVE-API-ORG'] = 'se-ref-adp-001-mitre'
    h['CVE-API-USER'] = 'eve@se-ref-adp-001-mitre.example.com'
    h['CVE-API-KEY'] = os.environ['A_API_KEY']

    print('Retrieving placeholder for ' + cve)
    s = 'https://cveawg-test.mitre.org/api/cve/'

    # url_get = s + cve
    # for testing, map all references to one of 10 CVE Records
    fake_cve = 'CVE-2023-2103' + cve[-1]
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
    # index zero is correct only if there is only one ADP operating on the CVE-2023-2103[0-9] records
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
