import requests
from bs4 import BeautifulSoup
import pandas as pd
from configs.fbref import championship_url
import re
from pathlib import Path


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


if __name__ == "__main__":
    championship = Tables(championship_url)

    # championship.overall_standings_table = pd.DataFrame(['Bristol City', 'Bristol Rovers'], columns=['Squad'])
    print(championship.find_team("Preston North End FC"))

    # write_df_to_csv(champ_tbl, "champ_tbl")
