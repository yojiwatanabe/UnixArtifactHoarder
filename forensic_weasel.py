import sys
import logging
from datetime import datetime
import os
import subprocess
import shlex

ERROR_CODE = 1
LOG = 'logs/{{{}}}.log'
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


class ArtifactCollector(object):
    def __init__(self):
        print('HERE HERE!')
        self.logger = logging.getLogger()
        self.start_logging()

    #   start_logging()
    #   Begin logging execution
    def start_logging(self):
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s %(levelname)-5s- - - %(message)s')

        file_handler = logging.FileHandler(LOG.replace('{{{}}}', '{date:%Y-%m-%d_%H:%M:%S}'.format(date=datetime.now())))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        clo_handler = logging.StreamHandler()
        clo_handler.setLevel(logging.DEBUG)
        clo_handler.setFormatter(formatter)
        self.logger.addHandler(clo_handler)

        self.logger.info('Started execution')

    def call_commands(self):
        for section in COMMANDS:
            for command in COMMANDS[section]:
                self.logger.info(section.upper() + ' | command: ' + command)
                try:
                    return_code = subprocess.call(shlex.split(command))
                except OSError as e:
                    self.logger.debug('Unknown command: ' + e.filename)
                except subprocess.CalledProcessError as e:
                    self.logger.debug('Could not find command!')
                if return_code == ERROR_CODE:
                    self.logger.debug('File does not exist, unable to run command: ' + command)


myClass = ArtifactCollector()
myClass.call_commands()
