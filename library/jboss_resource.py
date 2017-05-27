#!/usr/bin/python

from jboss.client import Client
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
    attributes_diff = dict()

    for key, value in desired.items():
        if current[key] is not value:
            attributes_diff[key] = value

    return attributes_diff


def present(client, read_response, data):
    if read_response['outcome'] == 'success':
        current_attributes = read_response['result']
        desired_attributes = data['attributes']

        current_managed_attributes = intersect(
            current_attributes, desired_attributes)

        if current_managed_attributes == desired_attributes:
            return False, False, current_attributes

        client.update(data['name'],
                      diff(current_managed_attributes, desired_attributes))

        return False, True, current_attributes

    client.add(data['name'], data['attributes'])
    return False, True, 'Added ' + data['name']


def absent(client, read_response, data):
    if read_response['outcome'] == 'success':
        client.remove(data['name'])

        return False, True, 'Removed ' + data['name']

    return False, False, data['name'] + ' is absent'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(aliases=['path'], required=True, type='str'),
            attributes=dict(required=False, type='dict'),
        ),
    )

    choice = {'present': present, 'absent': absent}

    client = Client('ansible', 'ansible')

    response = client.read(module.params['name'])

    is_error, has_changed, result = choice[module.params['state']](
        client,
        response,
        module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error", meta=result)


if __name__ == '__main__':
    main()
