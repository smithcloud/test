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


# 전체 플레이어 목록 조회 API
@app.get("/players", response_model=List[dict])
async def get_players():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "SELECT player_id, summoner_name FROM players;"
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No players found")

        return result
    finally:
        cursor.close()
        connection.close()

@app.get("/players", response_model=List[dict])
async def get_players():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "SELECT player_id, summoner_name FROM players;"
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No players found")

        return result
    finally:
        cursor.close()
        connection.close()


# 소환사 전적 조회 API
@app.get("/player-stats")
async def get_player_stats(summoner_name: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # 플레이어 기본 정보 조회
        player_query = """
        SELECT player_id, summoner_name, region, summoner_level, tier, profile_icon, created_at
        FROM players
        WHERE summoner_name = %s;
        """
        
        cursor.execute(player_query, (summoner_name,))
        player = cursor.fetchone()

        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        print({
            "player_id": player["player_id"],
            "summoner_name": player["summoner_name"],
            "region": player["region"],
            "summoner_level": player["summoner_level"],
            "tier": player["tier"],
            "profile_icon": player["profile_icon"],
            "created_at": player["created_at"]
        })
        return {
            "player_id": player["player_id"],
            "summoner_name": player["summoner_name"],
            "region": player["region"],
            "summoner_level": player["summoner_level"],
            "tier": player["tier"],
            "profile_icon": player["profile_icon"],
            "created_at": player["created_at"]
        }

    finally:
        cursor.close()
        connection.close()

@app.get("/healthcheck")
def health():
    return '{"status": ok.}'