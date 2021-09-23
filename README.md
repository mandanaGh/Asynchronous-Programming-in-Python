# Asynchronous-Programming-in-Python
In this assignment, we are supposed to perform metrics measurements between two Open vSwitches connecting to each other by using some agents. Agents are connected to OVS using Internal ports. 


# Description:
We assume that there are two agents, agent1 connects to OVS1 and agent2 connects to OVS2. The multicast address and port are as following:
BROADCAST_PORT = 1910
BROADCAST_ADDR = "239.255.255.250"

Agents check the multicast traffic in order to discover each other. Both agents can be considered as the client and the server sending/receiving packets to/from the multicast domain to measure some metrics (e.g. the rate of packet loss and latency) about the VXLAN.


Each agent periodically sends UDP packets to the multicast address. Each packet has a unique number. After sending one packet, the timer starts and an object of Timer class creates to maintain the ID number of the packet along with the other attributes (e.g. the start time, the latency, etc.).
When another agent (server) receives the packet then it sends the packet to its source address. By receiving the datagram the timer stops and the latency calculates as other attributes of the timer class. In this scenario, the packet is marked as a dropped packet if the sender won't receive it after a specific interval.

In order to calculate the average latency time, all latency times within a specific interval is stored in one list (latencyList) and at the end of the interval, the average of latency is calculated with respect to the number of packet loss in that interval.

In this program, we mostly use "call_later" method in event loop in order to arrange for the callback to be called after the given delay seconds.


# How to run the program
For setting up the test environment, pleaser run the "env_ipv4.sh" script as below:
    sudo ./env_ipv4.sh
    sudo ip netns exec agent1 route add default dev port1
    sudo ip netns exec agent2 route add default dev port2
 
In order to run the program, we run the below commands in two different terminals:
    sudo ip netns exec agent1 python3 main.py 10.1.1.5
    sudo ip netns exec agent2 python3 main.py 10.1.1.6



In order to check the correctness of the code, we create an artificial delay on the OVS interfaces in the namespace by using tc command. 
In this case, we remove the connectivity between ovs1 and ovs2. Both OVSs connect to each other by adding another agent(agent3). Finally, we add a fixed amount of delay to all packets going out of the local Ethernet on both ports of agent3.
For setting up the test environment, we run the "test_env.sh" script as below:
    sudo ./clean.sh
    sudo ./test_env.sh
    sudo ip netns exec agent1 route add default dev port1
    sudo ip netns exec agent2 route add default dev port2



For IPV6
    sudo ./clean.sh
    sudo ./env_ipv6.sh
    sudo ip -6 netns exec agent1 route add default dev port1
    sudo ip -6 netns exec agent2 route add default dev port2

sudo ip netns exec agent1 python3 mainIPV6.py fd01:2345:6789:abc1::5
sudo ip netns exec agent2 python3 mainIPV6.py fd01:2345:6789:abc1::6























