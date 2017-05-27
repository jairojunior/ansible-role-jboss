#!/usr/bin/python

import hashlib
from jboss.client import Client
from ansible.module_utils.basic import AnsibleModule


def extract_checksum(data):
    bytes_value = data['result']['content'][0]['hash']['BYTES_VALUE']
    return bytes_value.decode('base64').encode('hex')


def checksum(src):
    return hashlib.sha1(open(src).read()).hexdigest()


def present(client, read_response, data):
    if read_response['outcome'] == 'success':
        current_checksum = extract_checksum(read_response)

        desired_checksum = checksum(data['src'])

        if current_checksum == desired_checksum:
            return False, False, current_checksum

        client.update_deployment(data['name'], data['src'])
        return False, True, desired_checksum

    client.deploy(data['name'], data['src'])
    return False, True, 'Deployed ' + data['name']


def absent(client, read_response, data):
    if read_response['outcome'] == 'success':
        client.undeploy(data['name'])
        return False, True, 'Removed ' + data['name']

    return False, False, 'Deployment absent ' + data['name']


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            src=dict(required=True, type='str'),
        ),
    )

    choice = {'present': present, 'absent': absent}

    client = Client('ansible', 'ansible')

    response = client.read('/deployment=' + module.params['name'])

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
