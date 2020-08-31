INSTALLER_ISO_IMAGE=${1:-https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/latest/latest/rhcos-installer.x86_64.iso}
FINAL_RHCOS_IMAGE=${2:-https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/latest/latest/rhcos-4.5.6-x86_64-metal.x86_64.raw.gz}
FINAL_PATH=${3:-$PWD/coreos_offline.iso}

# download installer ISO
curl $INSTALLER_ISO_IMAGE -o /tmp/livecd.iso
mkdir /tmp/_iso_mount
mkdir /tmp/_custom_iso

# extract the ISO to modify it
mount -t iso9660 -o loop /tmp/livecd.iso /tmp/_iso_mount 
pushd /tmp/_iso_mount
tar cf - . | (cd /tmp/_custom_iso && tar xfp -)
popd

# modify kernel args to boot with extra ramdisk and to don't install ignition
pushd /tmp/_custom_iso
sed -i -r 's|^(  append initrd)=.*|\1=/images/initramfs.img,/images/initramfsExtra nomodeset ip=dhcp|g' isolinux/isolinux.cfg
popd

# download final rhcos image and generate extra ramdisk
mkdir /tmp/_custom_iso_extra
pushd /tmp/_custom_iso_extra
curl $FINAL_RHCOS_IMAGE -o metal.x86_64.raw.gz
find . | sed 's/^[.]\///' | cpio -o -H newc --no-absolute-filenames > /tmp/_custom_iso/images/initramfsExtra
popd

# rebuild iso
pushd /tmp/_custom_iso
mkisofs -o rhcos_custom.iso -b isolinux/isolinux.bin -c isolinux/boot.cat  -no-emul-boot -boot-load-size 4 -boot-info-table -R -J -V "RHCOS custom installer" .
popd

# copy to desired directory and remove temporary files
cp /tmp/_custom_iso/rhcos_custom.iso $FINAL_PATH
umount /tmp/_iso_mount
rm -rf /tmp/_iso_mount
rm -rf /tmp/_custom_iso
rm -rf /tmp/_custom_iso_extra
