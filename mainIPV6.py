import asyncio
import socket
import struct
import time
import fcntl
import struct
import sys

BROADCAST_PORT = 1910
#BROADCAST_ADDR = "239.255.255.250" # Multicast address
BROADCAST_ADDR = "ff0e::10"

INTERVAL = 2 # If the packet is not received during the specific INTERVAL, then it will be marked as a dropped packet
objdata = {} # objdata is a dictionary for storing objects
latencyList = [] # latencyList is a list of all latencies for each period of LATENCYINTERVAL
SENDINTERVAL = 0.5 # The interval between probes
LATENCYINTERVAL = 10 # LATENCYINTERVAL is the period of time for claculating Average latency
packetLoss = 0 # packetLoss is a global variable for counting the number of packet loss for each period of LATENCYINTERVAL

class Timer:
    def __init__(self, id):
        self.id = id
        self.start_time = None
        self.stop_time = None
        self.latency = None
        self.dropped = False

    def start(self,loop):
        self.start_time = time.time()
        # Schedule a call to mark_as_drop()
        loop.call_later(INTERVAL, self.mark_as_drop)

    def stop(self):
        self.stop_time = time.time()

    def total_latency(self):
        if self.dropped != True:
            self.stop()
            self.latency = (self.stop_time - self.start_time) / 2
            latencyList.append(self.latency)

    # Marking packet as a dropped packet if the packet is not received during a specific interval
    def mark_as_drop(self):
        if (self.latency is None):
            self.dropped = True
            global packetLoss # Global variable for counting packet loss
            packetLoss += 1

# Calculating the average latency times stored in the latencyList
def calc_avg_latency():
    global packetLoss
    print("****************************************")
    if (len(latencyList) != 0):
        print("Average Latency is: {}".format(sum(latencyList) / len(latencyList)))
    else:
        print("All packets are lost")
    print("Number of packet loss is: {}".format(packetLoss))
    print("****************************************\n")
    latencyList[:] = [] #removes the contents from the list
    packetLoss = 0
    # recursively call function calc_avg_latency()
    loop.call_later(LATENCYINTERVAL, calc_avg_latency)

# Sending broadcast probes
def send_packets(index, addr):
    t = Timer(str(index))
    objdata[index] = t
    t.start(loop)
    transport.sendto(str(index).encode("ascii"), (addr, BROADCAST_PORT))
    index += 1
    # recursively call function send_packets()
    loop.call_later(SENDINTERVAL, send_packets, index, addr)


# Server-side multicast
class MulticastServerProtocol:
    def connection_made(self, transport):
        self.translayer = transport

    def datagram_received(self, data, addr):
        #if (ip != addr[0]):
        message = data.decode()
        #print('Received %r from %s' % (message, addr))
        #print('Send %r to %s' % (message, addr))
        self.translayer.sendto(data, addr)


class DiscoveryClientProtocol:
    def __init__(self, loop, addr):
        self.loop = loop
        self.translayer = None
        self.addr = addr

    def connection_made(self, transport):
        self.translayer = transport
        sock = self.translayer.get_extra_info('socket')
        sock.settimeout(3)
        addrinfo = socket.getaddrinfo(self.addr, None)[0]
        if addrinfo[0] == socket.AF_INET: # Supporting IPv4
            ttl = struct.pack('@i', 1)
            sock.setsockopt(socket.IPPROTO_IP, 
                socket.IP_MULTICAST_TTL, ttl)

        else: # Supporting IPv6
            ttl = struct.pack('@i', 2)
            sock.setsockopt(socket.IPPROTO_IPV6, 
                socket.IPV6_MULTICAST_HOPS, ttl)

        #self.transport.sendto(sys.argv[1].encode("ascii"), (self.addr,BROADCAST_PORT))

        #Schedule a call to send_packets()
        loop.call_later(SENDINTERVAL, send_packets, 1, self.addr)
        ##Schedule a call to calc_avg_latency()
        loop.call_later(LATENCYINTERVAL, calc_avg_latency)


    def datagram_received(self, data, addr):
        # if the sender and the receiver have the same IP address, the packet will be discarded.
        if (sys.argv[1] != addr[0]):
            print("Reply from {}: {!r}".format(addr, data))
            t = objdata[int(data)]
            t.total_latency()

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        self.loop.stop()


def main():

    global loop
    loop = asyncio.get_event_loop()
    print("Starting UDP server")

    addrinfo = socket.getaddrinfo(BROADCAST_ADDR, None)[0]
    multisock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    multisock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    multisock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])

    if addrinfo[0] == socket.AF_INET: # IPv4
        multisock.bind(('', BROADCAST_PORT))
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        multisock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # IPv6 part
    else:
        multisock.bind(('', BROADCAST_PORT))
        mreq = group_bin + struct.pack('@I', 0)
        multisock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)


    listen = loop.create_datagram_endpoint(
        MulticastServerProtocol,
        sock=multisock,
    )

    # Create a UDP socket
    sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    connect = loop.create_datagram_endpoint(

        lambda: DiscoveryClientProtocol(loop,BROADCAST_ADDR),
        sock=sock,

    )
    global transport
    # Listen for incoming datagrams
    transport, protocol = loop.run_until_complete(listen)
    # Sending UDP datagrams to the server
    transport, protocol = loop.run_until_complete(connect)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # transport.close()
        loop.close()

if __name__ == '__main__':
    main()






