from datetime import datetime
import logging
import subprocess
import shlex

ERROR_CODE = 1
LOG = 'logs/{{{}}}.log'
ROOT_DIR = '/'
PRINT_COMMAND = 'find %s -type f -exec cat {} +'
LIST_COMMAND = 'find %s -type f -exec ls {} +'
COMMANDS = {'kernel_name_version'   : ['uname -rs'],
            'kernel modules'        : ['lsmod'],
            'network interfaces'    : ['ifconfig -a'],
            'networking information': [PRINT_COMMAND % '/etc/hosts',
                                       PRINT_COMMAND % '/etc/networks',
                                       PRINT_COMMAND % '/etc/protocols',
                                       PRINT_COMMAND % '/etc/ethers',
                                       PRINT_COMMAND % '/etc/netgroup',
                                       PRINT_COMMAND % '/etc/dhclients'],
            'hostname'              : ['hostname',
                                       PRINT_COMMAND % '/etc/hostname'],
            'login history'         : ['last -Faixw',
                                       PRINT_COMMAND % '/etc/logs/auth.log',
                                       PRINT_COMMAND % '/etc/logs/secure',
                                       PRINT_COMMAND % '/etc/logs/audit.log'],
            'unix distribution'     : [PRINT_COMMAND % '/etc/*release'],
            'socket connections'    : ['ss -p'],
            'processes'             : ['ps -eww'],
            'password files'        : [PRINT_COMMAND % '/etc/shadow',
                                       PRINT_COMMAND % '/etc/passwd'],
            'scheduled jobs'        : [PRINT_COMMAND % '/etc/cron*',
                                       PRINT_COMMAND % '/var/spool/cron/*'],
            'x window config files' : [PRINT_COMMAND % '/etc/X11/*'],
            'yum repositories'      : [PRINT_COMMAND % '/etc/yum.repos.d/*'],
            'cached yum data files' : [LIST_COMMAND % '/var/cache/yum'],
            'installed yum packages': ['yum list installed']}


class ArtifactCollector(object):
    def __init__(self):
        print('HERE HERE!')
        self.logger = logging.getLogger()
        self.start_logging()

    #   start_logging()
    #   Begin logging execution
    def start_logging(self):
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(levelname)-8s- - - %(message)s')

        file_handler = logging.FileHandler(LOG.replace('{{{}}}', '{date:%Y-%m-%d_%H:%M:%S}'.format(date=datetime.now())))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        clo_handler = logging.StreamHandler()
        clo_handler.setLevel(logging.DEBUG)
        clo_handler.setFormatter(formatter)
        self.logger.addHandler(clo_handler)

        self.logger.info('Started execution')

    # call_commands()
    # Function to iterate through the command dictionary and executing each command. It saves runtime information to the
    # log file and keeps track of unsuccessful commands.
    def call_commands(self):
        for section in COMMANDS:
            for command in COMMANDS[section]:
                self.logger.info(section.upper() + ' | command: ' + command)
                try:
                    return_code = subprocess.call(shlex.split(command))
                except OSError as e:
                    self.logger.warning('Unknown command: ' + e.filename)
                except subprocess.CalledProcessError as e:
                    self.logger.warning('Could not find command!')
                else:
                    if return_code == ERROR_CODE:
                        self.logger.warning('File does not exist, unable to run command: ' + command)
