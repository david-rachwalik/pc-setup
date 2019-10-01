# Ansible Playbooks

``` bash
cd ~/pc-setup/ansible_playbooks/
```

## Ansible for Windows 10

- Connect to Windows and gather facts about the environment

    ``` bash
    ansible-playbook win_status.yml
    ```

- Backup Windows application settings & data

    ``` bash
    ansible-playbook win_backup.yml
    ```

  - backup game saves, screenshots, addons
  - backup preferences for productivity programs

- Install Windows features and applications

    ``` bash
    ansible-playbook win_install.yml
    ```

  - update windows features, install patches, chocolatey upgrade, etc.
  - configure security settings

- Uninstall Windows features and applications

    ``` bash
    ansible-playbook win_uninstall.yml
    ```

## Ansible for Azure

- Connect to Azure and gather facts about resource groups

    ``` bash
    ansible-playbook az_app_status.yml
    ```

- Create an Azure WebApp

    ``` bash
    ansible-playbook az_app_create.yml
    ```

- Delete an Azure WebApp

    ``` bash
    ansible-playbook az_app_delete.yml
    ```
