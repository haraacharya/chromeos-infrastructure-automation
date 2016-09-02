from datetime import datetime
import logging
import logging.handlers



LOG_FILENAME = datetime.now().strftime('consecutive_logfile_%H_%M_%d_%m_%Y.log')

print LOG_FILENAME

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


logging.debug('This message should go to the log file')
logging.info('This message should go to the log file')



		
