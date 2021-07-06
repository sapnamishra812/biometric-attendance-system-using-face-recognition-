from tkinter import *
import tkinter.ttk as ttk
from tkinter.ttk import Progressbar
import tkinter as tk
from PIL import ImageTk,Image
import cv2
import numpy as np
import datetime,subprocess
import pyttsx3
import time,csv,os
import pandas as pd
from pathlib import Path
import shutil
import pymysql

###Connect to the database
connection = pymysql.connect(host='localhost',user='root',password='',db='SAFR')
cursor = connection.cursor()

#Size for displaying Image
w = 500;h = 360
size = (w, h)

windo = Tk()
windo.configure(background='white')
windo.title("SAFR: Student Attendance using Face\ud83d\ude00 Recogntion")
width  = windo.winfo_screenwidth()
height = windo.winfo_screenheight()
windo.geometry(f'{width}x{height}')
windo.iconbitmap('./images/app.ico')
windo.resizable(0,0)
s = 0
##AUdio initialization
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
face_clsfr=cv2.CascadeClassifier(cv2.haarcascades+'haarcascade_frontalface_alt.xml')

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def on_closing():
    from tkinter import messagebox
    if messagebox.askokcancel("Reset", "Do you want to Reset the System?"):
        res_sys()

def image_generate():
    global dn,imageFrame,display,id,name,cam,ic
    id = id_txt.get()
    name = name_txt.get()
    if id == '' or name == '':
        ict = tk.Label(windo, text="Please Enter Following....", width=22, height=1, fg="black", bg="yellow",
                      font=('times', 14, ' bold '))
        ict.place(x=280, y=247)
        windo.after(5000, destroy_widget, ict)
    else:

        ## Create the DB if not exitst
        db_sql = """CREATE DATABASE IF NOT EXISTS SAFR;"""
        cursor.execute(db_sql)

        ## Create the table and enter the data
        table_sql = """CREATE TABLE IF NOT EXISTS Reg_Students (
            Student_ID varchar(100) NOT NULL,
            NAME varchar(100) NOT NULL,
            DATE varchar(20) NOT NULL,
            Registration_Time varchar(20) NOT NULL,
            PRIMARY KEY (Student_ID)
        );
           """
        cursor.execute(table_sql)

        values = (id,)
        login_sql = 'SELECT * FROM reg_students WHERE Student_ID = % s'
        cursor.execute(login_sql, values)
        account = cursor.fetchone()
        if account:
            account = list(account)

            if account[0] == id:
                ict = tk.Label(windo, text=id+" is already Registered..", width=22, height=1, fg="black", bg="yellow",
                               font=('times', 14, ' bold '))
                ict.place(x=280, y=247)
                windo.after(5000, destroy_widget, ict)
        else:
            repn = Path('TrainingImage')
            if repn.is_dir():
                pass
            else:
                os.mkdir('TrainingImage')
            try:
                cam = cv2.VideoCapture(0)
                detector = cv2.CascadeClassifier(cv2.haarcascades+'haarcascade_frontalface_default.xml')
                imageFrame = tk.Frame(windo)
                imageFrame.place(x=665, y=53)
                display = tk.Label(imageFrame)
                display.grid()
                imageFrame1 = tk.Frame(windo)
                imageFrame1.place(x= 30, y=88)
                display1 = tk.Label(imageFrame1, borderwidth = 6,highlightbackground='yellow')
                display1.grid()

                ip = tk.Label(windo, text= name, width=14, height=1, fg="black", bg="yellow",
                              font=('times', 18, ' bold '))
                ip.place(x=30, y=260)

                ic = tk.Label(windo, text="Image Count: ", width=13, height=1, fg="black", bg="yellow",
                              font=('times', 14, ' bold '))
                def test():
                    global s,x,y,w,h,gray,g,ic
                    ret, img = cam.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, 1.3, 5)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 6)
                        s = s + 1
                        print(s)
                        cv2.imwrite("./TrainingImage/ " + name + "." + id + '.' + str(s) + ".jpg",
                                    gray[y:y + h, x:x + w])
                        ic.configure(text="Image Count: " + str(s+1), width=13, height=1, fg="black", bg="yellow",
                                      font=('times', 14, ' bold '))
                        ic.place(x=280, y=247)
                        gm = Image.fromarray(gray[y:y + h, x:x + w])
                        gm = gm.resize((190, 187), Image.ANTIALIAS)
                        imgtk1 = ImageTk.PhotoImage(image=gm)
                        display1.imgtk = imgtk1
                        display1.configure(image=imgtk1)
                        if s>80:
                            ic.destroy()
                            break
                    cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
                    rgb = cv2.cvtColor(cv2image, cv2.COLOR_RGBA2RGB)
                    img = Image.fromarray(rgb)
                    img = img.resize(size, Image.ANTIALIAS)
                    imgtk = ImageTk.PhotoImage(image=img)
                    display.imgtk = imgtk
                    display.configure(image=imgtk)
                    k = display.after(10, test)
                    if s>80:
                        display.after_cancel(k)
                        s = 0
                        windo.after(3000,destroy_widget,ic)
                        windo.after(2000, destroy_widget, imageFrame)
                        windo.after(2000, destroy_widget, display)
                        windo.after(2000, destroy_widget, imageFrame1)
                        windo.after(2000, destroy_widget, display1)
                        windo.after(2000, destroy_widget, ip)
                        speak('Thank you ' + name + ', Your Face Data is Captured')
                        breakcam()
                test()


                my_file = Path("./RegisteredStudents/RegisteredStudents.csv")
                ts = time.time()
                Date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                row = [id, name, Date, Time]
                head = ['Student_ID', 'Name', 'Date', 'Registration Time']
                dir2 = Path('RegisteredStudents')


                ## Enter the data into DB
                insert_sql = ("INSERT INTO Reg_Students(Student_ID,NAME,DATE,Registration_Time) VALUES (%s,%s, %s, %s)")
                table_data = (id, name, Date, Time)
                cursor.execute(insert_sql, table_data)
                connection.commit()
                if dir2.is_dir():
                    pass
                else:
                    os.mkdir('RegisteredStudents')
                if my_file.is_file():
                    print('file exists')
                    row = [id, name, Date, Time]
                    with open('./RegisteredStudents/RegisteredStudents.csv', 'a+',newline="") as csvFile:
                        writer = csv.writer(csvFile, delimiter=',')
                        writer.writerow(row)
                        csvFile.close()
                else:
                    wrinting = dict(zip(head, row))
                    with open('./RegisteredStudents/RegisteredStudents.csv', 'a+',newline="") as csvFile:
                        writer = csv.DictWriter(csvFile, delimiter=',', fieldnames=head)
                        writer.writeheader()
                        writer.writerow(wrinting)
                        csvFile.close()
            except Exception as e:
                print(e)
                ict = tk.Label(windo, text="Something went wrong....", width=22, height=1, fg="black", bg="yellow",
                               font=('times', 14, ' bold '))
                ict.place(x=280, y=247)
                windo.after(6000, destroy_widget, ict)
                windo.after(1000, destroy_widget, dn)
                windo.after(1000, destroy_widget, imageFrame)
                windo.after(1000, destroy_widget, display)
                windo.after(1000, destroy_widget, imageFrame1)
                windo.after(1000, destroy_widget, display1)
                windo.after(1000, destroy_widget, ip)
                speak('Something is wrong')
                print(e)
