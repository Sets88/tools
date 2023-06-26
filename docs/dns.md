# Get all DNS records

Some zones has AXFR protocol(DNS zone transfer) enabled so it allows to get all NS records from it with this command

    dig -t AXFR example.com
