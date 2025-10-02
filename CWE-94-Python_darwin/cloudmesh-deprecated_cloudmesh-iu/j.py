from cloudmesh.common.Shell import Shell
import subprocess
import asyncio
import sys
from subprocess import PIPE, Popen
import threading
from queue import Queue, Empty
import time
import os
import shlex

host = "r-003"
port = 9010

command = f'ssh juliet "ssh {host} ./ENV3/bin/jupyter-lab --ip localhost --port {port}"'
# command = f'ssh juliet "ssh {host} ./ENV3/bin/jupyter-lab --ip 0.0.0.0 --port {port}"'

# command = f'jupyter-lab --ip localhost --port {port} --no-browser'


localcommand = "ssh -L 9000:{host}:9000 -i {file} juliet"  # juliet = <username>@juliet.futuresystems.org


def live(command):
    file = None
    localhost = None
    process = subprocess.Popen(shlex.split(command),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    printed = False
    while True:
        output = process.stderr.readline()
        if output == b'' and process.poll() is not None:
            break
        if "file://" in str(output):
            file = output.strip().decode(encoding="utf-8")
        if "localhost" in str(output):
            localhost = output.strip().decode(encoding="utf-8")
        if file is not None and localhost is not None and not printed:
            print('File:', file)
            localhost = "http://" + localhost.split("http://")[1]
            print('Localhost:', localhost)
            printed = True
            # start jupyter
            jupyter = localcommand.format(host=host, file=file)
            print(jupyter)
            os.system(jupyter)
    rc = process.poll()


live(command)

"""
print (' '.join(c))
import subprocess
proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
while proc.poll() is None:
    output = proc.stdout.readline()
    e = proc.stderr.readline()
    print (output)
    print (e)
"""

"""
# os.system(f'ssh juliet "ssh {host} ./ENV3/bin/jupyter-lab --ip localhost --port {port}"')


p = await asyncio.create_subprocess_exec("ssh",  "juliet",
           f"ssh {host} ./ENV3/bin/jupyter-lab --ip localhost --port {port}",
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          universal_newlines=True)

output, errors = p.communicate()

print (output)
print (errors)
"""
