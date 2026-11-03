# Tennis Analytics: Serve, Surface, and Eras

A beginner friendly story about men's tennis at the Grand Slams, from 2000
to 2019, with a supplement that carries the story to 2024 and adds the
women's game.

## The story in one minute

Tennis has four Grand Slams. Think of them as the four biggest stages in
the sport: the Australian Open, the French Open, Wimbledon, and the US Open.
Win one, and you are remembered. Win many, and you define an era.

This project starts with a simple question: what actually wins Slam
matches? The answer is not one thing. A huge serve helps a lot. Grass helps
servers most, clay helps them least. And for almost two decades, three men
won almost everything.

Here are the verified headline numbers. Every one comes from the notebooks,
and every notebook says which data it used.

- Serve: match winners averaged 10.11 aces per match, losers averaged 7.34.
  Winners won 76.9 percent of their first serve points, losers won 66.1 percent.
  Winners saved 68.1 percent of break points faced, losers saved 56.0 percent.
- Surface: average aces per player match were 10.73 on grass, 9.00 on hard,
  and 6.16 on clay. First serve points won followed the same order: 74.0
  percent on grass, 71.6 percent on hard, 68.8 percent on clay. Clay matches
  lasted longest on average, 148.9 minutes, against 143.6 on hard and 133.2
  on grass.
- A new score, the Serve Dominance Index (SDI): (aces + first serve points
  won - double faults) / service points played x 100. John Isner leads at
  75.68, then Ivo Karlovic at 73.56, then Milos Raonic at 68.53, for players
  with at least 50 Slam matches. SDI is serve dominance points per 100
  service points. It is not a percentage. A huge serve alone did not win a
  Slam here: neither Isner nor Karlovic won one in this window.
- A second new score, the Surface Versatility Score: mean win rate across
  clay, grass, and hard, minus how spread out those three win rates are.
  On the full tour from 2000 to 2024, Novak Djokovic leads at 0.810, then
  Roger Federer at 0.776, then Rafael Nadal at 0.747. Nadal is the clay
  specialist: 0.902 on clay on tour, against 0.784 on grass and 0.772 on hard.
  Federer leads on grass at 0.878.
- The Big Three: Federer, Nadal, and Djokovic won 55 of the 80 Slams from
  2000 to 2019. All 55 came from 2003 onward, so they won 55 of 68 Slams from
  2003 to 2019. In Slam matches against each other in this data (45 matches),
  Nadal won 19, Djokovic won 16, and Federer won 10.
- Upsets: when the lower ranked player won, that happened in 28.3 percent
  of Slam matches (2,867 of 10,120). It was most common in round one, at
  30.4 percent. Rank 1 players won 31 of the 80 Slams, and ranks 2 to 4 won
  another 31. The top four ranks won 62 of 80.
- After 2019 (Sackmann supplement): from 2020 to 2024, Djokovic won 8 Slams,
  Carlos Alcaraz won 4, Nadal won 3, Jannik Sinner won 2, and Dominic Thiem
  and Daniil Medvedev won 1 each. In the women's game from 2000 to 2024,
  Serena Williams won 22 Slams, then Venus Williams and Justine Henin with
  7 each.

## What each notebook does

1. `notebooks/01_data_and_coverage.ipynb`: what the original files contain,
   and the 40 matches missing from Stats.csv.
2. `notebooks/02_serve_dominance.ipynb`: aces, first serve points won,
   break points saved, and the Serve Dominance Index.
3. `notebooks/03_surface_specialists.ipynb`: win rates by surface and the
   Surface Versatility Score.
4. `notebooks/04_big_three_eras.ipynb`: Big Three titles, timelines, and
   matches against each other.
5. `notebooks/05_grand_slam_trends.ipynb`: titles by surface, winners by
   rank band, upsets by round, and match length by surface.
6. `notebooks/06_supplement_and_limits.ipynb`: Slams 2020 to 2024, the full
   tour, and the women's game, from the Sackmann supplement.

## Words used in this project

- Ace: a serve the opponent does not touch.
- Double fault: two missed serves in a row, so the server loses the point.
- Break point: a chance for the returner to win the server's service game.
  Saving it means the server held on.
- Upset (in this project): the match winner had a worse rank number than
  the loser at match time.
- Surface: what the court is made of. Clay is slow, grass is fast, hard
  sits in between.

## Honest cuts

- The original data covers men's Slam singles only, 2000 to 2019. No
  women's matches, no other tournaments, no years after 2019.
- Surface in the original data is mapped from tournament name, not printed
  in the file. The supplement already has a surface column.
- The original data has rank, not seed. Rank bands are used, and are called
  ranks, not seeds.
- First serve points won is derived from the opponent's row, not printed
  in the file. The derivation is written out in `scripts/build_processed.py`.
- The Sackmann supplement comes from an archive mirror, because the
  original Sackmann repos returned 404 in November 2026. See
  `data/raw/PROVENANCE.md` for every URL and for the attribution to
  Jeff Sackmann.
- No maps, no betting odds analysis, and no prediction model. Odds columns
  exist in the original file but are mostly blank, and this project does
  not use them.

## Run it yourself

```
python scripts/download_data.py
python scripts/build_processed.py
python scripts/build_notebooks.py
python -m nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

Charts are in `charts/`. Processed tables are in `data/processed/`.
The story site is in `docs/index.html`, with chart copies in `docs/charts/`.

Original repo: github.com/jwavalosq/TennisAnalytics. This local build does
not delete or overwrite any original repo file. It builds on downloaded
copies in `data/raw/`.

Nothing here was published, pushed, posted, or signed into.
