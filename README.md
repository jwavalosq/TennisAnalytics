# Tennis Analytics: What Wins Grand Slam Matches

I love tennis, and I wanted to answer a simple question with real data: what actually wins matches at the four Grand Slams? I built this project to find out, and to tell the story in plain words that anyone can follow, even if they have never watched a match.

Read the story version: https://jwavalosq.github.io/TennisAnalytics/

## The question I started with

Tennis has four Grand Slams, the four biggest stages in the sport: the Australian Open, the French Open, Wimbledon, and the US Open. Win one, and you are remembered. Win many, and you define an era.

I started with 10,160 men's singles matches from those four tournaments, from 2000 to 2019. Then I added a supplement that carries the story to 2024 and brings in the women's game. My question was simple. Is it the serve? Is it the surface? Or is it simply that three men were better than everyone else for almost twenty years? The answer, it turns out, is all three.

## Why it matters

If you coach, scout, or just watch tennis, you need to know which skills decide matches and which ones only look decisive. A huge serve is exciting, but this data shows it is not enough on its own. The court under your feet changes what works. And an era can be so dominated by three players that the rest of the field is really playing for fourth place. I wanted numbers behind those intuitions, not just opinions.

## What I did, step by step

First, I loaded the original match, player, and stats files and checked what was actually in them. I found 40 matches with no stats rows at all. I counted them and left them out, rather than filling them in.

Second, I compared match winners with losers on the serve: aces, first serve points won, and break points saved.

Third, I split everything by surface, clay, grass, and hard, and built two original scores of my own. The Serve Dominance Index (SDI) combines aces, first serve points won, and double faults into one number per 100 service points. The Surface Versatility Score rewards winning a lot and winning evenly across all three surfaces.

Fourth, I traced the Big Three era, Federer, Nadal, and Djokovic, title by title and match by match against each other.

Fifth, I looked at who wins Slams by rank, how often the underdog wins, and how long matches last on each surface.

Sixth, I added the supplement. The original Sackmann data files returned 404 errors in November 2026, so I used an archive mirror of Sackmann's files, with full attribution to Jeff Sackmann, and documented the switch. That supplement covers the full men's and women's tours from 2000 to 2024: 74,906 men's rows and 68,624 women's rows.

The work is six notebooks and 16 charts, all executed end to end with zero cell errors. Every number in this README comes from those notebooks.

## What I found

**The serve decides matches.** Match winners averaged 10.11 aces per match, against 7.34 for losers. Winners won 76.9 percent of their first serve points, losers won 66.1 percent. Winners saved 68.1 percent of break points faced, losers saved 56.0 percent.

**The surface changes the serve.** Average aces per player match were 10.73 on grass, 9.00 on hard, and 6.16 on clay. First serve points won followed the same order: 74.0 percent on grass, 71.6 percent on hard, 68.8 percent on clay. Clay matches lasted longest on average, 148.9 minutes, against 143.6 on hard and 133.2 on grass.

**A huge serve alone did not win a Slam here.** On my Serve Dominance Index, John Isner leads at 75.68, then Ivo Karlovic at 73.56, then Milos Raonic at 68.53, for players with at least 50 Slam matches. SDI is serve dominance points per 100 service points, not a percentage. Neither Isner nor Karlovic won a Slam in this window.

**Versatility belongs to Djokovic.** On my Surface Versatility Score, Novak Djokovic leads at 0.810 on the full tour from 2000 to 2024, then Roger Federer at 0.776, then Rafael Nadal at 0.747. Nadal is the clay specialist: 0.902 on clay on tour, against 0.784 on grass and 0.772 on hard. Federer leads on grass at 0.878.

**Three men owned the era.** Federer, Nadal, and Djokovic won 55 of the 80 Slams from 2000 to 2019. All 55 came from 2003 onward, so they won 55 of 68 Slams from 2003 to 2019. When they played each other at Slams in this data, 45 matches in total, Nadal won 19, Djokovic won 16, and Federer won 10.

**The underdog wins more often than you might think.** When the lower ranked player won, that happened in 28.3 percent of Slam matches (2,867 of 10,120). It was most common in round one, at 30.4 percent. Rank 1 players won 31 of the 80 Slams, and ranks 2 to 4 won another 31. The top four ranks won 62 of 80.

**After 2019, the story continued.** From 2020 to 2024, Djokovic won 8 Slams, Carlos Alcaraz won 4, Nadal won 3, Jannik Sinner won 2, and Dominic Thiem and Daniil Medvedev won 1 each. In the women's game from 2000 to 2024, Serena Williams won 22 Slams, then Venus Williams and Justine Henin with 7 each.

## What it means, and who it helps

For a coach, the lesson is to build the serve first, but never stop there. The best servers in this data did not win Slams. The players who won Slams served well and did everything else well, on every surface. For a fan, the lesson is that eras are real. For almost two decades, the question at a Slam was rarely who would win. It was which of three men would win. For anyone learning data analytics, this project shows how to turn a sports question into a clean chain: check the data, compare groups, build a fair score, and say plainly what the score cannot prove.

## How to run it yourself

```
python scripts/download_data.py
python scripts/build_processed.py
python scripts/build_notebooks.py
python -m nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

Charts are in `charts/`. Processed tables are in `data/processed/`. The story site is in `docs/index.html`, with chart copies in `docs/charts/`.

The notebooks, in order:

1. `notebooks/01_data_and_coverage.ipynb`: what the original files contain, and the 40 matches missing from Stats.csv.
2. `notebooks/02_serve_dominance.ipynb`: aces, first serve points won, break points saved, and the Serve Dominance Index.
3. `notebooks/03_surface_specialists.ipynb`: win rates by surface and the Surface Versatility Score.
4. `notebooks/04_big_three_eras.ipynb`: Big Three titles, timelines, and matches against each other.
5. `notebooks/05_grand_slam_trends.ipynb`: titles by surface, winners by rank band, upsets by round, and match length by surface.
6. `notebooks/06_supplement_and_limits.ipynb`: Slams 2020 to 2024, the full tour, and the women's game, from the Sackmann supplement.

A few words I use in this project: an ace is a serve the opponent does not touch. A double fault is two missed serves in a row, so the server loses the point. A break point is a chance for the returner to win the server's service game, and saving it means the server held on. An upset here means the match winner had a worse rank number than the loser at match time. Surface is what the court is made of. Clay is slow, grass is fast, hard sits in between.

## What the limits are

I state these plainly, because they shape every finding above.

- The original data covers men's Slam singles only, 2000 to 2019. No women's matches, no other tournaments, no years after 2019.
- Surface in the original data is mapped from tournament name, not printed in the file. The supplement already has a surface column.
- The original data has rank, not seed. Rank bands are used, and are called ranks, not seeds.
- First serve points won is derived from the opponent's row, not printed in the file. The derivation is written out in `scripts/build_processed.py`.
- The Sackmann supplement comes from an archive mirror, because the original Sackmann repos returned 404 in November 2026. See `data/raw/PROVENANCE.md` for every URL and for the attribution to Jeff Sackmann.
- No maps, no betting odds analysis, and no prediction model. Odds columns exist in the original file but are mostly blank, and this project does not use them.

Full detail is in `BUILD_REPORT.md`, including how every number was verified and what could not be verified. This project was built locally and then published to this repo. It does not delete or overwrite any original repo file. It builds on downloaded copies in `data/raw/`.
