"""Build the six notebooks in notebooks/ from code strings.

Each notebook starts with a pip install cell, then loads only the
processed CSVs in data/processed/, so reruns are fast. Charts are saved
to charts/ with matching file names. No em dash character is used
anywhere in this script, so none can leak into the notebooks.
Run: python scripts/build_notebooks.py
Then execute: jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
"""
import os

import nbformat as nbf

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NBDIR = os.path.join(BASE, "notebooks")
os.makedirs(NBDIR, exist_ok=True)

PIP = (
    "%pip install pandas matplotlib seaborn numpy\n"
    "import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns\n"
    "plt.rcParams['figure.dpi'] = 120\n"
    "sns.set_theme(style='whitegrid')"
)
LOAD = (
    "import os\n"
    "PROC = os.path.join('..', 'data', 'processed')\n"
    "CH = os.path.join('..', 'charts')\n"
    "os.makedirs(CH, exist_ok=True)"
)


def nb(cells, path):
    doc = nbf.v4.new_notebook()
    doc.cells = cells
    doc.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    nbf.write(doc, path)
    print(f"wrote {path}")


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


def head(title, intro):
    return [code(PIP), md(f"# {title}\n\n{intro}"), code(LOAD)]


# ---------------------------------------------------------------- 01
nb(
    head(
        "01. What data do we have?",
        "Start here. A Grand Slam is one of the four biggest tennis tournaments: "
        "the Australian Open, the French Open (also called Roland Garros), Wimbledon, "
        "and the US Open. This project uses the original TennisAnalytics repo files, "
        "which cover only men's singles at those four Slams, from 2000 to 2019. "
        "Later notebooks add a wider tour supplement, but this chapter first checks "
        "exactly what the original files contain, and what they do not contain.",
    )
    + [
        md(
            "## The three original files\n\n"
            "Match.csv has one row per match, with round, date, tournament, year, and "
            "match length. Stats.csv has two rows per match, one per player, with aces, "
            "double faults, break points, serve numbers, and rank. Player.csv is a long "
            "player list with name, playing hand, country, and birthday. It lists far "
            "more players than ever appear in these Slam matches, so do not be surprised "
            "by its size."
        ),
        code(
            "match = pd.read_csv('../data/raw/Match.csv')\n"
            "player = pd.read_csv('../data/raw/Player.csv')\n"
            "stats = pd.read_csv('../data/raw/Stats.csv')\n"
            "print('Match rows, columns:', match.shape, list(match.columns))\n"
            "print('Player rows, columns:', player.shape, list(player.columns))\n"
            "print('Stats rows, columns:', stats.shape, list(stats.columns))\n"
            "print('Years:', sorted(match.year.unique()))\n"
            "print('Tournaments:', sorted(match.tournament.unique()))\n"
            "print('Rounds:', match['round'].value_counts().to_dict())"
        ),
        md(
            "## Coverage, and one honest gap\n\n"
            "There are 10,160 rows in Match.csv, which is 127 matches times 4 Slams "
            "times 20 years. Stats.csv has 20,240 player rows, which is 2 players times "
            "10,120 matches. That means 40 matches in Match.csv have no Stats rows at "
            "all. Those 40 also have blank match length and timing columns. They are "
            "kept out of every serve and win rate number in this project, and they are "
            "counted here so the gap is visible, not hidden."
        ),
        code(
            "in_stats = set(stats.match_id)\n"
            "missing = match[~match.match_id.isin(in_stats)]\n"
            "print('Matches in Match.csv:', len(match))\n"
            "print('Matches with Stats rows:', len(in_stats))\n"
            "print('Matches missing from Stats.csv:', len(missing))\n"
            "print(missing.groupby(['year', 'tournament']).size())\n"
            "print('Date range:', match.date.min(), 'to', match.date.max())\n"
            "print('Players in Player.csv:', len(player), 'from', player.country.nunique(), 'country codes')"
        ),
        md("## Chart: matches by round. Every Slam draw has the same shape."),
        code(
            "counts = match['round'].value_counts()\n"
            "order = ['1st Round', '2nd Round', '3rd Round', '4th Round', 'Quarterfinals', 'Semifinals', 'The Final']\n"
            "vals = [counts[r] for r in order]\n"
            "plt.figure(figsize=(9, 4.5)); plt.bar(order, vals, color='#2a7f62')\n"
            "plt.title('Slam matches by round, 2000 to 2019 (all four Slams)'); plt.ylabel('Matches'); plt.xticks(rotation=25, ha='right')\n"
            "for i, v in enumerate(vals): plt.text(i, v + 80, str(v), ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/01_matches_by_round.png'); plt.show()"
        ),
        md(
            "## What is missing, in plain words\n\n"
            "No surface column. Surface is mapped from tournament name in the processed "
            "data: Australian Open and US Open are Hard, French Open is Clay, Wimbledon "
            "is Grass. No women's matches. No matches after 2019. No seed column, only a "
            "rank number at match time. Notebook 06 fills the recent years and the women's "
            "gap with the Sackmann supplement, and every later claim says which data it uses."
        ),
        code(
            "print('Original repo: mens Slam singles only, 2000 to 2019.')\n"
            "print('Supplement in notebook 06: Sackmann tour data, ATP and WTA, 2000 to 2024.')\n"
            "print('Surface in original data is mapped from tournament name, not printed in the file.')"
        ),
    ],
    os.path.join(NBDIR, "01_data_and_coverage.ipynb"),
)

