from datetime import datetime
import logging
import logging.handlers



LOG_FILENAME = datetime.now().strftime('consecutive_logfile_%H_%M_%d_%m_%Y.log')

print LOG_FILENAME

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )

logging.debug('This message should go to the log file')
logging.info('This message should go to the log file')



		
