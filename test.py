#!/usr/bin/python
# -*-coding:utf-8-*-

from common import expect

# 参数
agent = dict()
agent['loginType'] = 'ssh'  # telnet
agent['ip'] = '127.0.0.1'
agent['userName'] = 'root'
agent['password'] = 'root'


def test():
    executor = expect.CommandExecutor(agent['loginType'], agent['ip'], '22',
                                      agent['userName'], agent['password'], log)
    return executor


if __name__ == '__main__':
    executor = test()
