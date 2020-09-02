#!/usr/bin/env python3

import os, etcd, json, time, platform, threading, uuid, socket, re, shutil, redis, subprocess

def hasenv(name):
    return os.getenv(name) != None

IS_DEVOPSRELPEASE = hasenv('DEVOPS_RELEASE')
IS_DEVOPSDEVELOP = not IS_DEVOPSRELPEASE and hasenv('DEVOPS')
IS_DEVOPS = hasenv('DEVOPS')
IS_LOCAL = not IS_DEVOPS

if IS_DEVOPSRELPEASE:
    PERMISSION_TTL = 30 * 60 # 30minutes
    REGISTER_TTL = 25
    RETRY_DELAY = 5
else:
    PERMISSION_TTL = 30
    REGISTER_TTL = 25
    RETRY_DELAY = 5

def connectEtcd():
    cli = None
    if IS_LOCAL:
        cli = etcd.Client(host='develop.91egame.com', port=2379)
    else:   
        cli = etcd.Client(host='etcd', port=2379)
    return cli

def doRefreshPermissions():
    index = None           
    while 1:        
        try:
            cli = connectEtcd()  
            while 1:
                chg = cli.watch('/devops/permission/', index=index, recursive=True, timeout=0)
                print("permission changed")
                index = chg.modifiedIndex + 1
                print(chg)
        except Exception as exc:
            print(exc)
            time.sleep(RETRY_DELAY)
        
doRefreshPermissions()
