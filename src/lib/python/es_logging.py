#
#	purpose: Define a class for logging error file to console and file
#	author:  M.Clerici
#	date:	 17.02.2014	
#   descr:	 It is a wrapper around standard logging module, and defines two handler (to console a file).
#			 File is named after the name of calling routine
#			 Maximum length of the file/backup files are also managed. 
#	history: 1.0 
#
import locals

try:
    import os, stat, glob, logging, logging.handlers
except ImportError: 
    print 'Error in importing module ! Exit'
    exit(1)

# Get base dir
try:
    base_dir = locals.es2globals['base_dir']
except EnvironmentError:
    print 'Error - basedir not defined in locals.  Exit'
    exit(1)

log_dir = base_dir+'log/'


#class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
#    def _open(self):
#        prevumask=os.umask(0o002)
#        #os.fdopen(os.open('/path/to/file', os.O_WRONLY, 0600))
#        rtv=logging.handlers.RotatingFileHandler._open(self)
#        os.umask(prevumask)
#        return rtv


def my_logger(name):
    logger = logging.getLogger('eStation2.'+name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    while len(logger.handlers) > 0:
        h = logger.handlers[0]
        logger.removeHandler(h)

    #os.chmod(log_dir, stat.S_IRWXU)
    #os.chmod(log_dir, stat.S_IRWXG)
    #os.chmod(log_dir, stat.S_IRWXO)

    # Create handlers
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)
    console_handler = logging.StreamHandler()

    #file_handler = logging.handlers.RotatingFileHandler(log_dir+name+'.log', maxBytes=100, backupCount=5)
    #file_handler = logging.FileHandler(log_dir+name+'.log')

    # Create formatter
    plain_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    # Add formatter to handlers
    console_handler.setFormatter(plain_formatter)
    #file_handler.setFormatter(plain_formatter)

    #handler=logging.FileHandler(os.path.join('/some/path/',name+'.log'),'w')
    #logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Define log handlers
    console_handler.setLevel(logging.DEBUG)
    #file_handler.setLevel(logging.DEBUG)

    return logger

