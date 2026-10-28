# -*- coding: utf-8 -*-
"""GitHub Git Data API 推送（修复中文路径）：blob 已存在的会复用。"""
import os,sys,json,base64,subprocess,urllib.request,urllib.error

REPO='anyeshengxiao/qs-robot-proto'
ROOT=r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto'
os.chdir(ROOT)

p=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n',
                 capture_output=True,text=True)
creds=dict(l.split('=',1) for l in p.stdout.strip().splitlines() if '=' in l)
AUTH=base64.b64encode(('%s:%s'%(creds['username'].strip(),creds['password'].strip())).encode()).decode()

def api(method,path,data=None):
    req=urllib.request.Request('https://api.github.com/repos/%s%s'%(REPO,path),
        method=method,
        headers={'Authorization':'Basic '+AUTH,'Accept':'application/vnd.github+json',
                 'User-Agent':'git-data-push','X-GitHub-Api-Version':'2022-11-28'},
        data=json.dumps(data).encode() if data is not None else None)
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print('HTTP',e.code,e.read().decode()[:300]); raise

def git(*a):
    return subprocess.run(['git','-c','core.quotepath=false']+list(a),capture_output=True).stdout.decode('utf-8').strip()

HEAD=git('rev-parse','HEAD')
REMOTE=api('GET','/git/ref/heads/main')['object']['sha']
print('local',HEAD[:8],'remote',REMOTE[:8])
if REMOTE==HEAD: print('up to date'); sys.exit(0)

files=git('diff','--name-only',REMOTE,HEAD).splitlines()
print('files:',len(files))

for f in files:
    content=subprocess.run(['git','show','%s:%s'%(HEAD,f)],capture_output=True).stdout
    assert content,'empty content '+f
    r=api('POST','/git/blobs',{'content':base64.b64encode(content).decode(),'encoding':'base64'})
    print('blob',f,r['sha'][:8])

def ls_tree(rev):
    entries=[]
    for line in git('ls-tree',rev).splitlines():
        meta,path=line.split('\t',1)
        mode,typ,sha=meta.split()
        entries.append({'path':path,'mode':mode,'type':typ,'sha':sha})
    return entries

dirs=set([''])
for f in files:
    parts=f.split('/')[:-1]
    for i in range(1,len(parts)+1): dirs.add('/'.join(parts[:i]))

root_sha=None
for d in sorted(dirs,key=lambda x:(x=='',-x.count('/'),x)):
    rev=('%s:%s'%(HEAD,d)) if d else (HEAD+'^{tree}')
    r=api('POST','/git/trees',{'tree':ls_tree(rev)})
    print('tree',d or '(root)',r['sha'][:8])
    if d=='': root_sha=r['sha']

msg=git('log','-1','--pretty=%B',HEAD)
cm=api('POST','/git/commits',{'message':msg,'tree':root_sha,'parents':[REMOTE]})
print('commit',cm['sha'])
api('PATCH','/git/refs/heads/main',{'sha':cm['sha'],'force':False})
print('REF UPDATED')
