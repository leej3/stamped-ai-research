from pathlib import Path
import subprocess,hashlib,json,urllib.request,urllib.parse,datetime
root=Path.cwd(); base=root/'research/retrospective'
annex_uuid=subprocess.check_output(['git','config','--get','remote.con-hub.annex-uuid'],text=True).strip()
paths=[p for folder in ['figures','review'] for p in sorted((base/folder).iterdir()) if p.suffix in {'.png','.pdf','.svg'}]
records=[]
for p in paths:
    key=subprocess.check_output(['git','annex','lookupkey',str(p)],text=True).strip()
    url='https://hub.centerforopenneuroscience.org/git-annex-p2phttp/git-annex/'+annex_uuid+'/key/'+urllib.parse.quote(key,safe='')
    with urllib.request.urlopen(url,timeout=30) as response:
        content=response.read()
        status=response.status
    local=p.read_bytes()
    assert content==local, str(p)
    subprocess.run(['git','annex','registerurl',key,url],check=True,capture_output=True)
    records.append({'path':str(p.relative_to(root)),'key':key,'url':url,'http_status':status,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'matches_local':True})
    print('Verified',p.name,len(content))
(base/'asset-retrieval.json').write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Anonymous full HTTP GET; exact byte comparison; registered URL','objects':records},indent=2)+'\n')