def fill_att():
    try:
        csv_destroyer()
    except:
        pass
    dir25 = Path('Trained_model')
    if dir25.is_dir():
        try:
            global display4,imageFrame4,cp,dn4,cap,off,label,n2,attendance
            cap = cv2.VideoCapture(0)
            # To test a video from testing video
            imageFrame4 = tk.Frame(windo)
            imageFrame4.place(x=560, y=51)
            off = tk.Button(windo, text='Stop\ud83d\ude80 Camera', command=destroyer1, bg="midnightblue", fg="white",
                           width=14,height=1, font=('times', 13, 'italic bold '), activebackground='yellow')
            off.place(x=615, y= 580)
            display4 = tk.Label(imageFrame4)
            display4.grid()
            col_names = ['Student_ID', 'Name', 'Date', 'Registration Time']
            attendance = pd.DataFrame(columns=col_names)
            def show_frame():
                # try:
                    global img
                    ret, frame = cap.read()
                    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    # out = cv2.VideoWriter('output.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
                    df = pd.read_csv("./RegisteredStudents/RegisteredStudents.csv")
                    frame = cv2.flip(frame, 1)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    recognizer = cv2.face.LBPHFaceRecognizer_create()
                    recognizer.read("./Trained_model/Model.yml")
                    faces = face_clsfr.detectMultiScale(gray, 1.3, 3)
                    for (x, y, w, h) in faces:
                        face_crop = gray[y:y + h, x:x + w]
                        Id, conf = recognizer.predict(face_crop)
                        if conf<100:
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                            aa = df.loc[df['Student_ID'] == Id]['Name'].values
                            aa = ''.join(str(e) for e in aa)
                            text = str(Id) + "-" + aa
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 3)
                            cv2.rectangle(frame, (x, y - 40), (x + w, y), (0,255,0), -1)
                            cv2.putText(frame, str(text), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                        (0,0,0), 2)
                            attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]
                            # attendance.drop_duplicates(['Name'], keep=False,inplace=True)
                        else:
                            text = 'Unknown'
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (51,51,255), 3)
                            cv2.rectangle(frame, (x, y - 40), (x + w, y), (51,51,255), -1)
                            cv2.putText(frame, str(text), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (255, 255, 255), 2)

                    # out.write(frame)
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    rgb = cv2.cvtColor(cv2image, cv2.COLOR_RGBA2RGB)
                    img = Image.fromarray(rgb)
                    img = img.resize((500,362),Image.ANTIALIAS)
                    imgtk = ImageTk.PhotoImage(image=img)
                    display4.imgtk = imgtk
                    display4.configure(image=imgtk)
                    display4.after(10, show_frame)
                # except Exception as e:
                #     print(e)
            show_frame()
            repn = Path('Attendance')
            if repn.is_dir():
                pass
            else:
                os.mkdir('Attendance')
        except Exception as e:
            print(e)
            nti = tk.Label(windo, text="Something went wrong....", width=22, height=1, fg="black", bg="yellow",
                           font=('times', 14, ' bold '))
            nti.place(x=280, y=247)
            windo.after(5000, destroy_widget, nti)
    else:
        nti = tk.Label(windo, text="Model Not Found..", width=22, height=1, fg="black", bg="yellow",
                       font=('times', 14, ' bold '))
        nti.place(x=280, y=247)
        windo.after(4000, destroy_widget, nti)

