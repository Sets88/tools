# Generate certificate authority(CA)

    openssl genrsa -des3 -out myCA.key 2048

# Generate root certificate

    openssl req -x509 -new -nodes -key myCA.key -sha256 -days 6000 -out myCA.pem

# Generate private key

    openssl genrsa -out testing.key 2048

# Generate CSR

    openssl req -new -key testing.key -out testing.csr


# Create ext file describeing related domains

    authorityKeyIdentifier=keyid,issuer
    basicConstraints=CA:FALSE
    keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
    subjectAltName = @alt_names

    [alt_names]
    DNS.1 = *.testing.com
    DNS.2 = testing.com
    DNS.3 = *.testing.dev
    DNS.2 = testing.dev

# Generate certificate

    openssl x509 -req -in testing.csr -CA myCA.pem -CAkey myCA.key -CAcreateserial -out testing.crt -days 825 -sha256 -extfile testing.ext
