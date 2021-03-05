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
addr=$(nmcli -g IP4.ADDRESS device show "$iface")
conn=$(nmcli -g GENERAL.CONNECTION device show "$iface")
# mac=$(nmcli -g GENERAL.HWADDR device show "$iface")
method=$(nmcli -g IPV4.METHOD con show "$conn")


echo "This script will enslave the external interface $iface to $brname"
echo "MAKE SURE YOU EXECUTE THIS LIKE"
echo "######"
echo "nohup ./enslaver.sh YesImReallySure &"
echo "or"
echo "nohup ./enslaver.sh YesImReallySure OVN &"
echo "######"
echo "Otherwise you might end up by dropping the interface IP"
echo "and blocking the access to this node"


if [ "$1" == "YesImReallySure" ]; then
    # This can be auto or manual
    echo "$method"
    if [ "$iface" = "$brname" ]; then
        echo "We are already using the interface, do nothing"
    else

        if [ "$2" == "OVN" ]; then
            ovs-vsctl add-port "$brname" "$iface"
            ip addr add 0.0.0.0 dev "$iface" && ip addr flush dev "$iface"

            if [ "$method" = "auto" ] && [ "$use_dhcp" -eq 1 ]; then
                echo "Setting IP by DHCP"
                dhclient -r "$iface" && \
                dhclient "$iface"
            else
                echo "Setting static IP"
                ip addr add "$addr" dev "$iface" && \
                ip link set "$iface" up
            fi
        else
            echo "Creating bridge"
            nmcli con add ifname "$brname" type bridge con-name "$brname"
            echo "Enslaving the external access interface to the bridge"
            nmcli con add type bridge-slave ifname "$iface" master "$brname"
            echo "Disabling stp in the bridge"
            nmcli con modify "$brname" bridge.stp no
            echo "Shutting down the external connection"
            nmcli con down "$conn"
            echo "Starting the bridge"
            nmcli con up "$brname"
            echo "Show bridge info"
            ip a s "$brname"
            echo "Flushing the interface current IP"
            ip addr add 0.0.0.0 dev "$iface" && \
            ip addr flush dev "$iface"

            if [ "$method" = "auto" ] && [ "$use_dhcp" -eq 1 ]; then
                echo "Setting IP by DHCP"
                dhclient -r "$iface" && \
                dhclient "$brname"
            else
                echo "Setting static IP"
                ip addr add "$addr" dev "$brname" && \
                ip link set "$brname" up
            fi
        fi
    fi

    echo "net.ipv6.conf.all.disable_ipv6 = 1" > /etc/sysctl.d/70-ipv6.conf
    echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.d/70-ipv6.conf

    sysctl --load /etc/sysctl.d/70-ipv6.conf
fi