# ---------------------------------------------------------------- 02
nb(
    head(
        "02. Serve dominance",
        "The serve is the one shot a player fully controls. An ace is a serve the "
        "opponent does not touch. A double fault is two missed serves in a row, so the "
        "server loses the point without a rally. A break point is a chance for the "
        "returner to win the server's service game. Saving it means the server held on. "
        "This chapter compares winners and losers on those three ideas, then builds one "
        "combined score, the Serve Dominance Index.",
    )
    + [
        md(
            "## How the Serve Dominance Index (SDI) works\n\n"
            "SDI is an original metric for this project. For one player in one match: "
            "SDI = (aces + first serve points won - double faults) / service points "
            "played x 100. Read it as serve dominance points per 100 service points. "
            "First serve points won is derived, not printed in the file: it is the "
            "server's first serves in, minus the points the opponent won returning "
            "first serves. Service points played is first serves in divided by first "
            "serve percentage. Aces appear twice on purpose, once alone and once inside "
            "first serve points won, so big servers score higher. SDI is not a percentage."
        ),
        code(
            "df = pd.read_csv(f'{PROC}/slam_player_matches.csv')\n"
            "print('Player match rows:', len(df))\n"
            "print(df.groupby('winner')[['aces', 'dbl_faults', 'first_serve_per', 'first_won_rate', 'sdi']].mean().round(3))\n"
            "print('Overall break points saved:', round(df.bp_saved.sum() / df.bp_faced.sum(), 4))\n"
            "print(df.groupby('winner').apply(lambda x: round(x.bp_saved.sum() / x.bp_faced.sum(), 4)))"
        ),
        md("## Chart: aces by surface. Grass rewards the serve most, clay least."),
        code(
            "g = df.groupby('surface')[['aces', 'dbl_faults', 'first_won_rate', 'sdi']].mean()\n"
            "print(g.round(3))\n"
            "plt.figure(figsize=(8, 4.5)); plt.bar(g.index, g['aces'], color=['#b5651d', '#2a7f62', '#3a6ea5'])\n"
            "plt.title('Average aces per player match, by surface (Slams, 2000 to 2019)'); plt.ylabel('Aces')\n"
            "for i, v in enumerate(g['aces']): plt.text(i, v + 0.3, f'{v:.2f}', ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/02_aces_by_surface.png'); plt.show()"
        ),
        md("## Chart: first serve points won, winners versus losers."),
        code(
            "w = df.groupby('winner')['first_won_rate'].mean()\n"
            "plt.figure(figsize=(7, 4.5)); plt.bar(['Loser', 'Winner'], [w[False], w[True]], color=['#c0392b', '#2a7f62'])\n"
            "plt.title('First serve points won rate, winners versus losers'); plt.ylabel('Share of first serves won'); plt.ylim(0, 1)\n"
            "for i, v in enumerate([w[False], w[True]]): plt.text(i, v + 0.03, f'{v:.3f}', ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/02_first_serve_winners_losers.png'); plt.show()"
        ),
        md(
            "## Chart: SDI leaders. Only players with at least 50 Slam matches are shown, "
            "so one great match cannot top the list."
        ),
        code(
            "summ = pd.read_csv(f'{PROC}/slam_player_summary.csv')\n"
            "top = summ[summ.matches >= 50].sort_values('sdi_mean', ascending=False).head(10)\n"
            "print(top[['name', 'matches', 'wins', 'aces_per_match', 'first_won_rate_mean', 'sdi_mean']].round(2).to_string(index=False))\n"
            "plt.figure(figsize=(9, 5)); plt.barh(top['name'][::-1], top['sdi_mean'][::-1], color='#3a6ea5')\n"
            "plt.title('Serve Dominance Index leaders, Slams 2000 to 2019 (min 50 matches)'); plt.xlabel('SDI, per 100 service points')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/02_sdi_leaders.png'); plt.show()"
        ),
        md(
            "## What SDI does not prove\n\n"
            "John Isner tops SDI and Ivo Karlovic is second, yet neither won a Slam in "
            "this window. A huge serve helps, but return, movement, and holding up over "
            "seven matches matter too. The highest SDI among the Big Three is Roger "
            "Federer, ahead of Novak Djokovic and Rafael Nadal, even though Nadal won "
            "the most Slams here on clay, where aces are rarest. Serve dominance is one "
            "skill, not the whole game."
        ),
        code(
            "for name in ['Roger Federer', 'Rafael Nadal', 'Novak Djokovic', 'John Isner', 'Ivo Karlovic']:\n"
            "    r = summ[summ.name == name].iloc[0]\n"
            "    print(f\"{name}: {int(r.matches)} matches, SDI {r.sdi_mean:.2f}, aces per match {r.aces_per_match:.2f}, break points saved {r.bp_save_rate:.3f}\")"
        ),
    ],
    os.path.join(NBDIR, "02_serve_dominance.ipynb"),
)

