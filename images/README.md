## Build installer ISO image
This Dockerfile allows to build an installer ISO, to be used in the cluster deployment.
It accepts an argument, INSTALLER_ISO, where you can choose the base ISO to use (pointing by default to https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/pre-release/latest-4.6/rhcos-live.x86_64.iso )
In order to build it, please use :

> podman build -t coreos-livecd [ --build-arg
> INSTALLER_ISO=/path/to/full_installer_iso ]

Please notice that this procedure will only work for OpenShift 4.6+
