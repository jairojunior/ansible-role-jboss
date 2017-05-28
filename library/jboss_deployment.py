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
        if current_checksum == checksum(src):
            return False, current_checksum

        return True, client.update_deployment(name, src)

    return True, client.deploy(name, src)


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
            host=dict(type='str', default='127.0.0.1'),
            port=dict(type='int', default=9990),
        ),
    )

    client = Client(username='ansible',
                    password='ansible',
                    host=module.params['host'],
                    port=module.params['port'])

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
