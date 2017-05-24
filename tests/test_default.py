import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_wildfly_running_and_enabled(Service):
    wildfly = Service('wildfly')

    assert wildfly.is_enabled


def test_wildfly_listening_http(Socket):
    socket = Socket('tcp://0.0.0.0:8080')

    assert socket.is_listening
