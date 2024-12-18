import streamlit as st
import random
import requests
import json
from faker import Faker
import datetime

# API URL 설정 (여기서 'http://localhost:8000/players'와 'http://localhost:8000/champions'는 실제 API URL로 변경해야 합니다)
API_URL_PLAYERS = "http://riotgames-backend-alb-1178588041.ap-northeast-2.elb.amazonaws.com/players"
API_URL_CHAMPIONS = "http://riotgames-backend-alb-1178588041.ap-northeast-2.elb.amazonaws.com/champions"
faker = Faker()

# API에서 플레이어 목록 가져오기
def fetch_players():
    response = requests.get(API_URL_PLAYERS)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching player data.")
        return []

# API에서 챔피언 목록 가져오기
def fetch_champions():
    response = requests.get(API_URL_CHAMPIONS)
    if response.status_code == 200:
        return [{ "id": champion['champion_id'], "name": champion['name'] } for champion in response.json()]
    else:
        st.error("Error fetching champion data.")
        return []

def generate_match_id():
    match_id = random.randint(1000000000, 9999999999)  # Unique match ID
    game_mode = random.choice(['CLASSIC', 'ARAM', 'RANKED'])
    game_duration = random.randint(1200, 3600)  # Random game duration between 20 to 60 minutes
    game_creation = faker.date_this_decade()  # Random date in the last decade
    region = 'KR'
    
    return (match_id, game_mode, game_duration, game_creation, region)

# 랜덤 값 생성 함수
def generate_player_data(players, champions, is_win, team_roles):
    def random_player():
        try:
            player = random.choice(players) if isinstance(players, list) else players
            if isinstance(player, dict):
                player_id = player.get('player_id')
                if player_id is not None:
                    return int(player_id)
            raise ValueError("Player must have a valid player_id")
        except Exception as e:
            st.error(f"Error getting player ID: {str(e)}")
            raise
    def random_champion():
        champion = random.choice(champions)
        return champion if isinstance(champion, dict) else {"id": 0}
    def random_role():
        available_roles = [role for role in ['TOP', 'JUNGLE', 'MID', 'BOT', 'SUPPORT'] if role not in team_roles]
        if not available_roles:
            raise ValueError("No roles available - all roles have been used")
        role = random.choice(available_roles)
        team_roles.append(role)
        return role
    random_kills = lambda: random.randint(0, 20)
    random_deaths = lambda: random.randint(0, 20)
    random_assists = lambda: random.randint(0, 20)
    random_gold = lambda: random.randint(0, 20000)
    random_damage = lambda: random.randint(0, 50000)
    
    # Set 'win' value based on is_win parameter
    return {
        'player_id': random_player(),
        'champion_id': random_champion().get('id', 0),
        'role': random_role(),
        'kills': random_kills(),
        'deaths': random_deaths(),
        'assists': random_assists(),
        'gold_earned': random_gold(),
        'damage_dealt': random_damage(),
        'damage_taken': random_damage(),
        'win': is_win
    }

def generate_random_data(players, champions):
    # Decide the win for the red team (True or False)
    red_team_win = random.choice([True, False])
    
    # Track used roles for each team separately
    blue_team_roles = []
    red_team_roles = []
    
    # Create blue team with win status opposite to red team
    blueTeam = []
    for _ in range(5):
        player_data = generate_player_data(players, champions, not red_team_win, blue_team_roles)
        blueTeam.append(player_data)
    
    # Create red team with all players having the same win status
    redTeam = []
    for _ in range(5):
        player_data = generate_player_data(players, champions, red_team_win, red_team_roles)
        redTeam.append(player_data)
    
    return redTeam, blueTeam


# Streamlit 인터페이스 설정
def create_match_data(match_info, red_team_info, blue_team_info):
    API_URL_CREATE_MATCH = "http://riotgames-backend-alb-1178588041.ap-northeast-2.elb.amazonaws.com/create_match"
    API_URL_ADD_PLAYERS = "http://riotgames-backend-alb-1178588041.ap-northeast-2.elb.amazonaws.com/add_players_to_match"
    
    match_id, game_mode, game_duration, game_creation, region = match_info
    
    # Create match data
    match_data = {
        "match_id": match_id,
        "game_mode": game_mode,
        "game_duration": game_duration,
        "game_creation": game_creation.strftime("%Y-%m-%d"),
        "region": region
    }
    
    # Send match data to API
    # First, create the match
    match_response = requests.post(API_URL_CREATE_MATCH, json=match_data)
    if match_response.status_code != 200:
        return False, "Failed to create match"
        
    # Prepare player data
    player_data = []
    for team_info in [red_team_info, blue_team_info]:
        for player in team_info:
            player_data.append({
                "match_id": match_id,
                "player_id": player.get("player_id", random.randint(1000, 9999)),  # Using numeric player_id
                "champion_id": player.get("champion_id", 0),
                "role": player.get("role", "UNKNOWN"),
                "kills": player.get("kills", 0),
                "deaths": player.get("deaths", 0),
                "assists": player.get("assists", 0),
                "gold_earned": player.get("gold_earned", 0),
                "damage_dealt": player.get("damage_dealt", 0),
                "damage_taken": player.get("damage_taken", 0),
                "win": player.get("win", False)
            })
    
    # Then, add players to the match
    players_response = requests.post(API_URL_ADD_PLAYERS, json=player_data)
    if players_response.status_code != 200:
        return False, "Failed to add players to match"
        
    return True, "Match data created successfully"

def main():
    # 페이지 제목
    st.title("Match Data Input")

    # API에서 플레이어 목록과 챔피언 목록 가져오기
    players = fetch_players()
    champions = fetch_champions()

    # Initialize session state for match data
    if 'match_data' not in st.session_state:
        st.session_state.match_data = None

    col1, col2 = st.columns(2)
    
    if col1.button("Generate Random Data"):
        redTeamInfo, blueTeamInfo = generate_random_data(players, champions)
        matchInfo = generate_match_id()
        st.session_state.match_data = (matchInfo, redTeamInfo, blueTeamInfo)
    
    if col2.button("Create Match Data"):
        if st.session_state.match_data:
            matchInfo, redTeamInfo, blueTeamInfo = st.session_state.match_data
            success, message = create_match_data(matchInfo, redTeamInfo, blueTeamInfo)
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.error("Please generate random data first")

    # Display match data if it exists
    if st.session_state.match_data:
        matchInfo, redTeamInfo, blueTeamInfo = st.session_state.match_data
        st.text("Red Team Info:")
    if st.session_state.match_data:
        st.json(redTeamInfo)
        st.text("Blue Team Info:")
        st.json(blueTeamInfo)
        st.text("Match Info:")
        st.json({"match_id": matchInfo[0], 
             "game_mode": matchInfo[1],
             "game_duration": matchInfo[2],
             "game_creation": matchInfo[3].strftime("%Y-%m-%d"),
             "region": matchInfo[4]})

if __name__ == "__main__":
    main()