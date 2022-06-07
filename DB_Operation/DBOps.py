import mysql.connector as conn
from datetime import date, datetime

class employee:
    def __init__(self, dbname):
        self.dbname=dbname

    def getcursor(self):
        try:
            mydb = conn.connect(host='localhost', user='root', passwd="root@mysql")
            cursor = mydb.cursor()
            cursor.execute('use '+str(self.dbname))
            cursor.execute('SET SQL_SAFE_UPDATES = 0')
            return mydb,cursor
        except Exception as e:
            raise e

    def loginvalidity(self,empid,passwd):
        try:
            if self.empidexist(empid):
                mydb, cursor = self.getcursor()
                q = 'select passwd from employees where empid=' + str(empid)
                cursor.execute(q)
                result = cursor.fetchall()
                cursor.close()
                if result[0][0] == str(passwd):
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            raise e

    def isadmin(self,empid):
        try:
            mydb,cursor = self.getcursor()
            q="select emprole from employees where empid="+str(empid)
            cursor.execute(q)
            res = cursor.fetchall()
            cursor.close()
            if res[0][0] == "Admin":
                return True
            else:
                return False
        except Exception as e:
            raise e

    def is_email_present(self,email):
        try:
            mydb,cursor=self.getcursor()
            q = "select count(*) from  employees where email='{}'".format(email)
            cursor.execute(q)
            res=cursor.fetchall()
            if res[0][0]>0:
                return True
            else:
                return False
        except Exception as e:
            raise (e)


    def get_emp_name(self,empid):
        try:
            mydb, cursor = self.getcursor()
            q = 'select empname from employees where empid=' + str(empid)
            cursor.execute(q)
            res = cursor.fetchall()
            name = res[0][0]
            return name
        except Exception as e:
            raise e

    def get_last_id(self):
        try:
            mydb,cursor=self.getcursor()
            q=f'SELECT empid FROM employees ORDER BY empid DESC LIMIT 1'
            cursor.execute(q)
            res=cursor.fetchall()
            return int(res[0][0])
        except Exception as e:
            raise e

    def get_emp_info(self,empid):
        try:
            mydb,cursor = self.getcursor()
            q = 'select empname, email, emprole, joining_date from employees where empid=' + str(empid)
            cursor.execute(q)
            r = cursor.fetchall()
            cursor.close()
            data = {}
            data['empid'] = empid
            data['empname'] = r[0][0]
            data['email'] = r[0][1]
            data['emprole'] = r[0][2]
            doj = str(r[0][3])
            data['doj'] = datetime.strptime(doj,'%Y-%m-%d').strftime('%d-%b-%Y').upper()
            return data
        except Exception as e:
            raise e



    def addemployee(self,data):
        try:
            mydb,cursor = self.getcursor()
            q = "insert into employees values({0},'{1}','{2}','{3}','{4}','{5}')".format(data['empid'],
                                                                                    data['empname'],
                                                                                    data['email'],
                                                                                    data['passwd'],
                                                                                    data['emprole'],
                                                                                    data['joining_date'])

            cursor.execute(q)
            mydb.commit()
            cursor.close()
            return True

        except Exception as e:
            raise e


    def deleteemployee(self,empid):
        try:
            mydb,cursor = self.getcursor()
            cursor.execute("delete from employees where empid=" + str(empid))
            mydb.commit()
            cursor.close()
            return True

        except Exception as e:
            raise e


    def empidexist(self,empid):
        try:
            mydb,cursor = self.getcursor()
            q='select count(*) from employees where empid = '+str(empid)
            cursor.execute(q)
            res = cursor.fetchall()
            cursor.close()
            if int(res[0][0])>0:
                return True
            else:
                return False

        except Exception as e:
            raise e


    def updateinfo(self, info):
        try:
            mydb,cursor = self.getcursor()
            q = f"update employees set empname='{0}', email='{1}', emprole='{2}' where empid={3}".format(info['empname'],info['email'],info['emprole'],info['empid'])
            cursor.execute(q)
            mydb.commit()
            cursor.close()
            return True
        except Exception as e:
            raise e

    def changepassword(self,empid,p1,p2):
        try:
            mydb,cursor=self.getcursor()
            if p1==p2:
                q="update employees set passwd='{0}' where empid={1}".format(p2,empid)
                cursor.execute(q)
                mydb.commit()
                cursor.close()
                return True
            else:
                return False
        except Exception as e:
            raise e


