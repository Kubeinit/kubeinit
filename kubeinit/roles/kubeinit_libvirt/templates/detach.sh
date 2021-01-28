#!/bin/bash
#
# We create the external bridge
# $iface is the network port on the machine
# The following command will make the hypervisor to lost the IP so it needs to be in a single line
# from: https://docs.openvswitch.org/en/latest/faq/issues/
iface=$(route | grep '^default' | grep -o '[^ ]*$')
addr=$(nmcli -g IP4.ADDRESS device show "$iface")
conn=$(nmcli -g GENERAL.CONNECTION device show "$iface")
mac=$(nmcli -g GENERAL.HWADDR device show "$iface")
method=$(nmcli -g IPV4.METHOD con show "$conn")
# This can be auto or manual
echo "$method"
if [ "$iface" = "br-ex" ]; then
    echo "We are already using the interface, do not nothing"
else
    if [ "$method" = "auto" ]; then
        echo "IP by DHCP"
        ovs-vsctl --may-exist add-br br-ex -- set Bridge br-ex other-config:hwaddr="$mac" && \
        ovs-vsctl add-port br-ex "$iface" && \
        /sbin/ifconfig "$iface" 0.0.0.0 && \
        /sbin/dhclient br-ex
    else
        echo "Static IP"
        ovs-vsctl --may-exist add-br br-ex && \
        ovs-vsctl add-port br-ex "$iface" && \
        ip addr flush dev "$iface" && \
        ip addr add "$addr" dev br-ex && \
        ip link set br-ex up
    fi
fi

echo "net.ipv6.conf.all.disable_ipv6 = 1" > /etc/sysctl.d/70-ipv6.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.d/70-ipv6.conf

sysctl --load /etc/sysctl.d/70-ipv6.conf
