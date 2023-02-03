## Configure SPF

SPF contains list of ip addresses emails using your domain may be sent from

Set TXT record on @(root) of domain if emails comes from root domain or TXT record on subdomain record with value like

    v=spf1 ip4:123.123.123.0/24 ip4:111.111.111.123 ~all

## Configure DKIM

DKIM contains public key which can be used to valudate email signature

Email has DKIM signature in header called "DKIM-Signature" like this

    DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=example.com;
      h=content-transfer-encoding:content-type:from:mime-version:subject:to:
      cc:content-type:from:subject:to; s=test;
      bh=nqfhf3ZE/SDd2EHCsvUXSEWS3RB+zcfMSd1mcEob1ba=;
      b=ftYo6rgpiuYBaga8FAhp9c7Ocn8HqKbD+MJ8uyjpbuo6QmmUVXdjcRdRt5sarWSuZPzx
      EiYzflYhLeaF/L1AxgHyp25woYil23+vd1tZgzX/SIcmF3L+h++EmSD+Kl0OW8UeEFUBsI
      CPxYVFaIZrNFmMeW7t1zlPyGhgxwIiQFA=

where "d" is domain this signature done for, "s" is selector which helps to find public key to validate signature, you can get it like this

    dig -t TXT test._domainkey.example.com

This record gonna be look like this, where "p" is an actual public key

    v=DKIM1; t=s; n=core; p=SOMEKEY

This record can also be a CNAME record rather then TXT record which may point to other domain of TXT record where DKIM record may be taken from

## Configure DMARC

DMARC record tells what to do with email on violation, it should be written in TXT _dmarc record and contain something like:

    v=DMARC1;p=none;sp=quarantine;pct=100;rua=mailto:dmarcreports@example.com;

## Configure MX record

DNS MX record points to the host where incomming email should be sent to