def destroyer():
    display4.destroy()
    imageFrame4.destroy()
    off.destroy()
    cam_break()

def destroyer1():
    ts = time.time()
    dat = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStam = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStam.split(":")
    fileN = "./Attendance/" + dat + "_" + Hour + "-" + Minute + "-" + Second + ".csv"
    attendance.drop_duplicates(['Name'], keep='first',inplace=True)
    print(attendance)
    attendance.to_csv(fileN, index=False)
    display4.destroy()
    imageFrame4.destroy()
    off.destroy()
    cam_break()
    csv_disp(fileN)

def cam_break():
    cap.release()

def model_training():
    qw12 = Path('TrainingImage')
    if qw12.is_dir():
        ic1 = tk.Label(windo, text="Model Trained..", width=13, height=1, fg="black", bg="yellow",
                       font=('times', 14, ' bold '))
        try:
            os.remove("./Trained_model/Model.yml")
        except:
            pass
        def getImagesAndLabels(path):
            detector = cv2.CascadeClassifier(cv2.haarcascades+'haarcascade_frontalface_default.xml')
            imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
            faceSamples = []
            Ids = []
            for imagePath in imagePaths:
                pilImage = Image.open(imagePath).convert('L')
                imageNp = np.array(pilImage, 'uint8')
                Id = int(os.path.split(imagePath)[-1].split(".")[1])
                faces = detector.detectMultiScale(imageNp)
                for (x, y, w, h) in faces:
                    faceSamples.append(imageNp[y:y + h, x:x + w])
                    Ids.append(Id)
            return faceSamples, Ids
        def gen_lab():
            ic1.configure(text="Model Trained..", width=13, height=1, fg="black", bg="yellow",
                           font=('times', 14, ' bold '))
            ic1.place(x=280, y=247)
            windo.after(4000, destroy_widget, ic1)

        def bar():
            import time
            progress['value'] = 20
            windo.update_idletasks()
            time.sleep(1)
            progress['value'] = 40
            windo.update_idletasks()
            time.sleep(1)
            progress['value'] = 60
            windo.update_idletasks()
            time.sleep(1)
            progress['value'] = 80
            windo.update_idletasks()
            time.sleep(1)
            progress['value'] = 100
            windo.update_idletasks()
            progress.destroy()
            windo.after(10, gen_lab)

        progress = Progressbar(windo, orient=HORIZONTAL, length=100, mode='determinate')
        progress.place(x=280, y=247)
        bar()
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        faces, Id = getImagesAndLabels("TrainingImage")
        qw = Path('Trained_model')
        if qw.is_dir():
            pass
        else:
            os.mkdir('Trained_model')
        recognizer.train(faces, np.array(Id))
        recognizer.save("./Trained_model/Model.yml")
        # windo.after(8000,destroy_widget,gif_play)
    else:
        i3 = tk.Label(windo, text="No Images found..", width=22, height=1, fg="black", bg="yellow",
                       font=('times', 14, ' bold '))
        i3.place(x=280, y=247)
        windo.after(4000, destroy_widget, i3)

