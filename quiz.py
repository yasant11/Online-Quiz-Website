from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_mysqldb import MySQL
from datetime import datetime
import pandas as pd


app = Flask(__name__, template_folder="template")
#config db
app.config['SECRET_KEY']='hi'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='NewPassword'
app.config['MYSQL_DB']='quiz'
app.config['a_user']='admin'
app.config['a_name']='YASANT'
app.config['a_pass']='123'


mysql=MySQL(app)

@app.route("/",methods =['GET','POST'])
def home():
    if request.method=='POST':
        detail=request.form
        username=detail['username']
        pswd=detail['pass']
        auth=detail['auth']
        if auth=='admin':
            if username==app.config['a_user'] and pswd==app.config['a_pass']:
                session['admin']=app.config['a_name']
                return redirect('/admin')    
            return redirect('/')
        cur=mysql.connection.cursor()
        check=cur.execute('select pass from users where username=%s',[username])
        if check==0:
            flash("Wrong username or password")
            return render_template('home.html')
        cnfm=cur.fetchall()  
        if cnfm[0][0]!=pswd:
            flash("Wrong username or password")
            return render_template('home.html')
        if auth=='users':
            session[auth]=username 
            return redirect('/profile')
    return render_template('home.html')
@app.route("/signup",methods =['GET','POST'])
def signup():
    if request.method=='POST':#now fetch details in a variable
        user_detail=request.form
        fname =user_detail['fname']#inside square brac name in html tag
        lname =user_detail['lname']
        username=user_detail['user']
        dob=user_detail['dob']
        country=user_detail['country']
        about=user_detail['about']
        occu=user_detail['occupation']
        pswd=user_detail['pass']
        cur=mysql.connection.cursor()
        check=cur.execute("select * from users where username=%s",[username])
        if check>0:
            flash('USERNAME ALREADY PRESENT')
            return render_template('signup.html') 
        cur.execute("insert into users(first_name,last_name,username,dob,bio,country,occupation,pass) values (%s,%s,%s,%s,%s,%s,%s,%s)",(fname,lname,username,dob,about,country,occu,pswd))
        mysql.connection.commit()
        cur.close()
        flash("Account Created")
        return redirect ("/")

    return render_template('signup.html') 
    
@app.route("/profile")
def profile():
    if 'users' in session:
        user=session['users']
        cur=mysql.connection.cursor()
        cur.execute("select * from users where username=%s",[user])
        user_det=cur.fetchall()
        return render_template('profile.html',user=user_det)
    else:
        flash('bahut tez ho rhe ho')
        return redirect(url_for("home"))
        
@app.route("/history")
def history():
    if 'users' in session:
        user=session['users']
        cur=mysql.connection.cursor()
        cur.execute("select * from users where username=%s",[user])
        user_det=cur.fetchall()
        cur.execute("select * from records where user=%s",[user])
        history=cur.fetchall()
        return render_template('history.html',user=user_det,records=history)
    else:
        flash('bahut tez ho rhe ho')
        return redirect(url_for("home"))
    
@app.route("/quizzes",methods =['GET','POST'])
def quizzes():
    if request.method=='POST':
        cur=mysql.connection.cursor()
        quiz_selected=request.form['submit']
        user=session['users']
        session['quiz_selected']=quiz_selected
        session["user_qno"]=0
        cur.execute("select * from questions where quiz=%s",[quiz_selected])
        questions=cur.fetchall()
        for question in questions:
            cur.execute("insert into active_user (user,q_sno,op1,op2,op3,op4,question_attempt,quiz) values (%s,%s,%s,%s,%s,%s,%s,%s)",[user,question[7],'unchecked','unchecked','unchecked','unchecked',0,quiz_selected])
            mysql.connection.commit()
            que=question[0]
            session[que]='unattemped'
        return redirect('/quiz')
    if 'users' in session:
        user=session['users']
        cur=mysql.connection.cursor()
        cur.execute("select * from users where username=%s",[user])
        user_det=cur.fetchall()
        cur.execute("select * from quiz")
        quizzes=cur.fetchall()
        return render_template('quizzes.html',user=user_det,quizzes=quizzes)
    else:
        flash('bahut tez ho rhe ho')
        return redirect(url_for("home"))
    
