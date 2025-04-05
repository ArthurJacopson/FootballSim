import random

class Team:
    def __init__(self, name, players=None):
        self.name = name
        self.players = players if players else []  # All players (active + substitutes)
        self.active_players = self.players[:11] if len(self.players) >= 11 else self.players[:]  # Starting 11
        self.substitutes = self.players[11:] if len(self.players) > 11 else []  # Bench
        self.score = 0

    def add_player(self, player):
        self.players.append(player)
        if len(self.active_players) < 11:
            self.active_players.append(player)
        else:
            self.substitutes.append(player)

    def get_player_by_position(self, position, active_only=True):
        pool = self.active_players if active_only else self.players
        position_players = [p for p in pool if p.position == position]
        return random.choice(position_players) if position_players else None

    def substitute_player(self, tired_player):
        if self.substitutes:
            sub = random.choice(self.substitutes)
            self.active_players[self.active_players.index(tired_player)] = sub
            self.substitutes.remove(sub)
            self.substitutes.append(tired_player)
            print(f"Substitution: {tired_player.name} (Fatigue: {tired_player.fatigue}) replaced by {sub.name}")
            tired_player.fatigue = 0  # Reset fatigue for the benched player
            return sub
        return tired_player

    def __str__(self):
        return f"{self.name} (Score: {self.score})"