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

# Configure TLS
jboss_resource:
  name: /core-service=management/security-realm=TLSRealm

jboss_resource:
  name: /core-service=management/security-realm=TLSRealm/server-identity=tls
  attributes:
    keystore-path: '/etc/pki/tls/jboss.jks'
    keystore-password: changeit
    alias: demo
    key-password: changeit

jboss_resource:
  name: /subsystem=undertow/server=default-server/https-listener=https
  attributes:
    socket-binding: https
    security-realm: TLSRealm
    enabled: true
'''

try:
    from jboss.client import Client
    from jboss.operation_error import OperationError
    HAS_JBOSS_PY = True
except ImportError:
    HAS_JBOSS_PY = False

from ansible.module_utils.basic import AnsibleModule


def diff(current, desired):
    attributes_diff = {}

    for key, value in desired.items():
        if not current[key] == value:
            attributes_diff[key] = value

    return attributes_diff


def present(client, path, attributes):
    exists, current_attributes = client.read(path)

    if exists:
        changed_attributes = diff(current_attributes, attributes)

        if changed_attributes:
            return True, client.update(path, changed_attributes)

        return False, current_attributes

    return True, client.add(path, attributes)


def absent(client, path):
    exists, _ = client.read(path)

    if exists:
        return True, client.remove(path)

    return False, '{} is absent'.format(path)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(aliases=['path'], required=True, type='str'),
            attributes=dict(required=False, type='dict'),
            host=dict(type='str', default='127.0.0.1'),
            port=dict(type='int', default=9990),
        ),
    )

    if not HAS_JBOSS_PY:
        module.fail_json(msg='jboss-py required for this module')

    client = Client(username='ansible',
                    password='ansible',
                    host=module.params['host'],
                    port=module.params['port'])

    try:
        state = module.params['state']
        if state == 'present':
            has_changed, result = present(
                client, module.params['name'], module.params['attributes'])
        else:
            has_changed, result = absent(client, module.params['name'])

        module.exit_json(changed=has_changed, meta=result)
    except OperationError as err:
        module.fail_json(msg=str(err))


if __name__ == '__main__':
    main()
