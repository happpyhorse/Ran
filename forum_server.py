#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import time
import random

import tornado.httpserver
import tornado.httpclient
import tornado.web
import tornado.options
from tornado.options import define, options, parse_command_line

import mysql_db

define('port', default=4812, help='given port', type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        sections = get_sections()
        uid = self.get_secure_cookie('user')
        forum = get_forum()
        posts = get_posts()
        print 'posts: ', posts
        if uid:
            user = get_user(uid)
        else:
            user = {}
        self.render('t_home.html', title='Ran - Home', user=user, forum=forum, sections=sections, posts=posts)

    def post(self):
        pass

def get_posts():
    res = []
    db = mysql_db.DB()
    ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, e.num  from User a, Section c, P_Topic d, Post_Include_P_Edit b left join (select t_pid, count(*) as num from P_Reply group by t_pid) e on b.pid=e.t_pid where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid')
    db.close_conn()
    print ret
    for i in ret:
        item = {}
        item['pid'] = i[2]
        item['icon'] = i[1]
        item['user'] = i[0]
        item['title'] = i[6]
        item['content'] = i[3]
        item['section'] = i[5]
        item['time'] = i[4]
        item['lastRe'] = 'to be added'
        item['reNum'] = 0 if not i[7] else i[7]
        res.append(item)
    print res
    return res

def get_replys(pid):
    res = []
    db = mysql_db.DB()
    ret = db.query_data('select * from User a, Post_Include_P_Edit b, P_Reply c where a.uid = b.uid and b.type = 2 and b.pid = c.pid and c.t_pid = %d' % int(pid))
    db.close_conn()
    print ret
    for i in ret:
        item = {}
        item['icon'] = i[4]
        item['user'] = i[5]
        item['time'] = i[14]
        item['content'] = i[13]
        res.append(item)
    print res
    return res

def get_forum():
    res = {}
    db = mysql_db.DB()
    ret = db.query_data('select count(*) from User')
    res['rMNum'] = ret[0][0]
    ret = db.query_data('select count(*) from Post_Include_P_Edit where type = 1')
    res['aTNum'] = ret[0][0]
    ret = db.query_data('select count(*) from Post_Include_P_Edit where type = 2')
    res['aRNum'] = ret[0][0]
    print 'res: ', res
    db.close_conn()
    return res


def get_user(uid):
    if not uid:
        return {}
    res = {}
    db = mysql_db.DB()
    uid = int(uid)
    ret = db.query_data('select u_name, icon, points, email from User where uid = %d' % uid)
    ret = ret[0]
    res['account'] = ret[0]
    res['icon'] = ret[1]
    res['balance'] = ret[2]
    res['mail'] = ret[3]
    ret = db.query_data('select count(pid) from Post_Include_P_Edit where uid = %d and type = 1' % uid)
    res['pNum'] = ret[0][0]
    ret = db.query_data('select count(pid) from Post_Include_P_Edit where uid = %d and type = 2' % uid)
    res['rNum'] = ret[0][0]
    ret = db.query_data('select count(user_uid) from Make_Friends where user_uid = %d' % uid)
    res['fNum'] = ret[0][0]
    db.close_conn()
    print 'res: ', res
    return res

class NewHandler(tornado.web.RequestHandler):
    def get(self):
        sections = get_sections()
        forum = get_forum()
        uid = self.get_secure_cookie('user')
        if uid:
            user = get_user(uid)
        self.render('t_new.html', title='Ran - New', sections=sections, forum=forum, user=user)
        pass

    def post(self):
        timeStamp = time.strftime('%Y%m%d%H%m%S', time.localtime())
        uid = int(self.get_secure_cookie('user'))
        title = self.get_argument('title')
        content = self.get_argument('content')
        sectionName = self.get_argument('sectionName')
        db = mysql_db.DB()
        res = db.query_data('select t_pid from P_Topic order by t_pid desc limit 1')
        if res:
            tPid = res[0][0] + 1
        else:
            tPid = 1
        res = db.query_data('select sid from Section where s_name = "%s"' % sectionName)
        if res:
            sid = res[0][0]
        sqlStr = [
            "insert into P_Topic value",
            "(%d, '%s', 0)"
        ]
        sqlStr = ''.join(sqlStr) % (tPid, title)
        res = db.insert_data(sqlStr)
        sqlStr = [
            "insert into Post_Include_P_Edit value",
            "(%d, 1, 0, '%s', '%s', %d, 1, %d)"
        ]
        sqlStr = ''.join(sqlStr) % (tPid, content, timeStamp, uid, sid)
        res = db.insert_data(sqlStr)
        db.close_conn()
        if res == 1:
            self.redirect('/home')
        else:
            self.redirect('/new')

class SignInHandler(tornado.web.RequestHandler):
    def get(self):
        sections = get_sections()
        action = self.get_argument('action', None)
        warning = self.get_argument('warning', None)
        if action == 'logout':
            self.set_secure_cookie('user', '')
        self.render('t_signin.html', title='Ran - Sign In', sections=sections, warning=warning)

    def post(self):
        pass

def get_sections():
    db = mysql_db.DB()
    res = db.query_data('select s_name from Section')
    db.close_conn()
    sections = [x[0] for x in res]
    return sections


class SignUpHandler(tornado.web.RequestHandler):
    def get(self):
        sections = get_sections()
        self.render('t_signup.html', title='Ran - Sign Up', sections=sections)

    def post(self):
        print 'hi'
        email =  self.get_argument('email')
        account =  self.get_argument('account')
        pwd =  self.get_argument('pwd1')
        name =  self.get_argument('name')
        print email, account, pwd, name
        db = mysql_db.DB()
        res = db.query_data('select Uid from User order by uid desc limit 1')
        print res
        if res:
            uid = res[0][0] + 1
        else:
            uid = 1
        sqlStr = [
            "insert into User value",
            "(%d, 0, '%s', '%s', 'pic/default.png', '%s', '', '', 10, 1)"
        ]
        sqlStr = ''.join(sqlStr) % (uid, pwd, email, name)
        print sqlStr
        res = db.insert_data(sqlStr)
        db.close_conn()
        print 'res: ', res
        if res == 1:
            self.set_secure_cookie('user', str(uid))
            self.redirect('/home')
        else:
            self.redirect('/signup')


class TopicHandler(tornado.web.RequestHandler):
    def get(self):
        pid = self.get_argument('pid')
        uid = self.get_secure_cookie('user')
        user = get_user(uid)
        replys = get_replys(pid)
        forum = get_forum()
        icon = self.get_argument('icon')
        account = self.get_argument('account')
        time = self.get_argument('time')
        content = self.get_argument('content')
        title = self.get_argument('title')
        section = self.get_argument('section')
        post = {'pid': pid, 'icon': icon, 'account': account, 'time': time, 'content': content, 'title': title, 'section': section}
        print post
        self.render('t_topic.html', title='Ran - Topic', user=user, forum=forum, replys=replys, post=post)

    def post(self):
        uid = self.get_secure_cookie('user')
        timeStamp = time.strftime('%Y%m%d%H%m%S', time.localtime())
        content = self.get_argument('content')
        sectionName = self.get_argument('section')
        tPid = self.get_argument('tPid')
        print content
        db = mysql_db.DB()
        res = db.query_data('select sid from Section where s_name = "%s"' % sectionName)
        if res:
            sid = res[0][0]
        res = db.query_data('select pid from Post_Include_P_Edit order by pid desc limit 1')
        pid = res[0][0] + 1
        sqlStr = [
            "insert into P_Topic value",
            "(%d, 'Reply', 0)"
        ]
        sqlStr = ''.join(sqlStr) % (pid)
        res = db.insert_data(sqlStr)
        sqlStr = [
            "insert into Post_Include_P_Edit value",
            "(%d, 2, 0, '%s', '%s', %d, 1, %d)"
        ]
        sqlStr = ''.join(sqlStr) % (pid, content, timeStamp, int(uid), sid)
        res = db.insert_data(sqlStr)
        sqlStr = [
            "insert into P_Reply value",
            "(%d, %d)"
        ]
        sqlStr = ''.join(sqlStr) % (int(pid), int(tPid))
        res = db.insert_data(sqlStr)
        db.close_conn()
        if res == 1:
            self.redirect('/home')
        else:
            self.redirect('/home')


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        uid = self.get_secure_cookie('user')
        user = get_user(uid)
        sections = get_sections()
        forum = get_forum()
        warning = self.get_argument('warning', None)
        self.render('t_config.html', title='Ran - Config', user=user, setions=sections, forum=forum, warning=warning)

    def post(self):
        uid = int(self.get_secure_cookie('user'))
        action = self.get_argument('action')
        db = mysql_db.DB()
        if action == 'info':
            address = self.get_argument('address')
            account = self.get_argument('account')
            sqlStr = 'update User set u_address = "%s", u_name = "%s" where uid = %d' % (address, account, uid)
            res = db.update_data(sqlStr)
        elif action == 'icon':
            icon = self.request.files.get('icon')[0]
            path = './static/pic/%s.png' % str(uid)
            f = open(path, 'wb')
            f.write(icon['body'])
            f.close()
            path = path.split('/', 2)[-1]
            sqlStr = 'update User set icon = "%s" where uid = %d' % (path, uid)
            res = db.update_data(sqlStr)
        elif action == 'pwd':
            print 'in pwd'
            newPwd = self.get_argument('new')
            sqlStr = 'update User set password = "%s" where uid = %d' % (newPwd, uid)
            res = db.update_data(sqlStr)
        db.close_conn()
        if res == 1:
            warning = 'updata success'
        else:
            warning = 'update fail'
        self.redirect('/config?warning=%s' % warning)

class DBHandler(tornado.web.RequestHandler):
    def get(self):
        param = self.get_argument('param')
        action = self.get_argument('action')
        if action == 'ck_mail':
            self.signup_check('email', param)
        elif action == 'ck_pwd':
            self.pwd_check(param)

    def post(self):
        print '1'
        mail = self.get_argument('mail')
        pwd = self.get_argument('pwd')
        self.signin_check(mail, pwd)

    def pwd_check(self, param):
        uid = int(self.get_secure_cookie('user'))
        sqlStr = "select * from User where uid = %d and password = '%s'" % (uid, param)
        db = mysql_db.DB()
        res = db.query_data(sqlStr)
        db.close_conn()
        if len(res) == 1:
            self.write('T')
        else:
            self.write('F')

    def signup_check(self, col, param):
        sqlStr = "select * from User where %s = '%s'" % (col, param)
        db = mysql_db.DB()
        res = db.query_data(sqlStr)
        db.close_conn()
        if len(res) == 0:
            self.write('T')
        else:
            self.write('F')

    def signin_check(self, mail, pwd):
        sqlStr = "select * from User where email = '%s' and password = '%s'"\
                  % (mail, pwd)
        db = mysql_db.DB()
        res = db.query_data(sqlStr)
        db.close_conn()
        if len(res) == 0:
            self.redirect('/signin?warning=Invalid Account or Password')
        else:
            if not self.get_secure_cookie('user'):
                uid = res[0][0]
                self.set_secure_cookie('user', str(uid))
            self.redirect('/home')

class PostModule(tornado.web.UIModule):
    def render(self, post):
        return self.render_string('modules/post.html', post=post)

class ReplyModule(tornado.web.UIModule):
    def render(self, reply):
        return self.render_string('modules/reply.html', reply=reply)


def send(url, data):
    client = tornado.httpclient.HTTPClient()
    url = url
    body = data
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
    }
    request = tornado.httpclient.HTTPRequest(
            url,
            method = 'POST',
            body = body,
            headers = headers
            )
    response = client.fetch(request)
    return response

def main():
    parse_command_line()
    settings = {
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'template_path': os.path.join(os.path.dirname(__file__), "templates"),
        'cookie_secret': 'QkLMyvr5Q2CNq+wlLX7q5vcGjjx6K0xZjSyvgTds7vY=',
        'ui_modules': {
            'Post': PostModule,
            'Reply': ReplyModule,
        },
        'debug': True
    }
    application = tornado.web.Application([
            (r'/home', MainHandler),
            (r'/new', NewHandler),
            (r'/signin', SignInHandler),
            (r'/signup', SignUpHandler),
            (r'/topic', TopicHandler),
            (r'/config', ConfigHandler),
            (r'/db', DBHandler),
            ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
