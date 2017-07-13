network_facts
=========

This role gathers facts about network devices to be used later in other roles or playbooks.

Facts gathered for all OS types :
hostname
interfaces
config
version
mgmt_interface_name

All but Arista :
config_lines : Arista returns JSON object, so to get the config_lines just use `config.cmds`.

Only NXOS and IOS-XR :
vrf_name

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.
The `cli` variable holds the credentials and transport type to connect to the device.
The `device_os` variable is the type of device OS that the current host is. We use this to decide which tasks and templates to run since each OS can have OS specific commands. This should be coming from a group var.

