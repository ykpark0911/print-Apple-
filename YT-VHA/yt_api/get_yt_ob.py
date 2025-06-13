# ── Google OAuth 2.0 인증을 통해 YouTube API 사용 권한을 얻는 모듈 ──
import os
from google_auth_oauthlib.flow import InstalledAppFlow  # 사용자 OAuth 2.0 인증 처리 클래스
from googleapiclient.discovery import build             # API 요청을 위한 서비스 객체 생성 함수

# SCOPES = 사용자의 YouTube 데이터 접근 권한 요청 범위
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"] # 읽기 전용 권한

def tester_login():
    current_dir = os.path.dirname(__file__)
    client_secret_filename = "client_secret_693447563027-1qjb80j8h2uj0phs3cvqfjcnb8tsat4m.apps.googleusercontent.com.json"
    client_secret_path = os.path.join(current_dir, client_secret_filename)
    
    # OAuth 흐름 초기화 (client_secret.json 파일과 요청 권한 설정)
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secret_path, SCOPES # 수정된 경로 사용
    )

    # 사용자 브라우저 열기 → 로그인 + 권한 허용 → 인증 정보 받기
    credentials = flow.run_local_server(port=0)
    
    # 인증된 credentials로 YouTube API 요청 메서드들 갖은 객체 생성
    youtube = build("youtube", "v3", credentials=credentials)

    return youtube  # 인증된 YouTube 객체 반환



def guest_login():
    youtube = build("youtube", "v3", developerKey="AIzaSyDjvvV6-FMydm-TYKiPqKzYl6wAzaRoUZk")

    return youtube