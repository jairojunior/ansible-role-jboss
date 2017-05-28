#!/usr/bin/python

from jboss.client import Client
from jboss.operation_error import OperationError
from ansible.module_utils.basic import AnsibleModule


def intersect(current, desired):
    managed_state = {}

    for key in desired:
        current_value = current[key]

        if isinstance(current_value, unicode):
            current_value = current_value.encode('utf-8')

        managed_state[key] = current_value

    return managed_state


def diff(current, desired):
    attributes_diff = {}

    for key, value in desired.items():
        if current[key] == value:
            attributes_diff[key] = value

    return attributes_diff


def present(client, path, attributes):
    exists, current_attributes = client.read(path)

    if exists:
        desired_attributes = attributes

        current_managed_attributes = intersect(
            current_attributes, desired_attributes)

        if current_managed_attributes == desired_attributes:
            return False, current_attributes

        client.update(path,
                      diff(current_managed_attributes, desired_attributes))

        return True, current_attributes

    client.add(path, attributes)
    return True, 'Added ' + path


def absent(client, path):
    exists = client.read(path)

    if exists:
        client.remove(path)

        return True, 'Removed ' + path

    return False, path + ' is absent'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(aliases=['path'], required=True, type='str'),
            attributes=dict(required=False, type='dict'),
        ),
    )

    client = Client('ansible', 'ansible')

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
