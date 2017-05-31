#!/usr/bin/python


ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.0'}

DOCUMENTATION = '''
---
module: jboss_resource
short_description: Manage JBoss configuration (datasources, queues, https, etc)
description:
    - Manages JBoss configuration/resources (i.e. Management Model) through Management API, locally or remote, ensuring resource state matches specified attributes.
author: "Jairo Junior (@jairojunior)"
options:
    name:
      description: Name of the configuration resource using JBoss-CLI path expression.
      required: true
      aliases: [path]
    state:
      description: Whether the resource should be present or absent.
      required: false
      default: present
      choices: [present, absent]
    attributes:
      description: Attributes defining the state of configuration resource.
      required: false
'''

EXAMPLES = '''
# Configure a datasource
jboss_resource:
name: "/subsystem=datasources/data-source=DemoDS"
state: present
attributes:
  driver-name: h2
  connection-url: "jdbc:h2:mem:demo;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE"
  jndi-name: "java:jboss/datasources/DemoDS"
  user-name: sa
  password: sa
  min-pool-size: 20
  max-pool-size: 40

# TLSRealm
jboss_resource:
name: "/core-service=management/security-realm=TLSRealm"

# Server identity
jboss_resource:
name: "/core-service=management/security-realm=TLSRealm/server-identity=ssl"
attributes:
  keystore-path: jboss.jks
  keystore-relative-to: /etc/pki/java
  keystore-password: changeit
  alias: demo
  key-password: changeit

# HTTPS Listener
jboss_resource:
name: "/subsystem=undertow/server=default-server/https-listener=https"
attributes:
  socket-binding: https
  security-realm: TLSRealm
  enabled: true
'''

RETURN = '''
meta:
    description: Management API response
    returned: success
    type: dict
    sample:"{'outcome': 'success', 'response-headers': {'process-state': 'reload-required'}}"
'''

try:
    from jboss.client import Client
    from jboss.operation_error import OperationError
    HAS_JBOSS_PY = True
except ImportError:
    HAS_JBOSS_PY = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback


def diff(current, desired):
    attributes_diff = {}

    for key, value in desired.items():
        if not current[key] == value:
            attributes_diff[key] = value

    return attributes_diff


def present(module, client, path, desired_attributes, exists, current_attributes):
    if exists:
        changed_attributes = diff(current_attributes, desired_attributes)

        if not changed_attributes:
            module.exit_json(changed=False,
                             msg='{0} exists with {1}'.format(path, current_attributes))

        if not module.check_mode:
            module.exit_json(changed=True,
                             msg='Updated {0} of {1}'.format(changed_attributes, path),
                             meta=client.update(path, changed_attributes))

        module.exit_json(changed=True,
                         diff=dict(before=current_attributes, after=desired_attributes))

    if not module.check_mode:
        module.exit_json(changed=True,
                         meta=client.add(path, desired_attributes),
                         msg='Added {0} with {1}'.format(path, desired_attributes))

    module.exit_json(changed=True,
                     diff=dict(before=current_attributes, after=desired_attributes))


def absent(module, client, path, exists):
    if exists:
        if not module.check_mode:
            module.exit_json(changed=True,
                             msg='Removed ' + path,
                             meta=client.remove(path))

        module.exit_json(changed=True, msg='Resouce exists')

    module.exit_json(changed=False, msg=path + ' is absent')


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=['path'], required=True, type='str'),
            state=dict(choices=['present', 'absent'], default='present'),
            attributes=dict(required=False, type='dict', default=dict()),
            username=dict(type='str', fallback=(env_fallback, ['JBOSS_MANAGEMENT_USER'])),
            password=dict(no_log=True, type='str', fallback=(env_fallback, ['JBOSS_MANAGEMENT_PASSWORD'])),
            host=dict(type='str', default='127.0.0.1', fallback=(env_fallback, ['JBOSS_MANAGEMENT_HOST'])),
            port=dict(type='int', default=9990, fallback=(env_fallback, ['JBOSS_MANAGEMENT_PORT']))
        ),
        supports_check_mode=True
    )

    if not HAS_JBOSS_PY:
        module.fail_json(msg='jboss-py required for this module')

    client = Client(module.params['username'],
                    module.params['password'],
                    module.params['host'],
                    module.params['port'])

    try:
        path = module.params['name']
        attributes = module.params['attributes']
        state = module.params['state']

        exists, current_attributes = client.read(path)

        if state == 'present':
            present(module, client, path, attributes, exists, current_attributes)
        else:
            absent(module, client, path, exists)
    except OperationError as err:
        module.fail_json(msg=str(err))


if __name__ == '__main__':
    main()
