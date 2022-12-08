# To pinhole NAT and share port

Remote host(the one to forward port from, let's call it H1) connects to ssh server to deploy port to(let's call it H2)
after successful connection H2 going to have open local port 1234 which is actually 22 port of H1, more then that localhost is not a constant,
it can be replaced to proxy any port and host available to H1

    ## send local 22 port to 11.22.33.44:1234
    ssh -g -R 1234:localhost:22 user@11.22.33.44

The other case when reachable to H2 host and port should be delivered onto H1 machine, H1 connects to ssh server of H2,
after successful connection H1 going to have open local port 1234 which is actually 22 port of "othermachine.com" proxied via H2

    ## bring port 22 on othermachine.com reachable by 11.22.33.44 to localhost:1234
    ssh -L 1234:othermachine.com:22 user@11.22.33.44
