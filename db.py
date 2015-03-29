#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json

import MySQLdb


class DB:
    def __init__(self):
        self.conn = MySQLdb.connect(
                host = 'localhost',
                user = 'root',
                #passwd = 'root1314',
                db = 'forum',
                port = 3306,
                )
        self.cur = self.conn.cursor()

    def close_conn(self):
        self.cur.close()
        self.conn.close()

    def execute_sql(self, sqlStr):
        try:
            return self.cur.execute(sqlStr)
        except Exception, e:
            print e
            return e

    def insert_data(self, sqlStr):
        res = self.execute_sql(sqlStr)
        self.conn.commit()
        return res

    def query_data(self, sqlStr):
        res = self.execute_sql(sqlStr)
        return self.cur.fetchall()

    def update_data(self, sqlStr):
        res = self.execute_sql(sqlStr)
        self.conn.commit()
        return res

    def del_data(self, sqlStr):
        res = self.execute_sql(sqlStr)
        self.conn.commit()
        return res

def get_wealth_list():
    db = DB()
    res = db.query_data('select u_name, points from User order by points desc limit 5')
    db.close_conn()
    return res

def get_all_users():
    db = DB()
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
    db = DB()
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
        db = DB()
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
    db = DB()
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
    db = DB()
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
    db = DB()
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
    db = DB()
    ret = db.query_data('select count(*) from User')
    res['rMNum'] = ret[0][0]
    ret = db.query_data('select count(*) from Post_Include_P_Edit where type = 1')
    res['aTNum'] = ret[0][0]
    ret = db.query_data('select count(*) from Post_Include_P_Edit where type = 2')
    res['aRNum'] = ret[0][0]
    ret = db.query_data('SELECT count(*) as cnt, DATE_FORMAT(P_Date, "%Y%m%d") days FROM forum.Post_Include_P_Edit where type = 1 group by days order by cnt desc')
    res['postMax'] = ret[0][0]
    res['postMin'] = ret[-1][0]
    ret = db.query_data('select avg(cnt) from (SELECT count(*) as cnt, DATE_FORMAT(P_Date, "%Y%m%d") days FROM forum.Post_Include_P_Edit where type = 1 group by days) a')
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
    db = DB()
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
    db = DB()
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

def get_sections():
    db = DB()
    res = db.query_data('select s_name from Section')
    db.close_conn()
    sections = [x[0] for x in res]
    return sections

def get_att(pid):
    res = {}
    db = DB()
    ret = db.query_data('select A_Name, A_Price from Attachment where T_Pid = %d' % int(pid))
    if ret:
        res['name'] = ret[0][0].split('/')[-1]
        res['url'] = ret[0][0]
        res['cost'] = ret[0][1]
    db.close_conn()
    return res

def del_user(uid):
    db = DB()
    res = db.del_data('delete from User where uid = %d' % int(uid))
    if res == 1:
        return 'T'
    else:
        return 'F'

def buy_att(buid, suid, cost):
    buid = int(buid)
    suid = int(suid)
    db = DB()
    res = db.query_data('select Points from User where uid = %d' % buid)
    points = int(res[0][0])
    cost = int(cost)
    if cost > points:
        db.close_conn()
        return 'F'
    else:
        points -= cost
        res = db.update_data('update User set Points = %d where uid = %d' % (points, buid))
        if res == 1:
            res = db.query_data('select Points from User where uid = %d' % suid)
            points = int(res[0][0])
            points += cost
            res = db.update_data('update User set Points = %d where uid = %d' % (points, suid))
            db.close_conn()
            return 'T'
        else:
            db.close_conn()
            return 'F'

def pwd_check(param, uid):
    sqlStr = "select * from User where uid = %d and password = '%s'" % (uid, param)
    db = DB()
    res = db.query_data(sqlStr)
    db.close_conn()
    if len(res) == 1:
        return 'T'
    else:
        return 'F'

def signup_check(col, param):
    sqlStr = "select * from User where %s = '%s'" % (col, param)
    db = DB()
    res = db.query_data(sqlStr)
    db.close_conn()
    if len(res) == 0:
        return 'T'
    else:
        return 'F'

def signin_check(mail, pwd):
    sqlStr = "select * from User where email = '%s' and password = '%s'"\
              % (mail, pwd)
    db = DB()
    res = db.query_data(sqlStr)
    if len(res) == 0:
        res = db.query_data("select * from Admin where email = '%s' and password = '%s'"\
                % (mail, pwd))
        db.close_conn()
        if len(res) == 0:
            return 'F', res
        else:
            return 'T-admin', res
    else:
        db.close_conn()
        return 'T', res

def get_post_by_id(uid):
    db = DB()
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
    db = DB()
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
    db = DB()
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

def get_friends_post(uid):
    db = DB()
    ret = db.query_data('select a.u_name, a.icon, b.pid, b.p_content, b.p_date, c.s_name, d.t_title, e.num  from User a, Section c, P_Topic d, Post_Include_P_Edit b left join (select t_pid, count(*) as num from P_Reply group by t_pid) e on b.pid=e.t_pid where a.uid = b.uid and b.sid = c.sid and b.type = 1 and d.t_pid = b.pid and a.uid in (select Friend_Uid from Make_Friends where User_Uid = %d)' % int(uid))
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

def new_post(uid, title, content, sectionName, att, timeStamp):
    db = DB()
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
    return res

def new_user(email, account, pwd):
    db = DB()
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
    return res, uid

def new_reply(uid, timeStamp, content, sectionName, tPid):
    db = DB()
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
    return res

def update_info(address, account, uid):
    db = DB()
    sqlStr = 'update User set u_address = "%s", u_name = "%s" where uid = %d' % (address, account, uid)
    res = db.update_data(sqlStr)
    db.close_conn()
    return res

def update_icon(uid, icon):
    db = DB()
    path = './static/pic/%s.png' % str(uid)
    f = open(path, 'wb')
    f.write(icon['body'])
    f.close()
    path = path.split('/', 2)[-1]
    sqlStr = 'update User set icon = "%s" where uid = %d' % (path, uid)
    res = db.update_data(sqlStr)
    db.close_conn()
    return res

def update_pwd(newPwd, uid):
    db = DB()
    sqlStr = 'update User set password = "%s" where uid = %d' % (newPwd, uid)
    res = db.update_data(sqlStr)
    db.close_conn()
    return res

def follow(uid, fid):
    sqlStr = [
        "insert into Make_Friends value",
        "(%d, %d)"
    ]
    sqlStr = ''.join(sqlStr) % (uid, fid)
    db = DB()
    res = db.insert_data(sqlStr)
    db.close_conn()
    return res

def get_draft(uid):
    db = DB()
    ret = db.query_data('select D_Title, D_Content from Draft where Uid = %d order by Did desc limit 1' % uid)
    db.close_conn()
    res = {}
    res['title'] = ret[0][0]
    res['content'] = ret[0][1]
    res = json.dumps(res)
    return res

def new_draft(title, content, udi):
    db = DB()
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
    return res

def main():
    db = DB()
    db.create_table()
    db.close_conn()


if __name__ == '__main__':
    main()
