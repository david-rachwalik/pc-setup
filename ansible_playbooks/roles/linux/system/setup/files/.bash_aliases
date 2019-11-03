# Anytime the aliases are updated, be sure to restart your shell; source (.) has permission errors
alias update='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_update.yml )'
alias shutdown='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml -e "shutdown=true" )'
alias clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml )'
alias win_up='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_update.yml --tags "windows" )'
alias wsl_up='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_update.yml --tags "linux" )'
alias win_clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml --tags "windows" )'
alias wsl_clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml --tags "linux" )'