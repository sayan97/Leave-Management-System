from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_cors import cross_origin
from functools import wraps
from DB_Operation.DBOps import employee, leaves

app = Flask(__name__)
app.secret_key = "my secret key"

#database name
dbname="lms"

empobj = employee(dbname) #object of employee class
leaveobj =leaves(dbname) #object of leaves class


#to check whether user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return wrap


@app.route('/',methods=['GET','POST'])
@cross_origin()
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
@cross_origin()
def login():
    return render_template('index.html')


@app.route('/logout',methods=['GET','POST'])
@cross_origin()
@login_required
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('login'))


@app.route('/checkuser',methods=['GET','POST'])
@cross_origin()
def checkuser():
    if request.method =='POST':
        empid = int(request.form['empid'])
        pw = str(request.form['pw'])

        if empobj.loginvalidity(empid,pw):
            session['logged_in'] = True
            session['empid'] = empid
            session['pw']=pw
            session['name']=empobj.get_emp_name(empid)
            if empobj.isadmin(session['empid']):
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('employee'))
        else:
            flash("Employee ID or Password is incorrect")
            return redirect(url_for('login'))


@app.route('/employee',methods=['GET','POST'])
@cross_origin()
@login_required
def employee():
    return render_template('employee.html',name=session['name'])

@app.route('/admin',methods=['GET','POST'])
@cross_origin()
@login_required
def admin():
    notification = len(leaveobj.get_pending_applications())
    return render_template('admin.html',name=session['name'],notification=notification)


#if user is admin

@app.route('/addemployee',methods=['GET','POST'])
@cross_origin()
@login_required
def add_emp():
    if request.method=='POST':
        data={}
        data['empname'] = request.form['empname']
        data['email'] = str(request.form['email'])
        data['emprole'] = request.form['emprole']
        data['joining_date']= request.form['doj']
        data['empid'] = empobj.get_last_id() + 1
        data['passwd']="pass@" + str(data['empid'])
        if empobj.is_email_present(data['email'])==False:
            added = empobj.addemployee(data)
            if added:
                flash('Employee added successfully')
                return redirect(url_for('admin'))
            else:
                flash('Something is wrong')
                return redirect(url_for('admin'))
        else:
            flash('Email ID is already present')
            return redirect(url_for('admin'))


@app.route('/deleteemployee', methods=['GET', 'POST'])
@cross_origin()
@login_required
def delete_emp():
    if request.method=='POST':
        eid=int(request.form['empid'])

        if empobj.empidexist(eid):
            empobj.deleteemployee(eid)
            flash("Employee {} is removed".format(str(eid)))
            return redirect(url_for('admin'))
        else:
            flash("Employee {} is not present".format(eid))
            return redirect(url_for('admin'))


@app.route('/searchemployee', methods=['GET', 'POST'])
@cross_origin()
@login_required
def search_employee():
    if request.method=='POST':
        empid=int(request.form['empid'])
        if empobj.empidexist(empid):
            return redirect(url_for('manageemp',empid=empid))
        else:
            flash("Employee id does not exist")
            return redirect(url_for('admin'))


@app.route('/<empid>/manageemp', methods=['GET', 'POST'])
@cross_origin()
@login_required
def manageemp(empid):
    empid=int(empid)
    info = empobj.get_emp_info(empid)
    levreq = leaveobj.curr_month_leave_requests(empid)
    levapp = leaveobj.curr_month_leave_approved(empid)
    return render_template('manageemp.html', name=session['name'], empid=empid, info=info, levreq=levreq, levapp=levapp)


@app.route('/<empid>/showleaves', methods=['GET', 'POST'])
@cross_origin()
@login_required
def showleaves(empid):
    leavedata=leaveobj.get_emp_leaves(empid)
    if len(leavedata)>0:
        return render_template('empleaves.html', name=session['name'], leavedata=leavedata)
    else:
        flash("No Leave Requests present")
        return redirect(url_for('manageemp',empid=empid))


