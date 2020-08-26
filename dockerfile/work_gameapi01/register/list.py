#!/usr/bin/env python3

import etcd, sys, os

def hasenv(name):
    return os.getenv(name) != None

IS_DEVOPSRELPEASE = hasenv('DEVOPS_RELEASE')
IS_DEVOPS = not IS_DEVOPSRELPEASE and hasenv('DEVOPS')
IS_LOCAL = not IS_DEVOPSRELPEASE and not IS_DEVOPS

cli = None
if IS_LOCAL:
    cli = etcd.Client(host='develop.91egame.com', port=2379)
else:   
    cli = etcd.Client(host='etcd', port=2379)

def list(path):
    dir = cli.read(path)
    for res in dir.children:
        # read(path) return path.....
        if res.key != path:
            #print(res.key)
            if not res.dir:
                print(res.key)
                print(res.value)
            list(res.key)

list(sys.argv[1])
