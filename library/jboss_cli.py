#!/usr/bin/python

import jboss_resource
from ansible.module_utils.basic import AnsibleModule


def execute(command):
    jboss_resource.management_request({})


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=['command'], required=True, type='str'),
        ),
    )

    is_error, result = execute(module.params['command'])

    if not is_error:
        module.exit_json(meta=result)
    else:
        module.fail_json(msg="Error", meta=result)


if __name__ == '__main__':
    main()
