import csv
import random

# Mock data with defenders included
teams = {
    "Galatasaray": ["Victor Osimhen", "Mauro Icardi", "Hakim Ziyech", "Kerem Aktürkoğlu", "Fernando Muslera",
                    "Barış Alper Yılmaz", "Davinson Sánchez"],
    "Fenerbahçe": ["Edin Džeko", "Dušan Tadić", "Joshua King", "İrfan Kahveci", "Dominik Livaković",
                   "Bright Osayi-Samuel", "Çağlar Söyüncü"],
    "Beşiktaş": ["Cenk Tosun", "Alex Oxlade-Chamberlain", "Rachid Ghezzal", "Gedson Fernandes", "Mert Günok",
                 "Necip Uysal", "Omar Colley"],
    "Trabzonspor": ["Paul Onuachu", "Mahmoud Trézéguet", "Edin Višća", "Anastasios Bakasetas", "Uğurcan Çakır",
                    "Jens Stryger Larsen", "Stefano Denswil"]
}

positions = {"Forward": "FW", "Midfielder": "MF", "Defender": "DF", "Goalkeeper": "GK"}
playstyles = ["Creative", "Aggressive", "Defensive", "Balanced"]


def generate_stats(position):
    if position == "GK":
        return {
            "Shooting": 0,
            "Passing": random.randint(30, 50),
            "Dribbling": random.randint(20, 40),
            "Defending": random.randint(40, 60),
            "Goalkeeping": random.randint(70, 95)
        }
    elif position == "DF":
        return {
            "Shooting": random.randint(30, 60),
            "Passing": random.randint(50, 80),
            "Dribbling": random.randint(40, 70),
            "Defending": random.randint(70, 95),
            "Goalkeeping": 0
        }
    else:
        return {
            "Shooting": random.randint(50, 90),
            "Passing": random.randint(50, 90),
            "Dribbling": random.randint(50, 90),
            "Defending": random.randint(50, 90),
            "Goalkeeping": 0
        }


def create_players_csv(filename="players.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["PlayerID", "Name", "Team", "Position", "Shooting", "Passing", "Dribbling", "Defending", "Goalkeeping",
             "PlayStyle"])

        player_id = 1
        for team, players in teams.items():
            for player in players:
                if "Muslera" in player or "Livaković" in player or "Günok" in player or "Çakır" in player:
                    position = "GK"
                elif player in ["Victor Osimhen", "Mauro Icardi", "Edin Džeko", "Joshua King", "Cenk Tosun",
                                "Paul Onuachu"]:
                    position = "FW"
                elif player in ["Hakim Ziyech", "Kerem Aktürkoğlu", "Dušan Tadić", "İrfan Kahveci",
                                "Alex Oxlade-Chamberlain",
                                "Rachid Ghezzal", "Gedson Fernandes", "Mahmoud Trézéguet", "Edin Višća",
                                "Anastasios Bakasetas"]:
                    position = "MF"
                else:
                    position = "DF"

                stats = generate_stats(position)
                playstyle = random.choice(playstyles)
                writer.writerow([
                    player_id, player, team, position,
                    stats["Shooting"], stats["Passing"], stats["Dribbling"], stats["Defending"], stats["Goalkeeping"],
                    playstyle
                ])
                player_id += 1

    print(f"CSV file '{filename}' generated successfully!")


if __name__ == "__main__":
    create_players_csv()