class leaves:
    def __init__(self, dbname):
        self.dbname=dbname

    def getcursor(self):
        try:
            mydb = conn.connect(host='localhost', user='root', passwd="root@mysql")
            cursor = mydb.cursor()
            query="use "+str(self.dbname)
            cursor.execute(query)
            cursor.execute("SET SQL_SAFE_UPDATES = 0")
            return mydb,cursor
        except Exception as e:
            raise e

    def is_emp_leave_present(self,empid):
        try:
            mydb,cursor=self.getcursor()
            q="select count(*) from leaves where empid="+str(empid)
            cursor.execute(q)
            r=cursor.fetchall()
            if r[0][0]>0:
                return True
            else:
                return False
        except Exception as e:
            raise e

    def curr_month_leave_requests(self,empid):
        try:
            today = date.today()
            mydb,cursor=self.getcursor()
            q="select start_date, days from leaves where empid="+str(empid)
            cursor.execute(q)
            r=cursor.fetchall()
            days = 0
            for i in r:
                if i[0].month == today.month:
                    days += i[1]
            return days
        except Exception as e:
            raise e

    def curr_month_leave_approved(self,empid):
        try:
            today = date.today()
            mydb,cursor=self.getcursor()
            q="select start_date, days from leaves where action='APPROVED' and empid="+str(empid)
            cursor.execute(q)
            r=cursor.fetchall()
            days = 0
            for i in r:
                if i[0].month == today.month:
                    days += i[1]
            return days
        except Exception as e:
            raise e

    def get_emp_leaves(self,empid):
        try:
            mydb,cursor=self.getcursor()
            q='select start_date, end_date, days, reason, action from leaves where empid={} order by start_date desc'.format(empid)
            cursor.execute(q)
            r=cursor.fetchall()
            info=[]
            for i in r:
                row={}
                row['date']=str(i[0])
                row['start']=datetime.strptime(str(i[0]), '%Y-%m-%d').strftime('%d-%b-%Y').upper()
                row['end']=datetime.strptime(str(i[1]), '%Y-%m-%d').strftime('%d-%b-%Y').upper()
                row['days']=i[2]
                row['reason']=i[3]
                row['action']=i[4]
                info.append(row)
            return info
        except Exception as e:
            raise e


    def applyleave(self, empid, empname, start, end, reason):
        try:
            mydb,cursor=self.getcursor()
            action='PENDING'
            q="select count(*) from leaves where empid ={0} AND start_date='{1}'".format(empid,start)
            res=cursor.fetchall()
            if len(res)==0:
                q = "insert into leaves values({0},'{1}','{2}','{3}','{4}','{5}',DATEDIFF(end_date, start_date) + 1)".format(empid, empname, start, end, reason, action)
                cursor.execute(q)
                mydb.commit()
                cursor.close()
                return True
            else:
                return False
        except Exception as e:
            raise e

    def approveleaves(self,empid,start):
        try:
            mydb,cursor = self.getcursor()
            action="APPROVED"
            q = "update leaves set action='{0}' where empid={1} and start_date='{2}'".format(action,empid,start)
            cursor.execute(q)
            mydb.commit()
            cursor.close()
            return True
        except Exception as e:
            raise e

    def rejectleaves(self,empid,start):
        try:
            mydb,cursor = self.getcursor()
            action='REJECTED'
            q = "update leaves set action='{0}' where empid={1} AND start_date='{2}'".format(action,empid,start)
            cursor.execute(q)
            mydb.commit()
            cursor.close()
            return True
        except Exception as e:
            raise e

    def is_applications_pending(self):
        try:
            mydb,cursor = self.getcursor()
            cursor.execute("select count(*) from leaves where action ='PENDING'")
            res=cursor.fetchall()
            cursor.close()
            if res[0][0]>0:
                return True
            else:
                return False
        except Exception as e:
            raise e


    def get_pending_applications(self):
        try:
            mydb, cursor = self.getcursor()
            cursor.execute("select empid,start_date,end_date,reason,empname,days from leaves where action='PENDING' order by start_date")
            r = cursor.fetchall()
            pending = []
            for i in r:
                data={}
                data['empid'] = i[0]
                data['date']=str(i[1])
                data['start'] = datetime.strptime(str(i[1]), '%Y-%m-%d').strftime('%d-%b-%Y').upper()
                data['end'] = datetime.strptime(str(i[2]), '%Y-%m-%d').strftime('%d-%b-%Y').upper()
                data['reason'] = i[3]
                data['empname']=i[4]
                data['days']=i[5]
                pending.append(data)
            return pending
        except Exception as e:
            raise e

    def get_emp_applications(self,empid):
        try:
            mydb, cursor = self.getcursor()
            cursor.execute("select * from leaves where empid="+str(empid))
            lst = cursor.fetchall()
            return lst
        except Exception as e:
            raise e

    def get_leaves_by_date(self,date):
        try:
            mydb,cursor=self.getcursor()
            q=f"select empid, empname, start_date, end_date, reason from leaves where '{0}'>= start_date and '{1}'<= end_date and action='APPROVED'".format(date,date)
            cursor.execute(q)
            res=cursor.fetchall()
            l=[]
            for i in res:
                data={}
                data['empid']=i[0]
                data['empname'] = i[1]
                data['start'] = datetime.strptime(str(i[2]), '%Y-%m-%d').strftime('%d-%b-%Y').upper()
                data['end'] = datetime.strptime(str(i[3]), '%Y-%m-%d').strftime('%d-%b-%Y').upper()
                data['reason'] = i[4]
                l.append(data)
            return l
        except Exception as e:
            raise e


