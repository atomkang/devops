#!/usr/bin/env python3

import sys, psutil, os

filter = sys.argv[1]

for pid in psutil.pids():
    p = psutil.Process(pid)
    cmds = p.cmdline()
    cmd = " ".join(cmds)
    if cmd.find(filter) != -1:        
        if input("kill " + cmd + "? ") != "N":
            os.system("kill " + str(pid))
