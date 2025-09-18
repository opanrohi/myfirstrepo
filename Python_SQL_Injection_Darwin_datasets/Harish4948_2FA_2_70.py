import pymysql
from tkinter import *
from PIL import Image,ImageTk
import imutils
import cv2, sys, numpy, os

def display():

    def dis():
        listbox1.delete(0, END)
        listbox2.delete(0, END)
        listbox3.delete(0, END)
        sec1 = sec.get()
        connection = pymysql.connect(host='localhost', user='root', password='', db='class')
        cm = connection.cursor()
        try:
            cm.execute("select regno from " + sec1)
            oo = cm.fetchall()
            for item in oo:
                listbox1.insert(END, item)
            cm.execute("select Name from " + sec1)
            oo = cm.fetchall()
            for item in oo:
                listbox2.insert(END, item)
            cm.execute("select attendence from " + sec1)
            oo = cm.fetchall()
            for item in oo:
                listbox3.insert(END, item)
            dt.config(text="Successful", bg="GREEN", fg="Dark GREEN")
        except:
            dt.config(text="Error", fg="RED", font="20")
        finally:
            cm.close()


    def OnVsb(*args):
        listbox1.yview(*args)
        listbox2.yview(*args)
        listbox3.yview(*args)
        listbox4.yview(*args)
        listbox5.yview(*args)
        listbox6.yview(*args)
        listbox7.yview(*args)
        listbox8.yview(*args)

    def OnMouseWheel(event):
        listbox1.yview("scroll", (event.delta - 100), "units")
        listbox2.yview("scroll", (event.delta - 100), "units")
        listbox3.yview("scroll", (event.delta - 100), "units")
        listbox4.yview("scroll", (event.delta - 100), "units")
        listbox5.yview("scroll", (event.delta - 100), "units")
        listbox6.yview("scroll", (event.delta - 100), "units")
        listbox7.yview("scroll", (event.delta - 100), "units")
        listbox8.yview("scroll", (event.delta - 100), "units")
        return "break"


    global R3
    R2.destroy()
    R3 = Tk()
    R3.title("")
    R3.geometry("1280x720")
    R3.config(bg="#436501")
    R3.resizable(width=FALSE, height=FALSE)
    Image_open = Image.open("login.jpg")
    image = ImageTk.PhotoImage(Image_open)
    logo = Label(R3, image=image, bg=gg)
    logo.place(x=0, y=0, bordermode="outside")
    listbox1 = Listbox(R3, width=7, borderwidth=0, highlightthickness=0, selectbackground="#436501", height=30, bg="#436501", fg=gw,
                       font="10")
    listbox1.bind("<MouseWheel>", OnMouseWheel)
    listbox1.place(x=17, y=145)

    listbox2 = Listbox(R3, width=7, height=30, highlightthickness=0, bg="#436501", borderwidth=0, selectbackground="#436501", fg=gw,
                       font="10")
    listbox2.bind("<MouseWheel>", OnMouseWheel)
    listbox2.place(x=145, y=145)

    listbox3 = Listbox(R3, width=20, borderwidth=0, height=30, bg="#436501", selectbackground="#436501", fg=gw, font="10",
                       highlightthickness=0)
    listbox3.bind("<MouseWheel>", OnMouseWheel)
    listbox3.place(x=270, y=145)
    c1=Label(text="Class",bg="#436501", fg="white")
    c1.place(x=426,y=73)
    sec=StringVar()
    ce1=Entry(textvariable=sec)
    ce1.place(x=611 ,y=73)
    c2=Label(text="Name",bg="#436501", fg="white")
    c2.place(x=29,y=123)
    c3 = Label(text="Regno no", bg="#436501", fg="white")
    c3.place(x=159, y=124)
    c4 = Label(text="Attandence perc", bg="#436501", fg="white")
    c4.place(x=270 ,y=123)
    cb2=Button(text="Display",bg="#436501", fg="white",command=dis)
    cb2.place(x=821 ,y=73)
    def home():
        R3.destroy()
        postlogin()

    cb3 = Button(text="Home", bg="#436501", fg="white", command=home)
    cb3.place(x=891, y=73)
    dt = Label(R3, font="10", bg=g)
    dt.place(x=940, y=660)
    R3.mainloop()


