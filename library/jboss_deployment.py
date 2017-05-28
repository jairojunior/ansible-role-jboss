#!/usr/bin/python

import hashlib
from jboss.client import Client
from jboss.operation_error import OperationError
from ansible.module_utils.basic import AnsibleModule


def checksum(src):
    return hashlib.sha1(open(src).read()).hexdigest()


def read_deployment(client, name):
    exists, result = client.read('/deployment=' + name)

    if exists:
        bytes_value = result['content'][0]['hash']['BYTES_VALUE']
        result = bytes_value.decode('base64').encode('hex')

    return exists, result


def present(client, name, src):
    exists, current_checksum = read_deployment(client, name)
    if exists:
        desired_checksum = checksum(src)

        if current_checksum == desired_checksum:
            return False, current_checksum

        client.update_deployment(name, src)
        return True, desired_checksum

    client.deploy(name, src)
    return True, 'Deployed ' + name


def absent(client, name):
    exists = read_deployment(client, name)
    if exists:
        client.undeploy(name)
        return True, 'Removed ' + name

    return False, 'Deployment absent ' + name


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            src=dict(required=True, type='str'),
        ),
    )

    client = Client('ansible', 'ansible')

    try:
        state = module.params['state']
        if state == 'present':
            has_changed, result = present(
                client, module.params['name'], module.params['src'])
        else:
            has_changed, result = absent(client, module.params['name'])

        module.exit_json(changed=has_changed, meta=result)
    except OperationError as err:
        module.fail_json(msg=str(err))


if __name__ == '__main__':
    main()
