#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Define a class to Executes commands from network and saves to log>>

import pexpect
import os
import datetime


class CommandExecutor ():
    def __init__(self, protocol, host, port, user, password):

        self.protocol = protocol
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.log = get_path (host)

    def login(self, prompt):
        logfile = open (self.log, 'a')
        if self.protocol == 'ssh':
            self.child = pexpect.spawn ('ssh ' + self.user + '@' + self.host + ' -p ' + self.port, logfile=logfile)
        elif self.protocol == 'telnet':
            self.child = pexpect.spawn ('telnet ' + self.host)
        response = self.child.expect ([pexpect.TIMEOUT, '(?i)yes/no', '[P|p]assword:?'])
        if response == 0:
            print ('ERROR: ' + self.protocol + ' timeout, host = ' + self.host)
            return False
        if response == 1:
            self.child.sendline ('yes')
            self.child.expect (prompt)
        if response == 2:
            self.child.sendline (self.password)
            self.child.expect (prompt)
        return self.child.before

    def login_no_password(self, prompt):
        logfile = open (self.log, 'a')

        if self.protocol == 'ssh':
            self.child = pexpect.spawn('ssh ' + self.user + '@' + self.host + ' -p ' + self.port, logfile=logfile)
        elif self.protocol == 'telnet':
            self.child = pexpect.spawn('telnet ' + self.host)
        self.child.expect(prompt)
        return self.child.before

    def send(self, cmd, prompt=pexpect.EOF, timeout=30, password=None):
        self.child.sendline (cmd)
        if password:
            # sudo 时 password无冒号
            response = self.child.expect ([pexpect.TIMEOUT, '(?i)yes/no', '[P|p]assword:?'])
            if response == 0:
                print ('ERROR: timeout, cmd = ' + cmd)
                return False
            if response == 1:
                self.child.sendline ('yes')
                response = self.child.expect ('[P|p]assword:?')
                if response == 0:
                    self.child.sendline (password)
                    self.child.expect (prompt, timeout)
                stdout = self.child.before
            if response == 2:
                self.child.sendline (password)
                self.child.expect (prompt, timeout)
                stdout = self.child.before
        else:
            self.child.expect (prompt, timeout)
            stdout = self.child.before.replace (cmd, '').strip ()
            lines = stdout.splitlines ()[:-1]
            stdout = '\n'.join (lines)
        return stdout

    def send_confirm(self, cmd, prompt=pexpect.EOF, timeout=30):
        self.child.sendline(cmd)
        # confirm input
        response = self.child.expect_exact([pexpect.TIMEOUT, 'Do you want to save the current configuration? (y/n)',
                                            'Are you sure you wish to continue? (y/n)'])
        if response == 0:
            print ('ERROR: timeout, cmd = ' + cmd)
            return False
        if response == 1:
            self.child.sendline('n')
            response = self.child.expect_exact('? (y/n)')
            if response == 0:
                self.child.sendline('y')
                self.child.expect_exact(prompt, timeout)
            stdout = self.child.before
        if response == 2:
            self.child.sendline('y')
            self.child.expect_exact(prompt, timeout)
            stdout = self.child.before
        return stdout

    def send_control(self, cmd):
        self.child.sendcontrol(cmd)
        stdout = self.child.before
        return stdout

    def logout(self):
        self.child.close()


def get_path(host):
    path = const.SCRIPT_ROOT_PATH
    if not os.path.exists (path):
        os.mkdir (path)
    log_file = 'details_' + host + '_' + \
               datetime.datetime.now ().strftime ('%Y%m%d%H%M%S%f') + '.log'
    return os.path.join (path, log_file)
