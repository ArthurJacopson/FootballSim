class Ball:
    def __init__(self, sectors):
        self.sectors = sectors
        self.current_sector = "Midfield 1st Side"  # Default starting position
        self.possessed = False  # Whether a player controls it
        self.team = None  # Team in possession (None if loose)
        self.player = None  # Player in possession (None if loose)

    def set_possession(self, team, player, sector):
        self.possessed = True
        self.team = team
        self.player = player
        self.current_sector = sector

    def set_loose(self, sector):
        self.possessed = False
        self.team = None
        self.player = None
        self.current_sector = sector

    def __str__(self):
        if self.possessed:
            return f"Ball with {self.player.name} ({self.team.name}) in {self.current_sector}"
        return f"Ball loose in {self.current_sector}"