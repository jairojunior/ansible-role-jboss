#!/usr/bin/python


ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.0'}

DOCUMENTATION = '''
---
module: jboss_deployment
short_description: Manage JBoss deployments
description:
    - Manages JBoss deployments through Management API, using local or remote artifacts and ensuring deployed content checksum matches source file checksum.
author: "Jairo Junior (@jairojunior)"
options:
    name:
      description: Name of deployment unit.
      required: true
    state:
      description: Whether the deployment should be present or absent.
      required: false
      default: present
      choices: [present, absent]
    src:
      description: Local or remote path of deployment file.
      required: false
    remote_src:
      description: If False, it will search for src at originating/master machine, if True it will go to the remote/target machine for the src. Default is False.
      required: false
      default: false
'''

EXAMPLES = '''
# Undeploy hawt.io
- jboss_deployment:
    name: hawtio.war
    state: absent

# Deploy hawt.io (uploads src from local)
- jboss_deployment:
    name: hawtio.war
    src: /opt/hawtio.war
    state: present

# Deploy app.jar (already present in remote host)
- jboss_deployment:
    name: app.jar
    state: absent
    remote_src: True
'''


try:
    from jboss.client import Client
    from jboss.operation_error import OperationError
    HAS_JBOSS_PY = True
except ImportError:
    HAS_JBOSS_PY = False

from ansible.module_utils.basic import AnsibleModule


def read_deployment(client, name):
    exists, result = client.read('/deployment=' + name)

    if exists:
        bytes_value = result['content'][0]['hash']['BYTES_VALUE']
        result = bytes_value.decode('base64').encode('hex')

    return exists, result


def present(client, name, src, remote_src, checksum_src):
    exists, current_checksum = read_deployment(client, name)

    if exists:
        if current_checksum == checksum_src:
            return False, current_checksum

        return True, client.update_deploy(name, src, remote_src)

    return True, client.deploy(name, src, remote_src)


def absent(client, name):
    exists, _ = read_deployment(client, name)
    if exists:
        return True, client.undeploy(name)

    return False, 'Deployment {} is absent'.format(name)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            src=dict(required=False, type='str'),
            remote_src=dict(type='bool', default=False),
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
                client,
                module.params['name'],
                module.params['src'],
                module.params['remote_src'],
                module.sha1(module.params['src']))
        else:
            has_changed, result = absent(client, module.params['name'])

        module.exit_json(changed=has_changed, meta=result)
    except OperationError as err:
        module.fail_json(msg=str(err))


if __name__ == '__main__':
    main()
