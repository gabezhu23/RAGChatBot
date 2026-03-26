from nba_api.stats.endpoints import leaguedashplayerstats
from database import engine, SessionLocal, Base
from models import Player
import time

Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    
    # Clear existing data
    db.query(Player).delete()
    db.commit()
    
    seasons = ["2021-22", "2022-23", "2023-24"]
    
    for season in seasons:
        print(f"Fetching {season} season data...")
        
        try:
            stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                per_mode_detailed="PerGame"
            )
            
            df = stats.get_data_frames()[0]
            
            for _, row in df.iterrows():
                player = Player(
                    name=row["PLAYER_NAME"],
                    team=row["TEAM_ABBREVIATION"],
                    season=season,
                    games_played=int(row["GP"]),
                    points_per_game=float(row["PTS"]),
                    assists_per_game=float(row["AST"]),
                    rebounds_per_game=float(row["REB"]),
                    steals_per_game=float(row["STL"]),
                    blocks_per_game=float(row["BLK"]),
                    field_goal_pct=float(row["FG_PCT"]),
                    three_point_pct=float(row["FG3_PCT"]),
                    free_throw_pct=float(row["FT_PCT"]),
                    minutes_per_game=float(row["MIN"])
                )
                db.add(player)
            
            db.commit()
            print(f"Seeded {len(df)} players for {season}")
            
            # Be polite to the NBA API
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching {season}: {e}")
            db.rollback()
    
    db.close()
    print("Database seeded successfully")

if __name__ == "__main__":
    seed_database()