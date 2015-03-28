#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import time
import random
import json

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
        #posts = get_posts()
        allPosts = get_all_posts_split_by_section()
        wealthList = get_wealth_list()
        if uid:
            user = get_user(uid)
        else:
            user = {}
        self.render(
                't_home.html', title='Ran - Home',
                user=user, forum=forum, sections=sections,
                allPosts=allPosts, wealthList=wealthList,
                )

    def post(self):
        pass

class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        adminId = self.get_secure_cookie('admin')
        forum = get_forum()
        allUsers = get_all_users()
        allPosts = get_all_posts()
        allReplys = get_all_replys()
        wealthList = get_wealth_list()
        cUser = get_admin(adminId)
        self.render(
                't_admin.html', title='Ran - Admin',
                allUsers=allUsers, forum=forum, allReplys=allReplys,
                allPosts=allPosts, wealthList=wealthList, cUser=cUser,
                )

def get_wealth_list():
    db = mysql_db.DB()
    res = db.query_data('select u_name, points from User order by points desc limit 5')
    db.close_conn()
    return res

def get_all_users():
    db = mysql_db.DB()
    ret = db.query_data('select u_name, email, icon, uid from User')
    db.close_conn()
    res = []
    for i in ret:
        item = {}
        item['account'] = i[0]
        item['mail'] = i[1]
        item['icon'] = i[2]
        item['id'] = i[3]
        res.append(item)
    return res

def get_all_posts():
    res = []
    db = mysql_db.DB()
    ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, e.num, a.uid  from User a, Section c, P_Topic d, Post_Include_P_Edit b left join (select t_pid, count(*) as num from P_Reply group by t_pid) e on b.pid=e.t_pid where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid')
    db.close_conn()
    for i in ret:
        item = {}
        item['pid'] = i[2]
        item['icon'] = i[1]
        item['user'] = i[0]
        item['uid'] = i[8]
        item['title'] = i[6]
        item['content'] = i[3]
        item['section'] = i[5]
        item['time'] = i[4]
        item['lastRe'] = 'to be added'
        item['reNum'] = 0 if not i[7] else i[7]
        res.append(item)
    return res

def get_all_posts_split_by_section():
    res = {}
    sections = get_sections()
    for section in sections:
        tmp = []
        db = mysql_db.DB()
        ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, e.num, a.uid  from User a, Section c, P_Topic d, Post_Include_P_Edit b left join (select t_pid, count(*) as num from P_Reply group by t_pid) e on b.pid=e.t_pid where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid and c.s_name = "%s"' % section)
        db.close_conn()
        for i in ret:
            item = {}
            item['pid'] = i[2]
            item['icon'] = i[1]
            item['user'] = i[0]
            item['uid'] = i[8]
            item['title'] = i[6]
            item['content'] = i[3]
            item['section'] = i[5]
            item['time'] = i[4]
            item['lastRe'] = 'to be added'
            item['reNum'] = 0 if not i[7] else i[7]
            tmp.append(item)
        res[section] = tmp
    return res

def get_all_replys():
    res = []
    db = mysql_db.DB()
    ret = db.query_data('select * from User a, Post_Include_P_Edit b, P_Reply c where a.uid = b.uid and b.type = 2 and b.pid = c.pid')
    db.close_conn()
    for i in ret:
        item = {}
        item['id'] = i[0]
        item['icon'] = i[4]
        item['user'] = i[5]
        item['time'] = i[14]
        item['content'] = i[13]
        res.append(item)
    return res

def get_post_topic(pid):
    db = mysql_db.DB()
    ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, a.uid  from User a, Section c, P_Topic d, Post_Include_P_Edit b where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid and b.pid = %d' % int(pid))
    ret = ret[0]
    db.close_conn()
    res = {}
    res['pid'] = ret[2]
    res['icon'] = ret[1]
    res['account'] = ret[0]
    res['title'] = ret[6]
    res['content'] = ret[3]
    res['section'] = ret[5]
    res['time'] = ret[4]
    res['id'] = ret[7]
    return res