@app.route('/editemployee', methods=['GET', 'POST'])
@cross_origin()
@login_required
def editemployee():
    if request.method=='POST':
        info={}
        info['empid']=int(request.form['empid'])
        info['empname']=request.form['empname']
        info['email']=request.form['email']
        info['emprole']=request.form['emprole']
        info['doj']=str(request.form['doj'])
        if empobj.updateinfo(info):
            flash("Employee {} updated successfully".format(info['empid']))
            return redirect(url_for('manageemp',empid=info['empid']))
        else:
            flash("Cannot update employee")
            return redirect(url_for('manageemp',empid=info['empid']))


@app.route('/manageleaves', methods=['GET', 'POST'])
@cross_origin()
@login_required
def view_pending_leaves():
        if leaveobj.is_applications_pending():
            leavedata = leaveobj.get_pending_applications() #dict
            return render_template('manageleave.html',name=session['name'],pending_leaves=leavedata)
        else:
            flash('No pending leave applications')
            return redirect(url_for('admin'))


@app.route('/<empid>/<start>/approve', methods=['GET', 'POST'])
@cross_origin()
@login_required
def approve(empid,start):
    empid=empid
    start=str(start)
    passed=leaveobj.approveleaves(empid,start)
    if passed:
        if leaveobj.is_applications_pending():
            flash('Leave Approved for ' + str(empid))
            return redirect(url_for('view_pending_leaves'))
        else:
            flash('Leave Approved for ' + str(empid))
            return redirect(url_for('admin'))

    else:
        flash('Cannot Approve Leave. SOMETHING IS WRONG!!')
        return redirect(url_for('view_pending_leaves'))

@app.route('/<empid>/<start>/reject', methods=['GET', 'POST'])
@cross_origin()
@login_required
def reject(empid,start):
    empid=empid
    start = str(start)
    passed=leaveobj.rejectleaves(empid,start)
    if passed:
        if leaveobj.is_applications_pending():
            flash('Leave rejected for ' + str(empid))
            return redirect(url_for('view_pending_leaves'))
        else:
            flash('Leave rejected for ' + str(empid))
            return redirect(url_for('admin'))

    else:
        flash('Cannot Reject Leave. SOMETHING IS WRONG!!')
        return redirect(url_for('view_pending_leaves'))

@app.route('/leavebydate', methods=['GET', 'POST'])
@cross_origin()
@login_required
def leavebydate():
    if request.method=='POST':
        date=str(request.form['date'])
        leaves = leaveobj.get_leaves_by_date(date)
        if len(leaves) > 0:
            return render_template('searchbydate.html',name=session['name'], leaves=leaves)
        else:
            flash('No leaves present on this day')
            return redirect(url_for('admin'))


#if user is employee

@app.route('/pastleaves', methods=['GET', 'POST'])
@cross_origin()
@login_required
def show_past_requests():
    if request.method=='POST':
        if leaveobj.is_emp_leave_present(session['empid']):
            leaves=leaveobj.get_emp_leaves(session['empid'])
            levreq=leaveobj.curr_month_leave_requests(session['empid'])
            levapp=leaveobj.get_emp_leaves(session['empid'])
            return render_template('leaverqst.html', leavedata=leaves, levreq=levreq, levapp=levapp)
        else:
            flash("No Leave Requests Present")
            return redirect(url_for('employee'))


@app.route('/newrequest',methods=['GET','POST'])
@cross_origin()
@login_required
def emp_newrequest():
    if request.method=='POST':
        start = str(request.form['start'])
        end = str(request.form['end'])
        reason = request.form['reason']
        if end<start:
            flash("To-Date should be greater than From-Date")
            return redirect(url_for('employee'))
        passed=leaveobj.applyleave(session['empid'],session['name'],start, end, reason)
        if passed:
            flash("New Leave Request Created")
            return redirect(url_for('employee'))
        else:
            flash("Cannot create a new request with this date")
            return redirect(url_for('employee'))


@app.route('/passchange',methods=['GET','POST'])
@cross_origin()
@login_required
def passchange():
    if request.method=='POST':
        p1=request.form['p1']
        p2=request.form['p2']
        if empobj.changepassword(session['empid'],p1,p2):
            flash('Password changed!')
            return redirect(url_for('employee'))
        else:
            flash('Password does not match')
            return redirect(url_for('employee'))

if __name__ == '__main__':
    app.run(debug=True)




