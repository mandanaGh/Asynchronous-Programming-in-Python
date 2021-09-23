# add the namespaces
ip netns add agent1
ip netns add agent2
ip netns add agent3


# create the switch
ovs-vsctl add-br ovs1
ovs-vsctl add-br ovs2
ifconfig ovs1 up
ifconfig ovs2 up


# Conneting two OVS to each other via patch port
#ovs-vsctl add-port ovs1 patch1 -- set interface patch1 type=patch
#ovs-vsctl add-port ovs2 patch2 -- set interface patch2 type=patch
#ovs-vsctl set interface patch1 options:peer=patch2
#ovs-vsctl set interface patch2 options:peer=patch1

#### PORT 1
ovs-vsctl add-port ovs1 port1 -- set Interface port1 type=internal
ip link set port1 netns agent1
ip netns exec agent1 ip link set dev port1 up
sudo ip netns exec agent1 ip addr add 10.1.1.5/24 dev port1

#### PORT 12
ovs-vsctl add-port ovs1 port12 -- set Interface port12 type=internal
ip link set port12 netns agent3
ip netns exec agent3 ip link set dev port12 up
sudo ip netns exec agent3 ip addr add 10.1.1.10/24 dev port12

#### PORT 2
ovs-vsctl add-port ovs2 port2 -- set Interface port2 type=internal
ip link set port2 netns agent2
ip netns exec agent2 ip link set dev port2 up
sudo ip netns exec agent2 ip addr add 10.1.1.6/24 dev port2

#### PORT 22
ovs-vsctl add-port ovs2 port22 -- set Interface port22 type=internal
ip link set port22 netns agent3
ip netns exec agent3 ip link set dev port22 up
sudo ip netns exec agent3 ip addr add 10.1.1.20/24 dev port22

# Create one linux bridge inside agent3
ip netns exec agent3 brctl addbr br0
ip netns exec agent3 brctl addif br0 port12
ip netns exec agent3 brctl addif br0 port22
ip netns exec agent3 ip link set dev br0 up


# Add delay
ip netns exec agent3 tc qdisc add dev port12 root netem delay 20ms
ip netns exec agent3 tc qdisc add dev port22 root netem delay 30ms


#Attach IP to OpenvSwitch "ovs1" and "ovs2"
#sudo ip addr add 10.1.1.1/24 dev ovs1
#sudo ip addr add 192.168.1.1/24 dev ovs2

#sudo ip netns exec agent1 route add default gw 10.1.1.1 port1
#sudo ip netns exec agent2 route add default gw 192.168.1.1 port2



