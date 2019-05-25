#!/bin/bash
#
# Encrypt configuration secrets.
# Copies the unencrypted secrets.secret.yml into secrets.yml and applies AES
# encryption to it, using the password stored in ~/.vault-pass.txt
#
# Run this from ./scripts/configure
#
set -e
cp ./scripts/configure/ansible/secrets.secret.yml ./scripts/configure/ansible/secrets.yml
ansible-vault encrypt ./scripts/configure/ansible/secrets.yml --vault-password-file ~/.vault-pass.txt
