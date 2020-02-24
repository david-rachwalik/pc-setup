# Anytime the aliases are updated, be sure to restart your shell; source (.) has permission errors
# https://linuxize.com/post/bash-functions/
# Able to pass parameters such as --tags or --skip-tags
# Example: inline ternary operator (conditional expression); a=$([ "$b" == 5 ] && echo "$c" || echo "$d")
    # if [ -n "$1" ]; then
    #     ansible-playbook "system_setup.yml $*"
    # else
    #     ansible-playbook "system_setup.yml"
    # fi
setup () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "system_setup.yml $*" || echo "system_setup.yml")
    ansible-playbook $play_run
}
clean () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "system_clean.yml $*" || echo "system_clean.yml")
    ansible-playbook $play_run
}
shutdown () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "system_clean.yml -e shutdown=true $*" || echo "system_clean.yml -e shutdown=true")
    ansible-playbook $play_run
}

# --- Alias Actions Required ---
# repoc         app repository create
# repod         app repository delete
# azc           azure webapp create
# azd           azure webapp delete
# appc          full app create
# appd          full app delete

repoc () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "app_create.yml --tags 'repo' $*" || echo "app_create.yml --tags 'repo'")
    ansible-playbook $play_run
}
repod () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "app_delete.yml --tags 'repo' $*" || echo "app_delete.yml --tags 'repo'")
    ansible-playbook $play_run
}
azc () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "app_create.yml --tags 'azure' $*" || echo "app_create.yml --tags 'azure'")
    ansible-playbook $play_run
}
azd () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "app_delete.yml --tags 'azure' $*" || echo "app_delete.yml --tags 'azure'")
    ansible-playbook $play_run
}
appc () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "app_repo_create.yml $*" || echo "app_repo_create.yml")
    ansible-playbook $play_run
}
appd () {
    cd "$HOME/pc-setup/ansible_playbooks"
    play_run=$([ -n "$1" ] && echo "app_repo_delete.yml $*" || echo "app_repo_delete.yml")
    ansible-playbook $play_run
}

test_args () {
    # echo "$?"
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