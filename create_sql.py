#!/usr/bin/env python
#-*- coding: utf-8 -*-

import random
import time

U_TOTAL = 97
P_TOTAL = 132
R_TOTAL = 798

#drop
#template_drop = 'drop table %s cascade constraints;\n'
template_drop = 'drop table %s;\n'
tableList = ['Admin', 'User', 'Section', 'Post_Include_P_Edit', 'P_Topic', 'P_Reply', 'Attachment', 'Draft', 'Point_Purchase', 'Make_Friends', 'Download', 'Submit']

#create
createList = [
    'CREATE TABLE Admin(AdminID INTEGER,Password VARCHAR(64),Email VARCHAR(64),Icon VARCHAR(64),Admin_Name VARCHAR(64),PRIMARY KEY (AdminID));\n',
    'CREATE TABLE User(UID INTEGER,U_AccessLevel INTEGER,Password VARCHAR(64),Email VARCHAR(64),Icon VARCHAR(64),U_Name VARCHAR(64),U_Address VARCHAR(64),PostalCode VARCHAR(32),Points INTEGER CHECK (Points > 0),AdminID INTEGER,PRIMARY KEY (UID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID));\n',
    'CREATE TABLE Section(SID INTEGER,S_Name VARCHAR(64),AdminID INTEGER,PRIMARY KEY (SID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID));\n',
    'CREATE TABLE Post_Include_P_Edit(PID INTEGER,Type INTEGER,Like_Amount INTEGER,P_Content VARCHAR(512),P_Date TIMESTAMP,UID INTEGER,AdminID INTEGER,SID INTEGER,PRIMARY KEY (PID),FOREIGN KEY (UID) REFERENCES User(UID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID),FOREIGN KEY (SID) REFERENCES Section(SID) ON DELETE CASCADE ON UPDATE CASCADE);\n',
    'CREATE TABLE P_Topic(T_PID INTEGER,T_Title VARCHAR(64),View_Amount INTEGER,PRIMARY KEY (T_PID));\n',
    'CREATE TABLE P_Reply(PID INTEGER,T_PID INTEGER,PRIMARY KEY (PID, T_PID),FOREIGN KEY (T_PID) REFERENCES P_Topic(T_PID) ON DELETE CASCADE ON UPDATE CASCADE);\n',
    'CREATE TABLE Attachment(AID INTEGER,A_Name VARCHAR(64),A_Size INTEGER,A_Price INTEGER,Download_Amount INTEGER,T_PID INTEGER,PRIMARY KEY (AID, T_PID),FOREIGN KEY (T_PID) REFERENCES P_Topic(T_PID) ON DELETE CASCADE ON UPDATE CASCADE);\n',
    'CREATE TABLE Draft(DID INTEGER,D_Title VARCHAR(64),D_Content VARCHAR(512),UID INTEGER,PRIMARY KEY (DID, UID),FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE ON UPDATE CASCADE);\n',
    'CREATE TABLE Point_Purchase(PPID INTEGER,PP_Amount INTEGER,PP_Date TIMESTAMP,UID INTEGER,PRIMARY KEY (PPID, UID),FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE ON UPDATE CASCADE);\n',
    'CREATE TABLE Make_Friends(User_UID INTEGER,Friend_UID INTEGER,PRIMARY KEY (User_UID, Friend_UID),FOREIGN KEY (User_UID) REFERENCES User(UID),FOREIGN KEY (Friend_UID) REFERENCES User(UID));\n',
    'CREATE TABLE Download(UID INTEGER,AID INTEGER,D_Date TIMESTAMP,PRIMARY KEY (UID, AID),FOREIGN KEY (UID) REFERENCES User(UID),FOREIGN KEY (AID) REFERENCES Attachment(AID));\n',
    'CREATE TABLE Submit(DID INTEGER,PID INTEGER,PRIMARY KEY (DID),FOREIGN KEY (DID) REFERENCES Draft(DID),FOREIGN KEY (PID) REFERENCES Post_Include_P_Edit(PID));\n',
    ]

#admin
adminId = 1
template_admin = 'INSERT INTO Admin VALUE(%d, "%s", "%s", "%s", "%s");\n'
initAdmin = [
    (adminId, 'admin123', 'mmxinran@gmail.com', '', 'Xinran Ma')]

