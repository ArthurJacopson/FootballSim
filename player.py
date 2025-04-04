import random


class Player:
    def __init__(self, player_id, name, team_name, position, shooting, passing, dribbling, defending, goalkeeping,
                 playstyle):
        self.player_id = player_id
        self.name = name
        self.team_name = team_name
        self.position = position
        self.stats = {
            "Shooting": int(shooting),
            "Passing": int(passing),
            "Dribbling": int(dribbling),
            "Defending": int(defending),
            "Goalkeeping": int(goalkeeping)
        }
        self.playstyle = playstyle

        self.actions = {
            "Pass": {
                "BaseOdds": {"Midfield 1st Side": 70, "Midfield 2nd Side": 70, "1st Side Close to Goal": 60,
                             "1st Side Penalty Area": 50, "2nd Side Close to Goal": 60, "2nd Side Penalty Area": 50},
                "Stat": "Passing",
                "OppStat": "Defending",
                "Outcomes": {"Success": ["Ball passed to teammate"], "Failure": ["Intercepted", "Out of bounds"]}
            },
            "Dribble": {
                "BaseOdds": {"Midfield 1st Side": 60, "Midfield 2nd Side": 60, "1st Side Close to Goal": 55,
                             "1st Side Penalty Area": 50, "2nd Side Close to Goal": 55, "2nd Side Penalty Area": 50},
                "Stat": "Dribbling",
                "OppStat": "Defending",
                "Outcomes": {"Success": ["Advances forward"], "Failure": ["Tackled", "Out of bounds"]}
            },
            "Shoot": {
                "BaseOdds": {"Midfield 1st Side": 10, "Midfield 2nd Side": 10, "1st Side Close to Goal": 20,
                             "1st Side Penalty Area": 40, "2nd Side Close to Goal": 20, "2nd Side Penalty Area": 40},
                "Stat": "Shooting",
                "OppStat": "Goalkeeping",
                "Outcomes": {"Success": ["Goal!"], "Failure": ["Saved by keeper", "Corner kick", "Out of bounds"]}
            },
            "Long Pass": {
                "BaseOdds": {"Midfield 1st Side": 50, "Midfield 2nd Side": 50, "1st Side Close to Goal": 40,
                             "1st Side Penalty Area": 30, "2nd Side Close to Goal": 40, "2nd Side Penalty Area": 30},
                "Stat": "Passing",
                "OppStat": "Defending",
                "Outcomes": {"Success": ["Ball reaches forward line"], "Failure": ["Intercepted", "Out of bounds"]}
            },
            "Tackle": {
                "BaseOdds": {"Midfield 1st Side": 60, "Midfield 2nd Side": 60, "1st Side Close to Goal": 65,
                             "1st Side Penalty Area": 70, "2nd Side Close to Goal": 65, "2nd Side Penalty Area": 70},
                "Stat": "Defending",
                "OppStat": "Dribbling",
                "Outcomes": {"Success": ["Ball won"], "Failure": ["Foul committed", "Player keeps ball"]}
            }
        }

        self.playstyle_modifiers = {
            "Creative": {"Pass": 10, "Long Pass": 15, "Shoot": -10, "Dribble": 0, "Tackle": -5},
            "Aggressive": {"Dribble": 10, "Shoot": 10, "Tackle": 10, "Pass": -10, "Long Pass": -5},
            "Defensive": {"Pass": 10, "Tackle": 15, "Dribble": -10, "Shoot": -10, "Long Pass": 0},
            "Balanced": {"Pass": 0, "Dribble": 0, "Shoot": 0, "Long Pass": 0, "Tackle": 0}
        }

    def choose_action(self, current_sector, is_defending=False):
        if is_defending:
            available_actions = ["Tackle"]
        else:
            available_actions = ["Pass", "Dribble", "Shoot", "Long Pass"] if self.position != "GK" else ["Pass",
                                                                                                         "Long Pass"]

        weights = []
        for action in available_actions:
            base_odds = self.actions[action]["BaseOdds"][current_sector]
            modifier = self.playstyle_modifiers[self.playstyle].get(action, 0)
            weights.append(base_odds + modifier)

        return random.choices(available_actions, weights=weights, k=1)[0]

    def perform_action(self, opponent, current_sector, is_defending=False):
        chosen_action = self.choose_action(current_sector, is_defending)
        action_data = self.actions[chosen_action]

        base_odds = action_data["BaseOdds"][current_sector]
        stat_value = self.stats[action_data["Stat"]]
        opp_stat_value = opponent.stats[action_data["OppStat"]]
        final_odds = max(0, min(100, base_odds + (stat_value // 2) - (opp_stat_value // 2)))

        roll = random.randint(1, 100)
        outcome = random.choice(action_data["Outcomes"]["Success" if roll <= final_odds else "Failure"])

        return chosen_action, outcome, final_odds, roll

    def __str__(self):
        return f"{self.name} ({self.team_name}, {self.position})"