from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, engine
from models import Player, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NBA Stats API")

@app.get("/")
def root():
    return {"message": "NBA Stats API is running"}

@app.get("/players/{player_name}")
def get_player(player_name: str, db: Session = Depends(get_db)):
    players = db.query(Player).filter(
        func.lower(Player.name).contains(player_name.lower())
    ).all()
    if not players:
        raise HTTPException(status_code=404, detail="Player not found")
    return players

@app.get("/teams/{team}/roster")
def get_team_roster(team: str, season: str = "2023-24", db: Session = Depends(get_db)):
    players = db.query(Player).filter(
        func.lower(Player.team) == team.lower(),
        Player.season == season
    ).all()
    if not players:
        raise HTTPException(status_code=404, detail="Team not found")
    return players

@app.get("/stats/leaders")
def get_leaders(
    category: str = "points",
    season: str = "2023-24",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    category_map = {
        "points": Player.points_per_game,
        "assists": Player.assists_per_game,
        "rebounds": Player.rebounds_per_game,
        "steals": Player.steals_per_game,
        "blocks": Player.blocks_per_game
    }
    if category not in category_map:
        raise HTTPException(status_code=400, detail=f"Category must be one of {list(category_map.keys())}")
    
    players = db.query(Player).filter(
        Player.season == season,
        Player.games_played >= 20
    ).order_by(category_map[category].desc()).limit(limit).all()
    return players

@app.get("/players/{player_name}/history")
def get_player_history(player_name: str, db: Session = Depends(get_db)):
    players = db.query(Player).filter(
        func.lower(Player.name).contains(player_name.lower())
    ).order_by(Player.season).all()
    if not players:
        raise HTTPException(status_code=404, detail="Player not found")
    return players