def news():
    def inr():
        classname=sec.get()
        stu = name.get()
        re1 = regno.get()
        at = att.get()
        connection = pymysql.connect(host='localhost', user='root', password='', db='class')
        cursor = connection.cursor()
        q = ("insert into "+str(classname)+" values(%s,%s,%s)")
        values=[stu,re1,at]
        try:
            cursor.execute(q,values)
            connection.commit()
            st.config(text="Successful",bg="GREEN",fg="Dark GREEN")
        except:
            st.config(text="Error",fg="RED",font="20")
        finally:
            connection.close()

    R2.destroy()
    R5=Tk()
    R5.title("New Class")
    R5.geometry("1280x720")
    R5.config(bg="#436501")
    R5.resizable(width=FALSE, height=FALSE)
    Image_open = Image.open("login.jpg")
    image = ImageTk.PhotoImage(Image_open)
    logo = Label(R5, image=image, bg=gg)
    logo.place(x=0, y=0, bordermode="outside")
    l0=Label(R5,text="Class",bg="#436501", fg="white")
    l0.place(x=15,y=5)
    sec = StringVar()
    name = StringVar()
    regno = StringVar()
    att = StringVar()
    e1=Entry(R5,textvariable=sec)
    e1.place(x=200,y=5)
    l1=Label(R5,text="Name",bg="#436501", fg="white")
    l1.place(x=15,y=70)
    e2=Entry(R5, textvariable=name)
    e2.place(x=200,y=70)
    l2=Label(R5, text="Regno",bg="#436501", fg="white")
    l2.place(x=15,y=120)
    e3=Entry(R5, textvariable=regno)
    e3.place(x=200,y=120)
    l4=Label(R5, text="Attendance",bg="#436501", fg="white")
    l4.place(x=15,y=170)
    st = Label(R5, font="10", bg=g)
    st.place(x=940, y=660)
    e4=Entry(R5, textvariable=att)
    e4.place(x=200,y=170)
    b1=Button(R5,text="Submit",bg="black",fg="silver",command=inr)
    b1.place(x=200,y=200)

    def home():
        R5.destroy()
        postlogin()

    b2=Button(R5, text="Home",bg="black",fg="silver",command=home)
    b2.place(x=200,y=230)
    R5.mainloop()

def newc():
    def inr1():
        var1 = var.get()
        connection = pymysql.connect(host='localhost', user='root', password='', db='class')
        cursor = connection.cursor()
        q = ("create table " + str(var1) + "(Name text,regno int,attendence text, PRIMARY KEY(regno))")
        try:
            cursor.execute(q)
            connection.commit()
            l.config(text="Successful",bg="GREEN",fg="Dark GREEN")
        except:
            l.config(text="Error",fg="RED",font="20")
        finally:
            connection.close()
    global R4
    R2.destroy()
    R4=Tk()
    R4.title("New Class")
    R4.geometry("1280x720")
    R4.config(bg="#436501")
    R4.resizable(width=FALSE, height=FALSE)

    Image_open = Image.open("login.jpg")
    image = ImageTk.PhotoImage(Image_open)
    logo = Label(R4, image=image, bg=gg)
    logo.place(x=0, y=0, bordermode="outside")

    l3 = Label(R4, text="Enter the name of the class",bg="#436501", fg="white")
    l3.place(x=174,y=318)
    var = StringVar()
    ec = Entry(R4, textvariable=var)
    ec.place(x=423,y=318)
    eb = Button(R4, text="Create", bg="black", fg="silver", command=inr1)
    eb.place(x=400,y=520)
    eb1 = Button(R4, text="quit", bg="black", fg="silver", command=quit)
    eb1.place(x=500,y=520)
    def home():
        R4.destroy()
        postlogin()
    sb2 = Button(R4, text="Home", bg="black", fg="silver", command=home)
    sb2.place(x=600,y=520)
    l = Label(R4, font="10", bg=g)
    l.place(x=940, y=660)
    R4.mainloop()
