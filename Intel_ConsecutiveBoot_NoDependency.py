import subprocess
import os
import sys
import time
import signal
from runMiniBat import RunMiniBat
from datetime import datetime
import logging
import logging.handlers


LOG_FILENAME = datetime.now().strftime('consecutive_logfile_%H_%M_%d_%m_%Y.log')
LOG_FILENAME_STR = os.path.abspath(LOG_FILENAME)
print ("Log file name is: %s"% LOG_FILENAME)
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )

#CONFIG PARAMETERS FOR USER TO CHANGE
#status_check should be true if tester wants to test system status in every loop else FALSE
status_check = True
faft_iterations = 1
dut_ip = "38.38.38.232"
cros_sdk_path = '/home/cssdesk/google_source'
#END CONFIG PARAMETERS FOR USER TO CHANGE

test = RunMiniBat()
script_working_directory = os.getcwd()
os.system("pgrep servod | xargs sudo kill -9")
p = subprocess.Popen('pgrep servod', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
retval = p.wait()
out, err = p.communicate()

if out:
	servod_pid = int(out.strip())
	print('servod Process found. Terminating it.')	
	os.kill(servod_pid, signal.SIGKILL)

print('starting a fresh servod...')
logging.info('starting a fresh servod...')

os.chdir(cros_sdk_path)	
print os.getcwd()
logging.info(os.getcwd())

servod_cmd = 'python ' + '/home/cssdesk/depot_tools/cros_sdk ' + 'sudo ' + 'servod ' + '--board=cyan ' + '&'
os.system(servod_cmd)
time.sleep(15)

import subprocess
output = subprocess.Popen(['pgrep', 'servod'], stdout=subprocess.PIPE).communicate()[0]

if output:
	print "Servod started successfully"
	logging.info("Servod started successfully")
else:
	print "Servod couldn't be started successfully. Exiting test."
	logging.error("Servod couldn't be started successfully. Exiting test.")
	exit()

def status_check():
	mainfw_type = test.run_command_on_dut("crossystem mainfw_type", dut_ip)
	print mainfw_type
	if mainfw_type.find("developer") != -1:
		print "System is in Developer mode."
		logging.info("System is in Developer mode.")
	else:
		print "System is in Normal mode"
		logging.info("System is in Normal mode.")

	wifi_check = test.run_command_on_dut('/usr/sbin/lspci | grep -i "intel corporation wireless"', dut_ip)
	print wifi_check
	if wifi_check.find("Intel Corporation Wireless") != -1:
		print "Wifi detected successfully"
		logging.info("Wifi detected successfully")
	else:
		print "Wifi detection failed. Exiting test."
		logging.error("Wifi detection failed. Exiting test.")
		exit()
	

if status_check:
	status_check()

pwr_btn_command = 'python /home/cssdesk/depot_tools/cros_sdk dut-control pwr_button:press sleep:0.5 pwr_button:release'
for i in xrange(1, faft_iterations+1):
	print ("STARTING ITERATION %d of %d" % (i, faft_iterations))
	logging.info("STARTING ITERATION %d of %d" % (i, faft_iterations))
	print "Sending shutdown command to the DUT"
	logging.info("Sending shutdown command to the DUT")
	test.run_command_on_dut("/sbin/shutdown -P now", dut_ip)
	time.sleep(11)
	if not test.check_if_dut_is_live(dut_ip):	
		print "system shutdown successful"
		logging.info("system shutdown successful")
		ec_uart_capture_enable_command = 'python /home/cssdesk/depot_tools/cros_sdk dut-control ec_uart_capture:on'
		ec_uart_capture_disable_command = 'python /home/cssdesk/depot_tools/cros_sdk dut-control ec_uart_capture:off'
		ec_console_system_status_command = 'python /home/cssdesk/depot_tools/cros_sdk dut-control ec_uart_cmd:powerinfo'
		ec_console_system_status_output = 'python /home/cssdesk/depot_tools/cros_sdk dut-control ec_uart_stream'
		os.system(ec_uart_capture_enable_command)
		os.system(ec_console_system_status_command)
		system_status_check = os.popen(ec_console_system_status_output).read()
		os.system(ec_uart_capture_disable_command)
		print system_status_check
		logging.debug(system_status_check)

		if system_status_check.find("G3") != -1:
			print "System successfully went to G3"
			logging.info("System successfully went to G3")
		else:
			print "System is not going to G3. Exiting test"
			logging.error("System is not going to G3. Exiting test")
			exit()
		

		print "Pressing powerbtn to poweron system"
		logging.info("Pressing powerbtn to poweron system")
		os.system(pwr_btn_command)
		time.sleep(40)
		if test.check_if_dut_is_live(dut_ip):
			print "System on using powerbtn successfull."
			logging.info("System on using powerbtn successfull.")
			if status_check:
				status_check()
			print ("ITERATION %d of %d COMPLETE" % (i, faft_iterations))
			logging.info("ITERATION %d of %d COMPLETE" % (i, faft_iterations))
			print ("============================================================")
			logging.info("============================================================")
		
	else:
		print "system is not shutting down by shutdown command. Check system status. Exiting test"
		logging.error("system is not shutting down by shutdown command. Check system status")
		exit()
print ""
logging.info("")
print ("Logs stored in: %s"% LOG_FILENAME_STR)
logging.info("Logs stored in: %s"% LOG_FILENAME_STR)