# ---------------------------------------------------------------- 03
nb(
    head(
        "03. Surface specialists",
        "A surface is what the court is made of. Clay is slow and the ball bounces high. "
        "Grass is fast and the ball stays low. Hard courts sit in between. A surface "
        "specialist is a player who wins far more on one surface than on the others. "
        "This chapter uses the Slam surface mapping from notebook 01, then checks it "
        "against the full tour, where players play many more matches on each surface.",
    )
    + [
        md(
            "## Surface Versatility Score, an original metric\n\n"
            "Versatility = mean win rate across Clay, Grass and Hard, minus the "
            "standard deviation of those three win rates. Standard deviation here just "
            "means how spread out the three numbers are. A player who wins a lot and "
            "wins evenly scores high. A player who wins a lot on one surface only loses "
            "points for the spread. Carpet is left out because it is rare after 2000. "
            "Minimum 50 tour matches on each of Clay, Grass and Hard."
        ),
        code(
            "surf = pd.read_csv(f'{PROC}/slam_surface_win_rates.csv')\n"
            "vers = pd.read_csv(f'{PROC}/tour_versatility.csv')\n"
            "print('Most versatile tour players, 2000 to 2024:')\n"
            "print(vers.head(10)[['name', 'Clay', 'Grass', 'Hard', 'mean_win_rate', 'std_win_rate', 'versatility']].round(3).to_string(index=False))\n"
            "for name in ['Rafael Nadal', 'Roger Federer', 'Novak Djokovic']:\n"
            "    r = vers[vers.name == name].iloc[0]\n"
            "    print(f\"{name}: Clay {r.Clay:.3f}, Grass {r.Grass:.3f}, Hard {r.Hard:.3f}, versatility {r.versatility:.3f}\")"
        ),
        md("## Chart: Big Three win rates by surface, full tour 2000 to 2024."),
        code(
            "big = vers[vers.name.isin(['Rafael Nadal', 'Roger Federer', 'Novak Djokovic'])].set_index('name')\n"
            "big[['Clay', 'Grass', 'Hard']].plot(kind='bar', figsize=(9, 5), color=['#b5651d', '#2a7f62', '#3a6ea5'])\n"
            "plt.title('Big Three win rates by surface, full tour 2000 to 2024'); plt.ylabel('Win rate'); plt.ylim(0, 1); plt.xticks(rotation=0)\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/03_big3_surface_win_rates.png'); plt.show()"
        ),
        md("## Chart: most versatile players on tour."),
        code(
            "top = vers.head(8)\n"
            "plt.figure(figsize=(9, 5)); plt.barh(top['name'][::-1], top['versatility'][::-1], color='#2a7f62')\n"
            "plt.title('Surface Versatility Score leaders, tour 2000 to 2024 (min 50 matches per surface)'); plt.xlabel('Versatility = mean win rate minus spread')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/03_versatility_leaders.png'); plt.show()"
        ),
        md(
            "## Chart: Slam win rates by surface for the same three players, as a check. "
            "The story is the same, but the numbers differ because Slams are only the "
            "toughest events, not the whole tour."
        ),
        code(
            "slam_big = surf[surf.name.isin(['Rafael Nadal', 'Roger Federer', 'Novak Djokovic'])]\n"
            "piv = slam_big.pivot(index='name', columns='surface', values='win_rate')\n"
            "print(piv.round(3))\n"
            "piv.plot(kind='bar', figsize=(9, 5), color=['#b5651d', '#2a7f62', '#3a6ea5'])\n"
            "plt.title('Big Three Slam win rates by surface, 2000 to 2019'); plt.ylabel('Win rate'); plt.ylim(0, 1); plt.xticks(rotation=0)\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/03_big3_slam_surface.png'); plt.show()"
        ),
        md(
            "## Reading the result honestly\n\n"
            "Nadal is the clear clay specialist: 0.902 on clay on tour, against 0.784 on "
            "grass and 0.772 on hard. Federer is the grass leader at 0.878. Djokovic "
            "leads versatility at 0.810, because he is strong everywhere and his three "
            "surfaces are close together. Versatility rewards balance, so it is not the "
            "same as being the best on one surface."
        ),
    ],
    os.path.join(NBDIR, "03_surface_specialists.ipynb"),
)