@app.route("/quiz",methods =['GET','POST'])
def quiz():
    if "quiz_selected" in session:
        user=session["users"]
        quiz=session["quiz_selected"]
        cur=mysql.connection.cursor()
        cur.execute("select * from questions where quiz=%s",[quiz])
        questions=cur.fetchall()
        cur.execute("select * from users where username=%s",[user])
        user_det=cur.fetchall()
        cur.execute("select * from active_user where user=%s",[user])
        user_status=cur.fetchall()
        if request.method=='POST':
            user_ans=request.form
            x=int(user_ans['qno'])
            #reset button
            if x==-2:
                y=session['user_qno']
                que=questions[y][0]
                session[que]='unattemped'
                cur.execute("update active_user set op1=%s,op2=%s,op3=%s,op4=%s,question_attempt=%s where user=%s and q_sno=%s",['unchecked','unchecked','unchecked','unchecked',0,user,questions[(y)%len(questions)][7]])
                mysql.connection.commit()
                cur.execute("select * from active_user where user=%s",[user])
                user_status=cur.fetchall()
                return render_template('quiz.html',user=user_det,question=questions[(y)%len(questions)],x=((y+1)%len(questions)),status=user_status)
            #save button
            if(x==-1):
                y=session['user_qno']
                que=questions[y][0]
                if que in user_ans:
                # update option status
                    session[que]=user_ans[que]
                    if user_ans[que]=='1':
                        cur.execute("update active_user set op1=%s,op2=%s,op3=%s,op4=%s,question_attempt=%s where user=%s and q_sno=%s",['checked','unchecked','unchecked','unchecked','marked',user,questions[(y)%len(questions)][7]])
                    if user_ans[que]=='2':
                        cur.execute("update active_user set op1=%s,op2=%s,op3=%s,op4=%s,question_attempt=%s where user=%s and q_sno=%s",['unchecked','checked','unchecked','unchecked','marked',user,questions[(y)%len(questions)][7]])
                    if user_ans[que]=='3':
                        cur.execute("update active_user set op1=%s,op2=%s,op3=%s,op4=%s,question_attempt=%s where user=%s and q_sno=%s",['unchecked','unchecked','checked','unchecked','marked',user,questions[(y)%len(questions)][7]])
                    if user_ans[que]=='4':
                        cur.execute("update active_user set op1=%s,op2=%s,op3=%s,op4=%s,question_attempt=%s where user=%s and q_sno=%s",['unchecked','unchecked','unchecked','checked','marked',user,questions[(y)%len(questions)][7]])
                else:
                    session[que]='unattemped'
                    cur.execute("update active_user set op1=%s,op2=%s,op3=%s,op4=%s,question_attempt=%s where user=%s and q_sno=%s",['unchecked','unchecked','unchecked','unchecked',0,user,questions[(y)%len(questions)][7]])
                mysql.connection.commit()
                cur.execute("select * from active_user where user=%s",[user])
                user_status=cur.fetchall()
                session['user_qno']=(y+1)%len(questions)
                return render_template('quiz.html',user=user_det,question=questions[(y+1)%len(questions)],x=((y+1)%len(questions))+1,status=user_status)
            
            #particular question or next button
            x=x%len(questions)
            if(x>=0 and x<len(questions)):
                session['user_qno']=x
                return render_template('quiz.html',user=user_det,question=questions[x],x=x+1,status=user_status)
            return render_template('quiz.html',user=user_det,question=questions[0],x=1,status=user_status)
        return render_template('quiz.html',user=user_det,question=questions[0],x=1,status=user_status)
    return redirect(url_for("home")) 
    if 'quiz_selected' in session:
        user=session['users']
        quiz_selected=session['quiz_selected']
        cur=mysql.connection.cursor()
        cur.execute("select * from users where username=%s",[user])
        user_det=cur.fetchall()
        return render_template('quiz.html',user=user_det)
    else:
        flash('bahut tez ho rhe ho')
        return redirect(url_for("home"))
  
@app.route("/submission")
def submission():
    if "quiz_selected" in session:
        username=session["users"]
        quiz=session["quiz_selected"]
        session.pop('quiz_selected',None)
        cur=mysql.connection.cursor()
        check=cur.execute("select * from quiz where quiz_name=%s",[quiz])
        total=cur.fetchall()[0][1]
        check=cur.execute("select * from questions where quiz=%s",[quiz])
        questions=cur.fetchall()
        check=cur.execute("select * from users where username=%s",[username])
        user=cur.fetchall()
        marks=0
        for question in questions:
            if session[question[0]]==question[5]:
                marks=marks+1
                session.pop(question[0],None)
        cur.execute("insert into records (user,quiz,marks,total) values (%s,%s,%s,%s)",[username,quiz,marks,total])
        mysql.connection.commit()
        cur.execute("delete from active_user where user=%s",[username])
        mysql.connection.commit()
        return render_template('submission.html',user=user,quiz=quiz,score=marks,total=total)
    return redirect(url_for("home")) 
  