def postlogin():
    global R2
    R2 = Tk()
    R2.title("SELECT")
    R2.geometry("1280x720")
    R2.config(bg=gg)
    Image_open = Image.open("Login.jpg")
    image = ImageTk.PhotoImage(Image_open)
    logo = Label(R2, image=image, bg=gg)
    logo.place(x=0, y=0, bordermode="outside")

    b1 = Button(R2, text="STUDENT Details", width=48, height=10, bg="#436501", fg="white", font="5", relief=FLAT,
                overrelief=RIDGE, borderwidth='5', activebackground=gw,command=display)
    b1.place(x=100, y=74)
    b1 = Button(R2, text="Create Class", width=48, height=10, bg="#436501", fg="white", font="5", relief=FLAT, overrelief=RIDGE,
                borderwidth='5', activebackground=gw,command=newc)
    b1.place(x=100, y=374)
    b1 = Button(R2, text="NEW Student", width=48, height=10, bg="#436501", fg="white", font="5", relief=FLAT,
                overrelief=RIDGE, borderwidth='5', activebackground=gw,command=news)
    b1.place(x=730, y=74)
    b1 = Button(R2, text="quit", width=48, height=10, bg="#436501", fg="white", font="5", relief=FLAT,
                overrelief=RIDGE, borderwidth='5', activebackground=gw,command=quit)
    b1.place(x=730, y=374)

    b1 = Button(R2, text="Logout", width=5, bg="#436501", fg="white", command=R2.destroy)
    b1.place(x=1210, y=20)
    R2.mainloop()

def face():
    size = 4
    haar_file = 'cascades/data/haarcascade_frontalface_default.xml'
    datasets = 'datasets'

    # Part 1: Create fisherRecognizer
    print('Training...')
    # Create a list of images and a list of corresponding names
    (images, labels, names, id) = ([], [], {}, 0)
    for (subdirs, dirs, files) in os.walk(datasets):
        for subdir in dirs:
            names[id] = subdir
            subjectpath = os.path.join(datasets, subdir)
            for filename in os.listdir(subjectpath):
                path = subjectpath + '/' + filename
                label = id
                images.append(cv2.imread(path, 0))
                labels.append(int(label))
            id += 1
    (width, height) = (130, 100)

    # Create a Numpy array from the two lists above
    [images, labels] = [numpy.array(lis) for lis in [images, labels]]

    # OpenCV trains a model from the images
    # NOTE FOR OpenCV2: remove '.face'
    model = cv2.face.FisherFaceRecognizer_create()
    model.train(images, labels)
    # Part 2: Use fisherRecognizer on camera stream
    face_cascade = cv2.CascadeClassifier(haar_file)
    webcam = cv2.VideoCapture(0)
    while (1 == 1):
        (_, im) = webcam.read()
        im = imutils.resize(im, width=200)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 255, 0), 2)
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (width, height))
            # Try to recognize the face
            prediction = model.predict(face_resize)
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3)
            if prediction[1] < 50:
                cv2.putText(im, '%s - %.0f' % (names[prediction[0]], prediction[1]), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
                print(names[prediction[0]])
                postlogin()
            else:
                cv2.putText(im, 'Scanning', (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
        cv2.imshow('OpenCV', im)
        key = cv2.waitKey(10)
        if key == 27:
            break


def login():
    def final():
        usr = user.get()
        pas = password.get()
        connection = pymysql.connect(host='localhost', user='root', password='', db='login')
        cursor = connection.cursor()
        q = ("select username from user where username=%s")
        q1 = ("select pass from user where pass=%s")
        if cursor.execute(q, usr) and cursor.execute(q1, pas):
            R1.destroy()
            face()
        else:
            Label(R1,text="INVALID USERNAME or PASSWORD",bg="red",fg=gw).place(x=680,y=650)
        connection.commit()
        connection.close()

    R1=Tk()
    R1.resizable(width=False,height=False)
    R1.geometry('1280x720')
    R1.title("Login")
    R1.configure(background=g)
    Image_open = Image.open("Login.jpg")
    image = ImageTk.PhotoImage(Image_open)
    logo = Label(R1, image=image, bg=g)
    logo.place(x=0, y=0, bordermode="outside")
    L1 = Label(R1, text="Username", width=10, bg="#436501", fg=gw, font=("bold", 20))
    L1.place(x=680,y=380)
    L2 = Label(R1, text="Password", width=10, bg="#436501", fg=gw, font=("bold", 20))
    L2.place(x=680,y=450)
    user = StringVar()
    password = StringVar()
    e1=Entry(R1,width=20,font=("bold",15),textvariable=user)
    e1.place(x=850,y=385)
    e2 = Entry(R1,show="*", width=20, font=("bold", 15), textvariable=password)
    e2.place(x=850,y=455)
    b1=Button(R1,text="Login",width=25,height=2,bg="#436501",fg="white",font="5",relief=RAISED,overrelief=RIDGE,command=final)
    b1.place(x=850,y=510)
    R1.mainloop()

gg = '#134e86'  # secondary color
g = "#0a2845#"  # color

gw = "white"
login()
#postlogin()
