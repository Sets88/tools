# Install yubico-piv-tool

Download it from https://developers.yubico.com/yubico-piv-tool/Releases/ or from (brew, apt, yum, or pacman)

# SSH Key

Generate new key

    ssh-keygen -b 2048 -t rsa -m PEM

or alter current key to PEM format

    ssh-keygen -p -m PEM

unfortunately 4096 and longer RSA keys are not supported by PIV specification

# Import key into yubikey

Slot 9a only can be used to store rsa key

    yubico-piv-tool --touch-policy=cached -s 9a -a import-key --pin-policy=once -i id_rsa

# Add card to ssh-agent

Remove old card if exists (as if it was previously added next command will not work even if "ssh-add -D" executed)

    ssh-add -e /usr/local/lib/libykcs11.dylib

Add new card

    ssh-add -s /usr/local/lib/libykcs11.dylib

Enter Yubikey PIN when it's asked for passphrase for PKCS#11
