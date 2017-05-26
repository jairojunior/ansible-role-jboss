#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=['command'], required=True, type='str'),
        ),
    )

    command = module.params['command']

    exit_code, out, err = module.run_command(
        'jboss-cli.sh -c ' + "'" + command + "'")

    module.exit_json(
        cmd=command,
        stdout=out,
        stderr=err,
        rc=exit_code,
        meta=json.loads(out.replace('=>', ':')),
        changed=True
    )


if __name__ == '__main__':
    main()
