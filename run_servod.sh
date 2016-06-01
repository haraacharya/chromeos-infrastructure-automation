cd /home/cssdesk/google_source

servod_process_id=`pgrep servod`

 if [ -n "$servod_process_id" ]; then
	echo "servod is already running. Will stop servod"
	echo "Stopping servod"
	kill -9 $servod_process_id
fi

echo "Starting servod"
echo $PWD

cros_sdk_bin=`which cros_sdk`

python /home/cssdesk/depot_tools/cros_sdk sudo servod --board=cyan &

echo "Will flash the coreboot and Ec"

python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:off
python /home/cssdesk/depot_tools/cros_sdk dut-control usb_mux_sel1:servo_sees_usbkey
sleep 1
python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:on

#python /home/cssdesk/depot_tools/cros_sdk cros flash usb:///dev/sdb ../../src/Binaries/Latest/chromiumos_test_image.bin


# PUT DUT in recovery mode
python /home/cssdesk/depot_tools/cros_sdk dut-control power_state:rec

# Let DUT see the USB
python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:off
python /home/cssdesk/depot_tools/cros_sdk dut-control usb_mux_sel1:dut_sees_usbkey
sleep 1
python /home/cssdesk/depot_tools/cros_sdk dut-control prtctl4_pwren:on
sleep 3
echo "Waiting for the system to boot from USB"
while true; do ping -c1 38.38.38.232 > /dev/null && break; done

#sudo rm -rf /home/cssdesk/.ssh/known_hosts

cd /home/cssdesk/autobat
echo $PWD

boot_src_dut=`ssh autobat rootdev -s`
boot_src_dut=`ssh autobat rootdev -s`
echo "will now print dut boot src"
echo $boot_src_dut

if echo $boot_src_dut | grep -i sda ; then 
	echo "DUT booted from USB"; 
	ssh autobat chromeos-install --yes
else
	echo "DUT didn't boot from USB"
	echo "Exiting test"
fi