# ---------------------------------------------------------------- 04
nb(
    head(
        "04. The Big Three era",
        "The Big Three are Roger Federer, Rafael Nadal, and Novak Djokovic. They are "
        "grouped together because, for most of this window, at least one of them won "
        "almost every Slam. This chapter counts their Slam matches and titles, compares "
        "them with the rest of the field, and counts their matches against each other.",
    )
    + [
        md(
            "## Titles first\n\n"
            "From 2000 to 2019 there were 80 Slam finals in this data. The Big Three won "
            "55 of them. All 55 came from 2003 onward, so from 2003 to 2019 they won 55 of "
            "68 Slams. Before that, in 2000 to 2002, they won none of the 12. The era did "
            "not start in 2000. It started when Federer won Wimbledon in 2003."
        ),
        code(
            "df = pd.read_csv(f'{PROC}/slam_player_matches.csv')\n"
            "fin = pd.read_csv(f'{PROC}/slam_finals_2000_2019.csv')\n"
            "big_ids = ['atp_103819', 'atp_104745', 'atp_104925']\n"
            "print(fin.groupby('name').size().sort_values(ascending=False).head(10))\n"
            "print('Big Three titles 2000 to 2019:', fin.player_id.isin(big_ids).sum(), 'of', len(fin))\n"
            "print('Big Three titles 2003 to 2019:', fin[(fin.year >= 2003)].player_id.isin(big_ids).sum(), 'of', len(fin[fin.year >= 2003]))\n"
            "for pid, name in [('atp_103819', 'Federer'), ('atp_104745', 'Nadal'), ('atp_104925', 'Djokovic')]:\n"
            "    g = df[df.player_id == pid]\n"
            "    print(f\"{name}: {len(g)} Slam matches, {int(g.winner.sum())} wins, win rate {g.winner.mean():.3f}\")"
        ),
        md("## Chart: Big Three Slam titles by player, 2000 to 2019."),
        code(
            "titles = fin.groupby('name').size().sort_values(ascending=False).head(6)\n"
            "plt.figure(figsize=(9, 5)); plt.bar(titles.index, titles.values, color='#3a6ea5')\n"
            "plt.title('Slam titles in the original data, 2000 to 2019'); plt.ylabel('Titles'); plt.xticks(rotation=20, ha='right')\n"
            "for i, v in enumerate(titles.values): plt.text(i, v + 0.4, str(v), ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/04_slam_titles_by_player.png'); plt.show()"
        ),
        md("## Chart: Big Three Slam matches per year. The lines show who was active and winning, year by year."),
        code(
            "big = df[df.player_id.isin(big_ids)].copy()\n"
            "big['player'] = big.player_id.map({'atp_103819': 'Federer', 'atp_104745': 'Nadal', 'atp_104925': 'Djokovic'})\n"
            "yr = big.groupby(['year', 'player']).size().unstack(fill_value=0)\n"
            "print(yr.tail(10))\n"
            "yr.plot(figsize=(10, 5), marker='o')\n"
            "plt.title('Big Three Slam matches per year, 2000 to 2019'); plt.ylabel('Matches')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/04_big3_matches_per_year.png'); plt.show()"
        ),
        md(
            "## Against each other\n\n"
            "In this Slam data, Big Three players met each other 45 times. Nadal won 19 "
            "of those matches, Djokovic 16, and Federer 10. Head to head, Nadal beat "
            "Federer 10 times and lost 4, Djokovic beat Federer 10 times and lost 6, and "
            "Nadal beat Djokovic 9 times and lost 6. These are Slam matches only, not "
            "their full tour meetings, so do not compare them with career head to head "
            "totals from other sources."
        ),
        code(
            "stats = pd.read_csv('../data/raw/Stats.csv')\n"
            "pairs = stats.groupby('match_id')['player_id'].apply(list)\n"
            "both = [mid for mid, ids in pairs.items() if sum(i in big_ids for i in ids) == 2]\n"
            "print('Big Three versus Big Three Slam matches:', len(both))\n"
            "bb = stats[stats.match_id.isin(both)]\n"
            "win = bb[bb.winner == True].merge(pd.read_csv('../data/raw/Player.csv'), on='player_id')\n"
            "print(win.groupby('name').size())\n"
            "import collections\n"
            "c = collections.Counter()\n"
            "names = {'atp_103819': 'Federer', 'atp_104745': 'Nadal', 'atp_104925': 'Djokovic'}\n"
            "for mid in both:\n"
            "    rows = bb[bb.match_id == mid]\n"
            "    w = rows[rows.winner == True].iloc[0]; l = rows[rows.winner == False].iloc[0]\n"
            "    c[(names[w.player_id], names[l.player_id])] += 1\n"
            "for k, v in sorted(c.items()): print(k, v)"
        ),
        md("## Chart: who won the 45 Big Three Slam meetings."),
        code(
            "vals = win.groupby('name').size()\n"
            "plt.figure(figsize=(8, 4.5)); plt.bar(vals.index, vals.values, color=['#3a6ea5', '#b5651d', '#2a7f62'])\n"
            "plt.title('Wins in Big Three versus Big Three Slam matches, 2000 to 2019'); plt.ylabel('Match wins')\n"
            "for i, v in enumerate(vals.values): plt.text(i, v + 0.4, str(v), ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/04_big3_head_to_head.png'); plt.show()"
        ),
    ],
    os.path.join(NBDIR, "04_big_three_eras.ipynb"),
)

