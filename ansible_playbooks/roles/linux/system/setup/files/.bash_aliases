# Anytime the aliases are updated, be sure to restart your shell; source (.) has permission errors
alias update='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook update.yml )'
alias shutdown='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook clean.yml -e "shutdown=true" )'
alias clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook clean.yml )'
alias win_up='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook update.yml --tags "windows" )'
alias wsl_up='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook update.yml --tags "linux" )'
alias win_clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook clean.yml --tags "windows" )'
alias wsl_clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook clean.yml --tags "linux" )'