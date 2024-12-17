from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import mysql.connector
import os
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 애플리케이션
app = FastAPI()

# CORS 설정
origins = [
    "*",  # React 개발 서버 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 
)

# MySQL 연결 설정
db_config = {
    'user': os.getenv('MYSQL_USERNAME'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DB'),
    'port': os.getenv('MYSQL_PORT'),
}
# 소환사 전적 조회 요청 데이터 모델
class PlayerStatsRequest(BaseModel):
    summoner_name: str

class ChampionRequest(BaseModel):
    id: int
    champion_name: str

class PlayerStats(BaseModel):
    match_id: int
    game_mode: str
    role: str
    kills: int
    deaths: int
    assists: int
    gold_earned: int
    damage_dealt: int
    damage_taken: int
    win: bool
    summoner_name: str
    champion_name: str

# MySQL 연결 함수
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection
    
@app.get("/images/tier/{tier_name}")
async def get_tier_image(tier_name: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # tier_images 테이블에서 이미지 경로 조회
        query = "SELECT tier_icon FROM tier_images WHERE tier_name = %s;"
        cursor.execute(query, (tier_name,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Tier not found")

        # 이미지 경로를 추출
        image_path = result['tier_icon']

        # 이미지 경로가 파일 시스템 내에 존재하는지 확인
        full_image_path = image_path
        print(full_image_path)
        if not os.path.exists(full_image_path):
            raise HTTPException(status_code=404, detail="Image not found")

        # 이미지 파일 반환
        return FileResponse(full_image_path, media_type='image/png')  # 필요에 따라 media_type 수정

    finally:
        cursor.close()
        connection.close()

@app.get("/healthcheck")
def health():
    return '{"status": ok.}'