# ---------------------------------------------------------------- 05
nb(
    head(
        "05. Grand Slam trends",
        "This chapter asks three simple questions about the 80 Slams from 2000 to 2019. "
        "Who won, by surface? Did the best ranked player usually win? And how often did "
        "the lower ranked player win, which is what an upset means in this project?",
    )
    + [
        md(
            "## Titles by surface, and a warning about seeds\n\n"
            "The original files have no seed column, so this chapter uses rank at match "
            "time instead, and says so. Rank 1 means the world number 1 at that time. "
            "A low seed and a low rank usually point the same way, but they are not the "
            "same thing, so any sentence about seeds here is really about ranks."
        ),
        code(
            "fin = pd.read_csv(f'{PROC}/slam_finals_2000_2019.csv')\n"
            "print('Titles by Slam:'); print(fin.groupby('tournament').size())\n"
            "print('Titles by surface:'); print(fin.groupby('surface').size())\n"
            "def band(r):\n"
            "    if r == 1: return 'Rank 1'\n"
            "    if r <= 4: return 'Rank 2 to 4'\n"
            "    if r <= 10: return 'Rank 5 to 10'\n"
            "    if r <= 32: return 'Rank 11 to 32'\n"
            "    return 'Rank 33 plus'\n"
            "fin['band'] = fin['rank'].apply(band)\n"
            "print(fin.groupby('band').size())\n"
            "print('Rank 1 winners:', (fin['rank'] == 1).sum(), 'of', len(fin))"
        ),
        md("## Chart: Slam winners by rank band. The top four ranks won most Slams."),
        code(
            "order = ['Rank 1', 'Rank 2 to 4', 'Rank 5 to 10', 'Rank 11 to 32', 'Rank 33 plus']\n"
            "vals = [int((fin.band == b).sum()) for b in order]\n"
            "plt.figure(figsize=(9, 4.5)); plt.bar(order, vals, color='#2a7f62')\n"
            "plt.title('Slam winners by rank band, 2000 to 2019'); plt.ylabel('Slams won'); plt.xticks(rotation=15, ha='right')\n"
            "for i, v in enumerate(vals): plt.text(i, v + 0.5, str(v), ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/05_winners_by_rank_band.png'); plt.show()"
        ),
        md(
            "## Upsets\n\n"
            "An upset here means the winner had a worse rank number than the loser. "
            "Across all 10,120 matches with Stats rows, that happened 2,867 times, or "
            "28.3 percent. Upsets are most common in the first round, at 30.4 percent, "
            "and rarer later, when the field is stronger. The final is the exception at "
            "33.8 percent, but that is only 27 finals out of 80, so one or two finals "
            "move the number a lot. Do not over read the final bar."
        ),
        code(
            "up = pd.read_csv(f'{PROC}/slam_upsets.csv')\n"
            "t = up.groupby('round')['upset'].agg(['mean', 'count', 'sum'])\n"
            "print(t.round(3))\n"
            "print('Overall upset rate:', round(up.upset.mean(), 4), 'on', len(up), 'matches')"
        ),
        md("## Chart: upset rate by round."),
        code(
            "order = ['1st Round', '2nd Round', '3rd Round', '4th Round', 'Quarterfinals', 'Semifinals', 'The Final']\n"
            "vals = [up[up['round'] == r].upset.mean() for r in order]\n"
            "plt.figure(figsize=(10, 4.5)); plt.bar(order, vals, color='#b5651d')\n"
            "plt.title('Upset rate by round, Slams 2000 to 2019'); plt.ylabel('Share of matches won by the lower ranked player'); plt.xticks(rotation=20, ha='right')\n"
            "for i, v in enumerate(vals): plt.text(i, v + 0.01, f'{v:.1%}', ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/05_upset_rate_by_round.png'); plt.show()"
        ),
        md("## Chart: how long matches lasted, by surface. Clay matches lasted longest on average."),
        code(
            "match = pd.read_csv('../data/raw/Match.csv')\n"
            "match['surface'] = match.tournament.map({'Australian Open': 'Hard', 'French Open': 'Clay', 'US Open': 'Hard', 'Wimbledon': 'Grass'})\n"
            "g = match.groupby('surface')['match_minutes'].agg(['mean', 'median', 'count'])\n"
            "print(g.round(1))\n"
            "plt.figure(figsize=(8, 4.5)); plt.bar(g.index, g['mean'], color=['#b5651d', '#2a7f62', '#3a6ea5'])\n"
            "plt.title('Average match length in minutes, by surface'); plt.ylabel('Minutes')\n"
            "for i, v in enumerate(g['mean']): plt.text(i, v + 2, f'{v:.1f}', ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/05_match_minutes_by_surface.png'); plt.show()"
        ),
    ],
    os.path.join(NBDIR, "05_grand_slam_trends.ipynb"),
)

