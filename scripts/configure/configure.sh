#!/bin/bash
#
# Configure host server with Ansible
# Assumes you have the vault password stored in ~/.vault-pass.txt
# Run this from ./scripts/configure
#
ansible-playbook \
    --vault-password-file ~/.vault-pass.txt \
    --inventory ./scripts/configure/ansible/hosts \
    ./scripts/configure/ansible/site.yml
