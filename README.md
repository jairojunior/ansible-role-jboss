[![Build Status](https://travis-ci.org/jairojunior/ansible-role-jboss.svg?branch=master)](https://travis-ci.org/jairojunior/ansible-role-jboss)

jboss
=========

This role installs and configures JBoss EAP (6.1+/7.0+), Wildfly (8/9/10), and products based on JBoss/Wildfly like Infinispan, Keycloak and apiman.

Requirements
------------

This role requires Ansible 2.3+ and a JRE/JDK - just need to be there - no need to update alternatives, set environment variables or anything.

Role Variables
--------------

The variables that can be passed to this role and a brief description about them are as follows:

```yaml
---
jboss_java_home: /opt/jdk1.8.0_131/
jboss_home: /opt/wildfly
jboss_user: wildfly
jboss_group: wildfly
jboss_service: wildfly
jboss_install_src: http://download.jboss.org/wildfly/10.1.0.Final/wildfly-10.1.0.Final.tar.gz
jboss_config: standalone.xml
jboss_mode: standalone
jboss_domain_config: domain.xml
jboss_host_config: host.xml
jboss_startup_wait: 30
jboss_shutdown_wait: 30
jboss_console_log: /var/log/wildfly/console.log
jboss_mgmt_user: ansible
jboss_mgmt_password: ansible
jboss_xms: 64m
jboss_xmx: 512m
jboss_opts: ''
jboss_java_opts: ''
jboss_properties:
  jboss.bind.address: 0.0.0.0
  jboss.bind.address.management: 127.0.0.1
  jboss.management.http.port: 9990
  jboss.management.https.port: 9993
  jboss.http.port: 8080
  jboss.https.port: 8443
  jboss.ajp.port: 8009
```

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

Standalone mode

```yaml
- hosts: servers
  roles:
     - role: jairojunior.jboss
       jboss_config: standalone-ha.xml
```

Domain mode

```yaml
- hosts: domain_controller
  roles:
    - role: jairojunior.jboss
      jboss_mode: domain
      jboss_host_config: host-master.xml
      jboss_properties:
          jboss.bind.address.management: 172.17.0.2
```

```yaml
- hosts: host_controllers
  roles:
    - role: jairojunior.jboss
      jboss_mode: domain
      jboss_host_config: host-slave.xml
      jboss_properties:
          jboss.domain.master.address: 172.17.0.2
          jboss.domain.slave.username: slave
          jboss.domain.slave.password: "{ 'supersafepassword' | b64encode }}"
```


License
-------

[Apache-2.0](./LICENSE)

Author Information
------------------

Jairo Junior (junior.jairo1@gmail.com) - Core committer of a Puppet Approved module for JBoss/Wildfly. [biemond/wildfly](https://github.com/biemond/biemond-wildfly)

Lots of the ideas employed here are inspired by what I learned developing/maintaining the module above.