# ---------------------------------------------------------------- 06
nb(
    head(
        "06. After 2019, the full tour, and the women's game",
        "The original data stops in 2019 and covers men's Slams only. That is a real "
        "limit, not a small footnote. This chapter uses the Sackmann supplement, kept in "
        "an archive mirror after the original Sackmann repos went offline, to answer "
        "three follow up questions: what happened at Slams from 2020 to 2024, what does "
        "the full tour add, and what does the women's game look like over the same span?",
    )
    + [
        md(
            "## A note on the supplement source\n\n"
            "Jeff Sackmann's original tennis_atp and tennis_wta repos returned 404 on "
            "2026-11-03. The files used here come from the Aneeshers tennis-sackmann-archive "
            "mirror, which states it archives Sackmann's data and asks users to attribute "
            "Jeff Sackmann. Numbers in this chapter are labelled Sackmann supplement, so "
            "they are never mixed silently with the original repo numbers."
        ),
        code(
            "atp = pd.read_csv(f'{PROC}/sackmann_atp_2000_2024.csv', usecols=['tourney_name', 'surface', 'tourney_level', 'round', 'winner_name', 'loser_name', 'winner_seed'])\n"
            "atp_fin = pd.read_csv(f'{PROC}/sackmann_atp_slam_finals.csv')\n"
            "wta_fin = pd.read_csv(f'{PROC}/sackmann_wta_slam_finals.csv')\n"
            "print('ATP supplement rows:', len(atp))\n"
            "print('ATP Slam finals 2000 to 2024:', len(atp_fin), 'WTA Slam finals:', len(wta_fin))\n"
            "print('ATP Slam finals 2020 to 2024:'); print(atp_fin[atp_fin.year >= 2020][['year', 'tourney_name', 'winner_name', 'loser_name']].to_string(index=False))"
        ),
        md(
            "## Why 2020 has only three men's Slam finals\n\n"
            "Wimbledon 2020 was cancelled, which the supplement reflects as three finals "
            "that year instead of four. That is not missing data. It is a real cancelled "
            "event. From 2020 to 2024 the men's Slam winners were Djokovic 8 times, Nadal "
            "3, Alcaraz 4, and Sinner 2, plus one each for Thiem and Medvedev, counting "
            "the finals listed above."
        ),
        code(
            "recent = atp_fin[atp_fin.year >= 2020]\n"
            "print(recent.groupby('winner_name').size().sort_values(ascending=False))\n"
            "print('WTA Slam titles 2000 to 2024, top winners:')\n"
            "print(wta_fin.groupby('winner_name').size().sort_values(ascending=False).head(8))"
        ),
        md("## Chart: men's Slam titles, 2020 to 2024, Sackmann supplement."),
        code(
            "vals = recent.groupby('winner_name').size().sort_values(ascending=False)\n"
            "plt.figure(figsize=(9, 5)); plt.bar(vals.index, vals.values, color='#3a6ea5')\n"
            "plt.title('Mens Slam titles, 2020 to 2024 (Sackmann supplement)'); plt.ylabel('Titles'); plt.xticks(rotation=20, ha='right')\n"
            "for i, v in enumerate(vals.values): plt.text(i, v + 0.1, str(v), ha='center')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/06_recent_slam_titles.png'); plt.show()"
        ),
        md("## Chart: women's Slam titles, 2000 to 2024, top winners, Sackmann supplement."),
        code(
            "wvals = wta_fin.groupby('winner_name').size().sort_values(ascending=False).head(8)\n"
            "plt.figure(figsize=(9, 5)); plt.barh(wvals.index[::-1], wvals.values[::-1], color='#7d3c98')\n"
            "plt.title('Womens Slam titles, 2000 to 2024, top 8 (Sackmann supplement)'); plt.xlabel('Titles')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/06_wta_titles.png'); plt.show()"
        ),
        md(
            "## Chart: full tour matches by surface, Sackmann ATP 2000 to 2024. "
            "Hard courts dominate the tour calendar, grass is a short season, and carpet "
            "fades away. This is why Slam only surface numbers and tour surface numbers differ."
        ),
        code(
            "atp_full = pd.read_csv(f'{PROC}/sackmann_atp_2000_2024.csv', usecols=['surface'])\n"
            "print(atp_full.surface.value_counts(dropna=False))\n"
            "vals = atp_full.surface.value_counts()\n"
            "plt.figure(figsize=(8, 4.5)); plt.bar(vals.index, vals.values, color='#2a7f62')\n"
            "plt.title('ATP tour matches by surface, 2000 to 2024 (Sackmann supplement)'); plt.ylabel('Matches'); plt.xticks(rotation=15, ha='right')\n"
            "plt.tight_layout(); plt.savefig(f'{CH}/06_tour_matches_by_surface.png'); plt.show()"
        ),
        md(
            "## Limits that stay limits\n\n"
            "The supplement has real serve stats for many tour matches, but coverage is "
            "uneven by year and event, so this project does not rebuild SDI on the full "
            "tour. The women's supplement is used only for Slam finals here, not for a "
            "full serve comparison, because the original repo has no women's serve data "
            "to compare it with. Both limits are kept in the BUILD_REPORT."
        ),
    ],
    os.path.join(NBDIR, "06_supplement_and_limits.ipynb"),
)

print("all notebooks built")
