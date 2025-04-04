import random

class Team:
    def __init__(self, name, players=None):
        self.name = name
        self.players = players if players else []
        self.score = 0

    def add_player(self, player):
        self.players.append(player)

    def get_player_by_position(self, position):
        position_players = [p for p in self.players if p.position == position]
        return random.choice(position_players) if position_players else None

    def __str__(self):
        return f"{self.name} (Score: {self.score})"