def destroy_widget(widget):
    widget.destroy()
def breakcam():
    cam.release()

def csv_disp(csv_file):
    try:
        destroyer()
    except:
        pass
    dir2 = Path('RegisteredStudents')
    if dir2.is_dir():
        try:
            global scrollbarx,scrollbary,TableMargin,tree,my_nam,des
            TableMargin = Frame(windo, width=100, height=100)
            TableMargin.place(x=690, y=51)
            scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
            scrollbary = Scrollbar(TableMargin, orient=VERTICAL)
            tree = ttk.Treeview(TableMargin, columns=("Student_ID", "Name", "Date", 'Registration Time'), height=100,
                                selectmode="extended",
                                yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
            scrollbary.config(command=tree.yview)
            scrollbary.pack(side=RIGHT, fill=Y)
            scrollbarx.config(command=tree.xview)
            scrollbarx.pack(side=BOTTOM, fill=X)
            tree.heading('Student_ID', text="Student_ID", anchor=W)
            tree.heading('Name', text="Name", anchor=W)
            tree.heading('Date', text="Date", anchor=W)
            tree.heading('Registration Time', text="Time", anchor=W)
            tree.column('#0', stretch=NO, minwidth=0, width=0)
            tree.column('#1', stretch=NO, minwidth=0, width=120)
            tree.column('#2', stretch=NO, minwidth=0, width=120)
            tree.column('#3', stretch=NO, minwidth=0, width=120)
            tree.column('#3', stretch=NO, minwidth=0, width=120)
            tree.pack()
            with open(csv_file) as f:
                reader = csv.DictReader(f, delimiter=',')
                for row in reader:
                    emp_id = row['Student_ID']
                    name = row['Name']
                    dt = row['Date']
                    ti = row['Registration Time']
                    tree.insert("", 0, values=(emp_id, name, dt, ti), tags=('oddrow',))
                    tree.tag_configure('oddrow', background='midnightblue', foreground='white', font=('times', 14, ' bold '))
            my_nam = tk.Label(windo, text="©Developed by Aditi,Priyanka,Sapna",bg="midnightblue", fg="white", width=67,
                              height=1, font=('times', 30, 'italic bold '))
            my_nam.place(x=0, y=780)

            des = tk.Button(windo, text='Close', command=csv_destroyer, bg="yellow", fg="black",
                             height=1, font=('times', 13, 'bold '), activebackground='red')
            des.place(x=690, y=607)
        except Exception as e:
            print(e)
    else:
        i1 = tk.Label(windo, text="No Data Found..", width=13, height=1, fg="black", bg="yellow",
                       font=('times', 14, ' bold '))
        i1.place(x=280,y=247)
        windo.after(5000, destroy_widget, i1)


def csv_destroyer():
    try:
        cam_break()
    except:
        pass
    scrollbarx.destroy()
    scrollbary.destroy()
    TableMargin.destroy()
    tree.destroy()
    my_nam.destroy()
    des.destroy()

def admin_panel():
    csv_disp('./RegisteredStudents/RegisteredStudents.csv')

sad_img = ImageTk.PhotoImage(Image.open("./images/t1.jpg"))
panel4 = Label(windo, image=sad_img)
panel4.pack()
panel4.place(x=0, y=50)

id_l = tk.Label(windo, text="Enter ID", width=13, height=1, fg="white", bg="midnightblue", font=('times', 14, ' bold '))
id_l.place(x=280, y=98)

def limitSizeid(*args):
    value = idValue.get()
    if len(value) > 8: idValue.set(value[:8])

idValue = StringVar()
idValue.trace('w', limitSizeid)

def limitSizename(*args):
    value1 = nameValue.get()
    if len(value1) > 12: nameValue.set(value1[:12])

nameValue = StringVar()
nameValue.trace('w', limitSizename)

def clear_id():
    id_txt.delete(first=0,last = 10)

def clear_name():
    name_txt.delete(first=0,last = 15)

id_txt = tk.Entry(windo, width=13, bg="white", fg="black", font=('times', 22, ' bold '), textvariable=idValue)
id_txt.place(x=280, y=125)

name_l = tk.Label(windo, text="Enter Name", width=13, height=1, fg="white", bg="midnightblue", font=('times', 14, ' bold '))
name_l.place(x=280, y=175)

name_txt = tk.Entry(windo, width=13, bg="white", fg="black", font=('times', 22, ' bold '), textvariable=nameValue)
name_txt.place(x=280, y=202)

clearButton = tk.Button(windo, command = clear_id,text="Clear",fg="white"  ,bg="midnightblue"  ,width=5  ,height=1 ,activebackground = "yellow" ,font=('times', 12, ' bold '))
clearButton.place(x=490, y=127)

clearButton1 = tk.Button(windo,command = clear_name, text="Clear",fg="white"  ,bg="midnightblue"  ,width=5 ,height=1, activebackground = "yellow" ,font=('times', 12, ' bold '))
clearButton1.place(x=490, y=204)

def open_fd():
    subprocess.Popen(r'explorer /select,"TrainingImage"')

cm = tk.Button(windo,command = open_fd, text="Check Face\ud83d\ude00 Images",fg="white"  ,bg="midnightblue"  ,width=18 ,height=1, activebackground = "yellow" ,font=('times', 18, ' bold '))
cm.place(x=280, y=290)

cd = tk.Button(windo, text="Registered Students",command = admin_panel,fg="white"  ,bg="midnightblue"  ,width=18 ,height=1, activebackground = "yellow" ,font=('times', 18, ' bold '))
cd.place(x=280, y=350)

my_name = tk.Label(windo, text="©Developed by Aditi,Priyanka,Sapna ", bg="midnightblue", fg="white", width=67,
                   height=1, font=('times', 30, 'italic bold '))
my_name.place(x=0, y=780)

start = tk.Label(windo, text="Student Attendance using Face\ud83d\ude00 Recognition", bg="midnightblue", fg="white", width=68,
                   height=1, font=('times', 30, 'italic bold '))
start.place(x=0, y=0)

start1 = tk.Label(windo, text="Enter your Face\ud83d\ude00 Data if you are a new user!", bg="yellow", fg="black", width=35,
                   height=1, font=('times', 20, 'bold '))
start1.place(x=0, y=50)

def tick():
    global time1
    time2 = time.strftime('%H:%M:%S')
    if time2 != time1:
        time1 = time2
        clock.config(text=time1)
    clock.after(200, tick)

time1 = ''
clock = Label(windo, font=('times', 20, 'bold'), bg='white')
clock.place(x=1390, y = 7)
tick()

def res_sys():
    try:
        sql_delete = "DROP TABLE reg_students"
        cursor.execute(sql_delete)
        connection.commit()
        shutil.rmtree('RegisteredStudents')
        shutil.rmtree('Trained_model')
        shutil.rmtree('TrainingImage')
        shutil.rmtree('Attendance')
    except Exception as e:
        print(e)

res = Button(windo,text = 'Reset',command = on_closing, width = 13,height = 1, font=('times', 13, 'bold'), bg='white')
res.place(x=10, y = 9)

sg = PhotoImage(file = "./images/cartoon.png")
sg_f = tk.Button(windo, borderwidth=0, image = sg,bg = 'white',command = image_generate )
sg_f.place(x=50, y=480)

ca = tk.Label(windo, text="Generate Faces", bg="midnightblue", fg="white", width=11,
                   height=1, font=('times', 16, 'italic bold '))
ca.place(x=48, y=590)

tm = PhotoImage(file = "./images/train.png")
t_m = tk.Button(windo,borderwidth=0,bg = 'white',image = tm,command = model_training)
t_m.place(x=250, y=480)

tb = tk.Label(windo, text="Train Model", bg="midnightblue", fg="white", width=11,
                   height=1, font=('times', 16, 'italic bold '))
tb.place(x=248, y=587)

tm1 = PhotoImage(file='./images/at.png')
t_m1 = tk.Button(windo,borderwidth=0,bg = 'white',image = tm1,command = fill_att)
t_m1.place(x=413, y=480)

tb1 = tk.Label(windo, text="Fill Attendance", bg="deeppink", fg="white", width=11,
                   height=1, font=('times', 16, 'italic bold '))
tb1.place(x=448, y=587)

windo.mainloop()