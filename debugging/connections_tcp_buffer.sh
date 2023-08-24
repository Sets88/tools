#! /bin/sh
# Retrieve all TCP connections within all namespaces and sort them by the size of the accumulated TCP buffer
# Large values in the second column may indicate that the application is struggling to handle the data flow or simply not reading from the stream adequately.
# Significant values in the third column indicate that there is still no confirmation that the data has been delivered, which may suggest network issues between the client and server
# or remote host is out of TCP buffer.

lsns -t net -n -o PID | xargs -I {} nsenter -t {} -n netstat -t -n | grep ESTABLISHED | sort -n -k 2 -k 3
