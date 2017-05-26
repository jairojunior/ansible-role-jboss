#!/usr/bin/python

import json
import logging
import requests
from requests.auth import HTTPDigestAuth
from ansible.module_utils.basic import AnsibleModule


def management_request(payload):
    url = 'http://127.0.0.1:9990/management'
    headers = {'Content-Type': 'application/json'}
    return requests.post(
        url, data=json.dumps(payload), headers=headers,
        auth=HTTPDigestAuth('ansible', 'ansible'))


def to_address(path):
    tokens = path.split('/')

    address = []

    for token in tokens[1:]:
        node_type, node_value = token.split('=')
        address.append({node_type: node_value})
    return address


def intersect(current, desired):
    managed_state = {}

    for key in desired:
        current_value = current[key]

        if isinstance(current_value, unicode):
            current_value = current_value.encode('utf-8')

        managed_state[key] = current_value

    return managed_state


def read(path):
    payload = {'operation': 'read-resource', 'address': to_address(path)}

    response = management_request(payload)

    return response.json()


def create(path, attributes):
    operation = {'operation': 'add', 'address': to_address(path)}

    payload = operation.copy()
    payload.update(attributes)

    response = management_request(payload)

    return response.json()


def present(data):

    path = data['name']
    desired_attributes = data['attributes']

    response = read(path)

    logging.debug("Response: " + str(response))

    if response['outcome'] == 'success':
        current_attributes = response['result']

        current_managed_attributes = intersect(
            current_attributes, desired_attributes)

        logging.debug(
            "Current: " + str(current_managed_attributes) +
            "Desired: " + str(desired_attributes))

        if current_managed_attributes == desired_attributes:
            return False, False, current_attributes

        return False, True, current_attributes

    create(path, desired_attributes)
    return False, True, 'Added ' + path


def absent(data):
    path = data['name']

    response = read(path)

    if response['outcome'] == 'success':
        payload = {'operation': 'remove', 'address': to_address(path)}

        management_request(payload)

        return False, True, 'Removed ' + path

    return False, False, path + ' is absent'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(aliases=['path'], required=True, type='str'),
            attributes=dict(required=False, type='dict'),
        ),
    )

    logging.basicConfig(filename='/tmp/ansible.log', level=logging.DEBUG)

    choice = {'present': present, 'absent': absent}

    is_error, has_changed, result = choice[module.params['state']](
        module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error", meta=result)


if __name__ == '__main__':
    main()
