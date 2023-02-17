# Configure server

Install wireguard

    apt install wireguard

Enable ip forwarding

    echo -e "\nnet.ipv4.ip_forward = 1" >> /etc/sysctl.conf
    sysctl -p

Generate public and private keys

    umask 077
    wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey

Create interface config file

    cat << EOF > /etc/wireguard/wg0.conf
    [Interface]
    PrivateKey = $(cat /etc/wireguard/privatekey)
    Address = 10.0.0.1/24
    PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
    ListenPort = 51234

    EOF

Create directory for client configs

    mkdir /etc/wireguard/clients

Create client keys

    wg genkey | tee /etc/wireguard/clients/client1 | wg pubkey > /etc/wireguard/clients/client1.pub

Create interface config file for client

    cat << EOF > /etc/wireguard/clients/client1.conf
    [Interface]
    Address = 10.0.0.2/32
    PrivateKey = $(cat /etc/wireguard/clients/client1)
    DNS = 8.8.8.8

    [Peer]
    PublicKey = $(cat /etc/wireguard/publickey)
    Endpoint = <server-public-ip>:51234
    AllowedIPs = 0.0.0.0/0, ::/0
    EOF

Add client to interface config file

    cat << EOF >> /etc/wireguard/wg0.conf
    [Peer]
    PublicKey = $(cat /etc/wireguard/clients/client1.pub)
    AllowedIPs = 10.0.0.2/32
    
    EOF

Start wireguard

    systemctl start wg-quick@wg0

Send /etc/wireguard/clients/client1.conf file to client
