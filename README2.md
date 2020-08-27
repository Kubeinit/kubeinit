## Purpose of this project
The purpose of this projecct is to automate the deployment of OpenShift (4.5) based on UPI , by producing ISO images that can be provisioned on servers via virtualmedia (or other means to upload an ISO).
The procedure for composing the ISOs is heavily based on https://github.com/openshift/assisted-service and the preparation of the install is also based on https://github.com/openshift-kni/baremetal-deploy/tree/master/ansible-ipi-install.

## Pre-requisites
You will need a server, which we will call *provisioner* from where all the procedure needs to be executed. From there, you could deploy as many clusters as you need.
This is an ansible playbook, so you need to have Ansible (2.5+) installed on the host from where you will run it.
When executing a baremetal deployment, you will need to consider all the requirements in terms of networking and DNS, as explained [here](https://docs.openshift.com/container-platform/4.5/installing/installing_bare_metal/installing-bare-metal.html#installation-infrastructure-user-infra_installing-bare-metal).
When performing a virtualized install, the desired number of masters and workers will be created on libvirt, and all the network automation will be provided by the playbook.

## How to deploy a cluster

### Inventory
As this is an ansible playbook, the first thing that needs to be defined is the inventory file. We are providing the [inventory.hosts.sample](https://raw.githubusercontent.com/yrobla/openshift-upi-virtualmedia-deploy/master/inventory/hosts.sample) file that you can use - simply copy the content to inventory.hosts into the same path, and modify as needed. There are instructions provided into the same file.

### Playbook
Once you have defined the inventory, you can run the playbook. Simply execute:

     ansible-playbook -v -i inventory/hosts playbook.yml
And the playbook will deploy the desired cluster for you.
However, this playbook is divided into several steps, which can be run automatically using tags:

 1. Node preparation - it will install all the requirements needed into the provisioner host to be able to deploy an OpenShift cluster, and configure libvirt, working directories, etc... You can run it individually by adding the *--tags=node_preparation* parameter to the ansible-playbook call.
 2. Installer preparation - It will pre-download the required artifacts and cache them for future use. Will create a pod for caching the images and anothe for private registry if needed. You can use the tag *installer_preparation*
 3. Installer configuration - It will generate ignition files, manifests, etc... in order to start the installation. It will also generate the ISOs that are going to be used for bootstrap, master and workers. You can use the tag *installer_configuration*
 4. Installer - It will create a bootstrap VM with the bootstrap ISO and start it. When choosing a virtualized install, it will create master and worker VMs and do the same, and finally will wait for install to complete. When doing an install on baremetal, the provisioning of the ISO and power on of the machine needs to be done manually.

## Configuration
### Ignition files
When needed, new ignition content can be added to master and worker roles. Simply create a new folder customize_ignition inside https://github.com/yrobla/openshift-upi-virtualmedia-deploy/tree/master/roles/installer-configuration/files , and create two new files called *master* or *worker*, with the ignition content you want to inject.

### Manifests
When deploying a new cluster, there is the possibility of injecting new manifests. Simply create a manifests folder inside https://github.com/yrobla/openshift-upi-virtualmedia-deploy/tree/master/roles/installer-configuration/files folder, and start adding manifests there.
