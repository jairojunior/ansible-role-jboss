#!/usr/bin/python

import json
import hashlib
import requests
from requests.auth import HTTPDigestAuth
from ansible.module_utils.basic import AnsibleModule


def management_request(payload):
    url = 'http://127.0.0.1:9990/management'
    headers = {'Content-Type': 'application/json'}
    return requests.post(
        url, data=json.dumps(payload), headers=headers,
        auth=HTTPDigestAuth('ansible', 'ansible'))


def read(name):
    payload = {'operation': 'read-resource', 'address': [{'deployment': name}]}

    response = management_request(payload)

    return response.json()


def deploy(data):
    name = data['name']

    add_operation = dict(
        operation='add',
        content=[dict(url='file:' + data['src'])],
        address=[dict(deployment=name)]
        )

    deploy_operation = dict(
        operation='deploy',
        address=[dict(deployment=name)]
        )

    composite = dict(
        operation='composite',
        steps=[add_operation, deploy_operation],
        address=[]
        )

    management_request(composite)


def undeploy(name):
    remove_operation = dict(
        operation='remove',
        address=[dict(deployment=name)]
        )

    undeploy_operation = dict(
        operation='undeploy',
        address=[dict(deployment=name)]
        )

    composite = dict(
        operation='composite',
        steps=[undeploy_operation, remove_operation],
        address=[]
        )

    management_request(composite)


def present(data):
    deployment_name = data['name']
    response = read(deployment_name)

    if response['outcome'] == 'success':
        bytes_value = response['result']['content'][0]['hash']['BYTES_VALUE']
        current_checksum = bytes_value.decode('base64').encode('hex')

        desired_checksum = hashlib.sha1(open(data['src']).read()).hexdigest()

        if current_checksum == desired_checksum:
            return False, False, current_checksum

    deploy(data)
    return False, True, 'Deployed ' + deployment_name


def absent(data):
    deployment_name = data['name']
    response = read(deployment_name)

    if response['outcome'] == 'success':
        undeploy(deployment_name)
        return False, True, 'Removed ' + deployment_name

    return False, False, 'Deployment absent ' + deployment_name


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            src=dict(required=True, type='str'),
        ),
    )

    choice = {'present': present, 'absent': absent}

    is_error, has_changed, result = choice[module.params['state']](
        module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error", meta=result)


if __name__ == '__main__':
    main()
