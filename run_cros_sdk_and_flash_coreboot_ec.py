import psutil
import subprocess
import shlex
import signal
import os
import os
import sys
import time
import zipfile
import shutil
import glob

from runMiniBat import RunMiniBat


dut_ip = "38.38.38.232"
cros_sdk_path = '/home/cssdesk/google_source'

test = RunMiniBat()
script_working_directory = os.getcwd()

dir_name = '/home/cssdesk/google_source/src/Binaries/Latest'
os_compressed_filename = "*.bz2"
coreboot_compressed_filename = "Amenia_ChromiumOS_Daily_71_image_16MB.zip"


def unzip_src_file(dir_name, os_compressed_filename, coreboot_compressed_filename):
	binary_src_location = dir_name + "/tmp"
	print binary_src_location
	if not os.path.exists(binary_src_location):
	    os.makedirs(binary_src_location)

	filelist = glob.glob(binary_src_location + "/*")
	for f in filelist:
	    os.remove(f)


	cmd_os_file_decompression = 'bzip2 -dckf ' +  dir_name + "/" + os_compressed_filename +  " > " +  binary_src_location + "/" + "chromium_test_image.bin"
	os.system(cmd_os_file_decompression)

	#coreboot
	coreboot_location =  dir_name + "/" + coreboot_compressed_filename
	print coreboot_location
	zip_ref = zipfile.ZipFile(coreboot_location, 'r')
	zip_ref.extractall(binary_src_location)
	zip_ref.close()
	for cb in glob.glob(binary_src_location + "/image*.bin"):
		print cb
		shutil.move(cb, binary_src_location + "/" + "image.bin")

	#ec
	for name in glob.glob(dir_name + "/*ec.bin"):
		print name
		shutil.copyfile(name, binary_src_location + "/" + "ec.bin")
	if os.path.isfile(binary_src_location + "/ec.bin") and os.path.isfile(binary_src_location + "/image.bin") and os.path.isfile(binary_src_location + "/chromium_test_image.bin"):
		return True
	else:
		return False




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
	exit()

#will flash coreboot and ec
print "Will prepare BKC images from release folder"
#cmd_creating_src = "python " + script_working_directory + "/" + "zip_unzip_files.py"
#os.system(cmd_creating_src)
if unzip_src_file(dir_name, os_compressed_filename, coreboot_compressed_filename):
	print "BKC images extracted successfully. Will continue flashing"
else:
	print "BKC images are not extracted. Exiting test"
	exit()

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


	


