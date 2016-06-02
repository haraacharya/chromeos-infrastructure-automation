import paramiko
import os
import time
import re
import subprocess

class RunMiniBat(object):
		
	def run_command_on_dut(self, command, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')
		stdin, stdout, stderr = client.exec_command(command)
		command_exit_status = stdout.channel.recv_exit_status()
		out= stdout.read()
		"""
		while not stdout.channel.exit_status_ready():
		    	# Only print data if there is data to read in the channel
		    	if stdout.channel.recv_ready():
				rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
				if len(rl) > 0:
			   		# Print data from stdout
			    		print stdout.channel.recv(1024),
		
			print "Command done."
		"""
		client.close()
		if command_exit_status == 0:
			return out
		else:
			return False	

	def copy_file_from_host_to_dut(self, src,dst, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')

		sftp = client.open_sftp()
		sftp.put(src, dst)		
		sftp.close()

		if self.run_command_on_dut("ls -l " + dst, dut_ip):	
			print ("File copy successfull")	
			return True
		else:
			print ("File copy unsuccessfull")	
			return False

	def copy_file_from_dut_to_host(self, src,dst, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')

		sftp = client.open_sftp()
		sftp.get(src, dst)		
		sftp.close()

		if os.path.isfile(dst):	
			print ("File copy successfull")	
			return True
		else:
			print ("File copy unsuccessfull")	
			return False


	def check_if_dut_is_live(self, dut_ip):
		hostname = dut_ip #example
		response = os.system("ping -c 1 " + hostname)

		#and then check the response...
		if response == 0:
			return True
		else:
			return False

	def wait_for_dut_to_come_back_on(self, minutes, dut_ip):
		minutes = int(minutes)
		t_end = time.time() + 60 * minutes
		while time.time() < t_end:
	    		if self.check_if_dut_is_live(dut_ip):
				return True
		return False


	def check_for_intel_test_status_to_send_result(self, minutes, dut_ip):
		print "Waiting for intel_test to be over"	
		time.sleep(500)	
		t_end = time.time() + 60 * int(minutes)
		while time.time() < t_end:
	    		if self.check_if_dut_is_live(dut_ip):
				intel_test_status = self.run_command_on_dut("status intel_test", dut_ip)
				print intel_test_status
				#pattern = re.compile("stop")
				#if pattern.match(intel_test_status):
				if intel_test_status.find("stop") != -1:
					print ("Intel_test has stopped. Will send the result.")
					return True

	def clean_up_dut(self, dut_ip, reboot_flag = True):
		error = 0
		print "This will cleanup the /tmp, /var/log and the intel_test file from /etc/init"		
		if self.check_if_dut_is_live(dut_ip):
			self.run_command_on_dut("rm -rf /var/lox/*", dut_ip)	
			if self.run_command_on_dut("ls -l /etc/init/intel_test.conf", dut_ip):
				self.run_command_on_dut("rm -rf /etc/init/intel_test.conf", dut_ip)
			else:
				print "intel_test.conf file doesn't exist"
		else:
			print "DUT is not up. Can not cleanup the DUT"
			return False				
		
		if reboot_flag:
			self.run_command_on_dut("reboot", dut_ip)
			time.sleep(50)
			if self.wait_for_dut_to_come_back_on(3, dut_ip):
				return True
			else:
				return False
			
		return True

	def collect_dut_logs(self, dut_ip):
		if self.check_if_dut_is_live(dut_ip):
			if self.run_command_on_dut("ls -l /tmp/log*", dut_ip):
				print "Deleting existing generate_log file"
				self.run_command_on_dut("rm -rf /tmp/log*", dut_ip)
			print "Waiting for the logs to be generated"	
			generate_logs_output = self.run_command_on_dut("generate_logs", dut_ip)
			
			return generate_logs_output
		else:
			print "DUT %s is not up" % dut_ip
			return False
			

	def collect_logs_in_parallel(self, dut_ip, log_collection_folder):
		output = self.collect_dut_logs(dut_ip)
		if output:
			log_file_string = re.search('Log files are available at (.*)', output)
			if log_file_string:
				dut_log_file_path = log_file_string.group(1)	
				print dut_log_file_path
				return dut_log_file_path
			else:
				print "log file was not created successufully"
				return False
		else:
			return False








