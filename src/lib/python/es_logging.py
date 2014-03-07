#
#	purpose: Define a class for logging error file to console and file
#	author:  M.Clerici
#	date:	 17.02.2014	
#   descr:	 It is a wrapper around standard logging module, and defines two handler (to console a file).
#			 File is named after the name of calling routine
#			 Maximum length of the file/backup files are also managed. 
#	history: 1.0 
#
#   TODO-M.C.: what is the difference between try/except, Logger and Exception Raising ?
#
try: 
	import os, glob, logging, logging.handlers
except ImportError: 
	pass

try:
    baseDir=os.environ['ESTATION2PATH']
except:
    print 'Error - ESTATION2PATH variable not defined ! Exit'
    exit

logDir=baseDir+'log/'

def myLogger(name):
	logger=logging.getLogger('eStation2.'+name)
	logger.setLevel(logging.DEBUG)

	# Remove existing handlers
	while len(logger.handlers) > 0:
		h=logger.handlers[0]
		logger.removeHandler(h)

	# Create handlers
	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(logging.DEBUG)
	fileHandler = logging.handlers.RotatingFileHandler(logDir+name+'.log',maxBytes=10000,backupCount=5)
	fileHandler.setLevel(logging.WARNING)

	# Create formatter
	plainformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

	# Add formatter to handlers
	consoleHandler.setFormatter(plainformatter)
	fileHandler.setFormatter(plainformatter)

    #handler=logging.FileHandler(os.path.join('/some/path/',name+'.log'),'w')
	logger.addHandler(fileHandler)
	logger.addHandler(consoleHandler)
	return logger

