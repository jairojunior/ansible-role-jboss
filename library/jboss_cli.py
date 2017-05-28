#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule


def create(command, online):
    cmd = 'jboss-cli.sh'

    if online:
        cmd += ' -c'

    cmd += " '{}'".format(command)

    return cmd


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=['command'], required=True, type='str'),
            online=dict(aliases=['connect'], default=True, type='bool'),
        ),
    )

    exit_code, out, err = module.run_command(
        create(module.params['command'], module.params['online']))

    module.exit_json(
        cmd=module.params['command'],
        stdout=out,
        stderr=err,
        rc=exit_code,
        meta=json.loads(out.replace('=>', ':')),
        changed=True
    )


if __name__ == '__main__':
    main()
