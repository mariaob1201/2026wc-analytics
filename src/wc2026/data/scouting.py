"""Scouted, public-source intelligence (qualitative semantics).

This is the "soft" knowledge that isn't in any stats CSV: coach, captain,
preferred shape, recent form and tournament context. Each fact is paired with
the public source it came from so the assessment stays auditable.

Gathered 2026-06-19. Update the dict (and ``SOURCES``) as new rounds are played
-- or replace with a live scraper of fixtures/lineups.
"""

from __future__ import annotations

# --- Mexico (host nation), as of 2026-06-19 -------------------------------- #
MEXICO = {
    "coach": "Javier Aguirre",
    "captain": "Edson Álvarez",
    "preferred_formation": "4-1-4-1",
    "squad_makeup": {"GK": 3, "DF": 6, "MF": 9, "FW": 8},
    "key_players": {
        "Guillermo Ochoa": "40-year-old GK chasing a record 6th World Cup",
        "Edson Álvarez": "captain, defensive-midfield anchor",
        "Raúl Jiménez": "veteran focal point of the attack",
        "Santiago Giménez": "in-form striker / alternate 9",
        "Orbelín Pineda": "creative midfield link",
        "Gilberto Mora": "17-year-old breakout talent",
        "César Montes": "first-choice CB (suspended for the South Korea game)",
        "Johan Vásquez": "ball-playing centre-back",
    },
    # Most recent results (newest last). (h)=home for Mexico unless neutral noted.
    "recent_results": [
        ("2026-03-28", "Portugal", "0-0", "Friendly"),
        ("2026-03-31", "Belgium", "1-1", "Friendly"),
        ("2026-05-22", "Ghana", "2-0", "Friendly"),
        ("2026-05-30", "Australia", "1-0", "Friendly"),
        ("2026-06-04", "Serbia", "5-1", "Friendly"),
        ("2026-06-11", "South Africa", "2-0", "World Cup (opener, Estadio Azteca)"),
        ("2026-06-18", "South Korea", "1-0", "World Cup"),
    ],
    "tournament_status": (
        "Top of Group A with 6 pts from 2 games (2-0 vs South Africa, 1-0 vs "
        "South Korea); 3 scored, 0 conceded; already qualified for the knockout "
        "stage with the Czechia group game still to play (June 24)."
    ),
    "group": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "scorers_so_far": ["Julián Quiñones", "Raúl Jiménez", "Luis Romo"],
    "narrative_notes": [
        "Unbeaten in last 7, with clean sheets against South Africa, South Korea,"
        " Ghana and Australia and creditable draws against Portugal and Belgium.",
        "Defensive solidity (two World Cup clean sheets) is the story so far; "
        "goals have come from midfield runners and set pieces, not just the 9.",
        "Host-nation advantage: opener at the Estadio Azteca, familiar altitude "
        "and climate.",
    ],
}

# --- Media & expert sentiment (public sources), as of 2026-06-19 ----------- #
# Reddit/r/soccer is not reachable from this environment (blocked to crawlers
# and the JSON API serves an SPA shell), so social sentiment here is drawn from
# accessible outlets (ESPN, Sports Illustrated). Add a Reddit feed later via an
# authenticated Reddit API client run locally.
MEXICO_MEDIA = {
    "overall_sentiment": "tempered / cautiously positive",
    "sentiment_summary": (
        "Results are excellent (top of the group, two clean sheets) but the "
        "expert read is muted: pundits praise the defensive organisation while "
        "doubting Mexico's cutting edge and ability to go deep."
    ),
    "expert_takes": [
        ("ESPN (Mark Ogden)", "Win over South Korea was \"largely unimpressive\"; "
         "Mexico \"lack a real cutting edge\" and \"the quality to go deep\" — "
         "tipped to hit the \"round of 16 wall\" (no QF since 1994 bar host years)."),
        ("ESPN tactical", "Credits Aguirre's pragmatic, no-nonsense defensive "
         "organisation and offside traps; reliance on discipline over individual "
         "brilliance. Luis Romo (a defensive mid) starting surprised analysts and "
         "may blunt midfield attacking thrust, though he scored the winner."),
        ("Aguirre (quote)", "\"It was difficult. They put us under a lot of "
         "pressure... one mistake was always going to make the difference.\" "
         "Relishes the \"volcano\" of a knockout at the Estadio Azteca."),
    ],
    # Opta supercomputer projection via Sports Illustrated.
    "knockout_path": {
        "round32": "June 30 at Estadio Azteca vs a best third-placed team from "
                   "groups C/E/F/H/I — Opta's most likely opponent is Senegal "
                   "(others: Brazil, Ecuador, Netherlands, Spain).",
        "round16": "Likely England, again at the Estadio Azteca.",
        "later": "QF at Miami, SF at Atlanta, Final at MetLife (New Jersey).",
        "edge": "Two home knockout rounds at altitude is a real structural edge.",
    },
    "market_odds": "ESPN/betting markets: Mexico ~55-1 to win the title "
                   "(shortened after the group results); USA 40-1 for comparison.",
}

