import time
import datetime
import os
import subprocess
from runMiniBat import RunMiniBat
import re
import multiprocessing

script_working_directory = os.getcwd()
log_collection_folder = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs(log_collection_folder)

#add the DUT ips to collect log from.
#data = (['38.38.38.237', log_collection_folder], ['38.38.38.2322', log_collection_folder])
data = ('38.38.38.201', '38.38.38.232')
def collect_logs_in_parallel_new((dut_ip)):
	print "collecting logs from: %s" % dut_ip
	test = RunMiniBat()
	output = test.collect_dut_logs(dut_ip)
	if output:
		log_file_string = re.search('Log files are available at (.*)', output)
		if log_file_string:
			dut_log_file_path = log_file_string.group(1)	
			print dut_log_file_path
			dut_log_file_name = "log_dut_ip_" + dut_ip + ".tar.gz"
			test.copy_file_from_dut_to_host(dut_log_file_path, log_collection_folder + "/" + dut_log_file_name, dut_ip )
			print "DUT %s system_log copied to: %s, log_name: %s" % (dut_ip, log_collection_folder, dut_log_file_name)
		else:
			print "log file was not created successufully"
			return False
	else:
		return False

def collect_logs_handler():
    p = multiprocessing.Pool(2)
    p.map(collect_logs_in_parallel_new, data)

if __name__ == "__main__":
	
	#output = test.clean_up_dut(dut_ip, reboot_flag = False)
	collect_logs_handler()


