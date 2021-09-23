#Deleting the Namespaces
ip netns del agent1
ip netns del agent2

#Deleting the OpenvSwitch
ovs-vsctl del-br ovs1
ovs-vsctl del-br ovs2
