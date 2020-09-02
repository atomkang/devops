#!/usr/bin/env python3

import os, etcd, json, time, platform, threading, uuid, socket, re, shutil, redis, subprocess

def hasenv(name):
    return os.getenv(name) != None

IS_DEVOPSRELPEASE = hasenv('DEVOPS_RELEASE')
IS_DEVOPSDEVELOP = not IS_DEVOPSRELPEASE and hasenv('DEVOPS')
IS_DEVOPS = hasenv('DEVOPS')
IS_LOCAL = not IS_DEVOPS

pidfile = '/work/.register.pid'
if IS_LOCAL:
    pidfile = 'tmp/register.pid'
open(pidfile, 'w').write(str(os.getpid()))

if IS_DEVOPSRELPEASE:
    PERMISSION_TTL = 30 * 60 # 30minutes
    REGISTER_TTL = 25
    RETRY_DELAY = 5
else:
    PERMISSION_TTL = 60 * 10
    REGISTER_TTL = 25
    RETRY_DELAY = 5

def connectEtcd():
    cli = None
    if IS_LOCAL:
        cli = etcd.Client(host='develop.91egame.com', port=2379)
    else:   
        cli = etcd.Client(host='etcd', port=2379)
    return cli

# devops format
# root: /devops/permission/
# { 
#   "path": string <domain>/[path] for access 
#   "subdomain": if true, like vue, nginx will pass <domain>/[path]?<argus> to container like /[path]?<argus>, or pass /?<argus> 
#   "client": default false, allow client connect to this server 
#   "server": default true, allow server connect to this server
# }

# register devops.json for servie finder provided by proxy
def doRegisterDevops():
    while 1:        
        try:
            cli = connectEtcd()
            file = '/work/code/devops.json'
            if IS_LOCAL:
                file = './tmp/devops.json'
            # config file not exists, sleep for next check
            if not os.path.isfile(file):
                time.sleep(REGISTER_TTL)
                continue
            jsdata = ''.join(open(file, 'r').readlines())
            cfg = json.loads(jsdata)
            path = cfg["path"]
            if not path.endswith('/'):
                path += '/'
            key = path + platform.node()
            jsobj = {
                "path": path
            }
            if "subdomain" in cfg:
                jsobj["subdomain"] = cfg["subdomain"]
            if hasenv('BRANCH'):
                jsobj["branch"] = os.getenv('BRANCH')
            print("register devops")
            cli.write(key, json.dumps(jsobj), ttl=REGISTER_TTL+5)                        
            time.sleep(REGISTER_TTL)
        except Exception as exc:
            print(exc)
            time.sleep(RETRY_DELAY)

# register service permission for ACL
def doRegisterPermission():
    while 1:
        try:
            cli = connectEtcd()
            permcfg = {
                'id': uuid.uuid4().hex,
                'host': socket.gethostname(),
                'time': int(time.time())
            }

            # register self
            # add 5s lifetime to prevent call refuse during cfg updating            
            print("refresh permission id " + permcfg['id'])
            cli.write('/devops/permission/' + permcfg['id'], json.dumps(permcfg), ttl=PERMISSION_TTL+5)            

            # write cfg
            file = '/work/run/permission.cfg'
            if IS_LOCAL:
                file = 'run/permission.cfg'
            open(file, 'w').write(json.dumps(permcfg))

            time.sleep(PERMISSION_TTL)
        except Exception as exc:
            print(exc)
            time.sleep(RETRY_DELAY)

RE_PERMISSIONID = re.compile('/devops/permission/(.+)')
REDIS_PERMISSIONIDS = 17

def doRefreshPermissions():
    # save permission to redis
    db = None
    if IS_LOCAL:
        db = redis.Redis(host='localhost', port=6379, db=REDIS_PERMISSIONIDS)
    else:
        db = redis.Redis(host='localhost', port=26379, db=REDIS_PERMISSIONIDS)
    db.flushdb()
    init = True
    index = None
    while 1:
        try:
            cli = connectEtcd()  
            if init:   
                dir = cli.read('/devops/permission/', waitIndex=index)      
                index = dir.etcd_index + 1 # read use etcd_index for init
                for child in dir.children:
                    if child.key == '/devops/permission/':
                        continue
                    res = RE_PERMISSIONID.search(child.key)
                    print("add " + res.group(1))
                    db.set(res.group(1).encode(), child.value.encode()) 
                init = False 
            while 1:
                # wait for changed
                chg = cli.watch('/devops/permission/', index=index, recursive=True, timeout=0)
                print("permission changed")            
                index = chg.modifiedIndex + 1 # for watch
                res = RE_PERMISSIONID.search(chg.key)            
                if chg.action == 'set':
                    print("add " + res.group(1))
                    db.set(res.group(1).encode(), chg.value.encode())
                elif chg.action == 'expire' or chg.action == 'delete':
                    print("delete " + res.group(1))
                    db.delete(res.group(1).encode())
                else:
                    print(chg)                  
        except Exception as exc:
            print(exc)
            time.sleep(RETRY_DELAY)
        
threading.Thread(target=doRegisterDevops).start()
threading.Thread(target=doRegisterPermission).start()
threading.Thread(target=doRefreshPermissions).start()
