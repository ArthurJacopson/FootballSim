import random
import csv
from team import Team
from player import Player
from ball import Ball


class Game:
    def __init__(self, team1_name, team2_name, csv_file="players.csv"):
        self.team1 = Team(team1_name)  # Defends 1st Side
        self.team2 = Team(team2_name)  # Defends 2nd Side
        self.load_players(csv_file)
        self.current_tick = 0
        self.max_ticks = 90
        self.ball = Ball(["Midfield 1st Side", "Midfield 2nd Side", "1st Side Close to Goal",
                          "1st Side Penalty Area", "2nd Side Close to Goal", "2nd Side Penalty Area"])
        self.sectors = self.ball.sectors  # Alias for convenience
        self.half_time = False

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

        print(f"Team 1 ({self.team1.name}) active players: {len(self.team1.active_players)}")
        for p in self.team1.active_players:
            print(f"  {p}")
        print(f"Team 2 ({self.team2.name}) active players: {len(self.team2.active_players)}")
        for p in self.team2.active_players:
            print(f"  {p}")

    def start_game(self):
        kickoff_team = random.choice([self.team1, self.team2])
        kickoff_player = kickoff_team.get_player_by_position("MF") or random.choice(kickoff_team.active_players)
        self.ball.set_possession(kickoff_team, kickoff_player,
                                 "Midfield 1st Side" if kickoff_team == self.team1 else "Midfield 2nd Side")
        print(
            f"Game starts! {self.ball.team.name} kicks off from {self.ball.current_sector} with {self.ball.player.name}.")

    def update_sector(self, action, outcome, direction):
        current_idx = self.sectors.index(self.ball.current_sector)
        if action == "Dribble" and "Advances" in outcome:
            new_idx = max(0, min(len(self.sectors) - 1, current_idx + direction * 2))
            if direction == 1 and current_idx >= 2:  # Fenerbahçe attacking 1st Side
                new_idx = min(3, new_idx)
            elif direction == -1 and current_idx <= 3:  # Galatasaray attacking 2nd Side
                new_idx = max(4, new_idx)
            self.ball.current_sector = self.sectors[new_idx]
        elif action == "Long Pass" and "reaches" in outcome:
            new_idx = max(0, min(len(self.sectors) - 1, current_idx + direction * 3))
            self.ball.current_sector = self.sectors[new_idx]

    def handle_out_of_bounds(self, last_team):
        if "Penalty" in self.ball.current_sector or "Close to Goal" in self.ball.current_sector:
            if (last_team == self.team1 and "1st Side" in self.ball.current_sector) or (
                    last_team == self.team2 and "2nd Side" in self.ball.current_sector):
                self.ball.team = self.team2 if "1st Side" in self.ball.current_sector else self.team1
                self.ball.player = self.ball.team.get_player_by_position("GK")
                self.ball.current_sector = "1st Side Penalty Area" if self.ball.team == self.team1 else "2nd Side Penalty Area"
                self.ball.possessed = True
                print(
                    f"Goal kick! {self.ball.team.name}'s {self.ball.player.name} restarts from {self.ball.current_sector}.")
            else:
                self.ball.team = self.team1 if "1st Side" in self.ball.current_sector else self.team2
                self.ball.player = self.ball.team.get_player_by_position("MF") or random.choice(
                    self.ball.team.active_players)
                self.ball.current_sector = "1st Side Penalty Area" if self.ball.team == self.team1 else "2nd Side Penalty Area"
                self.ball.possessed = True
                print(
                    f"Corner kick! {self.ball.team.name}'s {self.ball.player.name} takes it from {self.ball.current_sector}.")
        else:
            self.ball.team = self.team2 if last_team == self.team1 else self.team1
            self.ball.player = self.ball.team.get_player_by_position("DF") or random.choice(
                self.ball.team.active_players)
            self.ball.possessed = True
            print(
                f"Throw-in! {self.ball.team.name}'s {self.ball.player.name} takes it from {self.ball.current_sector}.")

    def move_players(self):
        ball_idx = self.sectors.index(self.ball.current_sector)
        for player in self.team1.active_players + self.team2.active_players:
            if player == self.ball.player:  # Ball possessor stays with the ball
                player.current_sector = self.ball.current_sector
                continue
            current_idx = self.sectors.index(player.current_sector)
            target_idx = ball_idx
            direction = -1 if player.team_name == self.team1.name else 1

            if self.ball.possessed and self.ball.team is not None:  # Ball is possessed
                if player.team_name == self.ball.team.name:  # Teammates
                    if player.position == "FW":
                        target_idx = ball_idx + direction * 2  # Push toward opponent’s goal
                    elif player.position == "MF":
                        target_idx = ball_idx  # Stay near ball
                    elif player.position == "DF":
                        target_idx = ball_idx - direction * 1  # Stay slightly back
                    elif player.position == "GK":
                        target_idx = 3 if player.team_name == "Galatasaray" else 5  # Own penalty area
                else:  # Opponents
                    if player.position == "FW":
                        target_idx = ball_idx + direction * 1  # Chase the ball
                    elif player.position == "MF":
                        target_idx = ball_idx  # Mark the ball
                    elif player.position == "DF" or player.position == "GK":
                        target_idx = 3 if player.team_name == "Fenerbahçe" else 5  # Defend goal
            else:  # Ball is loose or uninitialized
                if player.position == "FW" or player.position == "MF":
                    target_idx = ball_idx  # Move toward loose ball
                elif player.position == "DF":
                    target_idx = ball_idx - direction * 1  # Stay slightly back
                elif player.position == "GK":
                    target_idx = 3 if player.team_name == "Galatasaray" else 5  # Stay in goal

            target_idx = max(0, min(len(self.sectors) - 1, target_idx))
            if random.random() < 0.5 and current_idx != target_idx:  # 50% chance to move
                step = 1 if target_idx > current_idx else -1
                player.current_sector = self.sectors[current_idx + step]

    def simulate_tick(self):
        if self.current_tick == 45 and not self.half_time:
            print("\nHalf Time! Teams head to the locker room.")
            self.half_time = True
            kickoff_team = random.choice([self.team1, self.team2])
            kickoff_player = kickoff_team.get_player_by_position("MF") or random.choice(kickoff_team.active_players)
            self.ball.set_possession(kickoff_team, kickoff_player,
                                     "Midfield 1st Side" if kickoff_team == self.team1 else "Midfield 2nd Side")
            print(
                f"Second half starts! {self.ball.team.name} kicks off from {self.ball.current_sector} with {self.ball.player.name}.")
            return

        self.move_players()

        if not self.ball.possessed:
            self.ball.team = random.choice([self.team1, self.team2])
            self.ball.player = self.ball.team.get_player_by_position("MF") or random.choice(
                self.ball.team.active_players)
            opponent_team = self.team2 if self.ball.team == self.team1 else self.team1
            opponent = opponent_team.get_player_by_position("DF") or random.choice(opponent_team.active_players)

            action, outcome, odds, roll = self.ball.player.perform_action(opponent, self.ball.current_sector,
                                                                          ball_loose=True)
            print(
                f"Tick {self.current_tick}: {self.ball.player.name} ({self.ball.team.name}) attempts to {action.lower()} in {self.ball.current_sector}")
            print(f"Success Odds: {odds}% | Roll: {roll} | Outcome: {outcome}")

            if "controlled" in outcome:
                self.ball.possessed = True
        else:
            opponent_team = self.team2 if self.ball.team == self.team1 else self.team1
            if "1st Side Penalty Area" in self.ball.current_sector:
                opponent = self.team1.get_player_by_position(
                    "GK") if self.ball.team == self.team2 else opponent_team.get_player_by_position("DF")
            elif "2nd Side Penalty Area" in self.ball.current_sector:
                opponent = self.team2.get_player_by_position(
                    "GK") if self.ball.team == self.team1 else opponent_team.get_player_by_position("DF")
            else:
                opponent = opponent_team.get_player_by_position("DF") or random.choice(opponent_team.active_players)
            opponent = opponent or random.choice(opponent_team.active_players)

            action, outcome, odds, roll = self.ball.player.perform_action(opponent, self.ball.current_sector)
            print(
                f"Tick {self.current_tick}: {self.ball.player.name} ({self.ball.team.name}) attempts to {action.lower()} in {self.ball.current_sector}")
            print(f"Success Odds: {odds}% | Roll: {roll} | Outcome: {outcome}")

            direction = -1 if self.ball.team == self.team1 else 1
            if "Goal" in outcome:
                self.ball.team.score += 1
                kickoff_team = opponent_team
                self.ball.set_possession(kickoff_team, kickoff_team.get_player_by_position("MF") or random.choice(
                    kickoff_team.active_players),
                                         "Midfield 1st Side" if kickoff_team == self.team1 else "Midfield 2nd Side")
                print(
                    f"Goal! {self.ball.team.name} will restart from {self.ball.current_sector} with {self.ball.player.name}.")
            elif "Intercepted" in outcome or "Tackled" in outcome:
                self.ball.team = opponent_team
                self.ball.player = opponent
                def_action, def_outcome, def_odds, def_roll = opponent.perform_action(self.ball.player,
                                                                                      self.ball.current_sector,
                                                                                      is_defending=True)
                print(f"  {opponent.name} ({opponent_team.name}) counters with {def_action.lower()}:")
                print(f"  Success Odds: {def_odds}% | Roll: {def_roll} | Outcome: {def_outcome}")
                if "Ball won" in def_outcome:
                    self.ball.player = opponent
                elif "Foul" in def_outcome:
                    if opponent.red_card:
                        opponent_team.active_players.remove(opponent)
                        print(
                            f"{opponent.name} sent off! {opponent_team.name} down to {len(opponent_team.active_players)} players.")
                    self.ball.set_loose(self.ball.current_sector)
            elif "Out" in outcome:
                self.handle_out_of_bounds(self.ball.team)
            elif "Saved and out for corner" in outcome:
                self.ball.team = self.ball.team  # Attacking team keeps possession
                self.ball.player = self.ball.team.get_player_by_position("MF") or random.choice(
                    self.ball.team.active_players)
                self.ball.current_sector = "2nd Side Penalty Area" if self.ball.team == self.team1 else "1st Side Penalty Area"
                self.ball.possessed = True
                print(
                    f"Corner kick! {self.ball.team.name}'s {self.ball.player.name} takes it from {self.ball.current_sector}.")
            elif "reaches" in outcome:
                self.ball.player = self.ball.team.get_player_by_position("FW") or random.choice(
                    self.ball.team.active_players)
                print(f"  Ball reaches {self.ball.player.name}.")
            elif "passed" in outcome:
                nearby_players = [p for p in self.ball.team.active_players if
                                  abs(self.sectors.index(p.current_sector) - self.sectors.index(
                                      self.ball.current_sector)) <= 2 and p != self.ball.player]
                self.ball.player = random.choice(nearby_players) if nearby_players else random.choice(
                    self.ball.team.active_players)
                print(f"  Ball passed to {self.ball.player.name}.")

            self.update_sector(action, outcome, direction)

        if self.ball.player and self.ball.player.fatigue > 80 and random.random() < 0.3:
            self.ball.player = self.ball.team.substitute_player(self.ball.player)

    def run_game(self):
        self.start_game()
        for tick in range(1, self.max_ticks + 1):
            self.current_tick = tick
            self.simulate_tick()
        print("\nFinal Whistle! Match ends.")
        print(f"Final Score: {self.team1} - {self.team2}")


if __name__ == "__main__":
    game = Game("Galatasaray", "Fenerbahçe")
    game.run_game()