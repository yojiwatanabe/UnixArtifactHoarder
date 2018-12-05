from datetime import datetime
from subprocess import Popen, PIPE, CalledProcessError, call
import logging
import shlex
import os
import sys

SUPERUSER_ID = 0
FILE_NOT_FOUND_ERROR_CODE = 1
SUPERUSER_ERROR_CODE = 2
WILDCARD = '*'
LOG_DIRECTORY = '/var/log/artifactcollector/'
LOG_FILE = LOG_DIRECTORY + '{{{}}}.log'
OUTPUT_DIRECTORY = 'output/'
ROOT_DIR = '/'
PRINT_COMMAND = 'find %s -type f -print -exec tail {} ;'
LIST_COMMAND = 'find %s -type f -exec ls {} ;'
COMMANDS = {'kernel_name_version'   : ['uname -rs'],
            'kernel modules'        : ['lsmod'],
            'network interfaces'    : ['ifconfig -a'],
            'networking information': [PRINT_COMMAND % '/etc/hosts',
                                       PRINT_COMMAND % '/etc/networks',
                                       PRINT_COMMAND % '/etc/protocols',
                                       PRINT_COMMAND % '/etc/nsswitch.conf'],
            'hostname'              : ['hostname',
                                       PRINT_COMMAND % '/etc/hostname'],
            'login history'         : ['last -Faixw',
                                       PRINT_COMMAND % '/var/log/secure*',
                                       PRINT_COMMAND % '/var/log/audit*'],
            'unix distribution'     : [PRINT_COMMAND % '/etc/os-release'],
            'socket connections'    : ['ss -p',
                                       'ss -naop'],
            'processes'             : ['ps -eww',
                                       'pstree -alp'],
            'password files'        : [PRINT_COMMAND % '/etc/shadow',
                                       PRINT_COMMAND % '/etc/passwd'],
            'scheduled jobs'        : [PRINT_COMMAND % '/etc/cron*',
                                       PRINT_COMMAND % '/var/spool/cron'],
            'administrative db info': ['getent passwd',
                                       'getent group',
                                       'getent protocols',
                                       'getent networks',
                                       'getent services',
                                       'getent rpc'],
            'yum repositories'      : [PRINT_COMMAND % '/etc/yum.repos.d'],
            'cached yum data files' : [LIST_COMMAND % '/var/cache/yum'],
            'installed yum packages': ['yum list installed'],
            'startup scripts'       : [PRINT_COMMAND % '/etc/rc.d/*',
                                       PRINT_COMMAND % '/etc/rc.d/*/*',
                                       PRINT_COMMAND % '/etc/init*',
                                       PRINT_COMMAND % '/etc/init*/*'],
            'open files'            : ['lsof -R'],
            'ssh configuration'     : ['cd /home ;' + PRINT_COMMAND % '*/.ssh'],
            'user commands'         : [LIST_COMMAND % '/usr/bin',
                                       LIST_COMMAND % '/usr/local/bin'],
            'custom log sources'    : [PRINT_COMMAND % '/var/log/sudo']}


class ArtifactCollector(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self.check_log_directory()
        self.start_logging()
        self.check_root_access()
        # self.check_directories()
        self.call_commands()


    # check_log_directory()
    # Make sure the /var/log/ directory for Artifact Collector exists. Creates directory if it does not exist.
    @staticmethod
    def check_log_directory():
        if not os.path.exists(LOG_DIRECTORY):
            os.mkdir(LOG_DIRECTORY)

    #   start_logging()
    #   Begin logging execution
    def start_logging(self):
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(levelname)-8s- - - %(message)s')

        file_handler = logging.FileHandler(LOG_FILE.replace('{{{}}}',
                                                            r'{date:%Y-%m-%d_%H:%M:%S}'.format(date=datetime.now())))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        clo_handler = logging.StreamHandler()
        clo_handler.setLevel(logging.DEBUG)
        clo_handler.setFormatter(formatter)
        self.logger.addHandler(clo_handler)

        self.logger.debug('Started execution')

    # check_root_access()
    # Checks for the runtime's effective user ID permissions, exits if not enough access to collect artifacts
    def check_root_access(self):
        self.logger.debug('Checking effective user permissions')
        if os.geteuid() != SUPERUSER_ID:
            self.logger.debug("Runtime does not have superuser privileges. Re-run program with sudo. Exiting...")
            sys.exit(SUPERUSER_ERROR_CODE)
        else:
            self.logger.debug('Confirmed superuser privileges, running...')
            return

    # check_directories()
    # Sets up directory structure for file IO, ensures correct hierarchy for successful writing
    def check_directories(self):
        self.logger.debug('Checking directory structure...')
        section_directories = map(lambda x: x.replace(' ', '_'), COMMANDS)

        for section in section_directories:
            if not os.path.exists(OUTPUT_DIRECTORY + section):
                os.mkdir(OUTPUT_DIRECTORY + section)
                self.logger.debug('Directory %s does not exist, creating...' % section)
            else:
                self.logger.debug('Directory %s exists' % section)

    # call_commands()
    # Function to iterate through the command dictionary and executing each command. It saves runtime information to the
    # log file and keeps track of unsuccessful commands.
    def call_commands(self):
        for section in COMMANDS:
            for command in COMMANDS[section]:
                try:
                    if WILDCARD not in command:
                        process = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE, shell=False)
                    else:
                        process = Popen(command.replace(';', '\;;'), stdout=PIPE, stderr=PIPE, shell=True)
                    (output, error) = process.communicate()
                    self.output_syslog(section, command, output.decode('utf-8').rstrip(), error.decode('utf-8').rstrip())
                except OSError as e:
                    self.logger.warning('file/command -  ' + str(e))
                except CalledProcessError:
                    self.logger.warning('Could not find command!')
                except UnicodeDecodeError:
                    self.logger.warning('Error decoding unicode output.')
                except AttributeError:
                    self.logger.warning('Attribute error')
                else:
                    if process == FILE_NOT_FOUND_ERROR_CODE:
                        self.logger.warning('File does not exist, unable to run command: ' + command)

    # output_syslog()
    # Function to output the section, command, and output to the log at the info level. Main way of presenting data.
    def output_syslog(self, section, command, output, error):
        if error:
            to_write = "SECTION=\"" + section + '\"' + ' COMMAND=\"' + command + '\"' + ' ERROR=\"TRUE\"' \
                       + ' OUTPUT=\"' + error + '\"'
        else:
            to_write = "SECTION=\"" + section + '\"' + ' COMMAND=\"' + command + '\"' + ' ERROR=\"FALSE\"' \
                       + ' OUTPUT=\"' + output + '\"'

        self.logger.info(to_write)


    # def save_output(self, section, command, output):
    #     fname = os.path.join(OUTPUT_DIRECTORY + section.replace(' ', '_'), command.replace(' ', '_').replace('/', '_')
    #                          + '.txt')
    #     self.logger.info('Saving output to %s' % fname)
    #     file = open(fname, 'w')
    #     file.write(output)
    #     file.close()
    #     self.logger.info('Saved ./%s/%s successfully' % (section, command))
