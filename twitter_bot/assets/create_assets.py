from pyfootball.football import Football
from typing import List, Dict, Any
import csv
from pathlib import Path
import requests.exceptions
from dagster import asset


@asset
def get_comp_ids() -> List[Dict[str, Any]]:
    """
    Function to get all the competitions available from the football-data.org API.
    Returns:
        competition_ids and competition_names
    """
    fbl = Football()
    comps = fbl.get_all_competitions()
    return [{"comp_id": comp.id, "comp_name": comp.name} for comp in comps]


@asset
def write_comp_ids(get_comp_ids):
    """
    Function to create a csv containing all the competition IDs and names for those available
    in the football-data.org API
    """
    path = Path.cwd().parent.parent / "data" / "comp_ids.csv"
    with open(path, mode="w", encoding="utf-8") as csv_file:
        fieldnames = ["comp_id", "comp_name"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in get_comp_ids:
            writer.writerow(row)


@asset
def championship_id():
    return 2016


@asset
def get_comp_team_ids(championship_id) -> List[Dict[str, Any]]:
    """
    Given a comp_id, returns all the teams involved from the football-data.org API.
    Returns:
        team_ids and team_names
    """
    fbl = Football()
    teams = fbl.get_competition_teams(championship_id)
    return [{"team_id": team.id, "team_name": team.name} for team in teams]


@asset
def write_comp_team_ids(championship_id, get_comp_team_ids):
    """
    Given a comp_id, creates a csv containing all the team IDs and names involved
    for those available in the football-data.org API
    """
    path = Path.cwd().parent.parent / "data" / f"team_ids_{championship_id}.csv"
    try:
        with open(path, mode="w", encoding="utf-8") as csv_file:
            fieldnames = ["team_id", "team_name"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in get_comp_team_ids:
                writer.writerow(row)
    except requests.exceptions.HTTPError:
        print(f"Competition ID {championship_id} not found.")
        path.unlink()
