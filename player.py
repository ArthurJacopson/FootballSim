import random


class Player:
    def __init__(self, player_id, name, team_name, position, shooting, passing, dribbling, defending, goalkeeping,
                 playstyle):
        self.player_id = player_id
        self.name = name
        self.team_name = team_name
        self.position = position
        self.shooting = int(shooting)
        self.passing = int(passing)
        self.dribbling = int(dribbling)
        self.defending = int(defending)
        self.goalkeeping = int(goalkeeping)
        self.playstyle = playstyle
        self.fatigue = 0
        self.yellow_cards = 0
        self.red_card = False

        # Position tracking
        self.current_sector = None
        self.default_sector = {
            "Galatasaray": {"GK": "1st Side Penalty Area", "DF": "1st Side Close to Goal", "MF": "Midfield 1st Side",
                            "FW": "Midfield 2nd Side"},
            "Fenerbahçe": {"GK": "2nd Side Penalty Area", "DF": "2nd Side Close to Goal", "MF": "Midfield 2nd Side",
                           "FW": "Midfield 1st Side"}
        }[team_name][position]
        self.current_sector = self.default_sector

        self.actions = {
            "Pass": {
                "BaseOdds": {
                    "Midfield 1st Side": 70, "Midfield 2nd Side": 70,
                    "1st Side Close to Goal": 60, "1st Side Penalty Area": 50,
                    "2nd Side Close to Goal": 60, "2nd Side Penalty Area": 50
                },
                "Outcomes": {"Success": "Ball passed to teammate", "Fail": "Intercepted"}
            },
            "Dribble": {
                "BaseOdds": {
                    "Midfield 1st Side": 60, "Midfield 2nd Side": 60,
                    "1st Side Close to Goal": 55, "1st Side Penalty Area": 50,
                    "2nd Side Close to Goal": 55, "2nd Side Penalty Area": 50
                },
                "Outcomes": {"Success": "Advances forward", "Fail": "Tackled"}
            },
            "Shoot": {
                "BaseOdds": {
                    "Midfield 1st Side": 20, "Midfield 2nd Side": 20,
                    "1st Side Close to Goal": 40, "1st Side Penalty Area": 60,
                    "2nd Side Close to Goal": 40, "2nd Side Penalty Area": 60
                },
                "Outcomes": {"Success": "Goal!", "Fail": "Saved by keeper"}
            },
            "Long Pass": {
                "BaseOdds": {
                    "Midfield 1st Side": 50, "Midfield 2nd Side": 50,
                    "1st Side Close to Goal": 40, "1st Side Penalty Area": 30,
                    "2nd Side Close to Goal": 40, "2nd Side Penalty Area": 30
                },
                "Outcomes": {"Success": "Ball reaches forward line", "Fail": "Out of bounds"}
            },
            "Gain Control": {
                "BaseOdds": {
                    "Midfield 1st Side": 50, "Midfield 2nd Side": 50,
                    "1st Side Close to Goal": 50, "1st Side Penalty Area": 50,
                    "2nd Side Close to Goal": 50, "2nd Side Penalty Area": 50
                },
                "Outcomes": {"Success": "Ball controlled", "Fail": "Ball remains loose"}
            },
            "Tackle": {
                "BaseOdds": {
                    "Midfield 1st Side": 60, "Midfield 2nd Side": 60,
                    "1st Side Close to Goal": 65, "1st Side Penalty Area": 70,
                    "2nd Side Close to Goal": 65, "2nd Side Penalty Area": 70
                },
                "Outcomes": {"Success": "Ball won", "Fail": "Foul committed"}
            }
        }

        self.playstyle_modifiers = {
            "Aggressive": {"Shoot": 10, "Dribble": 5, "Tackle": 10, "Pass": -5},
            "Creative": {"Pass": 10, "Dribble": 10, "Shoot": 5, "Long Pass": 5},
            "Defensive": {"Tackle": 15, "Defending": 10, "Pass": 5, "Shoot": -10},
            "Balanced": {"Pass": 5, "Dribble": 5, "Shoot": 5, "Tackle": 5}
        }

    def __str__(self):
        return f"{self.name} ({self.team_name}, {self.position}, Sector: {self.current_sector}, Fatigue: {self.fatigue}, Cards: {self.yellow_cards + (2 if self.red_card else 0)})"

    def choose_action(self, current_sector, is_defending=False, ball_loose=False):
        if ball_loose:
            available_actions = ["Gain Control"]
            weights = [100]
        elif is_defending:
            available_actions = ["Tackle"]
            weights = [100]
        else:
            if self.position == "GK" and (
                    ("1st Side Penalty Area" in current_sector and self.team_name == "Galatasaray") or
                    ("2nd Side Penalty Area" in current_sector and self.team_name == "Fenerbahçe")):
                available_actions = ["Long Pass", "Pass"]
            else:
                available_actions = ["Pass", "Dribble", "Shoot", "Long Pass"] if self.position != "GK" else ["Pass",
                                                                                                             "Long Pass"]

            is_attacking_half = (self.team_name == "Galatasaray" and "2nd Side" in current_sector) or \
                                (self.team_name == "Fenerbahçe" and "1st Side" in current_sector)
            weights = []
            for action in available_actions:
                base_odds = self.actions[action]["BaseOdds"][current_sector]
                modifier = self.playstyle_modifiers[self.playstyle].get(action, 0)
                if is_attacking_half:
                    if action == "Shoot" and "Penalty" in current_sector:
                        modifier += 30
                    elif action == "Pass" and "Penalty" in current_sector:
                        modifier -= 20
                    elif action == "Long Pass" and "Penalty" in current_sector:
                        modifier -= 30
                weights.append(max(1, base_odds + modifier))

        return random.choices(available_actions, weights=weights, k=1)[0]

    def perform_action(self, opponent, current_sector, is_defending=False, ball_loose=False):
        chosen_action = self.choose_action(current_sector, is_defending, ball_loose)
        base_odds = self.actions[chosen_action]["BaseOdds"][current_sector]
        modifier = self.playstyle_modifiers[self.playstyle].get(chosen_action, 0)
        odds = max(1, min(100, base_odds + modifier))
        roll = random.randint(1, 100)
        outcome = self.actions[chosen_action]["Outcomes"]["Success"] if roll <= odds else \
        self.actions[chosen_action]["Outcomes"]["Fail"]

        # Corner kick chance after a save
        if chosen_action == "Shoot" and outcome == "Saved by keeper" and random.random() < 0.3:
            outcome = "Saved and out for corner"

        if chosen_action == "Tackle" and outcome == "Foul committed":
            self.yellow_cards += 1
            if self.yellow_cards >= 2 or random.random() < 0.1:
                self.red_card = True

        self.fatigue += random.randint(1, 5)
        return chosen_action, outcome, odds, roll