###Szükséges összetevők importálása
import os, cv2, time, threading, psutil
import platform
import ingredients.definitions as df
import numpy as np
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import tkinter.ttk as ttk
#--------------------------------------------------------

### Aktuális process adatok
current_process_pid = psutil.Process().pid
p = psutil.Process(current_process_pid)
cpu_count = psutil.cpu_count()

###Grafikus felhasználói felület (GUI)
window = Tk()
screen_w = window.winfo_screenwidth()
screen_h = window.winfo_screenheight()
x = screen_w / 2 - 768
y = screen_h / 2 - 432
window.geometry(f'{1536}x{864}+{int(x)}+{int(y)}')
window.title("Távoság meghatározás")
window.iconbitmap(os.getcwd()+'/icon/app.ico')
window.config(background="#FFFFFF")

cam_icon = PhotoImage(file = os.getcwd()+'/icon/kamera.png')
video_icon = PhotoImage(file = os.getcwd()+'/icon/video.png')
photo_icon = PhotoImage(file = os.getcwd()+'/icon/file_jpg.png')
stop_icon = PhotoImage(file = os.getcwd()+'/icon/stop.png')
pause_icon = PhotoImage(file = os.getcwd()+'/icon/pause.png')

AblakKeret = Frame(window, width=640, height=480)
AblakKeret.grid(row=0, column=0, padx=5, pady=5)

AblakKeret = Label(AblakKeret)
AblakKeret.grid(row=10, column=10)
#--------------------------------------------------------

###Global változók definiálása
filter = 0
approx = 0
brightness = 0
contrast = 1
cpu_val = 0
mem_val = 0
kvw = ''
exit = False
k = os.listdir("images")
kx=0
camera =""
pause=1
stop = FALSE
Minta_tavolsag = 0
Minta_szelesseg = 29.7
focalLength = 0
#--------------------------------------------------------

###Videó és webkamerakép feldolgozás
def VideoCapture():
    global camera
    global Minta_tavolsag
    global Minta_szelesseg
    global focalLength
    global stop
    global távLab
    cm = 0
    global kvw
    global pause
    if(camera.isOpened()) and pause:
        #Video/kamera olvasása
        ret, frame = camera.read()
        if not ret:
            Stopbuttoncmd()
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            contrast = ContrastScaler.get()
            brightness = BrightnessScaler.get()
            frame[:,:,2] = np.clip(contrast * frame[:,:,2] + brightness, 0, 255)
            frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
            
            c2 = df.konturkeres(frame, filter, approx)
            if c2!=0:
                i=0
                for cIdx in c2:
                    marker = cv2.minAreaRect(cIdx)
                    if marker[1][0]!=0:
                        if marker[1][0] < marker[1][1]:
                            marker=(marker[0][0],marker[0][1]),(marker[1][1],marker[1][0]),(90+marker[2])
                        cm = df.tavolsag(Minta_szelesseg, focalLength, marker[1][0]) #A távolság kiszámítás
                        if cm<4000: #Csak a 4 méternél közelebbi kontúrral foglalkozunk
                            i=i+1
                            #A megtalált kontúr kirajzolása
                            box = cv2.boxPoints(marker)
                            box = np.int0(box)
                            cv2.drawContours(frame, [box], -1, (0, 255, 0), 2)
                            
                            #A kiszámított távolság meghatározása és kiírása
                            l=0
                            for label in TávolságokKeret.grid_slaves():
                                l=l+1
                                if l == i:
                                    TávolságokKeret.grid_slaves()[29-i].configure(text="%.0f" % (i) + ": %.2fcm" % (cm))
                                elif l > i:
                                    TávolságokKeret.grid_slaves()[29-l].configure(text="")
                                elif l < i:
                                    TávolságokKeret.grid_slaves()[29-i].configure(text="%.0f" % (i) + ": %.2fcm" % (cm))

                            #Az azonosított objektumok számozása
                            tm=cv2.getTextSize("%.0f" % (i), cv2.FONT_HERSHEY_COMPLEX, int(marker[1][0])/100, 3)[0]
                            text_location=int(marker[0][0]-(tm[0])/2), int(marker[0][1]+(tm[1])/2)
                            cv2.putText(frame, "%.0f" % (i),
                                        text_location, cv2.FONT_HERSHEY_COMPLEX, int(marker[1][0])/100, (0, 0, 0), 3)
                    else:
                        l=0
                        for label in TávolságokKeret.grid_slaves():
                            l=l+1
                            if l > 1:
                                TávolságokKeret.grid_slaves()[29-l].configure(text="")
                            elif l == 1:
                                TávolságokKeret.grid_slaves()[29-l].configure(text="Not detekted")
            else:
                l=0
                for label in TávolságokKeret.grid_slaves():
                    l=l+1
                    if l > 1:
                        TávolságokKeret.grid_slaves()[29-l].configure(text="")
                    elif l == 1:
                        TávolságokKeret.grid_slaves()[29-l].configure(text="Not detekted")
            #Átméretezés
            if camera.get(cv2.CAP_PROP_FRAME_WIDTH) < camera.get(cv2.CAP_PROP_FRAME_HEIGHT):
                resize = cv2.resize(frame, (600,800))
            else:
                resize = cv2.resize(frame, (800,600))
            #Mejelenítéshez színkonverzió
            color = cv2.cvtColor(resize, cv2.COLOR_BGR2RGBA)
        
            #Videó megjelenítése
            img = Image.fromarray(color)
            imgtk = ImageTk.PhotoImage(image=img)
            kijelző1.imgtk = imgtk
            kijelző1.configure(image=imgtk)
    if not stop:
        if pause:
            window.after(5, VideoCapture)
    else:
        kijelző1.configure(image='')
    cv2.destroyAllWindows()

