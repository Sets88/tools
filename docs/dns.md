# Get all DNS records

Some zones has AXFR protocol(DNS zone transfer) enabled so it allows to get all NS records from it with this command

    dig -t AXFR example.com

# Records types

## A

Contains IPv4 address

## AAAA

Contains IPv6 address

## NS

Contains a domain name of DNS serving current DNS zone

## CNAME

Is a link pointing to other dns record

## TXT

Contains any text record

## MX

Contains the email server address responsible for email delivery for this domain
