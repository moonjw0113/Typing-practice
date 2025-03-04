import sys
from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QLocale
from random import *
from time import *
import socket
import re


#영어를 한글로 바꾸는 코드  출처:https://velog.io/@he1256/pyautogui-%EC%97%90%EC%84%9C-typewrite-%EC%82%AC%EC%9A%A9%EC%8B%9C-%ED%95%9C%EA%B8%80-%EC%98%81%EB%AC%B8-%EC%9D%B8%EC%8B%9D-%EB%B0%8F-%EB%B3%80%EA%B2%BD%EB%B2%95-by-using-win32API
import ctypes
from ctypes import wintypes
wintypes.ULONG_PTR = wintypes.WPARAM
hllDll = ctypes.WinDLL ("User32.dll", use_last_error=True)
VK_HANGUEL = 0x15

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))
class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))
def get_hanguel_state():
    return hllDll.GetKeyState(VK_HANGUEL)
def change_state():
    x = INPUT(type=1 ,ki=KEYBDINPUT(wVk=VK_HANGUEL))
    y = INPUT(type=1, ki=KEYBDINPUT(wVk=VK_HANGUEL,dwFlags=2))
    hllDll.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    sleep(0.05)
    hllDll.SendInput(1, ctypes.byref(y), ctypes.sizeof(y))

#if get_hanguel_state() == 0: #0 일경우 vk_key : 0x15(한글키)가 비활성화
#    change_state() #한글키 누르고(key_press) , 때기(release)
#***********************************************************************************************************************************************************************


# UI파일 연결
form_class = uic.loadUiType("./타자연습.ui")[0]

