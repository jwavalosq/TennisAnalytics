# BUILD REPORT: Tennis Analytics, Serve, Surface, and Eras

Local build only. Nothing was published, pushed, posted, or signed into.

## Files used

Original repo (jwavalosq/TennisAnalytics, main branch, Dataset folder):

- Match.csv: 10,160 rows, 9 columns.
- Player.csv: 53,666 rows, 5 columns.
- Stats.csv: 20,240 rows, 24 columns.
- README stub and MIT LICENSE, copied as original_README.md and
  original_LICENSE in data/raw/ for reference.

No original repo file was deleted or overwritten. This project works in a
fresh local folder and builds on downloaded copies in data/raw/.

Supplement (Sackmann data, via archive mirror):

- Aneeshers/tennis-sackmann-archive, atp_matches_2000.csv to
  atp_matches_2024.csv: 74,906 rows combined.
- Same mirror, wta_matches_2000.csv to wta_matches_2024.csv: 68,624 rows
  combined.
- Attribution to Jeff Sackmann, as requested by the mirror.
- Full URLs are in data/raw/PROVENANCE.md.

## What ran

- `python scripts/download_data.py`: fetched the original files and the
  Sackmann supplement. Files already present are skipped, not refetched.
- `python scripts/build_processed.py`: built 11 processed CSVs in
  data/processed/, including slam_player_matches.csv (20,240 rows),
  slam_player_summary.csv, slam_surface_win_rates.csv, slam_upsets.csv,
  slam_finals_2000_2019.csv, sackmann_atp_2000_2024.csv,
  sackmann_wta_2000_2024.csv, both Sackmann Slam finals files,
  tour_surface_win_rates.csv, and tour_versatility.csv.
- `python scripts/build_notebooks.py`: wrote 6 notebooks.
- `python -m nbconvert --to notebook --execute --inplace notebooks/*.ipynb`:
  all 6 notebooks executed end to end with zero cell errors.
- Chart count: 16 charts in charts/, copied to docs/charts/.

Notebooks and chart counts:

- 01_data_and_coverage.ipynb: 11 cells, 1 chart.
- 02_serve_dominance.ipynb: 13 cells, 3 charts.
- 03_surface_specialists.ipynb: 12 cells, 3 charts.
- 04_big_three_eras.ipynb: 13 cells, 3 charts.
- 05_grand_slam_trends.ipynb: 13 cells, 3 charts.
- 06_supplement_and_limits.ipynb: 14 cells, 3 charts.

## What failed or was approximated

1. Original Sackmann URLs 404. The first fetch of
   raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv
   and the matching player file returned 404, and the GitHub API for the
   JeffSackmann/tennis_atp repo also returned 404. Fix: used the
   Aneeshers/tennis-sackmann-archive mirror, with attribution to
   Jeff Sackmann, and documented the change in PROVENANCE.md and notebook 06.
   This is a source substitution, not a data invention: the mirror states
   it archives Sackmann's files.
2. `jupyter nbconvert` was not on the command path in this environment.
   Fix: ran `python -m nbconvert` instead. Same tool, same result.
3. First notebook build failed with a SyntaxError: the top cell used
   `pip install` as plain Python. Fix: changed it to `%pip install`, as a
   proper notebook magic, in scripts/build_notebooks.py, then rebuilt.
4. First draft of the 2020 to 2024 summary miscounted titles (Djokovic 7,
   Nadal 2). Fix: recounting from the printed finals table gave Djokovic 8
   and Nadal 3. The corrected numbers are in notebook 06 and in README.md.
5. Approximations, all labelled in code and notebooks:
   - Surface for original data is mapped from tournament name.
   - Service points played is first_serve_in / first_serve_per.
   - First serve points won is derived from the opponent row (see
     scripts/build_processed.py for the full reasoning).
   - SDI counts aces twice on purpose, once alone and once inside first
     serve points won.
   - Versatility ignores Carpet and needs 50 matches on each of Clay,
     Grass, and Hard.

## What was cut and why

- Maps: no geographic data in either source, and no map was faked.
- Seed analysis: the original files have no seed column, so rank bands
  are used and are called ranks, not seeds.
- Betting odds analysis: avg_odds and max_odds are blank for 10,388 of
  20,240 Stats rows, so no odds claim is made.
- Full tour SDI: Sackmann serve stat coverage is uneven by year and
  event, so SDI is computed only on the original Slam data, where the
  columns are consistent.
- Full women's serve comparison: the original repo has no women's serve
  data to compare with, so the women's supplement is used only for Slam
  finals in notebook 06.
- Years after 2024: the supplement files used here end in 2024. No 2025
  or 2026 result is claimed.
- Prediction model: none was built. This is a descriptive story project,
  and a model would need a separate validation design.

## Numbers that were verified, and where

- Winners 10.11 aces per match vs losers 7.34; first serve won 0.769 vs
  0.661; break points saved 0.681 vs 0.560: notebook 02 output.
- Aces by surface grass 10.73, hard 9.00, clay 6.16: notebook 02 output.
- SDI leaders Isner 75.68, Karlovic 73.56, Raonic 68.53: notebook 02 output.
- Versatility Djokovic 0.810, Federer 0.776, Nadal 0.747; Nadal clay 0.902:
  notebook 03 output.
- Big Three 55 of 80 Slams, 55 of 68 from 2003: notebook 04 output.
- Big Three Slam meetings 45, Nadal 19, Djokovic 16, Federer 10:
  notebook 04 output.
- Upsets 2,867 of 10,120, 28.3 percent, round one 30.4 percent:
  notebook 05 output.
- Rank bands: Rank 1 won 31 Slams, ranks 2 to 4 won 31: notebook 05 code
  and finals file.
- Recent Slams 2020 to 2024: Djokovic 8, Alcaraz 4, Nadal 3, Sinner 2,
  Thiem 1, Medvedev 1: notebook 06 output.
- Women's Slams 2000 to 2024: Serena Williams 22, Venus Williams 7,
  Justine Henin 7: notebook 06 output.

## What could not be verified

- The original repo files do not state their own upstream source inside
  the CSVs, so original repo figures are reported as repo figures, not
  as official ATP figures.
- Whether the archive mirror's Sackmann files match the original
  Sackmann files row for row could not be checked, because the originals
  are offline. The mirror's own provenance statement is reported instead.
- Player birthdays and country codes in Player.csv were not used for any
  claim, because many rows are for players outside the Slam matches and
  some birthdays are blank. No age claim is made.
- The 40 matches missing from Stats.csv could not be recovered from the
  original repo, because they have no Stats rows there either. They are
  counted and excluded, not filled in.

## Em dash check

Every file in this folder was checked for the em dash character, excluding
no directory except none needed (there is no virtual environment here).
No em dash was found in project files written by this build. The check
command and its result are recorded in the final report to the parent agent.
