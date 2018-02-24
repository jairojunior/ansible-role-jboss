import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_jboss_running_and_enabled(host):
    jboss = host.service('wildfly')

    assert jboss.is_enabled


def test_jboss_listening_http(host):
    socket = host.socket('tcp://0.0.0.0:8080')

    assert socket.is_listening


def test_mgmt_user_authentication(host):
    command = """curl --digest -L -D - http://localhost:9990/management \
                -u ansible:ansible"""

    cmd = host.run(command)

    assert 'HTTP/1.1 200 OK' in cmd.stdout
