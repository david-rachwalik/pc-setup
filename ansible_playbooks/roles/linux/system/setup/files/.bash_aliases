# Anytime the aliases are updated, be sure to restart your shell; source (.) has permission errors
# https://linuxize.com/post/bash-functions/
# Able to pass parameters such as --tags or --skip-tags
# Example: inline ternary operator (conditional expression); a=$([ "$b" == 5 ] && echo "$c" || echo "$d")
    # if [ -n "$1" ]; then
    #     ansible-playbook "system_setup.yml $*"
    # else
    #     ansible-playbook "system_setup.yml"
    # fi
clean () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "system_clean.yml $*" || echo "system_clean.yml")
    ansible-playbook $play_run
}
setup () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "system_setup.yml $*" || echo "system_setup.yml")
    ansible-playbook $play_run
}
shutdown () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "system_clean.yml -e shutdown=true $*" || echo "system_clean.yml -e shutdown=true")
    ansible-playbook $play_run
}

appc () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "proj_create.yml $*" || echo "proj_create.yml")
    ansible-playbook $play_run
}
appd () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "proj_delete.yml $*" || echo "proj_delete.yml")
    ansible-playbook $play_run
}

azc () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "az_app_create.yml $*" || echo "az_app_create.yml")
    ansible-playbook $play_run
}
azd () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "az_app_delete.yml $*" || echo "az_app_delete.yml")
    ansible-playbook $play_run
}

test_args () {
    echo "$?"
}

# update --tags "alias"
# ansible-playbook system_setup.yml --tags "alias"

# alias update='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_setup.yml )'
# alias shutdown='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml -e "shutdown=true" )'
# alias clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml )'
# alias win_up='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_setup.yml --tags "windows" )'
# alias wsl_up='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_setup.yml --tags "linux" )'
# alias win_clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml --tags "windows" )'
# alias wsl_clean='( cd "$HOME/pc-setup/ansible_playbooks" && ansible-playbook system_clean.yml --tags "linux" )'