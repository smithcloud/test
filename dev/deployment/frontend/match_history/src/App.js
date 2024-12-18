import React, { useState } from 'react';
import './App.css';

const API_BASE_URL = 'http://riotgames-backend-alb-1178588041.ap-northeast-2.elb.amazonaws.com';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [playerStats, setPlayerStats] = useState(null);
  const [matchHistory, setMatchHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/player-stats?summoner_name=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) {
        throw new Error('플레이어를 찾을 수 없습니다');
      }
      const data = await response.json();
      setPlayerStats(data);
      
      // Match history 조회
      const matchResponse = await fetch(`${API_BASE_URL}/matches/${data.player_id}`);
      if (matchResponse.ok) {
        const matchData = await matchResponse.json();
        setMatchHistory(matchData);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>소환사 전적 검색</h1>
        <form onSubmit={handleSearch}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="소환사 닉네임을 입력하세요"
          />
          <button type="submit">검색</button>
        </form>
      </header>

      {loading && <div className="loading-text">로딩중...</div>}
      {error && <div className="error-message">{error}</div>}
      
      {playerStats && (
        <div className="player-stats">
          <h2>
            <img 
              src={`https://ddragon.leagueoflegends.com/cdn/14.24.1/img/profileicon/${playerStats.profile_icon}`}
              alt="Profile Icon"
              style={{width: '40px', height: '40px', marginRight: '10px', verticalAlign: 'middle'}}
            />
            {playerStats.summoner_name}
          </h2>
          <div className="stats-container">
            <p>레벨: {playerStats.summoner_level}</p>
            <p>티어: {playerStats.tier} <img src={`${API_BASE_URL}/images/tier/${playerStats.tier}`} alt={`${playerStats.tier} 티어`} style={{height: '50px'}} /></p>
          </div>
        </div>
      )}

      {matchHistory.length > 0 && (
        <div className="match-history">
          <h3>매치 기록</h3>
          <div className="matches-container">
            {matchHistory.map((match) => (
              <div key={match.match_id} className={`match-card ${match.win ? 'win' : 'lose'}`}>
                <div className="match-info">
                  <p>{match.game_mode} ({Math.floor(match.game_duration / 60)}:{(match.game_duration % 60).toString().padStart(2, '0')})</p>
                  <p>
                    <img 
                      src={`https://ddragon.leagueoflegends.com/cdn/14.24.1/img/champion/${match.champion_name.replace(/\s+/g, '')}.png`}
                      alt={match.champion_name}
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '8px',
                        marginRight: '10px',
                        verticalAlign: 'middle',
                        border: '2px solid rgba(0,0,0,0.1)'
                      }}
                    />
                    {match.champion_name}
                  </p>
                </div>
                <div className="match-stats">
                  <p><span style={{color: '#2c3e50'}}>{match.kills}</span> / <span style={{color: '#dc3545'}}>{match.deaths}</span> / <span style={{color: '#4a9eff'}}>{match.assists}</span></p>
                  <p>Gold: {match.gold_earned.toLocaleString()}</p>
                  <p>Damage: {match.damage_dealt.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;