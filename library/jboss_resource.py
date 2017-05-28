#!/usr/bin/python

from jboss.client import Client
from jboss.operation_error import OperationError
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
