# SOCKET

SO_RESUSEPORT is a flag that allows multiple threads or even processes to use the same port for receiving incoming connections.


# TCP

SO_KEEPALIVE - This is a mechanism that allows detecting connection breaks between the client and the server. It works on the principle of sending empty packets to the server to keep the connection active. If the server does not receive packets within a certain time, it closes the connection. This prevents the connection from hanging in case the client or server stops responding.

TCP_NODELAY - Nagle's algorithm buffers the data being sent, trying to send larger packets to avoid the overhead of transmitting small packets, which can lead to some delay in data transmission.


# Overcoming Losses in the Communication Channel

Suppose we have a connection where, say, 30% of packets are lost, and there is no possibility to change the provider or improve the quality of the channel, nor can we change the location. We can try to solve the problem as follows:

WireGuard Server -> UDPspeeder Server -> Network -> UDPspeeder Client -> WireGuard Client

Now in more detail:
UDPspeeder is a simple UDP tunnel that reformats UDP packets by adding FEC (Forward Error Correction) data. FEC data allows for the recovery of lost packets. Thus, if 30% of packets are lost, UDPspeeder can recover them. There are downsides:
- It works in User Space, which is not very good for performance
- It adds some delay (in my tests about 10-20ms)
- It only works with UDP packets

Thus, if you use WireGuard within this channel, you can get a good result, as WireGuard works over UDP, and if packets are lost, UDPspeeder can recover them.

Setting up the stand:
IP of the host where the WireGuard server is configured - 10.1.0.1
IP of the host where the WireGuard client is configured - 10.1.0.2

UDPspeeder on the server:

```
./speederv2 -s -l 10.1.0.1:8888 -r 10.1.0.1:7777 -f20:10
```

- The `-l` parameter is the address and port on which the UDPspeeder server will wait for the UDPspeeder client
- The `-r` parameter is the outgoing address and port to which UDPspeeder will intercept to send it into the communication channel with FEC
- The `-f` parameter is the FEC parameters (Forward Error Correction), 20:10 means that for every 20 packets, 10 FEC packets will be added

UDPspeeder on the client:

```
./speederv2 -c -l 10.1.0.2:3333 -r 45.66.77.88:8888 -f20:10
```

- The `-l` parameter is the address and port on which the UDPspeeder client will wait for a connection, in our

case WireGuard
- The `-r` parameter is the address and port of the UDPspeeder server
- The `-f` parameter is the FEC parameters (Forward Error Correction), 20:10 means that for every 20 packets, 10 FEC packets will be added

Note: Avoid using 127.0.0.1 as the IP address for UDPSpeeder entry points, because the MTU of the lo interface is usually significantly higher than the common 1500 for Ethernet networks. As a result, UDPSpeeder will form packets that cannot pass through Ethernet interfaces.

WireGuard on the server:
In the file `/etc/wireguard/wg0.conf`
- In the [Interface] section, `ListenPort` should be equal to the port on which UDPspeeder intercepts packets, in our case, this is 7777

WireGuard on the client:
In the file `/etc/wireguard/wg0.conf`
- In the [Peer] section, `Endpoint` should be equal to the address and port on which the UDPspeeder client waits for a connection, in our case, this is 3333
