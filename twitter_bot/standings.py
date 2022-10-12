import requests
from bs4 import BeautifulSoup
import pandas as pd
from configs.fbref import championship_url
import re
from pathlib import Path
from functools import partialmethod


def write_df_to_csv(df: pd.DataFrame, name: str):
    path = Path.cwd().parent / "data" / f"{name}.csv"
    df.to_csv(path, header=True, index=False)


class Tables:
    def __init__(self, url):
        self.url = url
        self.overall_standings_table = self.get_overall_standings_table()

    def get_overall_standings_table(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find(
            "table", {"id": re.compile("(results).*(overall)")}
        )  # results2022-2023101_overall
        headers = []
        for i in table.find_all("th", {"scope": "col"}):
            headers.append(i.text)

        df = pd.DataFrame(columns=headers)

        for row in table.find_all("tr")[1:]:
            length = len(df)
            row_text = [str(length + 1)] + [i.text for i in row.find_all("td")]
            df.loc[len(df)] = row_text
        df["Squad"] = df["Squad"].str.strip()
        return df

    def find_team(self, team_name):
        """
        Given a team_name, looks to match up with teams within the overall_standings_table.
        i.e. if supplying 'Preston North End FC', returns 'Preston'
        Returns:
            str: Name of team in table
        """
        search_name = ""
        for sub_name in team_name.split():
            search_name += " " + sub_name
            search_name = search_name.lstrip()
            contains = self.overall_standings_table["Squad"].str.contains(search_name)
            matches = contains.sum()
            if matches == 1:
                return self.overall_standings_table[contains]["Squad"].item()
            if matches > 1:
                continue
        return None

    def _get_team_stat(self, team_name: str, stat: str):
        team_name = self.find_team(team_name)
        tbl = self.overall_standings_table
        return tbl.loc[tbl["Squad"] == f"{team_name}"][f"{stat}"].item()

    get_team_form = partialmethod(_get_team_stat, stat="Last 5")
    get_team_position = partialmethod(_get_team_stat, stat="Rk")
    get_team_games_played = partialmethod(_get_team_stat, stat="MP")
    get_team_wins = partialmethod(_get_team_stat, stat="W")
    get_team_draws = partialmethod(_get_team_stat, stat="D")
    get_team_loss = partialmethod(_get_team_stat, stat="L")
    get_team_goals_for = partialmethod(_get_team_stat, stat="GF")
    get_team_goals_against = partialmethod(_get_team_stat, stat="GA")
    get_team_goal_difference = partialmethod(_get_team_stat, stat="GD")
    get_team_points = partialmethod(_get_team_stat, stat="Pts")
    get_team_top_scorer = partialmethod(_get_team_stat, stat="Top Team Scorer")

    @staticmethod
    def form_to_emoji(form: str):
        win = "\U0001F7E2"
        draw = "\U0001F7E1"
        loss = "\U0001F534"
        form = form.replace("W", win).replace("D", draw).replace("L", loss)
        return form

    def runner_get_form_emoji(self, team_name):
        return self.form_to_emoji(self.get_team_form(team_name))

    def collect_stats(self, team_name: str):
        return {
            "position": self.get_team_position(team_name),
            "wins": self.get_team_wins(team_name),
            "draws": self.get_team_draws(team_name),
            "loss": self.get_team_loss(team_name),
            "goals_for": self.get_team_goals_for(team_name),
            "goals_against": self.get_team_goals_against(team_name),
            "form_emoji": self.runner_get_form_emoji(team_name),
            "top_scorer": self.get_team_top_scorer(team_name),
        }


if __name__ == "__main__":
    championship = Tables(championship_url)
    _team_name = "Burnley"
    print(championship.runner_get_form_emoji(_team_name))
    print(championship.get_team_position(_team_name))
    print(championship.get_team_games_played(_team_name))

    print(championship.overall_standings_table.columns)
