#!/bin/bash
#
# Enslave a physical interface to the external bridge
#
# Execute as: nohup detach.sh &
#

# The name of the bridge that will enslave the external access interface.
brname="kiextbr0"
# To choose if we configure the bridge
# with DHCP or static IP even if the interface
# was using DHCP
use_dhcp=0

iface=$(ip route get "8.8.8.8" | grep -Po '(?<=(dev )).*(?= src| proto)')
addr=$(nmcli -g IP4.ADDRESS device show "${iface}")
conn=$(nmcli -g GENERAL.CONNECTION device show "${iface}")
# mac=$(nmcli -g GENERAL.HWADDR device show "${iface}")
method=$(nmcli -g IPV4.METHOD con show "$conn")


echo "This script will enslave the external interface ${iface} to ${brname}"
echo "MAKE SURE YOU EXECUTE THIS LIKE"
echo "######"
echo "nohup ./enslaver.sh YesImReallySure &"
echo "or"
echo "nohup ./enslaver.sh YesImReallySure OVN &"
echo "######"
echo "Otherwise you might end up by dropping the interface IP"
echo "and blocking the access to this node"


if [ "$1" == "YesImReallySure" ]; then
    echo "IP: ${addr}"
    echo "Method: ${method}"
    # This can be auto or manual
    if [ "${iface}" = "${brname}" ]; then
        echo "We are already using the interface, do nothing"
    else

        if [ "$2" == "OVN" ]; then
            # From:
            # https://blog.christophersmart.com/2020/07/27/how-to-create-linux-bridges-and-open-vswitch-bridges-with-networkmanager/
            echo "Install dependencies"
            dnf install -y NetworkManager-ovs openvswitch
            systemctl enable --now openvswitch
            systemctl restart NetworkManager
            echo "Enslaving the physical interface with an OVS bridge"
            nmcli con add type ovs-bridge conn.interface ovs-bridge con-name ovs-bridge
            nmcli con add type ovs-port conn.interface port-ovs-bridge master ovs-bridge con-name ovs-bridge-port
            nmcli con add type ovs-interface slave-type ovs-port conn.interface ovs-bridge master ovs-bridge-port con-name ovs-bridge-int

            nmcli con add type ovs-port conn.interface ovs-port-eth master ovs-bridge con-name ovs-port-eth
            nmcli con add type ethernet conn.interface "${iface}" master ovs-port-eth con-name ovs-port-eth-int

            # nmcli con modify ovs-bridge-int ipv4.method disabled ipv6.method disabled
            # nmcli con modify ovs-bridge-int ipv4.method static ipv4.address 192.168.123.100/24
            # nmcli con modify ovs-bridge-int 802-3-ethernet.mtu 9000
            # nmcli con modify ovs-port-eth-int 802-3-ethernet.mtu 9000

            nmcli con down "${conn}" ; \
            nmcli con up ovs-port-eth-int ; \
            nmcli con up ovs-bridge-int

            nmcli con modify "${conn}" ipv4.method disabled ipv6.method disabled

            if [ "${method}" = "auto" ] && [ "${use_dhcp}" -eq 1 ]; then
                echo "Setting IP by DHCP"
                dhclient -r "${iface}" && \
                dhclient ovs-bridge-int
            else
                echo "Setting static IP"
                nmcli con modify ovs-bridge-int ipv4.method static ipv4.address "${addr}"
            fi
        else
            echo "Enslaving the physical interface without OVN"
            echo "Creating bridge"
            nmcli con add ifname "${brname}" type bridge con-name "${brname}"
            echo "Enslaving the external access interface to the bridge"
            nmcli con add type bridge-slave ifname "${iface}" master "${brname}"
            echo "Disabling stp in the bridge"
            nmcli con modify "${brname}" bridge.stp no
            echo "Shutting down the external connection"
            nmcli con down "$conn"
            echo "Starting the bridge"
            nmcli con up "${brname}"
            echo "Show bridge info"
            ip a s "${brname}"
            echo "Flushing the interface current IP"
            ip addr add 0.0.0.0 dev "${iface}" && \
            ip addr flush dev "${iface}"

            if [ "${method}" = "auto" ] && [ "${use_dhcp}" -eq 1 ]; then
                echo "Setting IP by DHCP"
                dhclient -r "${iface}" && \
                dhclient "${brname}"
            else
                echo "Setting static IP"
                ip addr add "${addr}" dev "${brname}" && \
                ip link set "${brname}" up
            fi
        fi
    fi

    echo "net.ipv6.conf.all.disable_ipv6 = 1" > /etc/sysctl.d/70-ipv6.conf
    echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.d/70-ipv6.conf

    sysctl --load /etc/sysctl.d/70-ipv6.conf
fi
