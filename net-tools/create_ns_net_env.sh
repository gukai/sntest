#!/bin/bash
create_namespace(){
    # $1: namespace name
    ip netns | grep "$1" > /dev/null
    if [ "$?" != "0" ]; then
        echo "Create namepace $1"
        ip netns add $1
    else
        echo "Namespace $1 exist already."
    fi
}

create_vethpair_and_plugin_namespace(){
    # $1: name of namespace which plugin the veth pair.
    ip link show if_${1}_out > /dev/null
    if [ "$?" != "0" ];then
        echo "Create veth pair for namespace $1"
        ip link add name if_${1}_out type veth peer name if_${1}
    else
        echo "Veth pair is already exists in namespace $1"
    fi

    ip link show if_${1} > /dev/null
    if [ "$?" == "0" ];then
        echo "Put veth in namesapce $1"
        ip link set dev if_${1} netns $1
    else
        echo "Veth pair if_${1} already in namespace $1"
    fi
}

create_ovs_br_plugin_veth(){
    # $1: namesspace name 
    # $2: ovs bridge name
    ovs-vsctl br-exists $2 > /dev/null
    if [ "$?" != "0" ];then
        echo "Create bridge $2, it is not exists."
        ovs-vsctl add-br $2
    else
        echo "Bridge $2 is exist already."
    fi

    ovs-vsctl list-ports $2 | grep if_${1}_out > /dev/null
    if [ $? != 0 ];then
        ovs-vsctl add-port $2 if_${1}_out
    else
        echo "Bridge $2 had port if_${1}_out already."
    fi
}

set_net_env(){
    # $1: namespace name
    # $2: cidr for namespace interface
    ip link set dev if_${1}_out up
    ip netns exec $1 ip link set dev lo up
    ip netns exec $1 ip link set dev if_${1} up
    ip netns exec $1 ip address add $2 dev if_${1}
}


create_one_node(){
    # $1: namespace name
    # $2: ovs bridge name.
    # $3: cidr for namespace interface.
    create_namespace $1
    create_vethpair_and_plugin_namespace $1
    create_ovs_br_plugin_veth $1 $2
    set_net_env $1 $3
}


#create_one_node <namespace_name> <ovs_br> <cider>
create_one_node "$1" "$2" "$3"