# --- X / social & fan reaction --------------------------------------------- #
# Direct X (Twitter) access is not available here: the site is auth-walled (it
# serves a JS shell to crawlers), the X API is paid-only, and nitter mirrors are
# defunct. So social sentiment is captured INDIRECTLY via news outlets that
# report the X/fan reaction. To pull native posts, add an X API v2 client
# (paid Basic tier) or a logged-in scraper run locally.
MEXICO_SOCIAL = {
    "net_mood": "euphoric in the street, impatient in the stadium",
    "positive": [
        "Nationwide street celebrations after qualifying first; mariachis at the "
        "Ángel de la Independencia in Mexico City (NPR).",
        "Wholesome cross-fan moments went viral: Mexican fans doing 'Gangnam "
        "Style', lifting a South Korean supporter, chanting \"Korean brother, "
        "you're Mexican now\" (Fox Sports).",
        "Aguirre: the players are \"euphoric... it relieves some of the pressure.\"",
    ],
    "negative": [
        "Home fans BOOED at halftime after a scoreless, uninspiring first 45 — "
        "in-stadium frustration despite the result, echoing the 'unimpressive' "
        "expert verdict.",
        "A racism controversy: a Mexican supporter filmed making a slant-eye "
        "gesture at a South Korea fan; authorities/organisers took action "
        "(GiveMeSport, Global Times).",
    ],
    "caveat": "Reaction captured via news aggregators, not native X posts "
              "(X API is paid and the site is auth-walled).",
}

SOURCES = [
    ("NPR — Mexico first to reach the knockout stage (fan celebrations)",
     "https://www.npr.org/2026/06/19/g-s1-129056/mexico-becomes-first-country-to-reach-knockout-stage-of-world-cup"),
    ("Fox Sports — South Korea & Mexico fans celebrating together",
     "https://www.foxsports.com/stories/soccer/south-koreas-world-cup-fans-enjoying-mexico"),
    ("GiveMeSport — action taken over fan's gesture",
     "https://www.givemesport.com/action-taken-against-mexico-racist-gesture-south-korea-world-cup/"),
    ("ESPN — Mexico beat South Korea but 'a work in progress'",
     "https://www.espn.com/soccer/story/_/id/49113986/mexico-south-korea-world-cup-reaction-analysis"),
    ("SI — Mexico's knockout-stage path after winning Group A (Opta)",
     "https://www.si.com/soccer/mexico-2026-world-cup-knockout-stage-path-after-winning-group-a"),
    ("ESPN — Aguirre relishes Azteca knockout matches",
     "https://www.espn.com/soccer/story/_/id/49114368/aguirre-relishes-azteca-knockout-matches-mexico-win-group-a"),
    ("ESPN — World Cup title odds (Mexico 55-1)",
     "https://www.espn.com/espn/betting/story/_/id/48386952/espn-soccer-futbol-world-cup-betting-odds-championship-groups"),
    ("Mexico 2026 World Cup roster (Aguirre, Ochoa)",
     "https://www.si.com/soccer/mexico-2026-world-cup-roster-confirmed-full-list-of-players-historic-inclusions"),
    ("Mexico vs South Korea lineups / 4-1-4-1",
     "https://www.prizepicks.com/playbook-article/mexico-vs-south-korea-lineups-world-cup-2026-starting-xis"),
    ("Group A standings & results",
     "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_A"),
    ("Group A preview (teams, context)",
     "https://www.espn.com/soccer/story/_/id/48957098/group-2026-world-cup-teams-records-stats-know-mexico-south-korea-czechia-south-africa"),
]
