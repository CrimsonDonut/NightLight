import os

high_score_file = "highscore.txt"

def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    else:
        return 0

def save_high_score(score):
    with open(high_score_file, "w") as f:
        f.write(str(score))

