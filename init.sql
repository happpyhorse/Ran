SET FOREIGN_KEY_CHECKS=0;
drop table Admin;
drop table User;
drop table Section;
drop table Post_Include_P_Edit;
drop table P_Topic;
drop table P_Reply;
drop table Attachment;
drop table Draft;
drop table Point_Purchase;
drop table Make_Friends;
drop table Download;
drop table Submit;
SET FOREIGN_KEY_CHECKS=1;

CREATE TABLE Admin(AdminID INTEGER,Password VARCHAR(64),Email VARCHAR(64),Icon VARCHAR(64),Admin_Name VARCHAR(64),PRIMARY KEY (AdminID));
CREATE TABLE User(UID INTEGER,U_AccessLevel INTEGER,Password VARCHAR(64),Email VARCHAR(64),Icon VARCHAR(64),U_Name VARCHAR(64),U_Address VARCHAR(64),PostalCode VARCHAR(32),Points INTEGER CHECK (Points > 0),AdminID INTEGER,PRIMARY KEY (UID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID));
CREATE TABLE Section(SID INTEGER,S_Name VARCHAR(64),AdminID INTEGER,PRIMARY KEY (SID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID));
CREATE TABLE Post_Include_P_Edit(PID INTEGER,Type INTEGER,Like_Amount INTEGER,P_Content VARCHAR(512),P_Date TIMESTAMP,UID INTEGER,AdminID INTEGER,SID INTEGER,PRIMARY KEY (PID),FOREIGN KEY (UID) REFERENCES User(UID),FOREIGN KEY (AdminID) REFERENCES Admin(AdminID),FOREIGN KEY (SID) REFERENCES Section(SID) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE P_Topic(T_PID INTEGER,T_Title VARCHAR(64),View_Amount INTEGER,PRIMARY KEY (T_PID));
CREATE TABLE P_Reply(PID INTEGER,T_PID INTEGER,PRIMARY KEY (PID, T_PID),FOREIGN KEY (T_PID) REFERENCES P_Topic(T_PID) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE Attachment(AID INTEGER,A_Name VARCHAR(64),A_Size INTEGER,A_Price INTEGER,Download_Amount INTEGER,T_PID INTEGER,PRIMARY KEY (AID, T_PID),FOREIGN KEY (T_PID) REFERENCES P_Topic(T_PID) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE Draft(DID INTEGER,D_Title VARCHAR(64),D_Content VARCHAR(512),UID INTEGER,PRIMARY KEY (DID, UID),FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE Point_Purchase(PPID INTEGER,PP_Amount INTEGER,PP_Date TIMESTAMP,UID INTEGER,PRIMARY KEY (PPID, UID),FOREIGN KEY (UID) REFERENCES User(UID) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE Make_Friends(User_UID INTEGER,Friend_UID INTEGER,PRIMARY KEY (User_UID, Friend_UID),FOREIGN KEY (User_UID) REFERENCES User(UID),FOREIGN KEY (Friend_UID) REFERENCES User(UID));
CREATE TABLE Download(UID INTEGER,AID INTEGER,D_Date TIMESTAMP,PRIMARY KEY (UID, AID),FOREIGN KEY (UID) REFERENCES User(UID),FOREIGN KEY (AID) REFERENCES Attachment(AID));
CREATE TABLE Submit(DID INTEGER,PID INTEGER,PRIMARY KEY (DID),FOREIGN KEY (DID) REFERENCES Draft(DID),FOREIGN KEY (PID) REFERENCES Post_Include_P_Edit(PID));

