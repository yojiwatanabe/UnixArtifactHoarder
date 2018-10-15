import sys
import logging
from datetime import datetime
import os
import subprocess
import shlex

ERROR_CODE = 1
ROOT_DIR = '/'
PRINT_COMMAND = 'find %s -type f -exec cat {} +'
COMMANDS = {'kernel_name_version': ['uname -rs'],
            'kernel modules': ['lsmod'],
            'network interfaces': ['ifconfig -a'],
            'networking information': [PRINT_COMMAND % '/etc/hosts',
                                       PRINT_COMMAND % '/etc/networks',
                                       PRINT_COMMAND % '/etc/protocols',
                                       PRINT_COMMAND % '/etc/ethers',
                                       PRINT_COMMAND % '/etc/netgroup',
                                       PRINT_COMMAND % '/etc/dhclients'],
            'hostname': ['hostname',
                         PRINT_COMMAND % '/etc/hostname']}

for section in COMMANDS:
    for command in COMMANDS[section]:
        print(section.upper())
        print(command)
        try:
            return_code = subprocess.call(shlex.split(command))
        except OSError as e:
            print('Unknown command: ' + e.filename)
        except subprocess.CalledProcessError as e:
            print(e)
            print('Could not find command!')
        if return_code == ERROR_CODE:
            print('File does not exist, unable to run command: ' + command)
