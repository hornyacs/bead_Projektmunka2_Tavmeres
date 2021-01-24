import numpy as np
import cv2 as cv2
def konturkeres(kep, a, b):
        #Szűrés és hsv színtér konvertálás
        if a==0:
            blurred_kep = cv2.GaussianBlur(kep, (5, 5), 0)
        else:
            blurred_kep = cv2.bilateralFilter(kep, 15, 75, 150)
        hsv = cv2.cvtColor(blurred_kep, cv2.COLOR_BGR2HSV)
        
        #szín tartomány szerinti szűrése és maszkolás
        color_min = np.array([10, 130, 128])
        color_max = np.array([40, 255, 255])
        mask = cv2.inRange(hsv, color_min, color_max)
        
        #Kontúrok keresése
        if b==0:
            (_,contours,_) = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            (_,contours,_) = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        contours2=[]          
        for cntrIdx in contours: #Végignézzük a megtalált kontúrokat
            
            #Csak azokat vesszük figyelembe, ami 4 csúccsal rendelkezik
            approx = cv2.approxPolyDP(cntrIdx,0.05*cv2.arcLength(cntrIdx,True),True)
            if len(approx)==4:
             m = cv2.minAreaRect(cntrIdx)
             arany = 0.0
             #A kontúr hosszúsága és szélessége nem lehet 0
             if m[1][0]!=0.0 and m[1][1]!=0.0:
               #A kontúr hosszúság és szélesség arányának kiszámítása az A4 méretek elkülönítése miatt
               if m[1][0] > m[1][1]:
                  arany = m[1][0]/m[1][1]
               else:
                  arany = m[1][1]/m[1][0]
             #A megfelelő aránnyal rendelkező kontúrok megtartása 2,97/2,1=1,414
             if (arany > 1.35) and (arany < 1.48):
                 contours2.append(cntrIdx)
        if len(contours2)!=0: #Ha van ilyen paraméterekkel rendelekző kontúr, akkor átadjuk ezt egy kontúr tömbben
            return(contours2)
        else: #Egyébként 0-át adunk vissza
            return (0)

def tavolsag(knownWidth, focalLength, perWidth):
        # távolság számítás
        return (knownWidth * focalLength) / perWidth