###Képek feldolgozása
def Kepek():
    global Minta_tavolsag
    global Minta_szelesseg
    global focalLength
    global stop
    global távLab
    global k
    global kx
    global pause
    cm = 0
    if kx == len(k) or stop:
        Stopbuttoncmd()
    elif k!=0 and pause:
        image = cv2.imread("images/" + k[kx])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        contrast = ContrastScaler.get()
        brightness = BrightnessScaler.get()
        image[:,:,2] = np.clip(contrast * image[:,:,2] + brightness, 0, 255)
        image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)

        c2 = df.konturkeres(image, filter, approx) #A kontúr keresés a betöltött képen
        if c2!=0: #Ha van talált kontúr
            i=0
            for cIdx in c2:
                marker = cv2.minAreaRect(cIdx)
                if marker[1][0]!=0:
                    if marker[1][0] < marker[1][1]: #Ha a mintaképtől eltérő pozíciójú képet kapunk, akkor megcseréljük a szélesség és hosszúság adatokat a későbbi helyes számítás miatt
                        marker=(marker[0][0],marker[0][1]),(marker[1][1],marker[1][0]),(90+marker[2])
                    
                    cm = df.tavolsag(Minta_szelesseg, focalLength, marker[1][0]) #A távolság kiszámítása
                    if cm<400: #Csak a 4 méternél közelebbi kontúrral foglalkozunk
                        i=i+1
                        
                        #A megtalált kontúr kirajzolása
                        box = cv2.boxPoints(marker)
                        box = np.int0(box)
                        cv2.drawContours(image, [box], -1, (0, 255, 0), 5)
                        #A kiszámított távolság meghatározása és kiírása
                        l=0
                        for label in TávolságokKeret.grid_slaves():
                            l=l+1
                            if l == i:
                                TávolságokKeret.grid_slaves()[29-i].configure(text="%.0f" % (i) + ": %.2fcm" % (cm))
                            elif l > i:
                                TávolságokKeret.grid_slaves()[29-l].configure(text="")
                            elif l < i:
                                TávolságokKeret.grid_slaves()[29-i].configure(text="%.0f" % (i) + ": %.2fcm" % (cm))
                        #Az azonosított objektumok számozása
                        tm=cv2.getTextSize("%.0f" % (i), cv2.FONT_HERSHEY_COMPLEX, int(marker[1][0])/100, 5)[0]
                        text_location=int(marker[0][0]-(tm[0])/2), int(marker[0][1]+(tm[1])/2)
                        cv2.putText(image, "%.0f" % (i),
                                    text_location, cv2.FONT_HERSHEY_COMPLEX, int(marker[1][0])/100, (0, 0, 0), 5)

                else:
                    l=0
                    for label in TávolságokKeret.grid_slaves():
                        l=l+1
                        if l > 1:
                            TávolságokKeret.grid_slaves()[29-l].configure(text="")
                        elif l == 1:
                            TávolságokKeret.grid_slaves()[29-l].configure(text="Not detekted")
        else:
            l=0
            for label in TávolságokKeret.grid_slaves():
                l=l+1
                if l > 1:
                    TávolságokKeret.grid_slaves()[29-l].configure(text="")
                elif l == 1:
                    TávolságokKeret.grid_slaves()[29-l].configure(text="Not detekted")

        #A kép átméretezése és megjelenítése
        resize = cv2.resize(image, (480,640))
        color = cv2.cvtColor(resize, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(color)
        imgtk = ImageTk.PhotoImage(image=img)
        kijelző1.imgtk = imgtk
        kijelző1.configure(image=imgtk)
    if not stop:
            cv2.destroyWindow(k[kx])
            kx=kx+1
            if pause:
                window.after(2000, Kepek)
    else:
            kx=0
            kijelző1.configure(image='')
    cv2.destroyAllWindows()

###Parancs definíciók
def bilateralFiltercmd():
    global filter
    filter = 1
    bilateralFilterbutton.configure ( bg ='light blue')
    GaussianBlurbutton.configure ( bg = window.cget('bg'))

def GaussianBlurcmd():
    global filter
    filter = 0
    GaussianBlurbutton.configure ( bg ='light blue')
    bilateralFilterbutton.configure ( bg = window.cget('bg'))

def ApproxSIMPLEcmd():
    global approx
    approx = 1
    ApproxSIMPLEbutton.configure ( bg ='light blue')
    ApproxNONEbutton.configure ( bg = window.cget('bg'))

def ApproxNONEcmd():
    global approx
    approx = 0
    ApproxNONEbutton.configure ( bg ='light blue')
    ApproxSIMPLEbutton.configure ( bg = window.cget('bg'))

def Képekbuttoncmd():
    global kvw
    global stop
    stop = FALSE
    kvw = 'k'
    kx=0,
    Kamerabutton.configure ( state = DISABLED)
    Videóbutton.configure ( state = DISABLED)
    Képekbutton.configure ( state = DISABLED)
    Stopbutton.configure ( state = NORMAL)
    Pausebutton.configure ( state = NORMAL)
    if not t1._started._flag:
        t1.start()
    else:
        t_video()

def Videóbuttoncmd():
    global kvw
    global stop
    stop = FALSE
    kvw = 'v'
    Kamerabutton.configure ( state = DISABLED)
    Videóbutton.configure ( state = DISABLED)
    Képekbutton.configure ( state = DISABLED)
    Stopbutton.configure ( state = NORMAL)
    Pausebutton.configure ( state = NORMAL)
    if not t1._started._flag:
        t1.start()
    else:
        t_video()

def Kamerabuttoncmd():
    global kvw
    global stop
    stop = FALSE
    kvw = 'w'
    Kamerabutton.configure ( state = DISABLED)
    Videóbutton.configure ( state = DISABLED)
    Képekbutton.configure ( state = DISABLED)
    Stopbutton.configure ( state = NORMAL)
    Pausebutton.configure ( state = NORMAL)
    if not t1._started._flag:
        t1.start()
    else:
        t_video()


def Stopbuttoncmd():
    global kvw
    global stop
    global kx
    global camera
    stop = TRUE
    kx=0
    kijelző1.configure(image='')
    if kvw !='k':
        cv2.destroyAllWindows();
        camera.release()
    if not pause:
        Pausebuttoncmd()
    l=0
    for label in TávolságokKeret.grid_slaves():
       l=l+1
       TávolságokKeret.grid_slaves()[29-l].configure(text="")
    Kamerabutton.configure ( state = NORMAL)
    Videóbutton.configure ( state = NORMAL)
    Képekbutton.configure ( state = NORMAL)
    Stopbutton.configure ( state = DISABLED)
    Pausebutton.configure ( state = DISABLED)

def Pausebuttoncmd():
    global pause
    if pause == 0:
        pause = 1
        if kvw !='k':
            window.after(5, VideoCapture)
        else:
            window.after(200, Kepek)
        Pausebutton.configure(text=" Szünet")
    else:
        pause = 0
        Pi=stop_icon.subsample(1,1)
        Pausebutton.configure(text=" Elindít")

def Beállításokalaphelyzetcmd():
    BrightnessScaler.set(0)
    ContrastScaler.set(1)

###GUI további elemei
TávolságokKeret = LabelFrame(AblakKeret, text='Távolságok', font = "Consolas 11 bold")
TávolságokKeret.grid(row=0, column=0, rowspan=10, ipadx=5, ipady=5, sticky='nesw')
for i in range(28):
    távLab = Label(TávolságokKeret, text='', font = "Consolas 12 bold")
    távLab.grid(row=i+1, column=0, sticky=EW)

üressor0 = Label(TávolságokKeret).grid(row=0, column=0, padx=60, pady=5, sticky='w')
	
### KameraKeret
KameraKeret = LabelFrame(AblakKeret, width=1152, height=680)
KameraKeret.grid(row=2, column=1, rowspan=8, padx=5, pady=5, columnspan=5)
KameraKeretElölnézet = tk.Frame(KameraKeret, width=1152, height=680)
KameraKeretElölnézet.grid(padx=5, pady=5, sticky='nesw')
KameraKeretElölnézet.grid_propagate(0)
kijelző1 = tk.Label(KameraKeretElölnézet)
kijelző1.grid(row=0, column=0, sticky='nesw')
kijelző1.place(in_=KameraKeretElölnézet, anchor="c", relx=.5, rely=.5)

Képekbuttonimage=photo_icon.subsample(1,1)
### Képek
Képekbutton = Button(AblakKeret, width=16, height=70, text=' Képek', image= Képekbuttonimage, compound = LEFT, font = "Consolas 14", command = Képekbuttoncmd, borderwidt=4)
Képekbutton.grid(row=0, column=1, rowspan=2, padx=20, pady=2, sticky='nesw')

Videóbuttonimage=video_icon.subsample(1,1)
### Videó
Videóbutton = Button(AblakKeret, width=16, height=70, text=' Videó', image= Videóbuttonimage, compound = LEFT, font = "Consolas 14", command = Videóbuttoncmd, borderwidt=4)
Videóbutton.grid(row=0, column=2, rowspan=2, padx=20, pady=2, sticky='nesw')

Kamerabuttonimage=cam_icon.subsample(1,1)
### Webkamera
Kamerabutton = Button(AblakKeret, width=16, height=70, text=' Webkamera', image= Kamerabuttonimage, compound = LEFT, font = "Consolas 14", command = Kamerabuttoncmd, borderwidt=4)
Kamerabutton.grid(row=0, column=3, rowspan=2, padx=20, pady=2, sticky='nesw')

Pausebuttonimage=pause_icon.subsample(1,1)
### Stop
Pausebutton = Button(AblakKeret, width=16, height=70, text=' Szünet', image= Pausebuttonimage, compound = LEFT, font = "Consolas 14", command = Pausebuttoncmd, state=DISABLED, borderwidt=4)
Pausebutton.grid(row=0, column=4, rowspan=2, padx=20, pady=2, sticky='nesw')

Stopbuttonimage=stop_icon.subsample(1,1)
### Stop
Stopbutton = Button(AblakKeret, width=16, height=70, text=' Leállítás', image= Stopbuttonimage, compound = LEFT, font = "Consolas 14", command = Stopbuttoncmd, state=DISABLED, borderwidt=4)
Stopbutton.grid(row=0, column=5, rowspan=2, padx=20, pady=2, sticky='nesw')

###Beállítások és tesztek kerete
BeállításTesztKeret = LabelFrame(AblakKeret, text='Beállítások/Tesztek', font = "Consolas 11 bold")
BeállításTesztKeret.grid(row=0, column=6, rowspan=10, ipadx=5, ipady=5, sticky='nw')

üressor = Label(BeállításTesztKeret).grid(row=1, column=0, sticky='we')

###SZűrőKeret
SZűrőKeret = LabelFrame(BeállításTesztKeret, text='Szűrő teszt', font = "Consolas 10 bold")
SZűrőKeret.grid(row=2, column=0 ,sticky='nesw', ipadx=5, ipady=5, columnspan=2)
### GaussianBlurbutton
GaussianBlurbutton = Button(SZűrőKeret, width=15, height=2, text='GaussianBlur', font = "Consolas 10", bg ='light blue', command = GaussianBlurcmd)
GaussianBlurbutton.grid(row=1, column=0, columnspan=2, padx=30, pady=5, sticky='nesw')
### bilateralFilterbutton
bilateralFilterbutton = Button(SZűrőKeret, width=15, height=2, text='bilateralFilter', font = "Consolas 10", command = bilateralFiltercmd)
bilateralFilterbutton.grid(row=2, column=0, columnspan=2, padx=30, pady=5, sticky='nesw')

üressor = Label(BeállításTesztKeret).grid(row=3, column=0, sticky='we')

###ApproxKeret
ApproxKeret = LabelFrame(BeállításTesztKeret, text='Kontúr teszt (Approx)', font = "Consolas 10 bold")
ApproxKeret.grid(row=4, column=0 ,sticky='nesw', ipadx=5, ipady=5, columnspan=2)
### ApproxNONEbutton
ApproxNONEbutton = Button(ApproxKeret, width=15, height=2, text='NONE', font = "Consolas 10", command = ApproxNONEcmd)
ApproxNONEbutton.grid(row=2, column=0, columnspan=2, padx=30, pady=5, sticky='nesw')
### ApproxSIMPLEbutton
ApproxSIMPLEbutton = Button(ApproxKeret, width=15, height=2, text='SIMPLE', font = "Consolas 10", bg ='light blue', command = ApproxSIMPLEcmd)
ApproxSIMPLEbutton.grid(row=1, column=0, columnspan=2, padx=30, pady=5, sticky='nesw')

üressor = Label(BeállításTesztKeret).grid(row=5, column=0, sticky='we')

###BeállításokKeret
BeállításokKeret = LabelFrame(BeállításTesztKeret, text='Beállítások', font = "Consolas 10 bold")
BeállításokKeret.grid(row=6, column=0 ,sticky='nesw', ipadx=5, ipady=5, columnspan=1)
Label(BeállításokKeret, text="Fényerő", font = "Consolas 10").grid(row=1, column=1, sticky='ws')
BrightnessScaler = Scale(BeállításokKeret, from_=-64, to=64, resolution=1, orient=HORIZONTAL)
BrightnessScaler.grid(row=1, column=0, sticky='w')
BrightnessScaler.set(brightness)
Label(BeállításokKeret, text="Kontraszt", font = "Consolas 10").grid(row=2, column=1, sticky='ws')
ContrastScaler = Scale(BeállításokKeret, from_=0, to=2, resolution=0.1, orient=HORIZONTAL)
ContrastScaler.grid(row=2, column=0, sticky='w')
ContrastScaler.set(contrast)
### Beállításokalaphelyzet
Beállításokalaphelyzetbutton = Button(BeállításokKeret, width=5, height=2, text='Alaphelyzet', font = "Consolas 10", command = Beállításokalaphelyzetcmd)
Beállításokalaphelyzetbutton.grid(row=3, column=0, columnspan=2, padx=30, pady=5, sticky='nesw')

###MérésekKeret
MérésekKeret = LabelFrame(AblakKeret, text='Mérések', font = "Consolas 11 bold")
MérésekKeret.grid(row=8, column=6, rowspan=1, ipadx=5, ipady=5, sticky='sew')
MérCPULab = Label(MérésekKeret, text="", font = "Consolas 10 bold")
MérCPULab.grid(row=1, column=0, sticky=W)
MérMemLab = Label(MérésekKeret, text="", font = "Consolas 10 bold")
MérMemLab.grid(row=2, column=0, sticky=W)
MérMem2Lab = Label(MérésekKeret, text="", font = "Consolas 10 bold")
MérMem2Lab.grid(row=3, column=0, sticky=W)

###ProcessBar
s = ttk.Style()
s.theme_use('clam')
ProcessBar = ttk.Progressbar(MérésekKeret, style="red.Horizontal.TProgressbar", orient = HORIZONTAL, length = 100, mode = 'determinate')
ProcessBar.grid(row=1, column=1, sticky='w')
	
#App bezárási folyamat
def on_closing():
    global exit
    if messagebox.askokcancel("Kilépés", "Biztosan ki akar lépni?"):
        exit = True
        cv2.destroyAllWindows()
        if kvw !='k':
            if camera:
                camera.release()
        time.sleep(1)
        window.destroy()

#Videó szál definíciók
def t_video():
    global camera
    global kvw
    global Minta_tavolsag
    global Minta_szelesseg
    global focalLength
    if kvw == 'k':
        # Lap távolsága a minta képalapján
        Minta_tavolsag = 50
        #A mintakép betöltése
        mintakep = cv2.imread("samples/_sampleimage.jpg")
        c = max(df.konturkeres(mintakep, 0, 0), key = cv2.contourArea)
        marker = cv2.minAreaRect(c)
        focalLength = (marker[1][0] * Minta_tavolsag) / Minta_szelesseg
        Kepek()
    elif kvw == 'v':
        # Lap távolsága a minta képalapján
        Minta_tavolsag = 100
        #A mintakép betöltése
        mintakep = cv2.imread("samples/_samplevideo.jpg")
        c = max(df.konturkeres(mintakep, 0, 0), key = cv2.contourArea)
        marker = cv2.minAreaRect(c)
        focalLength = (marker[1][0] * Minta_tavolsag) / Minta_szelesseg
        camera = cv2.VideoCapture('video/IMG_0925.mp4')
        #Kamera felbontás beállítása
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        #Kamera indítás előtti várakoztatás
        time.sleep(1)
        VideoCapture()
    else:
        os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
        os.environ["OPENCV_VIDEOIO_DEBUG"] = "1"
        # Lap távolsága a minta képalapján
        Minta_tavolsag = 120
        #A mintakép betöltése
        mintakep = cv2.imread("samples/_sampleweb.jpg")
        c = max(df.konturkeres(mintakep, 0, 0), key = cv2.contourArea)
        marker = cv2.minAreaRect(c)
        focalLength = (marker[1][0] * Minta_tavolsag) / Minta_szelesseg
        camera = cv2.VideoCapture(0)
        #Kamera felbontás beállítása
        #camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        #camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        #Kamera indítás előtti várakoztatás
        time.sleep(1)
        VideoCapture()

#Mérések szál definíciók
def t_cpu():
    global exit
    while not exit:
        cpu_val = p.cpu_percent()
        if cpu_val/cpu_count > 70:
            fc = "red"
            pc = "red"
        else:
            fc = "black"
            pc = "green2"
        MérCPULab.configure(text="  CPU:" +"%3.0f%%" % int(cpu_val/cpu_count), fg = fc)
        MérCPULab.grid(row=1, column=0, sticky=EW)
        ProcessBar['value'] = int(cpu_val/cpu_count)
        s.configure("red.Horizontal.TProgressbar", background=pc)

        mem_val = p.memory_info().rss/(1024*1024)
        MérMemLab.configure(text="Használt memória: " + "%4.0fMB" % int(mem_val))
        MérMemLab.grid(row=2, column=0, sticky=EW, columnspan=2)

        mem_val_pagefile = p.memory_info().pagefile/(1024 *1024)
        MérMem2Lab.configure(text="Lefoglalt memória: " + "%4.0fMB" % int(mem_val_pagefile))
        MérMem2Lab.grid(row=3, column=0, sticky=EW, columnspan=2)
        time.sleep(0.7)
 
#Szálkezelés
t1 = threading.Thread(target=t_video)  #Külön szál a videó feldolgozáshoz
t2 = threading.Thread(target=t_cpu)  #Külön szál a Mérésekhez
t2.start()
window.protocol("WM_DELETE_WINDOW", on_closing) #App bezárás
window.mainloop()   #GUI elindítása