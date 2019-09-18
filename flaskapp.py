from flask import Flask, render_template, request
import pyodbc
import base64
from werkzeug import secure_filename
import os
from collections import Counter
from flask import send_file,send_from_directory

s1 = ""
s2 = ""

UPLOAD_FOLDER = '/home/ubuntu/flaskapp/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

app = Flask(__name__)
app.config['SECRET_KEY']='nvsk123'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def my_form():
    return render_template("main.html")
    

    
 
@app.route('/login', methods = ["POST"])
def method():
    username = ""
    password = ""
    if request.method == 'POST':
        #code for insert
        if request.form['action'] == "login":
            print("Hi entered login")
            #try:
            print("Entered try")
           conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.1.1};'
                            'Server=localhost;'
                            'UID=SA;'
                                  'PWD=123@Avinash;'
                            'DATABASE=CLOUDPROJECT;')
        
            cursor = conn.cursor()
                #cursor1 = conn.cursor()
            print("got connected")   
            s1 = '''SELECT * FROM STUDENT WHERE uid=?;'''
            print(s1)
                
            val = (request.form['userid'])
            cursor.execute(s1,val)
            rows = cursor.fetchall()
            conn.commit()
            if(len(rows)>=1):
                #rows = cursor.fet()
                for row in rows:
                    username,password=row.uid,row.password
                print(password)
                print(type(password))
                print('\n')
                print(request.form['password'])
                print(type(request.form['password']))
                if(password.strip()==request.form['password'].strip()):
                    #user already exists and password also matches
                    #displays all his/her details
                    #render template to display.html
                    #print("path:")
                    #print(row.fdata)
                    return render_template('display.html', output1=row.fname, output2=row.lname, output3=row.email, path=row.fdata,output4= row.wcount)
                else:
                    #user id is correct, but password is wrong
                    #render template saying invalid credentials
                    return render_template('main.html', output="Invalid Credentials")    
                    
            else:
                #user is new and his data is not present in the database
                #redirect to sign up page
                return render_template('sub.html')
                
                    
            cursor.close()
            conn.close()
            #except:
                #return "Hi"
                
@app.route('/signup', methods = ["GET", "POST"])
def sub_method():
   conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.1.1};'
                            'Server=localhost;'
                            'UID=SA;'
                                  'PWD=123@Avinash;'
                            'DATABASE=CLOUDPROJECT;')
    
    path = ""  
    wcount= 0
    cursor = conn.cursor()
    if request.method == 'POST':
        #code for insert
        if request.form['action'] == "insert":
            #file name is fetched
            file=request.files['myFile']
            #if the file name field is not empty
            if(request.files['myFile']!=None):
                #checking if its in allowed file or not
                if file and allowed_file(file.filename):
                    #we are trying to fetch only the file name but not the entire path
                    filename = secure_filename(file.filename)
                    mimetype = file.content_type
                    if(mimetype=="text/plain"):
                        name = "file_" + request.form['userid'] + ".txt"
                    elif(mimetype=="application/pdf"):
                        name = "file_" + request.form['userid'] + ".pdf"
                    
                    #saving file to a path
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
                    #getting the full path and storing it in a variable called path
                    path=os.path.join(app.config['UPLOAD_FOLDER'], name)
                    print("path saved")
                    with open(path, 'rb') as f:
                        p=f.read()
                        words=p.split()
                        #print(words)
                        wcount=len(words)
                    
                    '''
                    num_words = 0
 
                    with open(path, 'rb') as f:
                        for line in f:
                            words = line.split()
                            num_words += len(words)
                            wcount=num_words
                    print("Number of words:")
                    print(num_words)'''
        
            else:
                path=None
                wcount=0
                
            s2 = '''INSERT INTO STUDENT VALUES (?,?,?,?,?,?,?);''' 
            val = (request.form['userid'],request.form['password'],request.form['firstname'],request.form['lastname'],request.form['email'],path,wcount)
            cursor.execute(s2,val)
            print("step2")
            conn.commit()
            print("step3")
            if(cursor.rowcount>=1):
                s1 = '''SELECT * FROM STUDENT WHERE uid=?;'''
                val = (request.form['userid'])
                cursor.execute(s1,val)
                rows=cursor.fetchall()
                return render_template('display.html',output1=rows[0].fname,output2=rows[0].lname,output3=rows[0].email,path=rows[0].fdata,output4=rows[0].wcount)
                
            cursor.close()
            conn.close()
            
@app.route('/download/<path:filename>', methods = ["GET", "POST"])
def download(filename):
    print("I'm doing the last step")
    tup=os.path.split(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], tup[1], as_attachment=True)
        
                      
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

