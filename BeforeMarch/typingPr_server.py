import socket
import select
import csv
import sys
from PyQt6.QtWidgets import *
from PyQt6 import uic
import threading

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen()


# 소켓 리스트 초기화
sockets_list = [server_socket]

print("서버가 시작되었습니다. 연결을 기다리는 중...")

records = [] #기록 나열

# CSV 파일에서 데이터 읽기
with open('records.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)  # 딕셔너리 형태로 읽기
    for row in reader:
        records.append({"name": row['name'], "speed": int(row['speed']), "acc": int(row['acc']), "maxSpeed": int(row['maxSpeed'])})

form_class = uic.loadUiType("typingPrServer.ui")[0]

class MainWindow(QMainWindow, form_class) :
    
    first:QLabel
    second:QLabel
    third:QLabel
    fourth:QLabel
    fifth:QLabel
    exitButton:QPushButton
    
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.show()
        self.first = self.First
        self.second = self.Second
        self.third = self.Third
        self.fourth = self.Fourth
        self.fifth = self.Fifth
        self.exitButton = self.Finish
        
        self.rank()
        
        self.exitButton.pressed.connect(self.finish)


    def rank(self):
        sorted_records = sorted(records, key=lambda x: x["speed"], reverse=True)
        for rank, record in enumerate(sorted_records, start=1):
            print(f"{rank}위: {record['name']} - 속도: {record['speed']} - 정확도: {record['acc']}")
            if rank == 1:
                self.first.setText(f"{rank}위: {record['name']} - 속도: {record['speed']} - 정확도: {record['acc']}")
            if rank == 2:
                self.second.setText(f"{rank}위: {record['name']} - 속도: {record['speed']} - 정확도: {record['acc']}")
            if rank == 3:
                self.third.setText(f"{rank}위: {record['name']} - 속도: {record['speed']} - 정확도: {record['acc']}")
            if rank == 4:
                self.fourth.setText(f"{rank}위: {record['name']} - 속도: {record['speed']} - 정확도: {record['acc']}")
            if rank == 5:
                self.fifth.setText(f"{rank}위: {record['name']} - 속도: {record['speed']} - 정확도: {record['acc']}")
    
    def finish(self):
        # CSV 파일로 저장
        with open('records.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'speed', 'acc', 'maxSpeed']  # 필드 이름 정의
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()  # 헤더(열 이름) 작성
            for record in records:
                writer.writerow(record)  # 각 레코드 작성
        
        
        self.close()
    
def handle_clients():
    while True:
        try:
            # select를 사용하여 읽기 가능 소켓 확인
            readable, writable, exceptional = select.select(sockets_list, [], [])

            for s in readable:
                if s is server_socket:
                    # 새로운 클라이언트 연결 수락
                    client_socket, addr = server_socket.accept()
                    print(f"클라이언트 {addr}가 연결되었습니다.")
                    sockets_list.append(client_socket)  # 클라이언트 소켓을 리스트에 추가

                else:
                    # 클라이언트로부터 데이터 수신
                    data = s.recv(1024)
                    if data:
                        print(f"클라이언트 {s.getpeername()}로부터 받은 데이터: {data.decode()}")
                        data = data.decode()
                        print(data)
                        mode, spd, acc, maxspd =  data.split()
                        spd, acc, maxspd = map(int, (spd, acc, maxspd))
                        records.append({"name": f"사용자{len(records) + 1}", "speed": spd, "acc": acc, "maxSpeed": maxspd})
                        Window.rank()

                    else:
                        # 클라이언트가 연결을 종료한 경우
                        print(f"클라이언트 {s.getpeername()}가 연결을 종료했습니다.")
                        sockets_list.remove(s)
                        s.close()
                    
                    
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window = MainWindow()
    
    # 소켓 서버를 별도의 스레드에서 실행
    server_thread = threading.Thread(target=handle_clients, daemon=True)
    server_thread.start()
    
    app.exec()