class MainClass(QMainWindow, form_class):
    
    input:QLineEdit # 입력
    text1:QPlainTextEdit # 현재 문장
    text2:QLabel # 다음 문장
    speed:QLabel # 타수
    long:QRadioButton # 긴글 연습 버튼
    short:QRadioButton # 짧은글 연습 버튼
    accuracy:QLabel # 정확도
    aveAcc:QLabel # 평균 정확도
    aveSpeed:QLabel # 평균 속도
    maxSpeed:QLabel # 최고 속도
    errorCount:QLabel # 오타 수
    exitButton:QPushButton # 종료버튼
    startTime = 0 # 시작시간.  현재시간 - 시작시간 = 사용시간
    typeCount = 0 # 정타만
    typeCount1 = 0 # 정타 오타 상관X
    start = False # 처음 타자 치면 True 됨
    senKorean = [] # 문장의 한글 분헤
    inputKorean = [] # 입력값의 한글 분해
    nowText = '' # 현재 문장
    lineCount = 0 # 몇 번째 줄
    flag = '' # login에서 넘어올때 짧은글인지 긴글인지 확인하는 플래그
    texts = [] # 문장 리스트
    totalTime = 0 # 누적 시간
    totalCount = 0 # 누적 정타
    totalCount1 = 0 # 누적 정타 + 오타
    maxSpd = 0 # 최고속도
    htmlStr = ''
    htmlColor = ''
    correct = True
    htmlText = ''
    maxLine = 3 # 짧은글연습 종료할때 문장 개수
    
    

    def __init__(self) :
        QMainWindow.__init__(self)
        # 연결한 Ui를 준비한다.
        self.setupUi(self)        
        self.input = self.Input
        self.text1 = self.Text1
        self.text2 = self.Text2
        self.speed = self.Speed
        self.accuracy = self.Accuracy
        self.aveAcc = self.AverageAccuracy
        self.aveSpeed = self.AverageSpeed
        self.maxSpeed = self.MaxSpeed
        self.errorCount = self.ErrorCount
        self.exitButton = self.ExitButton
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('localhost', 12345))  # 서버에 연결
        except:
            print('서버 연결 실패')
            QMessageBox.critical(self, "연결 실패", "서버에 연결할 수 없습니다.")   
        
        
        # 문자열이 바뀌면 changed()메서드 실행
        self.input.textChanged.connect(self.changed)
        # return을 누르면 enter()메서드 실행
        self.input.returnPressed.connect(self.enter)
        
        self.input.mousePressEvent = self.on_click
        
        self.exitButton.setFocus()
        
        self.exitButton.pressed.connect(self.close)
    
    def on_click(self, event):
        if get_hanguel_state() == 0: #0 일경우 vk_key : 0x15(한글키)가 비활성화
            change_state() #한글키 누르고(key_press) , 때기(release)
        
        
    def SetTypingMode(self):
        self.texts = []
        if self.flag == 'LONG':
            f = open('긴글연습.txt', 'r', encoding='UTF8')
            for line in f:
                self.texts.append(''.join(line.split('\n')))
            self.text2.setText(self.texts[self.lineCount])
            self.text1.setPlainText(self.text2.text())
            self.nowText = self.text2.text()
            self.text2.setText(self.texts[self.lineCount + 1])
            self.lineCount += 1
            
        elif self.flag == 'SHORT':
            f = open('짧은글연습.txt', 'r', encoding='UTF8')
            for line in f:
                self.texts.append(''.join(line.split('\n')))
            self.text2.setText(self.texts[randint(0, len(self.texts) - 1)])
            self.text1.setPlainText(self.text2.text())
            self.nowText = self.text2.text()
            self.text2.setText(self.texts[randint(0, len(self.texts) - 1)])
            while self.text2.text() == self.nowText:
                self.text2.setText(self.texts[randint(0, len(self.texts) - 1)])
            self.lineCount += 1
            
            
    def changed(self):
        if len(self.nowText) == len(self.input.text()) - 1: # 문장과 입력값의 길이가 같으면 check()메서드 실행
            self.check(self.nowText, self.input.text())
        elif not self.start:
            self.start = True
            self.startTime = time() # 초시계 시작
        else:
            self.count(self.nowText[:len(self.input.text())], self.input.text()[:len(self.input.text())])
            if time() != self.startTime:
                self.speed.setText('타수: '+ str(int(self.typeCount / (time() - self.startTime) * 60)) + '타') # 타수 입력
            if self.typeCount1 > 0:
                self.accuracy.setText('정확도: ' + str(int(self.typeCount / self.typeCount1 * 100)) + '%') # 정확도 입력
        if len(self.input.text()) == 0:
            self.start = False
          
    def enter(self):
        if len(self.nowText) == len(self.input.text()): # 문장과 입력값의 길이가 같으면 check()메서드 실행
            self.check(self.nowText, self.input.text())

    def check(self, a, b):  # 다음 문장으로 넘어갈때 실행하는 함수
        self.count(a, b)
                
        # 문장 업데이트 후 초기화
        self.speed.setText('타수: '+ str(int(self.typeCount / (time() - self.startTime) * 60)) + '타') # 타수 입력
        self.accuracy.setText('정확도: ' + str(int(self.typeCount / self.typeCount1 * 100)) + '%')  # 정확도 입력
        self.totalTime += time() - self.startTime
        self.totalCount += self.typeCount
        self.totalCount1 += self.typeCount1
        self.aveAcc.setText('평균: ' + str(int(self.totalCount / self.totalCount1 * 100)) + '%')
        self.aveSpeed.setText('평균: ' + str(int(self.totalCount / self.totalTime * 60)) + '타')
        if self.maxSpd < int(self.typeCount / (time() - self.startTime) * 60):
            self.maxSpd = int(self.typeCount / (time() - self.startTime) * 60)
            self.maxSpeed.setText('최고: ' + str(self.maxSpd) + '타')
        self.errorCount.setText('오타 수: ' + str(self.totalCount1 - self.totalCount))
        self.start = False
        self.input.clear()
        
        
        if self.flag == 'LONG':
            if len(self.texts) - self.lineCount == 1:
                self.text1.setPlainText(self.text2.text())
                self.nowText = self.text2.text()
                self.text2.setText('')
            elif len(self.texts) - self.lineCount == 0:
                self.text1.setPlainText('')
                self.finish()
            else:
                self.text2.setText(self.texts[self.lineCount])
                self.text1.setPlainText(self.text2.text())
                self.nowText = self.text2.text()
                self.text2.setText(self.texts[self.lineCount + 1])
            self.lineCount += 1

        elif self.flag == 'SHORT':
            self.text1.setPlainText(self.text2.text())
            self.nowText = self.text2.text()
            self.text2.setText(self.texts[randint(0, len(self.texts) - 1)])
            while self.text2.text() == self.nowText:
                self.text2.setText(self.texts[randint(0, len(self.texts) - 1)])
            if self.lineCount == self.maxLine:
                self.finish()
            self.lineCount += 1
            
    # 정타와 오타를 판별하는 메서드
    def count(self, a, b):
        # 변수 초기화
        self.typeCount = 0
        self.typeCount1 = 0
        self.htmlColor = ''
        self.htmlStr = ''

        for i in range(len(a)):
            self.correct = True
            # 한글 분해
            self.senKorean = self.Break(a[i])
            self.inputKorean = self.Break(b[i])
            # 특수문자
            if len(self.senKorean) == 0:
                self.typeCount1 += 1
                if a[i] == b[i]:
                    self.typeCount += 1
                else:
                    self.correct = False
            # 한글
            else:
                if len(self.inputKorean) != len(self.senKorean):
                    self.typeCount1 += 3
                    self.correct = False
                    if len(self.inputKorean) < len(self.senKorean):
                        for j in range(len(self.inputKorean)):
                            if self.senKorean[j] == self.inputKorean[j]:
                                self.typeCount += 1
                    if len(self.inputKorean) > len(self.senKorean):
                        for j in range(len(self.senKorean)):
                            if self.senKorean[j] == self.inputKorean[j]:
                                self.typeCount += 1
                else:
                    self.typeCount1 += len(self.senKorean)
                    for j in range(len(self.senKorean)):
                        if self.senKorean[j] == self.inputKorean[j]:
                            self.typeCount += 1
                        else:
                            self.correct = False
            if self.correct:
                self.html(a[i], 'b')
            else:
                self.html(a[i], 'r')
        self.htmlText = ''
        for i in range(len(self.htmlStr)):
            if self.htmlColor[i] == 'b':
                self.htmlText += self.htmlStr[i]
            else:
                self.htmlText += '<font color = "red">' + self.htmlStr[i] + '</font>'
        self.htmlText += self.nowText[len(self.htmlStr):]
        self.text1.clear()
        self.text1.appendHtml(self.htmlText)
                

    def html(self, word, color):
        self.htmlColor += color
        if word == ' ' and color == 'r':
            self.htmlStr += '_'
        else:
            self.htmlStr += word

# 한글을 초성 중성 종성으로 분해하는 메서드
    def Break(self, korean):
        breaked = []
        if ord('가') <= ord(korean) <= ord('힣'):
            index = ord(korean) - ord('가')
            breaked.append(int(((index / 28) / 21)))
            breaked.append(int((index / 28) % 21))
            if int(index % 28) > 0:
                breaked.append(int(index % 28))
        return(breaked)
    
    #짧은글연습, 긴글연습 끝났을때
    
    def finish(self):
        try:
            self.pattern = r'\d+'
            message = f"{self.flag} {re.findall(self.pattern, self.aveSpeed.text())[0]} {re.findall(self.pattern, self.aveAcc.text())[0]} {re.findall(self.pattern, self.maxSpeed.text())[0]}"
            # meessage = 모드, 타수, 정확도, 최고타수
            self.client_socket.sendall(message.encode())
            self.client_socket.close()
            print('sent')
            self.close()
        except Exception as e:
            print(e)
        
        
if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    window = MainClass() 
    window.show()
    app.exec()