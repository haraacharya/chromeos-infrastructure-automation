import os, zipfile
import shutil
import glob

dir_name = '/home/cssdesk/google_source/src/Binaries/Latest'
os_compressed_filename = "*.bz2"
coreboot_compressed_filename = "Amenia_ChromiumOS_Daily_71_image_16MB.zip"
ec_filename = "Amenia_ChromiumOS_Daily_71_ec.bin"

binary_src_location = dir_name + "/tmp"
print binary_src_location
if not os.path.exists(binary_src_location):
    os.makedirs(binary_src_location)

filelist = glob.glob(binary_src_location + "/*")
for f in filelist:
    os.remove(f)


#os.chdir(dir_name) # change directory from working dir to dir with files


cmd_os_file_decompression = 'bzip2 -dckf ' +  dir_name + "/" + os_compressed_filename +  " > " +  binary_src_location + "/" + "chromium_test_image.bin"
os.system(cmd_os_file_decompression)

#coreboot
coreboot_location =  dir_name + "/" + coreboot_compressed_filename
print coreboot_location
zip_ref = zipfile.ZipFile(coreboot_location, 'r')
zip_ref.extractall(binary_src_location)
zip_ref.close()

for name in glob.glob(dir_name + "/*ec.bin"):
	print name
	shutil.copyfile(name, binary_src_location + "/" + "ec.bin")

