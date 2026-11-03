"""Build processed CSVs from data/raw/ into data/processed/.

Run from the project root:
    python scripts/build_processed.py

Key definitions, stated once so every notebook uses the same numbers:
- Surface is NOT a column in the original repo files. It is mapped from
  tournament name, using the well known home surface of each Slam:
  Australian Open and US Open are Hard, French Open is Clay,
  Wimbledon is Grass. This mapping is used only for the original repo
  data. The Sackmann supplement already carries a surface column.
- Service points played, for one player in one match, is estimated as
  first_serve_in divided by first_serve_per. The file stores
  first_serve_per as a decimal, so this estimate is close but not exact.
- First serve points won, for one player, is derived from the opponent
  row in the same match: first_serve_in minus the opponent's
  first_serve_rtn_won. Why this works: first_serve_rtn_won plus
  second_serve_rtn_won equals return_pts for that player, so
  first_serve_rtn_won is the points the returner won against first
  serves. The server's first serve points won is what is left.
  Small rounding differences are possible. This is a derived estimate,
  not a column printed in the source file.
- Serve Dominance Index (SDI), original metric for this project, per
  player match: (aces + first_serve_won - double_faults) divided by
  service points played, times 100. Read it as serve dominance points
  per 100 service points. Aces are counted again inside first serve
  points won, on purpose, so big servers score higher. It is not a
  percentage and it can be above 50.
- Surface Versatility Score, original metric for this project, per
  player on the Sackmann tour data: mean win rate across Clay, Grass
  and Hard, minus the standard deviation of those three win rates.
  Carpet is ignored because it is rare after 2000. A high score needs
  both a high win rate and a balanced win rate. Minimum 50 matches on
  each of Clay, Grass and Hard.
- Upset, in this project, means the match winner had a worse (higher)
  rank number than the loser at match time, using the rank column in
  Stats.csv. Seed is not in the original repo files, so rank bands are
  used instead of seeds, and this is stated wherever seeds are discussed.
"""
import glob
import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "data", "processed")
SURFACE_MAP = {
    "Australian Open": "Hard",
    "French Open": "Clay",
    "US Open": "Hard",
    "Wimbledon": "Grass",
}
BIG3 = {
    "atp_103819": "Roger Federer",
    "atp_104745": "Rafael Nadal",
    "atp_104925": "Novak Djokovic",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    match = pd.read_csv(os.path.join(RAW, "Match.csv"))
    player = pd.read_csv(os.path.join(RAW, "Player.csv"))
    stats = pd.read_csv(os.path.join(RAW, "Stats.csv"))

    # Opponent first serve return won, per match.
    opp = {}
    for mid, g in stats.groupby("match_id"):
        if len(g) == 2:
            a, b = g.iloc[0], g.iloc[1]
            opp[(mid, a["player_id"])] = b["first_serve_rtn_won"]
            opp[(mid, b["player_id"])] = a["first_serve_rtn_won"]

    df = stats.merge(match, on="match_id").merge(player, on="player_id")
    df["surface"] = df["tournament"].map(SURFACE_MAP)
    df["opp_first_rtn_won"] = [
        opp.get((mid, pid), np.nan)
        for mid, pid in zip(df["match_id"], df["player_id"])
    ]
    df["svpt_played"] = df["first_serve_in"] / df["first_serve_per"]
    df["first_won"] = df["first_serve_in"] - df["opp_first_rtn_won"]
    df["first_won_rate"] = df["first_won"] / df["first_serve_in"]
    df["sdi"] = (df["aces"] + df["first_won"] - df["dbl_faults"]) / df["svpt_played"] * 100
    df["bp_save_rate_match"] = df["bp_saved"] / df["bp_faced"]
    df.to_csv(os.path.join(OUT, "slam_player_matches.csv"), index=False)

    # Player aggregates, Slam data only.
    rows = []
    for (pid, name), g in df.groupby(["player_id", "name"]):
        bp_faced = g["bp_faced"].sum()
        rows.append(
            {
                "player_id": pid,
                "name": name,
                "matches": len(g),
                "wins": int(g["winner"].sum()),
                "win_rate": g["winner"].mean(),
                "aces_per_match": g["aces"].mean(),
                "dbl_faults_per_match": g["dbl_faults"].mean(),
                "first_serve_per_mean": g["first_serve_per"].mean(),
                "first_won_rate_mean": g["first_won_rate"].mean(),
                "sdi_mean": g["sdi"].mean(),
                "bp_save_rate": g["bp_saved"].sum() / bp_faced if bp_faced else np.nan,
            }
        )
    pd.DataFrame(rows).sort_values("matches", ascending=False).to_csv(
        os.path.join(OUT, "slam_player_summary.csv"), index=False
    )

    # Win rate by surface, Slam data only.
    surf = (
        df.groupby(["player_id", "name", "surface"])
        .agg(matches=("winner", "size"), wins=("winner", "sum"))
        .reset_index()
    )
    surf["win_rate"] = surf["wins"] / surf["matches"]
    surf.to_csv(os.path.join(OUT, "slam_surface_win_rates.csv"), index=False)

    # Match level upset table.
    w = stats[stats["winner"] == True][["match_id", "rank"]].rename(columns={"rank": "winner_rank"})
    l = stats[stats["winner"] == False][["match_id", "rank"]].rename(columns={"rank": "loser_rank"})
    up = match.merge(w, on="match_id").merge(l, on="match_id")
    up["upset"] = up["winner_rank"] > up["loser_rank"]
    up.to_csv(os.path.join(OUT, "slam_upsets.csv"), index=False)

    # Slam finals, original repo data.
    finals = df[(df["round"] == "The Final") & (df["winner"] == True)][
        ["year", "tournament", "surface", "name", "player_id", "rank"]
    ].sort_values(["year", "tournament"])
    finals.to_csv(os.path.join(OUT, "slam_finals_2000_2019.csv"), index=False)

    # Sackmann tour data, ATP and WTA, 2000 to 2024.
    atp_files = sorted(glob.glob(os.path.join(RAW, "sackmann_atp", "atp_matches_*.csv")))
    atp = pd.concat([pd.read_csv(f) for f in atp_files], ignore_index=True)
    atp.to_csv(os.path.join(OUT, "sackmann_atp_2000_2024.csv"), index=False)
    wta_files = sorted(glob.glob(os.path.join(RAW, "sackmann_wta", "wta_matches_*.csv")))
    wta = pd.concat([pd.read_csv(f) for f in wta_files], ignore_index=True)
    wta.to_csv(os.path.join(OUT, "sackmann_wta_2000_2024.csv"), index=False)

    # Sackmann Slam finals, ATP and WTA.
    for data, label in [(atp, "atp"), (wta, "wta")]:
        gs = data[(data["tourney_level"] == "G") & (data["round"] == "F")].copy()
        gs["year"] = gs["tourney_date"].astype(str).str[:4].astype(int)
        gs[["year", "tourney_name", "surface", "winner_name", "loser_name", "winner_seed", "winner_rank"]].to_csv(
            os.path.join(OUT, f"sackmann_{label}_slam_finals.csv"), index=False
        )

    # Tour surface win rates and versatility, Sackmann ATP.
    wlong = atp[["surface", "winner_name"]].rename(columns={"winner_name": "name"})
    wlong["won"] = 1
    llong = atp[["surface", "loser_name"]].rename(columns={"loser_name": "name"})
    llong["won"] = 0
    long = pd.concat([wlong, llong])
    tour = (
        long.groupby(["name", "surface"]).agg(matches=("won", "size"), wins=("won", "sum")).reset_index()
    )
    tour["win_rate"] = tour["wins"] / tour["matches"]
    tour.to_csv(os.path.join(OUT, "tour_surface_win_rates.csv"), index=False)
    piv = tour.pivot(index="name", columns="surface", values="win_rate")
    cnt = tour.pivot(index="name", columns="surface", values="matches")
    keep = piv[(cnt[["Clay", "Grass", "Hard"]] >= 50).all(axis=1)].dropna(subset=["Clay", "Grass", "Hard"])
    vers = keep[["Clay", "Grass", "Hard"]].copy()
    vers["mean_win_rate"] = vers[["Clay", "Grass", "Hard"]].mean(axis=1)
    vers["std_win_rate"] = vers[["Clay", "Grass", "Hard"]].std(axis=1)
    vers["versatility"] = vers["mean_win_rate"] - vers["std_win_rate"]
    vers = vers.reset_index().sort_values("versatility", ascending=False)
    vers.to_csv(os.path.join(OUT, "tour_versatility.csv"), index=False)

    print(f"slam player matches: {len(df)}")
    print(f"ATP Sackmann rows: {len(atp)}, WTA rows: {len(wta)}")
    print("done")


if __name__ == "__main__":
    main()
