#!/usr/bin/env python
#-*- coding: utf-8 -*-

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


    def create_table(self):
        sqlStr = [
            'CREATE TABLE Admin(AdminID INTEGER,Password VARCHAR(16),Email VARCHAR(16),Icon VARCHAR(16),Admin_Name VARCHAR(16),PRIMARY KEY (AdminID));',
            'CREATE TABLE User(UID INTEGER,U_AccessLevel INTEGER,Password VARCHAR(16),Email VARCHAR(16),Icon VARCHAR(16),U_Name VARCHAR(16),U_Address VARCHAR(16),PostalCode VARCHAR(8),Points INTEGER,AdminID INTEGER,PRIMARY KEY (UID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID));',
            'CREATE TABLE Section(SID INTEGER,S_Name VARCHAR(16),AdminID INTEGER,PRIMARY KEY (SID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID));',
            'CREATE TABLE Post_Include_P_Edit(PID INTEGER,Type INTEGER,Like_Amount INTEGER,P_Content VARCHAR(64),P_Date TIMESTAMP,UID INTEGER,AdminID INTEGER,SID INTEGER,PRIMARY KEY (PID),FOREIGN KEY (UID) REFERENCES User(UID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID),FOREIGN KEY (SID) REFERENCES Section(SID));',
            'CREATE TABLE P_Topic(T_PID INTEGER,T_Title VARCHAR(16),View_Amount INTEGER,PRIMARY KEY (T_PID));',
            'CREATE TABLE P_Reply(PID INTEGER,T_PID INTEGER,PRIMARY KEY (PID, T_PID),FOREIGN KEY (T_PID) REFERENCES P_Topic(T_PID) ON DELETE CASCADE ON UPDATE CASCADE);',
            'CREATE TABLE Attachment(AID INTEGER,A_Name VARCHAR(16),A_Size INTEGER,A_Price INTEGER,Download_Amount INTEGER,T_PID INTEGER,PRIMARY KEY (AID, T_PID),FOREIGN KEY (T_PID) REFERENCES P_Topic(T_PID) ON DELETE CASCADE ON UPDATE CASCADE);',
            'CREATE TABLE Draft(DID INTEGER,D_Title VARCHAR(16),D_Content VARCHAR(64),UID INTEGER,PRIMARY KEY (DID, UID),FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE ON UPDATE CASCADE);',
            'CREATE TABLE Point_Purchase(PPID INTEGER,PP_Amount INTEGER,PP_Date TIMESTAMP,UID INTEGER,PRIMARY KEY (PPID, UID),FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE ON UPDATE CASCADE);',
            'CREATE TABLE Make_Friends(User_UID INTEGER,Friend_UID INTEGER,PRIMARY KEY (User_UID, Friend_UID),FOREIGN KEY (User_UID) REFERENCES User(UID),FOREIGN KEY (Friend_UID) REFERENCES User(UID));',
            'CREATE TABLE Download(UID INTEGER,AID INTEGER,D_Date TIMESTAMP,PRIMARY KEY (UID, AID),FOREIGN KEY (UID) REFERENCES User(UID),FOREIGN KEY (AID) REFERENCES Attachment(AID));',
            'CREATE TABLE Submit(DID INTEGER,PID INTEGER,PRIMARY KEY (DID),FOREIGN KEY (DID) REFERENCES Draft(DID),FOREIGN KEY (PID) REFERENCES Post_Include_P_Edit(PID));',
            ]
        for item in sqlStr:
            self.execute_sql(item)

def main():
    db = DB()
    db.create_table()
    db.close_conn()


if __name__ == '__main__':
    main()
