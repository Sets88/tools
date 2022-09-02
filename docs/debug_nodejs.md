## Create container in namespace of other container to attach to it with gdb

    $ docker run -u0 --pid container:<container>  --privileged -ti --rm --name debugger <image_name_of_original_container> sh

## Find pid of target process

    $ ps aux
    PID   USER     TIME  COMMAND
         1 node      1:05 /sbin/docker-init -- docker-entrypoint.sh python test.py
         6 node      1d13 node index.js
         66 root      0:00 sh
         72 root      0:00 ps aux

# Install required for debugger packages

    apt install -y lldb git python3 make g++
    apt install -y gdb # Will use it to create a core dump
    npm install -g llnode


## Do a core dump of a process

To not block process it's better to do a core dump rather then debug on working process

    gdb --batch-silent -p <some_pid> -ex "generate-core-file test.core" -ex detach -ex quit

## Start debugger

    llnode node --core test.core

## Use v8 * to debug

    (lldb) v8 help
