#!/bin/bash

sub_addr=$1
hostname=$2

echo $hostname > /etc/hostname

#get NIC name
nic1="eno16777736"
tmp_var=`ip -o link show | grep -v LOOPBACK | grep -v eno16777736 | awk '{print $2}'`
nic2=${tmp_var%:}

#get NIC path
nic1_file="/etc/sysconfig/network-scripts/ifcfg-$nic1"
nic2_file="/etc/sysconfig/network-scripts/ifcfg-$nic2"


#get NIC UUID
#nic1_uuid=`nmcli -f GENERAL.UUID con show $nic1 | awk '{print $2}'`
#nic2_uuid=`nmcli -f GENERAL.UUID con show $nic2 | awk '{print $2}'`

#get NIC mac
nic1_mac=`ip link show $nic1 | grep 'link/ether' | awk '{print $2}' | tr '[a-z]' '[A-Z]'`
nic2_mac=`ip link show $nic2 | grep 'link/ether' | awk '{print $2}' | tr '[a-z]' '[A-Z]'`




cat > $nic1_file <<EOF
HWADDR=$nic1_mac
TYPE=Ethernet
BOOTPROTO=static
NAME=eno16777736
ONBOOT=yes
IPADDR=192.168.1.$sub_addr
NETMASK=255.255.255.0
GATEWAY=192.168.1.254
DNS1=114.114.114.114
EOF

cat > $nic2_file <<EOF
HWADDR=$nic2_mac
TYPE=Ethernet
BOOTPROTO=static
NAME=$nic2
ONBOOT=yes
IPADDR=10.30.0.$sub_addr
NETMASK=255.255.255.0
DNS1=114.114.114.114
EOF

systemctl restart network
chmod -x /usr/lib/gukai/net/init_nic.sh
