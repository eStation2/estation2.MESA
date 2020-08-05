#
# purpose: Define a class for logging error file to console and file
# author:  M.Clerici
# date:	 17.02.2014
# descr:	 It is a wrapper around standard logging module, and defines two handler (to console a file).
#            File is named after the name of calling routine
#            Maximum length of the file/backup files are also managed.
# history: 1.0
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sys import platform

from future import standard_library

from config import es_constants
import inspect

try:
    import os, stat, glob, logging, logging.handlers
except ImportError:
    print('Error in importing module ! Exit')
    exit(1)

# Get log_dir
try:
    log_dir = es_constants.log_dir
except EnvironmentError:
    print('Error - log_dir not defined in es_constants.  Exit')
    exit(1)

standard_library.install_aliases()

# class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
#    def _open(self):
#        prevumask=os.umask(0o002)
#        #os.fdopen(os.open('/path/to/file', os.O_WRONLY, 0600))
#        rtv=logging.handlers.RotatingFileHandler._open(self)
#        os.umask(prevumask)
#        return rtv

# Used to detect if called by unittest (for disabling logging)
# Reference: https://stackoverflow.com/questions/25025928/how-can-a-piece-of-python-code-tell-if-its-running-under-unittest
def in_unit_test():
  current_stack = inspect.stack()
  for stack_frame in current_stack:
    for program_line in stack_frame[4]:    # This element of the stack frame contains
      if "unittest" in program_line:       # some contextual program lines
        return True
  return False

if 'check_unittest' not in locals():
    check_unittest = in_unit_test()

def parse_user_setting(user_def):
    log_level = logging.INFO
    if user_def == "info" or user_def == "INFO":
        log_level = logging.INFO
    if user_def == "debug" or user_def == "DEBUG":
        log_level = logging.DEBUG
    if user_def == "warning" or user_def == "WARNING":
        log_level = logging.WARNING
    if user_def == "error" or user_def == "ERROR":
        log_level = logging.ERROR
    if user_def == "fatal" or user_def == "FATAL":
        log_level = logging.FATAL

    return log_level


def my_logger(name):
    # Convert user_settings to logging variable
    user_logging_level = parse_user_setting(es_constants.log_general_level)

    # logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

    logger = logging.getLogger('eStation2.' + name)
    # Try setting from user config .. in case of error set a default level
    try:
        logger.setLevel(user_logging_level)
    except:
        logger.setLevel(logging.INFO)

    # Remove existing handlers
    while len(logger.handlers) > 0:
        h = logger.handlers[0]
        logger.removeHandler(h)

    # Create handlers
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)
    console_handler = logging.StreamHandler()

    if platform == 'win32':
        # TODO: Pierluigi select the correct replacment
        name = name.replace(':', '_')

    file_handler = logging.handlers.RotatingFileHandler(log_dir + name + '.log', maxBytes=50000, backupCount=3)

    # Create formatter
    plain_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    # Add formatter to handlers
    console_handler.setFormatter(plain_formatter)
    file_handler.setFormatter(plain_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Define log handlers
    # Try setting from user config .. in case of error set a default level
    try:
        console_handler.setLevel(user_logging_level)
        file_handler.setLevel(user_logging_level)
    except:
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

    if check_unittest:
        logger.disabled = True

    return logger
