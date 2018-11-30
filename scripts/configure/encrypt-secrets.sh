#!/bin/bash
#
# Encrypt configuration secrets.
# Copies the unencrypted secrets.secret.yml into secrets.yml and applies AES
# encryption to it, using the password stored in ~/.vault-pass.txt
#
# Run this from ./scripts/configure
#
set -e
cp ./ansible/secrets.secret.yml ./ansible/secrets.yml
ansible-vault encrypt ./ansible/secrets.yml --vault-password-file ~/.vault-pass.txt
