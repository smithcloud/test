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

# 플레이어의 매치 히스토리 조회 API
@app.get("/matches/{player_id}")
async def get_player_matches(player_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT m.match_id, m.game_duration, m.game_mode, mp.kills, mp.deaths, mp.assists, 
               mp.gold_earned, mp.damage_dealt, mp.win, c.name as champion_name
        FROM matches m
        JOIN match_players mp ON m.match_id = mp.match_id
        JOIN champions c ON mp.champion_id = c.champion_id
        WHERE mp.player_id = %s
        ORDER BY m.match_id DESC
        LIMIT 10;
        """
        cursor.execute(query, (player_id,))
        matches = cursor.fetchall()

        if not matches:
            return []

        return matches

    finally:
        cursor.close()
        connection.close()


class MatchCreateRequest(BaseModel):
    match_id: int
    game_mode: str
    game_duration: int
    game_creation: str
    region: str

# 매치에 플레이어 참여 요청 데이터 모델
class MatchPlayerRequest(BaseModel):
    match_id: int
    player_id: int
    champion_id: int
    role: str
    kills: int
    deaths: int
    assists: int
    gold_earned: int
    damage_dealt: int
    damage_taken: int
    win: bool

# 매치 생성 API
@app.post("/create_match")
async def create_match(request: MatchCreateRequest):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # 매치 생성
        query = """
        INSERT INTO matches (match_id, game_mode, game_duration, game_creation, region)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (request.match_id, request.game_mode, request.game_duration, request.game_creation, request.region))
        connection.commit()

        # 생성된 match_id 반환
        match_id = cursor.lastrowid
        return {"match_id": match_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating match: {str(e)}")
    finally:
        cursor.close()
        connection.close()


# 매치에 플레이어 참여 API
@app.post("/add_players_to_match")
async def add_players_to_match(request: List[MatchPlayerRequest]):
    valid_roles = ["TOP", "JUNGLE", "MID", "BOT", "SUPPORT"]
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Group players by team (win status)
        red_team = [p for p in request if p.win]
        blue_team = [p for p in request if not p.win]
        
        # Check for duplicate roles within each team
        for team, team_name in [(red_team, "Red"), (blue_team, "Blue")]:
            team_roles = [p.role for p in team]
            if len(team_roles) != len(set(team_roles)):
                raise HTTPException(status_code=400, detail=f"{team_name} team has duplicate roles. Each role must be unique within a team.")
        
        for player in request:
            # Validate role
            if player.role not in valid_roles:
                raise HTTPException(status_code=400, detail=f"Invalid role: {player.role}. Must be one of {valid_roles}")
            
            # Validate match_id exists
            cursor.execute("SELECT 1 FROM matches WHERE match_id = %s", (player.match_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Match ID {player.match_id} does not exist")

            # Validate player_id exists
            cursor.execute("SELECT 1 FROM players WHERE player_id = %s", (player.player_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Player ID {player.player_id} does not exist")
                
            # Validate champion_id exists
            cursor.execute("SELECT 1 FROM champions WHERE champion_id = %s", (player.champion_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Champion ID {player.champion_id} does not exist")

            # Validate non-negative numeric fields
            if any(v < 0 for v in [player.kills, player.deaths, player.assists, 
                                 player.gold_earned, player.damage_dealt, player.damage_taken]):
                raise HTTPException(status_code=400, detail="Numeric stats cannot be negative")
            
            # match_players 테이블에 플레이어 추가
            query = """
            INSERT INTO match_players (match_id, player_id, champion_id, role, kills, deaths, assists, 
            gold_earned, damage_dealt, damage_taken, win)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            cursor.execute(query, (player.match_id, player.player_id, player.champion_id, player.role,
                                   player.kills, player.deaths, player.assists, player.gold_earned,
                                   player.damage_dealt, player.damage_taken, player.win))
                                   
        connection.commit()

        return {"detail": "Players added successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error adding players to match: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.get("/healthcheck")
def health():
    return '{"status": ok.}'