def get_replys(pid):
    res = []
    db = mysql_db.DB()
    ret = db.query_data('select * from User a, Post_Include_P_Edit b, P_Reply c where a.uid = b.uid and b.type = 2 and b.pid = c.pid and c.t_pid = %d' % int(pid))
    db.close_conn()
    for i in ret:
        item = {}
        item['id'] = i[0]
        item['icon'] = i[4]
        item['user'] = i[5]
        item['time'] = i[14]
        item['content'] = i[13]
        res.append(item)
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
    ret = db.query_data('SELECT count(*) as cnt, DATE_FORMAT(P_Date, "%Y%m%d") days FROM forum.Post_Include_P_Edit group by days order by cnt desc')
    res['postMax'] = ret[0][0]
    res['postMin'] = ret[-1][0]
    ret = db.query_data('select avg(cnt) from (SELECT count(*) as cnt, DATE_FORMAT(P_Date, "%Y%m%d") days FROM forum.Post_Include_P_Edit group by days) a')
    res['postAvg'] = '%.1f' % ret[0][0]
    ret = db.query_data('SELECT U_name FROM User U WHERE NOT EXISTS ( SELECT * FROM Section S WHERE NOT EXISTS (SELECT * FROM Post_Include_P_Edit P WHERE P.UID=U.UID and P.SID=S.SID))')
    if ret:
        res['activeMember'] = ret[0][0]
    else:
        res['activeMember'] = ''
    db.close_conn()
    return res

def get_admin(adminId):
    if not adminId:
        return {}
    res = {}
    db = mysql_db.DB()
    adminId = int(adminId)
    ret = db.query_data('select Admin_Name from Admin where AdminID = %d' % adminId)
    ret = ret[0]
    res['account'] = ret[0]
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
    res['id'] = uid
    db.close_conn()
    return res

class NewHandler(tornado.web.RequestHandler):
    def get(self):
        sections = get_sections()
        forum = get_forum()
        wealthList = get_wealth_list()
        uid = self.get_secure_cookie('user')
        if uid:
            user = get_user(uid)
        self.render(
                't_new.html', title='Ran - New',
                sections=sections, forum=forum, user=user,
                wealthList=wealthList,
                )
        pass

    def post(self):
        timeStamp = time.strftime('%Y%m%d%H%m%S', time.localtime())
        uid = int(self.get_secure_cookie('user'))
        title = self.get_argument('title')
        content = self.get_argument('content')
        sectionName = self.get_argument('sectionName')
        att = self.request.files.get('att')
        db = mysql_db.DB()
        res = db.query_data('select t_pid from P_Topic order by t_pid desc limit 1')
        if res:
            tPid = res[0][0] + 1
        else:
            tPid = 1
        res = db.query_data('select sid from Section where s_name = "%s"'\
                % sectionName)
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
        if att:
            cost = int(self.get_argument('cost'))
            att = att[0]
            res = db.query_data('select Aid from Attachment \
                    order by Aid desc limit 1')
            if res:
                aid = res[0][0] + 1
            else:
                aid = 1
            path = './static/att/%s.%s.rar' % (str(aid), att['filename'].split('.')[-1])
            f = open(path, 'wb')
            f.write(att['body'])
            f.close()
            path = path.split('/', 2)[-1]
            sqlStr = 'insert into Attachment value (%d, "%s", 0, %d, 0, %d)' %\
                     (aid, path, cost, tPid)
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
        email =  self.get_argument('email')
        account =  self.get_argument('account')
        pwd =  self.get_argument('pwd1')
        db = mysql_db.DB()
        res = db.query_data('select Uid from User order by uid desc limit 1')
        if res:
            uid = res[0][0] + 1
        else:
            uid = 1
        sqlStr = [
            "insert into User value",
            "(%d, 0, '%s', '%s', 'pic/default.png', '%s', '', '', 10, 1)"
        ]
        sqlStr = ''.join(sqlStr) % (uid, pwd, email, account)
        res = db.insert_data(sqlStr)
        db.close_conn()
        if res == 1:
            self.set_secure_cookie('user', str(uid))
            self.redirect('/home')
        else:
            self.redirect('/signup')

def get_att(pid):
    res = {}
    db = mysql_db.DB()
    ret = db.query_data('select A_Name, A_Price from Attachment where T_Pid = %d' % int(pid))
    if ret:
        res['name'] = ret[0][0].split('/')[-1]
        res['url'] = ret[0][0]
        res['cost'] = ret[0][1]
    db.close_conn()
    return res



