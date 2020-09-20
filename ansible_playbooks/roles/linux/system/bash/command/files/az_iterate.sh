#!/bin/bash

# --- Script to quickly iterate upon 'azure' command for development ---

cd ~/pc-setup/ansible_playbooks
ansible-playbook system_setup.yml --tags "py" --skip-tags "windows"

# azure --debug login
azure --debug --secret-key="AutoTestKey" --secret-value="007" secret
