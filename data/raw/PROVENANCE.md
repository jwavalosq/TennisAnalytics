# Provenance: where every number comes from

## Original repo files, built on, not deleted

This project is built on the TennisAnalytics repo by jwavalosq
(github.com/jwavalosq/TennisAnalytics). The original repo files, preserved
as downloaded copies in this folder, are:

- `Dataset/Match.csv`, copied here as `Match.csv`
  - https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/Dataset/Match.csv
  - 10,160 rows, 9 columns: match_id, round, date, avg_minutes_game,
    avg_seconds_point, avg_minutes_set, tournament, year, match_minutes.
- `Dataset/Player.csv`, copied here as `Player.csv`
  - https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/Dataset/Player.csv
  - 53,666 rows, 5 columns: player_id, name, hand, country, birthday.
  - This is a long player list. Most listed players never appear in the
    Slam matches in Match.csv and Stats.csv.
- `Dataset/Stats.csv`, copied here as `Stats.csv`
  - https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/Dataset/Stats.csv
  - 20,240 rows, 24 columns: match_id, player_id, pts, rank, winner, sets,
    set scores 1 to 5, avg_odds, max_odds, total_pts, service_pts, return_pts,
    aces, bp_saved, bp_faced, first_serve_rtn_won, second_serve_rtn_won,
    first_serve_in, dbl_faults, first_serve_per.
- The original README stub, copied here as `original_README.md`
  - https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/README.md
  - It says only: TennisAnalytics, Data Analytics applied on one of the
    best sports on earth: Tennis.
- The original LICENSE (MIT, copyright 2024 Jesus Wladimir Avalos Quizhpi),
  copied here as `original_LICENSE`
  - https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/LICENSE

Coverage of the original files, checked in notebook 01:

- Men's singles only, at the four Grand Slams only.
- Years 2000 to 2019. Dates run from 2000-01-17 to 2019-12-07.
- 508 matches per year, 2,540 per Slam, 127 matches per Slam per year.
- Rounds: 1st Round 5,120; 2nd Round 2,560; 3rd Round 1,280; 4th Round 640;
  Quarterfinals 320; Semifinals 160; The Final 80.
- Stats.csv covers 10,120 matches, not 10,160. 40 matches in Match.csv have
  no Stats rows and blank timing columns. They are excluded from every
  serve and win rate number.
- No surface column. Surface is mapped from tournament name:
  Australian Open is Hard, French Open is Clay, US Open is Hard,
  Wimbledon is Grass. This mapping is used only for the original data.
- No seed column. Rank at match time is used instead, and is called rank,
  not seed, wherever it matters.
- No women's data. No matches after 2019. No data past the Slams.
- No official body is cited as the source of the original CSVs inside the
  files themselves. Treat original repo figures as repo figures, not as
  official ATP figures, unless the same number is also confirmed in the
  Sackmann supplement, which is labelled separately.

## Supplement: Sackmann tour data, via an archive mirror

The task brief suggested Jeff Sackmann's tennis_atp data. On 2026-11-03 the
original repos returned 404:

- https://github.com/JeffSackmann/tennis_atp (404)
- https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv (404)

Independent reports found in web search confirm the original Sackmann ATP
and WTA repos were no longer public in 2026. The files used here come from
the archival mirror that states it preserves Sackmann's data and asks users
to attribute Jeff Sackmann:

- Mirror repo: https://github.com/Aneeshers/tennis-sackmann-archive
- Mirror files used, in `sackmann_atp/`:
  - https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_2000.csv
    through atp_matches_2024.csv (one file per year, 2000 to 2024)
- Mirror files used, in `sackmann_wta/`:
  - https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/wta/wta_matches_2000.csv
    through wta_matches_2024.csv (one file per year, 2000 to 2024)
- Attribution: match results and stats compiled by Jeff Sackmann,
  redistributed by the archive mirror. Every supplement number in this
  project is labelled "Sackmann supplement" so it is never mixed silently
  with original repo numbers.

Coverage of the supplement, checked in notebook 06:

- ATP: 74,906 matches, tourney dates 2000-01-03 to 2024-12-18.
  Surfaces: Hard 40,871; Clay 24,244; Grass 7,699; Carpet 2,039; blank 53.
- WTA: 68,624 matches, tourney dates 2000-01-03 to 2024-11-25.
- Slam finals in the supplement, 2000 to 2024: 99 men's finals and 99
  women's finals. The expected 100 is short by one because Wimbledon 2020
  was cancelled, so 2020 has three finals, not four. That is a real event
  cancellation, not missing data.
- The supplement already carries a surface column, so no tournament to
  surface mapping is needed for supplement numbers.

## How to rebuild

1. `python scripts/download_data.py` (refetches every URL above)
2. `python scripts/build_processed.py` (builds data/processed/)
3. `python scripts/build_notebooks.py` (writes notebooks/)
4. `python -m nbconvert --to notebook --execute --inplace notebooks/*.ipynb`

Nothing in this project was published, pushed, posted, or signed into.
This is a local build only.
