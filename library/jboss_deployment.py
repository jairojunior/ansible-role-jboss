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
    state: present
    src: /tmp/app.jar
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


def present(module, client, name, src, remote_src, checksum_src, exists, current_checksum):
    if exists:
        if current_checksum == checksum_src:
            module.exit_json(changed=False,
                             meta='Deployment {0} exists with {1}'.format(name, current_checksum))

        if not module.check_mode:
            module.exit_json(changed=True,
                             meta=client.update_deploy(name, src, remote_src),
                             msg='Update deployment {0} content with {1}. Previous content checksum {2}'.format(name, checksum_src, current_checksum))

        module.exit_json(changed=True, diff=dict(before=current_checksum, after=checksum_src))

    if not module.check_mode:
        module.exit_json(changed=True,
                         meta=client.deploy(name, src, remote_src),
                         msg='Deployed {0}'.format(name))

    module.exit_json(changed=True, diff=dict(before='', after=checksum_src))


def absent(module, client, name, exists):
    if exists:
        if not module.check_mode:
            module.exit_json(changed=True,
                             meta=client.undeploy(name),
                             msg='Undeployed {0}'.format(name))

        module.exit_json(changed=True, msg='Deployment exists')

    module.exit_json(changed=False, msg='Deployment {0} is absent'.format(name))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            state=dict(choices=['present', 'absent'], default='present'),
            src=dict(required=False, type='str'),
            remote_src=dict(type='bool', default=False),
            host=dict(type='str', default='127.0.0.1'),
            port=dict(type='int', default=9990),
        ),
        supports_check_mode=True
    )

    if not HAS_JBOSS_PY:
        module.fail_json(msg='jboss-py required for this module')

    client = Client(username='ansible',
                    password='ansible',
                    host=module.params['host'],
                    port=module.params['port'])

    try:
        name = module.params['name']
        state = module.params['state']
        src = module.params['src']
        checksum_src = module.sha1(src)
        remote_src = module.params['remote_src']

        exists, current_checksum = read_deployment(client, name)

        if state == 'present':
            present(module, client, name, src, remote_src, checksum_src, exists, current_checksum)
        else:
            absent(module, client, name, exists)
    except OperationError as err:
        module.fail_json(msg=str(err))


if __name__ == '__main__':
    main()
