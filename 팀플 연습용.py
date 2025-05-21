import json
from datetime import datetime
import re
import requests
from datetime import timedelta

# 파일 경로 설정
file_path ="C:\\Users\\cjwon\\OneDrive\\바탕 화면\\Takeout\\YouTube 및 YouTube Music\\시청 기록\\시청 기록.json"

# JSON 파일 열기
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 데이터 파싱 및 출력
for item in data:
    if 'titleUrl' in item:  # 시청한 동영상만 필터링
        title = item.get('title')
        url = item.get('titleUrl')
        time = item.get('time')

        # 시간 포맷 변환 (UTC → 한국시간)
        time = datetime.fromisoformat(time.replace('Z', '+00:00')).astimezone()
        time_str = time.strftime('%Y-%m-%d %H:%M:%S')

    

# 🔑 발급받은 API 키 입력
API_KEY = 'AIzaSyAJ88JuXAdk6h4WkIQRsIJQRpcxay6xOJY'

# 📁 watch-history.json 파일 경로
file_path = 'C:\\Users\\cjwon\\OneDrive\\바탕 화면\\Takeout\\YouTube 및 YouTube Music\\시청 기록\\시청 기록.json'

# ▶ 영상 ID 추출 함수
def extract_video_id(url):
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

# ▶ ISO 8601 포맷 → 초 변환
def parse_duration(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

# ▶ 영상 ID 목록 추출
video_ids = [extract_video_id(item['titleUrl']) for item in data if 'titleUrl' in item]
video_ids = list(filter(None, video_ids))  # None 제거
video_ids = list(set(video_ids))  # 중복 제거

# ▶ API 요청으로 전체 시청 시간 계산
total_seconds = 0

for i in range(0, len(video_ids), 50):  # 50개씩 나눠서 요청
    chunk = video_ids[i:i+50]
    ids = ','.join(chunk)
    url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={ids}&key={API_KEY}'
    response = requests.get(url)
    items = response.json().get('items', [])

    for item in items:
        duration = item['contentDetails']['duration']
        total_seconds += parse_duration(duration)

# ▶ 결과 출력
total_time = timedelta(seconds=total_seconds)
print(f'📊 최대 추정 시청 시간: {total_time} (약 {total_time.total_seconds() / 3600:.2f}시간)')