class TopicHandler(tornado.web.RequestHandler):
    def get(self):
        pid = self.get_argument('pid')
        uid = self.get_secure_cookie('user')
        user = get_user(uid)
        replys = get_replys(pid)
        post = get_post_topic(pid)
        att = get_att(pid)
        forum = get_forum()
        wealthList = get_wealth_list()
        self.render(
                't_topic.html', title='Ran - Topic',
                user=user, forum=forum, replys=replys,
                post=post, wealthList=wealthList, att=att,
                )

    def post(self):
        uid = self.get_secure_cookie('user')
        timeStamp = time.strftime('%Y%m%d%H%m%S', time.localtime())
        content = self.get_argument('content')
        sectionName = self.get_argument('section')
        tPid = self.get_argument('tPid')
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
            self.redirect('/topic?pid=%d' % int(tPid))
        else:
            self.redirect('/home')


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        uid = self.get_secure_cookie('user')
        user = get_user(uid)
        sections = get_sections()
        forum = get_forum()
        wealthList = get_wealth_list()
        warning = self.get_argument('warning', None)
        self.render(
                't_config.html', title='Ran - Config',
                user=user, setions=sections, forum=forum,
                warning=warning, wealthList=wealthList,
                )

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
            icon = self.request.files.get('icon')
            icon = icon[0]
            path = './static/pic/%s.png' % str(uid)
            f = open(path, 'wb')
            f.write(icon['body'])
            f.close()
            path = path.split('/', 2)[-1]
            sqlStr = 'update User set icon = "%s" where uid = %d' % (path, uid)
            res = db.update_data(sqlStr)
        elif action == 'pwd':
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
        action = self.get_argument('action')
        if action == 'ck_mail':
            param = self.get_argument('param')
            self.signup_check('email', param)
        elif action == 'ck_pwd':
            param = self.get_argument('param')
            self.pwd_check(param)
        elif action == 'buy_att':
            buid = self.get_argument('buid')
            suid = self.get_argument('suid')
            cost = self.get_argument('cost')
            self.buy_att(buid, suid, cost)
        elif action == 'del_user':
            uid = self.get_argument('uid')
            self.del_user(uid)

    def post(self):
        mail = self.get_argument('mail')
        pwd = self.get_argument('pwd')
        self.signin_check(mail, pwd)

    def del_user(self, uid):
        db = mysql_db.DB()
        res = db.del_data('delete from User where uid = %d' % int(uid))
        if res == 1:
            self.write('T')
        else:
            self.write('F')



    def buy_att(self, buid, suid, cost):
        buid = int(buid)
        suid = int(suid)
        db = mysql_db.DB()
        res = db.query_data('select Points from User where uid = %d' % buid)
        points = int(res[0][0])
        cost = int(cost)
        if cost > points:
            db.close_conn()
            self.write('F')
        else:
            points -= cost
            res = db.update_data('update User set Points = %d where uid = %d' % (points, buid))
            if res == 1:
                res = db.query_data('select Points from User where uid = %d' % suid)
                points = int(res[0][0])
                points += cost
                res = db.update_data('update User set Points = %d where uid = %d' % (points, suid))
                db.close_conn()
                self.write('T')
            else:
                db.close_conn()
                self.wirte('F')


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
        if len(res) == 0:
            res = db.query_data("select * from Admin where email = '%s' and password = '%s'"\
                    % (mail, pwd))
            db.close_conn()
            if len(res) == 0:
                self.redirect('/signin?warning=Invalid Account or Password')
            else:
                if not self.get_secure_cookie('admin'):
                    adminId = res[0][0]
                    self.set_secure_cookie('admin', str(adminId))
                self.redirect('/admin')
        else:
            db.close_conn()
            if not self.get_secure_cookie('user'):
                uid = res[0][0]
                self.set_secure_cookie('user', str(uid))
            self.redirect('/home')

class MemberHandler(tornado.web.RequestHandler):
    def get(self, part, uid):
        user = get_user(uid)
        cUid = self.get_secure_cookie('user')
        cUser = get_user(cUid)
        posts = get_post_by_id(uid)
        replys = get_reply_by_id(uid)
        if part == 'reply':
            posts = []
        elif part == 'post':
            replys = []
        self.render(
                't_member.html', title='Ran - Member',
                user=user, replys=replys, posts=posts,
                cUser=cUser,
                )

def get_post_by_id(uid):
    db = mysql_db.DB()
    ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, e.num  from User a, Section c, P_Topic d, Post_Include_P_Edit b left join (select t_pid, count(*) as num from P_Reply group by t_pid) e on b.pid=e.t_pid where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid and a.uid = %d' % int(uid))
    db.close_conn()
    tmp = []
    for i in ret:
        item = {}
        item['account'] = i[0]
        item['pid'] = i[2]
        item['icon'] = i[1]
        item['user'] = i[0]
        item['uid'] = uid
        item['title'] = i[6]
        item['content'] = i[3]
        item['section'] = i[5]
        item['time'] = i[4]
        item['lastRe'] = 'to be added'
        item['reNum'] = 0 if not i[7] else i[7]
        tmp.append(item)
    return tmp

