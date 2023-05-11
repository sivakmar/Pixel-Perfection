from flask import Flask,render_template,request,redirect,url_for,session,json
import ibm_db,requests
app=Flask(__name__)
app.secret_key='fujsbfijsdbfjdi'
conn=ibm_db.connect("database=bludb; hostname=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; port=30426; uid=rgj24177; password=TOI51voQjEovGoD5; security=SSL; SSLServercertificate=DigiCertGlobalRootCA.crt","","")
print("Connection successfull")
@app.route('/')
def home():
    return render_template("homepage.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['myname']
        usermail=request.form['mymail']
        userpassword=request.form['mypass']
        sql='select * from user where email=?'
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,usermail)
        ibm_db.execute(stmt)
        info=ibm_db.fetch_assoc(stmt)
        if info:
            msg2="You have been already registered : Kindly Login"
            return render_template("login.html",msg=msg2)
        else:
            sql='select count(*) from user'
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.execute(stmt)
            length=ibm_db.fetch_assoc(stmt)
            print(length)
            insert_sql='insert into user values (?,?,?,?)'
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,usermail)
            ibm_db.bind_param(prep_stmt,3,userpassword)
            ibm_db.bind_param(prep_stmt,4,length ['1']+1)
            ibm_db.execute(prep_stmt)
            msg2="You are successfully registered: Kindly Login"
            return render_template("login.html",msg=msg2)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u_email = request.form['umail']
        u_pass = request.form['upass']
        app.logger.info(f"The email id of the user: {u_email} and password: {u_pass}")
        sql="select * from user where email= ? and password=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt, 1,u_email)
        ibm_db.bind_param(stmt,2,u_pass)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        if account:
            session['Loggedin']=True
            session['USERD']=account['USERD']
            session['NAME']=account['NAME']
            return redirect(url_for('bgremoval'))
        else:
            msg="Check Email and password you have entered"
            return render_template("login.html",msg=msg)
    return render_template('login.html')

@app.route('/bgremoval',methods=['GET','POST'])
def bgremoval():
    if request.method=='POST':
        user_img=request.files['userfile']
        url = "https://human-background-removal.p.rapidapi.com/cutout/portrait/body"
        files = { "image": user_img }
        headers = {
	    "X-RapidAPI-Key": "086a9578acmsh841a56215c18256p184b98jsna1c9a193e6b1",
	    "X-RapidAPI-Host": "human-background-removal.p.rapidapi.com"
        }
        response = requests.post(url, files=files, headers=headers)
        json_data = response.json()
        image_url = json_data['data']['image_url']
        sql="insert into image_url (USERD,IMAGE_BG) values(?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,session['USERD'])
        ibm_db.bind_param(stmt,2,image_url)
        ibm_db.execute(stmt)
        return render_template("backgroundremoval.html", image_url=image_url,user_img=user_img,text='')
    return render_template("backgroundremoval.html",text="An error occured please try again!")

@app.route('/vhremoval',methods=['GET','POST'])
def vhremoval():
    if request.method=='POST':
        user_img=request.files['userfile']
        url = "https://vehicle-background-removal.p.rapidapi.com/cutout/universal/vehicle"
        files={"image": user_img}
        headers = {
	    "X-RapidAPI-Key": "086a9578acmsh841a56215c18256p184b98jsna1c9a193e6b1",
	    "X-RapidAPI-Host": "vehicle-background-removal.p.rapidapi.com"
        }  
        response = requests.post(url, files=files, headers=headers)
        json_data = response.json()
        image_url = json_data['data']['elements'][0]['image_url']
        sql="insert into image_url (USERD,VEHICLE_BG) values(?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,session['USERD'])
        ibm_db.bind_param(stmt,2,image_url)
        ibm_db.execute(stmt)
        return render_template("vehicleremoval.html", image_url=image_url,user_img=user_img,text='')
    return render_template("vehicleremoval.html",text="An error occured please try again!")
@app.route('/cartoonimage',methods=['GET','POST'])
def cartoonimage():
    selected_option = None
    if request.method=='POST':
        selected_option = request.form['my-select']
        user_img=request.files['userfile']
        url = "https://cartoon-yourself.p.rapidapi.com/facebody/api/portrait-animation/portrait-animation"
        files = { "image": user_img }
        payload = { "type": selected_option }
        headers = {
	    "X-RapidAPI-Key": "086a9578acmsh841a56215c18256p184b98jsna1c9a193e6b1",
	    "X-RapidAPI-Host": "cartoon-yourself.p.rapidapi.com"
        }
        response = requests.post(url,data=payload , files=files, headers=headers)
        json_data = response.json()
        image_url = json_data['data']['image_url']
        sql="insert into image_url (USERD,CARTOON_IMG) values(?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,session['USERD'])
        ibm_db.bind_param(stmt,2,image_url)
        ibm_db.execute(stmt)
        return render_template("cartoonimage.html", image_url=image_url,user_img=user_img,text='')
    return render_template("cartoonimage.html",text="An error occured please try again!")
@app.route('/beautyimage',methods=['GET','POST'])
def beautyimage():
    if request.method=='POST':
        user_img=request.files['userfile']
        retouch=request.form['retouch']
        whitening=request.form['whitening']
        url = "https://ai-skin-beauty.p.rapidapi.com/face/editing/retouch-skin"
        files = { "image": user_img}
        payload = {
	"retouch_degree": retouch,
	"whitening_degree": whitening
}       
        headers = {
	"X-RapidAPI-Key": "086a9578acmsh841a56215c18256p184b98jsna1c9a193e6b1",
	"X-RapidAPI-Host": "ai-skin-beauty.p.rapidapi.com"
}
        response = requests.post(url, data=payload, files=files, headers=headers)
        json_data=response.json()
        image_url=json_data['data']['image_url']
        sql="insert into image_url (USERD,SKIN_BEAUTY) values(?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,session['USERD'])
        ibm_db.bind_param(stmt,2,image_url)
        ibm_db.execute(stmt)
        return render_template("beautyimage.html",image_url=image_url,user_img=user_img,text='')
    return render_template("beautyimage.html",text="An error occured please try again!")      
@app.route('/beautyimages')
def beautyimages():
    sql = "SELECT (SKIN_BEAUTY) FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row=[]
    while True:
        data=ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            row.append(data)
            app.logger.info(row)
    return render_template("beautyimages.html",rows=row)
@app.route('/bgremoveimages')
def bgremoveimages():
    sql = "SELECT (IMAGE_BG) FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row=[]
    while True:
        data=ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            row.append(data)
            app.logger.info(row)
    return render_template("bgremoveimages.html",rows=row)
@app.route('/cartoonimages')
def cartoonimages():
    sql = "SELECT CARTOON_IMG FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row=[]
    while True:
        data=ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            row.append(data)
            app.logger.info(row)
    return render_template("cartoonimages.html",rows=row)
@app.route('/vehiclebgimages')
def vehiclebgimages():
    sql = "SELECT (VEHICLE_BG) FROM IMAGE_URL WHERE USERD=" +str(session['USERD'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row=[]
    while True:
        data=ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            row.append(data)
            app.logger.info(row)
    return render_template("vehiclebgimages.html",rows=row)
@app.route('/myimages')
def myimages():
    return render_template('myimages.html')
@app.route('/logout')
def logout():
    session.pop('Loggedin',None)
    session.pop('USERD',None)
    return render_template('login.html')
        
if __name__=='__main__':
    app.run(debug=True)
        