#!/usr/bin/env python3

import etcd, sys, os

def hasenv(name):
    return os.getenv(name) != None

IS_DEVOPSRELPEASE = hasenv('DEVOPS_RELEASE')
IS_DEVOPSDEVELOP = not IS_DEVOPSRELPEASE and hasenv('DEVOPS')
IS_DEVOPS = hasenv('DEVOPS')
IS_LOCAL = not IS_DEVOPS

cli = None
if IS_LOCAL:
    cli = etcd.Client(host='develop.91egame.com', port=2379)
else:   
    cli = etcd.Client(host='etcd', port=2379)

def wait(path):
    while 1:
        chg = cli.watch(path, recursive=True)
        print(chg)        

wait(sys.argv[1])