def get_post_by_key(key):
    db = mysql_db.DB()
    ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, e.num, a.uid  from User a, Section c, P_Topic d, Post_Include_P_Edit b left join (select t_pid, count(*) as num from P_Reply group by t_pid) e on b.pid=e.t_pid where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid and d.t_title like "%%%s%%"' % key)
    db.close_conn()
    print 'ret: ', ret
    tmp = []
    for i in ret:
        item = {}
        item['account'] = i[0]
        item['pid'] = i[2]
        item['icon'] = i[1]
        item['user'] = i[0]
        item['uid'] = i[8]
        item['title'] = i[6]
        item['content'] = i[3]
        item['section'] = i[5]
        item['time'] = i[4]
        item['lastRe'] = 'to be added'
        item['reNum'] = 0 if not i[7] else i[7]
        tmp.append(item)
    return tmp

def get_reply_by_id(uid):
    res = []
    db = mysql_db.DB()
    ret = db.query_data('select * from User a, Post_Include_P_Edit b, P_Reply c where a.uid = b.uid and b.type = 2 and b.pid = c.pid and a.uid = %d' % int(uid))
    db.close_conn()
    for i in ret:
        item = {}
        item['id'] = i[0]
        item['icon'] = i[4]
        item['user'] = i[5]
        item['time'] = i[14]
        item['content'] = i[13]
        res.append(item)
    return res

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        searchKey = self.get_argument('searchInput')
        cUid = self.get_secure_cookie('user')
        cUser = get_user(cUid)
        posts = get_post_by_key(searchKey)
        self.render(
                't_search.html', title='Ran - Search',
                posts=posts, cUser=cUser,
                )

class FriendsHandler(tornado.web.RequestHandler):
    def get(self):
        uid = self.get_secure_cookie('user')
        user = get_user(uid)
        posts = get_friends_post(uid)
        self.render(
                't_friends.html', title='Ran - Friends',
                user=user, posts=posts,
                )

def get_friends_post(uid):
    db = mysql_db.DB()
    ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, e.num  from User a, Section c, P_Topic d, Post_Include_P_Edit b left join     (select t_pid, count(*) as num from P_Reply group by t_pid) e on b.pid=e.t_pid where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid and a.uid in (select Friend_Uid from Make_Friends where User_Uid = %d)' % int(uid))
    db.close_conn()
    tmp = []
    for i in ret:
        item = {}
        item['account'] = ret[0]
        item['pid'] = i[2]
        item['icon'] = i[1]
        item['user'] = i[0]
        item['uid'] = uid
        item['title'] = i[6]
        item['content'] = i[3]
        item['section'] = i[5]
        item['time'] = i[4]
        item['lastRe'] = 'to be added'
        item['reNum'] = 0 if not i[7] else i[7]
        tmp.append(item)
    return tmp


class FollowHandler(tornado.web.RequestHandler):
    def get(self, fid):
        uid = self.get_secure_cookie('user')
        if fid == uid:
            self.write('F')
        else:
            self.follow(int(uid), int(fid))

    def follow(self, uid, fid):
        sqlStr = [
            "insert into Make_Friends value",
            "(%d, %d)"
        ]
        sqlStr = ''.join(sqlStr) % (uid, fid)
        db = mysql_db.DB()
        res = db.insert_data(sqlStr)
        db.close_conn()
        if res == 1:
            self.write('T')
        else:
            self.write('F')

class DraftHandler(tornado.web.RequestHandler):
    def get(self):
        uid = int(self.get_secure_cookie('user'))
        db = mysql_db.DB()
        ret = db.query_data('select D_Title, D_Content from Draft where Uid = %d order by Did desc limit 1' % uid)
        db.close_conn()
        res = {}
        res['title'] = ret[0][0]
        res['content'] = ret[0][1]
        res = json.dumps(res)
        self.write(res)

    def post(self):
        title = self.get_argument('title')
        content = self.get_argument('content')
        uid = int(self.get_secure_cookie('user'))

        db = mysql_db.DB()
        res = db.query_data('select Did from Draft order by Did desc limit 1')
        if res:
            did = res[0][0] + 1
        else:
            did = 1

        sqlStr = [
            "insert into Draft value",
            "(%d, '%s', '%s', %d)"
        ]
        sqlStr = ''.join(sqlStr) % (did, title, content, uid)
        res = db.insert_data(sqlStr)
        db.close_conn()
        if res == 1:
            self.write('T')
        else:
            self.write('F')

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
            (r'/member/([a-z]+)/([0-9]+)', MemberHandler),
            (r'/follow/([0-9]+)', FollowHandler),
            (r'/friends', FriendsHandler),
            (r'/draft', DraftHandler),
            (r'/search', SearchHandler),
            (r'/admin', AdminHandler),
            ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
