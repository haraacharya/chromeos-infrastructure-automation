import psutil
import subprocess
import shlex
import signal
import os
import os
import sys
import time
from runMiniBat import RunMiniBat


dut_ip = "38.38.38.232"
test = RunMiniBat()

cros_sdk_path = '/home/cssdesk/google_source'

p = subprocess.Popen('pgrep servod', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
retval = p.wait()
out, err = p.communicate()

if out:
	servod_pid = int(out.strip())
	print('servod Process found. Terminating it.')	
	os.kill(servod_pid, signal.SIGKILL)

print('starting a fresh servod...')
os.chdir(cros_sdk_path)	
print os.getcwd()

servod_cmd = 'python ' + '/home/cssdesk/depot_tools/cros_sdk ' + 'sudo ' + 'servod ' + '--board=cyan ' + '&'
os.system(servod_cmd)
time.sleep(15)

import subprocess
output = subprocess.Popen(['pgrep', 'servod'], stdout=subprocess.PIPE).communicate()[0]

if output:
	print "Servod started successfully"
else:
	print "Servod couldn't be started successfully. Exiting test."


servo_sees_usb_cmd1 = 'python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:off'
servo_sees_usb_cmd2 = 'python /home/cssdesk/depot_tools/cros_sdk dut-control usb_mux_sel1:servo_sees_usbkey'
servo_sees_usb_cmd3 = 'python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:on'

os.system(servo_sees_usb_cmd1)
os.system(servo_sees_usb_cmd2)
time.sleep(1)
os.system(servo_sees_usb_cmd3)


#flashing the test image onto the USB
#cmd_flashing_to_usb = 'python /home/cssdesk/depot_tools/cros_sdk cros flash usb:///dev/sdb ../../src/Binaries/Latest/chromiumos_test_image.bin'
#os.system(cmd_flashing_to_usb)


# PUT DUT in recovery mode
recovery_cmd = 'python /home/cssdesk/depot_tools/cros_sdk dut-control power_state:rec'
os.system(recovery_cmd)

# Let DUT see the USB
dut_sees_usb_cmd1 = 'python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:off'
dut_sees_usb_cmd2 = 'python /home/cssdesk/depot_tools/cros_sdk dut-control usb_mux_sel1:dut_sees_usbkey'

dut_sees_usb_cmd3 = 'python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:on'

os.system(dut_sees_usb_cmd1)
os.system(dut_sees_usb_cmd2)
time.sleep(1)
os.system(dut_sees_usb_cmd3)


time.sleep(3)
print "Waiting for the system to boot from USB"

if test.wait_for_dut_to_come_back_on(2, dut_ip):
	boot_src = test.run_command_on_dut("rootdev -s", dut_ip)
else:
	print "System didn't comeback after reboot"
	exit()

print boot_src

if boot_src.find("sda") != -1:
	print "system booted from USB"
else:
	print "system boot from USB failed. Exiting test."
	exit()
		
print "will initiate os installation"
test.run_command_on_dut("chromeos-install --yes", dut_ip)
print "OS installation complete. Will reboot the system to boot it from emmc."
test.run_command_on_dut("reboot", dut_ip)

time.sleep(6)

print "Wait for system to comeback on after reboot"
if test.wait_for_dut_to_come_back_on(2, dut_ip):
	boot_src = test.run_command_on_dut("rootdev -s", dut_ip)
else:
	print "System didn't bootback after BKC OS installation. Exiting test."
	exit()

print boot_src

if boot_src.find("mmc") != -1:
	print "system booted from emmc."
else:
	print "system boot from EMMC failed. Exiting test"


	


