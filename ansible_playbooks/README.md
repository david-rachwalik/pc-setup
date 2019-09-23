            ::: Ansible for Windows 10 :::

1) Connect to Windows and gather facts about the environment
- ansible-playbook win_status.yml

2) Backup Windows settings
- ansible-playbook win_backup.yml

3) Install Windows features and applications
- ansible-playbook win_install.yml

4) Uninstall Windows features and applications
- ansible-playbook win_uninstall.yml


Backup application settings and update Windows:
- backup game saves, screenshots, addons
- backup preferences for productivity programs
- update windows features, install patches, chocolatey upgrade, etc.
- configure security settings

*) For other playbook plans, see TODO.md


            ::: Ansible for Azure :::

1) Connect to Azure and gather facts about resource groups
- ansible-playbook az_app_status.yml

2) Create an Azure WebApp
- ansible-playbook az_app_create.yml

3) Delete an Azure WebApp
- ansible-playbook az_app_delete.yml
