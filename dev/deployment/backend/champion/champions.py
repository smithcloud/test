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

# 챔피언 목록 조회 API
@app.get("/champions", response_model=List[dict])
async def get_champions():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT champion_id, name 
        FROM champions;
        """
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No champions found")

        return result
    finally:
        cursor.close()
        connection.close()

@app.get("/healthcheck")
def health():
    return '{"status": ok.}'