#user
template_user = 'INSERT INTO User VALUE(%d, %d, "%s", "%s", "%s", "%s", "%s", "%s", %d, %d);\n'
uIds = xrange(0, U_TOTAL)
uLevel = 0
uPwd = 'user1314'
mails = ['%s@gmail.com' % str(x) for x in uIds]
icon = 'pic/default.png'
lastName = ['James', 'Jack', 'Tom', 'Lyn', 'Mike']
middleName = ['Bill', 'Jim', 'John', 'Gil', 'Mora']
firstName = ['Ran', 'Fan', 'Hu', 'Aki', 'Bing']
#uName = random.choice(firstName) + ' ' + random.choice(middleName) + ' ' + random.choice(lastName)
uAddress = ''
uPcode = ''
uPoints = 10

#friends
template_friends = 'insert into Make_Friends value (%d, %d);\n'

#sections
template_sections = 'insert into Section value(%d, "%s", %d);\n'
sectionList = ['sport', 'news', 'music', 'movie', 'star', 'creative', 'food', 'other']
sIds = xrange(len(sectionList))

#posts
pIds = xrange(P_TOTAL)
man = ['I', 'You', 'He', 'She', 'It', 'Ran', 'Hu', 'Aki']
verb = ['play', 'eat', 'look', 'run with', 'fight with', 'sleep in', 'read', 'watch']
nerb = ['food', 'cake', 'donut', 'cup cake', 'football', 'computer', 'market', 'library']
#title = random.choice(man) + ' ' + random.choice(verb) + ' ' + random.choice(nerb)
#content = random.choice(man) + ' ' + random.choice(verb) + ' ' + random.choice(nerb)
#timeStamp = time.strftime('%Y%m%d%H%m%S', time.localtime())
viewAmount = 0
template_title = 'insert into P_Topic value (%d, "%s", %d);\n'
template_content = 'insert into Post_Include_P_Edit value (%d, %d, %d, "%s", "%s", %d, %d, %d);\n'
postType = 1
replyType = 2
likeAmount = 0

#replys
template_reply = 'insert into P_Reply value (%d, %d);\n'
rIds = [x + P_TOTAL for x in xrange(R_TOTAL)]


def init():
    with open('init.sql', 'w') as f:
        #drop table
        f.write('SET FOREIGN_KEY_CHECKS=0;\n')
        for table in tableList:
            f.write(template_drop % table)
        f.write('SET FOREIGN_KEY_CHECKS=1;\n')
        f.write('\n')
        #create table
        for item in createList:
            f.write(item)
        f.write('\n')
        #insert admin
        for admin in initAdmin:
            f.write(template_admin % (admin[0], admin[1], admin[2], admin[3], admin[4]))
        f.write('\n')
        #insert user
        for uId in uIds:
            uName = random.choice(firstName) + ' ' + random.choice(middleName) + ' ' + random.choice(lastName)
            f.write(template_user % (uId, uLevel, uPwd, mails[uId], icon, uName, uAddress, uPcode, uPoints, adminId))
        f.write('\n')
        #insert friends
        for uId in uIds:
            for i in xrange(random.randint(0, 5)):
                fId = random.randint(0, U_TOTAL)
                if uId == fId:
                    continue
                f.write(template_friends % (uId, fId))
        f.write('\n')
        #insert section
        for sId in sIds:
            f.write(template_sections % (sId, sectionList[sId], adminId))
        f.write('\n')
        #insert post
        for pId in pIds:
            title = random.choice(man) + ' ' + random.choice(verb) + ' ' + random.choice(nerb)
            content = random.choice(man) + ' ' + random.choice(verb) + ' ' + random.choice(nerb)
            stamp = random.randint(10, 20)
            timeStamp = time.strftime('%Y%m%d%H%m%S', time.localtime(time.time() - stamp*100000))
            f.write(template_title % (pId, title, viewAmount))
            f.write(template_content % (pId, postType, likeAmount, content, timeStamp, random.choice(uIds), adminId, random.choice(sIds)))
        f.write('\n')
        #insert post
        for rId in rIds:
            title = random.choice(man) + ' ' + random.choice(verb) + ' ' + random.choice(nerb)
            content = random.choice(man) + ' ' + random.choice(verb) + ' ' + random.choice(nerb)
            stamp = random.randint(0, 10)
            timeStamp = time.strftime('%Y%m%d%H%m%S', time.localtime(time.time() - stamp*100000))
            f.write(template_title % (rId, title, viewAmount))
            f.write(template_content % (rId, replyType, likeAmount, content, timeStamp, random.choice(uIds), adminId, random.choice(sIds)))
            f.write(template_reply % (rId, random.choice(pIds)))

def main():
    init()


if __name__ == '__main__':
    main()
