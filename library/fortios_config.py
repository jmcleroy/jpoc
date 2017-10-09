#!/usr/bin/python
#
# Ansible module to manage configuration on fortios devices
# (c) 2016, Benjamin Jolivot <bjolivot@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'community',
    'version': '0.1'
}

DOCUMENTATION = """
---
module: fortios_address
version_added: "2.3"
author: "Benjamin Jolivot (@bjolivot)"
short_description: Manage fortios firewall config
description:
  - This module provide management of FortiOS Devices configuration
options:
  host:
    description:
      - Specifies the DNS hostname or IP address for connecting to the remote fortios device
    required: true
  username:
    description:
      - Configures the username used to authenticate to the remote device.
    required: true
  password:
    description:
      - Specifies the password used to authenticate to the remote device.
    required: true
  timeout
    description:
      - Specifies timeout in seconds for connecting to the remote device.
      required: false 
      default: 60
  vdom
    description:
      - Specifies on which vdom to apply configuration
      required: false
      default: None
  src
    description:
      - target configuration file path
      required: false
  dest
    description:
      - Backup configuration file path
      required: false
  filter
    description:
      - in case of backup, if you want partial config, you can restrict by giving expected configuration path (ex: firewall address)
      required: false
      default: ""
  state
    description:
      - Specifies if address need to be added or deleted
      required: true
      choices: ['updated', 'backuped']
  logfile
    description:
      - logfile path to log command sent to the device and responses
      required: false 

notes:
  - This module requires pyFG python library
"""

EXAMPLES = """
- name: Backup current config
  fortios_config:
    host: 192.168.0.254
    username: admin
    password: password
    state: backuped
    dest: ./backup.conf
- name: Backup only address objects, log all commands to file
  fortios_config:
    host: 192.168.0.254
    username: admin
    password: password
    state: backuped
    dest: ./backup_address_objects.conf
    filter: "firewall address"
    logfile: fortios.log
- name: Update configuration from file
  fortios_config:
    host: 192.168.0.254
    username: admin
    password: password
    state: updated
    src: new_configuration.conf
"""

RETURN = """
running_config:
  description: full config string
  returned: always
  type: string
change_string:
  description: The commands really executed by the module
  returned: only if config changed
  type: string
"""
import logging
from ansible.module_utils.basic import AnsibleModule

# check for pyFG lib
try:
    from pyFG import *
    from pyFG.fortios import logger
    from pyFG.exceptions import *

    HAS_PYFG = True
except:
    HAS_PYFG = False

# some blocks don't support update, so remove them
NOT_UPDATABLE_CONFIG_OBJECTS = [
    "vpn certificate local",
]


def main():
    argument_spec = dict(
        host=dict(required=True),
        username=dict(required=True),
        password=dict(required=True, type='str'),
        timeout=dict(type='int', default=60),
        vdom=dict(type='str', default=None),
        state=dict(required=True, choices=['backuped', 'updated']),
        src=dict(type='str'),
        dest=dict(type='str'),
        filter=dict(type='str', default=""),
        logfile=dict(type='str'),
    )

    required_if = [
        ['state', 'backuped', ['dest']],
        ['state', 'updated', ['src']],
    ]

    # could not backup and update
    mutually_exclusive = [
        ['src', 'filter'],
        ['src', 'path'],
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=mutually_exclusive,
    )

    if module.params['logfile'] is not None:
        try:
            logger.setLevel(logging.DEBUG)
            fh = logging.FileHandler(module.params['logfile'])
            fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)
        except:
            module.fail_json(msg="Problem with logfile, read only ?")

    retkwargs = dict(changed=False)

    # fail if pyFG not present
    if not HAS_PYFG:
        module.fail_json(msg='Could not import the python library pyFG required by this module')

    # define device
    f = FortiOS(module.params['host'],
                username=module.params['username'],
                password=module.params['password'],
                timeout=module.params['username'],
                vdom=module.params['vdom'])

    # connect
    try:
        f.open()
    except:
        module.fail_json(
            msg='Error connecting device'
        )

    # get  config
    try:
        f.load_config(path=module.params['filter'])
        retkwargs['running_config'] = f.running_config.to_text()

    except:
        module.fail_json(
            msg='Error reading running config'
        )

    if module.params['state'] == 'backuped':
        # backup
        try:
            backup_file = open(module.params['dest'], "w")
            backup_file.write(retkwargs['running_config'])
            backup_file.close()
        except:
            module.fail_json(
                msg='Error writing running config to file {0}'.format(module.params['dest'])
            )
    else:
        # update config
        # store config in str
        try:
            conf_str = open(module.params['src'], 'r').read()
            f.load_config(in_candidate=True, config_text=conf_str)
        except:
            module.fail_json(msg="Can't open configuration file, or configuration invalid")

        # get updates lines
        change_string = f.compare_config()

        # remove not updatable parts
        c = FortiConfig()
        c.parse_config_output(change_string)

        for o in NOT_UPDATABLE_CONFIG_OBJECTS:
            c.del_block(o)

        change_string = c.to_text()

        if change_string != "":
            retkwargs['change_string'] = change_string
            retkwargs['changed'] = True

        # Commit if not check mode
        if module.check_mode == False and change_string != "":
            try:
                f.commit(change_string)
            except FailedCommit as e:
                # rollback
                module.fail_json(msg="Unable to commit change, check your args, the error was {0}".format(e.message))

    module.exit_json(**retkwargs)


if __name__ == '__main__':
    main()
    