@app.route("/admin")
def admin():
    if 'admin' in session:
        cur=mysql.connection.cursor()
        cur.execute('select count(quiz_name) from quiz')
        quiz=cur.fetchall()
        cur.execute('select count(username) from users')
        users=cur.fetchall()
        cur.execute('select count(distinct user) from active_user')
        au=cur.fetchall()
        return render_template('admin.html',admin_user=app.config['a_user'],admin_name=app.config['a_name'],tot_user=users,tot_quiz=quiz,au=au)
    else  :
        flash('bahut tez ho rhe ho')
        return redirect(url_for("home")) 
    
@app.route("/active_users",methods=['GET','POST'])
def active_users():
    if request.method=='POST':
        quiz=request.form['submit']
        cur=mysql.connection.cursor()
        cur.execute('delete from questions where quiz=%s',[quiz])
        mysql.connection.commit()
        cur.execute('delete from records where quiz=%s',[quiz])
        mysql.connection.commit()
        cur.execute('delete from quiz where quiz_name=%s',[quiz])
        mysql.connection.commit()
    if 'admin' in session:
        cur=mysql.connection.cursor()
        cur.execute("select * from quiz")
        quizzes=cur.fetchall()
        return render_template('active_users.html',admin_user=app.config['a_user'],admin_name=app.config['a_name'],quizzes=quizzes)
    else  :
        flash('bahut tez ho rhe ho')
        return redirect(url_for("home")) 

@app.route("/upload",methods =['GET','POST'])
def upload():
    if request.method=='POST':
        quiz=request.form['test']
        cur=mysql.connection.cursor()
        check=cur.execute('select * from quiz where quiz_name=%s',[quiz])
        if check>0:
            flash('Quiz already uploaded')
            return redirect('/upload')
        file=request.files['file']
        #file.save(os.path.join(app.config['upload_location'],file.filename))
        x=pd.read_excel(file)
        df=pd.DataFrame(x)
        tot_q=df.shape[0]
        if tot_q<10:
            cur.execute('insert into quiz (quiz_name,total) values(%s,%s)',[quiz,tot_q])
            mysql.connection.commit()
            for i in range(0,tot_q):
                if df['answer'][i]=='A' or df['answer'][i]=='B' or df['answer'][i]=='C' or df['answer'][i]=='D':
                    ans=ord(df['answer'][i])-ord('A')+1
                elif df['answer'][i]=='a'or df['answer'][i]=='b' or df['answer'][i]=='c' or df['answer'][i]=='d':
                    ans=ord(df['answer'][i])-ord('a')+1
                else:
                    ans=df['answer'][i]
                cur.execute("insert into questions(question,option_a,option_b,option_c,option_d,correct_option,quiz) values(%s,%s,%s,%s,%s,%s,%s)",[df['question'][i],df['option1'][i],df['option2'][i],df['option3'][i],df['option4'][i],ans,quiz])
            mysql.connection.commit()
        else:
            cur.execute('insert into quiz (quiz_name,total) values(%s,%s)',[quiz,'10'])
            mysql.connection.commit()
            for i in range(0,10):
                if df['answer'][i]=='A' or df['answer'][i]=='B' or df['answer'][i]=='C' or df['answer'][i]=='D':
                    ans=ord(df['answer'][i])-ord('A')+1
                elif df['answer'][i]=='a'or df['answer'][i]=='b' or df['answer'][i]=='c' or df['answer'][i]=='d':
                    ans=ord(df['answer'][i])-ord('a')+1
                else:
                    ans=df['answer'][i]
                cur.execute("insert into questions(question,option_a,option_b,option_c,option_d,correct_option,quiz) values(%s,%s,%s,%s,%s,%s,%s)",[df['question'][i],df['option1'][i],df['option2'][i],df['option3'][i],df['option4'][i],ans,quiz])
            mysql.connection.commit()
        
        flash('UPLOAD SUCCESSFUL')
    if 'admin' in session:
        return render_template('upload.html',admin_user=app.config['a_user'],admin_name=app.config['a_name'])
    else :
        flash('bahut tez ho rhe ho')
        return redirect(url_for("home")) 

@app.route("/logout")
def logout():
    if "admin" in session:
        session.clear()
        return redirect(url_for("home"))     
    elif "users" in session:
        session.clear()
        return redirect(url_for("home")) 
    else:
        return redirect(url_for("home")) 


if __name__=='__main__':  
    app.run(debug=True)    
