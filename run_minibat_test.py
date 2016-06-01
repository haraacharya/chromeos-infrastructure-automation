import time
import os
import subprocess
from runMiniBat import RunMiniBat

test = RunMiniBat()



def main():
	dut_ip = "38.38.38.232"
	#remove rootfs verification 
	if test.check_if_dut_is_live(dut_ip):
		command_ouput = test.run_command_on_dut("/usr/share/vboot/bin/make_dev_ssd.sh --remove_rootfs_verification --partitions 2", dut_ip)
	else:
		print "DUT is not live"
		exit()
	
	print "rootfs verification removed successfully"
	print command_ouput
	#Reboot system
	if command_ouput:
		test.run_command_on_dut("reboot", dut_ip)
	else:
		print ("Couldn't run the command reboot")
		exit()

	print "Reboot command executed successfully"
	print "Waiting for system to come back on"
	time.sleep(30)
	#wait for system to come up and mount root partition
	if test.wait_for_dut_to_come_back_on(2, dut_ip):
		test.run_command_on_dut("mount -o remount,rw /", dut_ip)
	else:
		print "System didn't comeback after reboot"
		exit()

	print "root partition mounted successfully"

	#copy intel_test to /etc/init/
	intel_test_location = os.getcwd()
	if test.copy_file_from_host_to_dut(intel_test_location + "/intel_test.conf", "/etc/init/intel_test.conf", dut_ip):
		print "intel_test.conf copied successfully."
	else:
		print "intel_test.conf couldn't get copied. Exiting test."
		exit()
	#start intel_test
	if test.check_if_dut_is_live(dut_ip):
		command_ouput = test.run_command_on_dut("start intel_test", dut_ip)	
	if command_ouput:
		print  "Intel test has been started. Test result will be stored in dut /var/log/intel_minibat_result.log"
	else:
		print "intel_test was not started successfully. Exiting test."
		exit()

	#keep checking if status intel_test running or stopped and then copy the file to host and send an email
	#sendemail -t harax.k.acharya@intel.com -f "hara.acharya@gmail.com" -u "amenia minibat result" -m "amenia minibat result" -a "/home/cssdesk/Desktop/intel_minibat_result.log"

	if test.check_for_intel_test_status_to_send_result(10, dut_ip):
		log_copy_status = test.copy_file_from_dut_to_host("/var/log/intel_minibat_result.log", intel_test_location + "/intel_minibat_result.log", dut_ip)

		if log_copy_status:
			print "minibat log file copied to server"
		else:
			print "log file copy failed"
			print "Will not be able to send the email"
			exit()

	p = subprocess.Popen('sendemail -t "harax.k.acharya@intel.com, nitinx.dutt@intel.com" -f "hara.acharya@gmail.com" -u "amenia minibat result" -m "amenia minibat result" -a "/home/cssdesk/Desktop/intel_minibat_result.log"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print line,
	retval = p.wait()


if __name__ == "__main__":
    main()


