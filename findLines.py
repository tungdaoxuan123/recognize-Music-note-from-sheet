import cv2
import numpy as np
import math
    
def distance(note1,note2):
    return math.dist(note1,note2)

def checkSimilar(notes,note,w):
    for i in notes:
        if distance(i,note) < w:
            return False
    return True
# Load image, convert to grayscale, Otsu's threshold
image = cv2.imread('test.png')
def cropBar(image):
    result = image.copy()
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    note = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=5)
    cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        for i in range(len(c)-2):
            c = np.delete(c,1,0)

    SuitableNoteSize = abs(cnts[0][0][0][1] - cnts[1][0][0][1] )
    dimension = thresh.shape

    crop_img = []
    index = 0
    while index + 5 <= len(cnts):
        crop_img.append(note[cnts[index][0][0][1]-SuitableNoteSize*7:cnts[index][0][0][1]+SuitableNoteSize*2,0:dimension[1]])
        index += 5
    return crop_img

def findTrebelClef(croppedBar):
    SuitableNoteSize = int(croppedBar.shape[0]/9)
    template = cv2.imread('trebelClef.png',0)

    suitableNote = cv2.resize(template,(0,0),fx = SuitableNoteSize*3 / template.shape[1],fy = SuitableNoteSize*7 / template.shape[0])
    w, h = suitableNote.shape[::-1]
    res = cv2.matchTemplate(croppedBar,suitableNote,cv2.TM_CCOEFF_NORMED)
    threshold = 0.35
    loc = np.where( res >= threshold)
    notes = []
    for pt in zip(*loc[::-1]):
        return pt[0]+w

def findBassClef(croppedBar):
    SuitableNoteSize = int(croppedBar.shape[0]/9)
    template = cv2.imread('bassClef.png',0)

    suitableNote = cv2.resize(template,(0,0),fx = SuitableNoteSize*4 / template.shape[1],fy = SuitableNoteSize*5 / template.shape[0])
    w, h = suitableNote.shape[::-1]
    res = cv2.matchTemplate(croppedBar,suitableNote,cv2.TM_CCOEFF_NORMED)
    threshold = 0.25
    loc = np.where( res >= threshold)
    notes = []
    for pt in zip(*loc[::-1]):
        return pt[0]+w

cropped = cropBar(image)
clef = findTrebelClef(cropped[0])
if clef == None:
    clef = findBassClef(cropped[0])

def lineChecker(img,x,y):
    noteSize = img.shape[0]/9*0.5
    blackDetector = 0
    whiteNote = []
    while x < img.shape[1]:
        if img[y,x] == 0:
            blackDetector += 1
        else:
            if blackDetector > noteSize:
                #check if it really a black note
                blackNote = True
                for i in range (0,int(img.shape[0]/9/2)):
                    if img[y+i,x- int(blackDetector/2)] != 0 or img[y-i,x- int(blackDetector/2)] != 0:
                        blackNote = False
                        break
                if blackNote:
                    cv2.circle(img,(x-int(blackDetector/2),y), 1, (255,255,255), -1)
            elif blackDetector!=0:
                #2 case: a note tail, a white note
                #we check if it a note tail first
                isTail = True
                isHalfBNote = 0
                for i in range (0,int(img.shape[0]/9/2)):
                    if img[y+i,x- int(blackDetector/2)-1] != 0 or img[y-i,x- int(blackDetector/2)-1] != 0:
                        isTail = False
                if isTail:
                    blackDetector = 0
                    x+= int(noteSize)-1
                    continue
                else:
                    whiteNote.append([y,x- int(blackDetector/2)])
                #maybe it will be a half Bnote
            blackDetector = 0
        x += 1
    for i in range(1,len(whiteNote)):
        dist = distance(whiteNote[i],whiteNote[i-1])
        if dist > noteSize*1.5 and dist < noteSize*2 * 1.1:
            cv2.circle(img,(int((whiteNote[i][1]+whiteNote[i-1][1])/2),whiteNote[i][0]), 1, (0,0,0), -1)
    return

def inLineChecker(img,x,y):
    noteSize = img.shape[0]/9*0.5
    blackDetector = 0
    whiteNote = []
    while x < img.shape[1]:
        if img[y,x] == 0 and img[y - int(noteSize*0.6),x] == 0 and img[y + int(noteSize*0.6),x] == 0:
            blackDetector += 1
        else:
            if blackDetector >= noteSize:
                blackNote = True
                for i in range (0,int(img.shape[0]/9/3)):
                    if img[y+i,x- int(blackDetector/2)] != 0 or img[y-i,x- int(blackDetector/2)] != 0:
                        blackNote = False
                        break
                if blackNote:
                    cv2.circle(img,(x-int(blackDetector/2),y), 1, (255,255,255), -1)
            elif blackDetector!=0:
                whiteNote.append([y,x- int(blackDetector/2)])
            blackDetector = 0

        x+=1
    for i in range(1,len(whiteNote)):
        print(whiteNote[i])
        dist = distance(whiteNote[i],whiteNote[i-1])
        if dist > noteSize*1.3 and dist < noteSize*2 * 1.3:
            cv2.circle(img,(int((whiteNote[i][1]+whiteNote[i-1][1])/2),whiteNote[i][0]), 1, (255,255,255), -1)

def drawCheckLine(img):
    step = int(img.shape[0]/9)
    start = int(img.shape[0]/9/2)
    for i in range(0,9):
        lineChecker(img,clef,start + i*step)
    return

def inLineCheck(img):
    step = int(img.shape[0]/9)
    start = int(img.shape[0]/9)
    for i in range(0,8):
        inLineChecker(img,clef,start + i*step)
        cv2.circle(img,(clef,start+step* i), 4, (0,0,0), -1)
    return

for i in cropped:
    drawCheckLine(i)
    inLineCheck(i)
    cv2.imshow("Blobs Using Area", i)
    cv2.waitKey(0)
    cv2.destroyAllWindows()