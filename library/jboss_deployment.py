#!/usr/bin/python

import jboss_resource
from ansible.module_utils.basic import AnsibleModule


def present():
    jboss_resource.management_request({})


def absent():
    jboss_resource.management_request({})


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
