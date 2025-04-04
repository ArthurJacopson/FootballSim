import random
import csv
from team import Team
from player import Player


class Game:
    def __init__(self, team1_name, team2_name, csv_file="players.csv"):
        self.team1 = Team(team1_name)
        self.team2 = Team(team2_name)
        self.load_players(csv_file)
        self.current_tick = 0
        self.max_ticks = 90
        self.ball_team = None
        self.ball_player = None
        self.sectors = ["Midfield 1st Side", "Midfield 2nd Side", "1st Side Close to Goal",
                        "1st Side Penalty Area", "2nd Side Close to Goal", "2nd Side Penalty Area"]
        self.current_sector = None

    def load_players(self, csv_file):
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                player = Player(row["PlayerID"], row["Name"], row["Team"], row["Position"],
                                row["Shooting"], row["Passing"], row["Dribbling"],
                                row["Defending"], row["Goalkeeping"], row["PlayStyle"])
                if player.team_name == self.team1.name:
                    self.team1.add_player(player)
                elif player.team_name == self.team2.name:
                    self.team2.add_player(player)

        print(f"Team 1 ({self.team1.name}) players: {len(self.team1.players)}")
        for p in self.team1.players:
            print(f"  {p.name}, {p.position}")
        print(f"Team 2 ({self.team2.name}) players: {len(self.team2.players)}")
        for p in self.team2.players:
            print(f"  {p.name}, {p.position}")

    def start_game(self):
        self.ball_team = random.choice([self.team1, self.team2])
        self.ball_player = self.ball_team.get_player_by_position("MF")
        if self.ball_player is None:
            print(f"Warning: No midfielder found for {self.ball_team.name}. Selecting a random player.")
            self.ball_player = random.choice(self.ball_team.players) if self.ball_team.players else None
        if self.ball_player is None:
            raise ValueError(f"No players available for {self.ball_team.name}. Check CSV data.")
        self.current_sector = "Midfield 1st Side" if self.ball_team == self.team1 else "Midfield 2nd Side"
        print(f"Game starts! {self.ball_team.name} kicks off with {self.ball_player.name}.")

    def update_sector(self, action, outcome):
        current_idx = self.sectors.index(self.current_sector)
        direction = 1 if self.ball_team == self.team2 else -1
        if action == "Dribble" and "Advances" in outcome:
            self.current_sector = self.sectors[max(0, min(len(self.sectors) - 1, current_idx + direction))]
        elif action == "Long Pass" and "reaches" in outcome:
            self.current_sector = self.sectors[max(0, min(len(self.sectors) - 1, current_idx + 2 * direction))]
        elif "Goal" in outcome or "Out" in outcome or "Corner" in outcome:
            self.current_sector = random.choice(["Midfield 1st Side", "Midfield 2nd Side"])

    def simulate_tick(self):
        opponent_team = self.team2 if self.ball_team == self.team1 else self.team1
        opponent = (opponent_team.get_player_by_position("DF") if "Penalty" not in self.current_sector
                    else opponent_team.get_player_by_position("GK"))

        if opponent is None:
            position_needed = "DF" if "Penalty" not in self.current_sector else "GK"
            print(f"Warning: No {position_needed} found for {opponent_team.name}. Selecting a random player.")
            opponent = random.choice(opponent_team.players)

        action, outcome, odds, roll = self.ball_player.perform_action(opponent, self.current_sector, is_defending=False)
        print(
            f"Tick {self.current_tick}: {self.ball_player.name} ({self.ball_team.name}) attempts to {action.lower()} in {self.current_sector}")
        print(f"Success Odds: {odds}% | Roll: {roll} | Outcome: {outcome}")

        if "Goal" in outcome:
            self.ball_team.score += 1
            self.ball_team = opponent_team
            self.ball_player = self.ball_team.get_player_by_position("MF") or random.choice(self.ball_team.players)
        elif "Intercepted" in outcome or "Tackled" in outcome:
            self.ball_team = opponent_team
            self.ball_player = opponent
            def_action, def_outcome, def_odds, def_roll = opponent.perform_action(self.ball_player, self.current_sector,
                                                                                  is_defending=True)
            print(f"  {opponent.name} ({opponent_team.name}) counters with {def_action.lower()}:")
            print(f"  Success Odds: {def_odds}% | Roll: {def_roll} | Outcome: {def_outcome}")
            if "Ball won" in def_outcome:
                self.ball_player = opponent
            elif "Foul" in def_outcome:
                self.ball_player = self.ball_team.get_player_by_position("MF") or random.choice(self.ball_team.players)
        elif "reaches" in outcome or "passed" in outcome:
            self.ball_player = self.ball_team.get_player_by_position(
                "FW" if "reaches" in outcome else "MF") or random.choice(self.ball_team.players)

        self.update_sector(action, outcome)

    def run_game(self):
        self.start_game()
        for tick in range(1, self.max_ticks + 1):
            self.current_tick = tick
            self.simulate_tick()
        print(f"\nFinal Score: {self.team1} - {self.team2}")


if __name__ == "__main__":
    game = Game("Galatasaray", "Fenerbahçe")
    game.run_game()