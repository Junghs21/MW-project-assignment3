import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 4096  # 버퍼 크기 설정
        try:
            with open('./response.bin', 'rb') as file:
                self.RESPONSE = file.read()  # 응답 파일 읽기
        except FileNotFoundError:
            print("response.bin 파일을 찾을 수 없습니다.")

        self.DIR_PATH = './request'
        self.IMAGE_DIR = './images'  # 이미지 저장 경로
        self.createDir(self.DIR_PATH)
        self.createDir(self.IMAGE_DIR)

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def save_request(self, data):
        """클라이언트 요청을 파일로 저장"""
        filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.bin")
        filepath = os.path.join(self.DIR_PATH, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
        print(f"Saved request to {filepath}")

    def save_image(self, image_data):
        """이미지 파일 저장"""
        filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.png")
        filepath = os.path.join(self.IMAGE_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        print(f"Saved image to {filepath}")

    def parse_multipart(self, data):
        """멀티파트 데이터 파싱"""
        try:
            # 헤더에서 boundary를 추출
            headers, body = data.split(b"\r\n\r\n", 1)
            headers = headers.decode('utf-8')
            content_type = [line for line in headers.split("\r\n") if "Content-Type" in line]
            if content_type:
                boundary = content_type[0].split("boundary=")[-1]
                boundary = boundary.encode('utf-8')

                # boundary 기준으로 데이터 분리
                parts = body.split(boundary)
                for part in parts:
                    if b'Content-Disposition' in part:
                        # 이미지 데이터 찾기
                        image_data = part.split(b'\r\n\r\n', 1)[1].rstrip(b'--\r\n')
                        return image_data
            return None
        except Exception as e:
            print(f"Error parsing multipart data: {e}")
            return None

    def run(self, ip, port):
        """서버 실행"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\\Ctrl+C\\ for stopping the server...\n\n")

        try:
            while True:
                # 클라이언트의 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)  # 타임아웃 설정 (5초)
                print("Request message...\n")

                # 클라이언트의 요청 받기
                request_data = clnt_sock.recv(self.bufsize)
                if request_data:
                    print(f"Received data: {request_data}")
                    if b'image' in request_data:
                        # 이미지 데이터인 경우 multipart 파싱 후 저장
                        print("==========실습 2 Result==========")
                        image_data = self.parse_multipart(request_data)
                        if image_data:
                            self.save_image(image_data)
                        else:
                            print("이미지 데이터가 없습니다.")
                    else:
                        # 일반 요청은 파일로 저장
                        print("==========실습 1 Result==========")
                        self.save_request(request_data)

                # 응답 전송
                clnt_sock.sendall(self.RESPONSE)

                # 클라이언트 소켓 닫기
                clnt_sock.close()
        except KeyboardInterrupt:
            print("\nStop the server...")
        finally:
            # 서버 소켓 닫기
            self.sock.close()

if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
