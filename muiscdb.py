#!/usr/bin/env python3
# ============================================================
#   musicdb — AI-Powered Music Search Engine
#   Genres: RnB, HipHop, Soul, Classical, Orchestra, Afrobeats,
#           Amapiano, Trap, Rock, EDM, Pop, Afro House,
#           Reggaeton, Latino/Latina, Movie Soundtracks,
#           Kenyan HipHop, Kenyan Trap, Kenyan Drill & more
#   Modes: FAST SEARCH  (local database)
#          DEEP SEARCH  (live AI + web sources)
# ============================================================

import os, sys, json, time, hashlib, re, textwrap, argparse
from datetime import datetime

# ── Dependency bootstrap ──────────────────────────────────────
def install(pkg):
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

for dep in ["requests", "rich", "fuzzywuzzy", "python-Levenshtein"]:
    try:
        __import__(dep.replace("-","_").split(".")[0])
    except ImportError:
        print(f"[setup] Installing {dep} ...")
        install(dep)

import requests
from rich.console import Console
from rich.table   import Table
from rich.panel   import Panel
from rich.text    import Text
from rich         import box
from fuzzywuzzy   import fuzz, process

console = Console()

# ============================================================
#  SECTION 1 — STATIC DATABASE  (Fast Search source)
#  Each entry: title, year, artist, album_or_single, genre,
#              views (millions), country
# ============================================================
MUSIC_DB = [

    # ── RnB ──────────────────────────────────────────────────
    {"title":"Blinding Lights",       "year":2019,"artist":"The Weeknd",        "release":"After Hours (Album)",      "genre":"rnb",       "views_m":5100,"country":"Canada"},
    {"title":"Best Part",             "year":2017,"artist":"Daniel Caesar ft. H.E.R.","release":"Freudian (Album)", "genre":"rnb",       "views_m":650, "country":"Canada"},
    {"title":"Kiss Me More",          "year":2021,"artist":"Doja Cat ft. SZA",  "release":"Single",                   "genre":"rnb",       "views_m":700, "country":"USA"},
    {"title":"Good Days",             "year":2020,"artist":"SZA",               "release":"Single",                   "genre":"rnb",       "views_m":380, "country":"USA"},
    {"title":"Leave The Door Open",   "year":2021,"artist":"Silk Sonic",        "release":"An Evening With Silk Sonic","genre":"rnb",      "views_m":560, "country":"USA"},
    {"title":"Essence",               "year":2021,"artist":"WizKid ft. Tems",   "release":"Made In Lagos (Album)",    "genre":"rnb",       "views_m":420, "country":"Nigeria"},
    {"title":"Pick Up Your Feelings", "year":2020,"artist":"Jazmine Sullivan",  "release":"Heaux Tales (Album)",      "genre":"rnb",       "views_m":120, "country":"USA"},
    {"title":"Die For You",           "year":2016,"artist":"The Weeknd",        "release":"Starboy (Album)",          "genre":"rnb",       "views_m":1800,"country":"Canada"},

    # ── HipHop ───────────────────────────────────────────────
    {"title":"God's Plan",            "year":2018,"artist":"Drake",             "release":"Scorpion (Album)",         "genre":"hiphop",    "views_m":1800,"country":"Canada"},
    {"title":"HUMBLE.",               "year":2017,"artist":"Kendrick Lamar",    "release":"DAMN. (Album)",            "genre":"hiphop",    "views_m":1200,"country":"USA"},
    {"title":"Old Town Road",         "year":2019,"artist":"Lil Nas X",         "release":"7 (EP)",                   "genre":"hiphop",    "views_m":1000,"country":"USA"},
    {"title":"Sicko Mode",            "year":2018,"artist":"Travis Scott",      "release":"Astroworld (Album)",       "genre":"hiphop",    "views_m":1300,"country":"USA"},
    {"title":"Rockstar",              "year":2017,"artist":"Post Malone ft. 21 Savage","release":"Beerbongs & Bentleys","genre":"hiphop","views_m":1500,"country":"USA"},
    {"title":"Not Like Us",           "year":2024,"artist":"Kendrick Lamar",    "release":"Single",                   "genre":"hiphop",    "views_m":800, "country":"USA"},
    {"title":"Rich Flex",             "year":2022,"artist":"Drake & 21 Savage", "release":"Her Loss (Album)",         "genre":"hiphop",    "views_m":900, "country":"USA/Canada"},
    {"title":"Luther",                "year":2024,"artist":"Kendrick Lamar ft. SZA","release":"GNX (Album)",         "genre":"hiphop",    "views_m":600, "country":"USA"},

    # ── Soul ─────────────────────────────────────────────────
    {"title":"River",                 "year":2016,"artist":"Leon Bridges",      "release":"Coming Home (Album)",      "genre":"soul",      "views_m":95,  "country":"USA"},
    {"title":"Hold On, We're Going Home","year":2013,"artist":"Drake",          "release":"Nothing Was The Same",     "genre":"soul",      "views_m":700, "country":"Canada"},
    {"title":"Golden",                "year":2019,"artist":"Jill Scott",        "release":"Who Is Jill Scott? (Album)","genre":"soul",     "views_m":30,  "country":"USA"},
    {"title":"Black Parade",          "year":2020,"artist":"Beyoncé",           "release":"Single",                   "genre":"soul",      "views_m":120, "country":"USA"},
    {"title":"Needed Me",             "year":2016,"artist":"Rihanna",           "release":"Anti (Album)",             "genre":"soul",      "views_m":480, "country":"Barbados"},

    # ── Classical ─────────────────────────────────────────────
    {"title":"Moonlight Sonata",      "year":1801,"artist":"Ludwig van Beethoven","release":"Op.27 No.2 (Album)",    "genre":"classical", "views_m":250, "country":"Germany"},
    {"title":"Clair de Lune",         "year":1905,"artist":"Claude Debussy",    "release":"Suite bergamasque",       "genre":"classical", "views_m":180, "country":"France"},
    {"title":"Four Seasons - Spring", "year":1725,"artist":"Antonio Vivaldi",   "release":"The Four Seasons (Album)","genre":"classical", "views_m":400, "country":"Italy"},
    {"title":"Für Elise",             "year":1810,"artist":"Ludwig van Beethoven","release":"Bagatelle No.25",       "genre":"classical", "views_m":300, "country":"Germany"},
    {"title":"Nocturne Op.9 No.2",    "year":1832,"artist":"Frédéric Chopin",   "release":"Op.9 Nocturnes",         "genre":"classical", "views_m":200, "country":"Poland"},

    # ── Orchestra / Soundtrack-adjacent ──────────────────────
    {"title":"Also Sprach Zarathustra","year":1896,"artist":"Richard Strauss",  "release":"Tone Poem Op.30",         "genre":"orchestra", "views_m":60,  "country":"Germany"},
    {"title":"Symphony No.5 in C Minor","year":1808,"artist":"Ludwig van Beethoven","release":"Op.67",              "genre":"orchestra", "views_m":150, "country":"Germany"},
    {"title":"Bolero",                "year":1928,"artist":"Maurice Ravel",     "release":"Single Work",             "genre":"orchestra", "views_m":80,  "country":"France"},
    {"title":"1812 Overture",         "year":1882,"artist":"Pyotr Ilyich Tchaikovsky","release":"Op.49",            "genre":"orchestra", "views_m":70,  "country":"Russia"},

    # ── Afrobeats ─────────────────────────────────────────────
    {"title":"Ye",                    "year":2018,"artist":"Burna Boy",         "release":"Outside (Album)",          "genre":"afrobeats", "views_m":500, "country":"Nigeria"},
    {"title":"Peru",                  "year":2021,"artist":"Fireboy DML ft. Ed Sheeran","release":"Single",         "genre":"afrobeats", "views_m":600, "country":"Nigeria"},
    {"title":"Calm Down",             "year":2022,"artist":"Rema",              "release":"Rave & Roses (Album)",     "genre":"afrobeats", "views_m":1200,"country":"Nigeria"},
    {"title":"Terminator",            "year":2022,"artist":"Asake",             "release":"Mr. Money With The Vibe", "genre":"afrobeats", "views_m":300, "country":"Nigeria"},
    {"title":"Monalisa",              "year":2022,"artist":"Lojay & Sarz",      "release":"Lojay x Sarz EP",         "genre":"afrobeats", "views_m":150, "country":"Nigeria"},
    {"title":"Last Last",             "year":2022,"artist":"Burna Boy",         "release":"Love, Damini (Album)",     "genre":"afrobeats", "views_m":750, "country":"Nigeria"},
    {"title":"Electricity",           "year":2022,"artist":"Kizz Daniel",       "release":"Single",                   "genre":"afrobeats", "views_m":200, "country":"Nigeria"},
    {"title":"Sungba",                "year":2021,"artist":"Ayra Starr",        "release":"19 & Dangerous (Album)",   "genre":"afrobeats", "views_m":100, "country":"Nigeria"},

    # ── Amapiano ──────────────────────────────────────────────
    {"title":"Tshwala Bam",           "year":2023,"artist":"TitoM & Yuppe ft. S.N.E","release":"Single",            "genre":"amapiano",  "views_m":200, "country":"South Africa"},
    {"title":"John Vuli Gate",        "year":2020,"artist":"Mapara A Jazz",     "release":"Single",                   "genre":"amapiano",  "views_m":180, "country":"South Africa"},
    {"title":"Iyo",                   "year":2023,"artist":"Kabza De Small",    "release":"I Am The King Of Amapiano","genre":"amapiano", "views_m":90,  "country":"South Africa"},
    {"title":"Love You Tonight",      "year":2022,"artist":"Uncle Waffles",     "release":"Single",                   "genre":"amapiano",  "views_m":80,  "country":"South Africa"},
    {"title":"Emcimbini",             "year":2019,"artist":"Kabza De Small ft. Samthing Soweto","release":"Single",  "genre":"amapiano",  "views_m":120, "country":"South Africa"},
    {"title":"Sgudi Snyc",            "year":2022,"artist":"DJ Maphorisa & Kabza","release":"Scorpion Kings (Album)","genre":"amapiano",  "views_m":70,  "country":"South Africa"},

    # ── Trap ──────────────────────────────────────────────────
    {"title":"XO Tour Llif3",         "year":2017,"artist":"Lil Uzi Vert",      "release":"Luv Is Rage 2 (Album)",   "genre":"trap",      "views_m":1100,"country":"USA"},
    {"title":"No Role Modelz",        "year":2014,"artist":"J. Cole",           "release":"2014 Forest Hills Drive", "genre":"trap",      "views_m":500, "country":"USA"},
    {"title":"Congratulations",       "year":2016,"artist":"Post Malone",       "release":"Single",                   "genre":"trap",      "views_m":1700,"country":"USA"},
    {"title":"Mask Off",              "year":2017,"artist":"Future",            "release":"Future (Album)",           "genre":"trap",      "views_m":700, "country":"USA"},
    {"title":"Bad and Boujee",        "year":2016,"artist":"Migos",             "release":"Culture (Album)",          "genre":"trap",      "views_m":1000,"country":"USA"},
    {"title":"Tunnel Vision",         "year":2017,"artist":"Kodak Black",       "release":"Painting Pictures",       "genre":"trap",      "views_m":800, "country":"USA"},
    {"title":"Drip Too Hard",         "year":2018,"artist":"Lil Baby & Gunna",  "release":"Single",                   "genre":"trap",      "views_m":600, "country":"USA"},

    # ── Rock ──────────────────────────────────────────────────
    {"title":"Bohemian Rhapsody",     "year":1975,"artist":"Queen",             "release":"A Night at the Opera",    "genre":"rock",      "views_m":1700,"country":"UK"},
    {"title":"Smells Like Teen Spirit","year":1991,"artist":"Nirvana",          "release":"Nevermind (Album)",        "genre":"rock",      "views_m":1400,"country":"USA"},
    {"title":"Hotel California",      "year":1977,"artist":"Eagles",            "release":"Hotel California (Album)","genre":"rock",      "views_m":900, "country":"USA"},
    {"title":"Stairway to Heaven",    "year":1971,"artist":"Led Zeppelin",      "release":"Led Zeppelin IV",         "genre":"rock",      "views_m":600, "country":"UK"},
    {"title":"Back In Black",         "year":1980,"artist":"AC/DC",             "release":"Back in Black (Album)",   "genre":"rock",      "views_m":800, "country":"Australia"},
    {"title":"Wonderwall",            "year":1995,"artist":"Oasis",             "release":"(What's the Story) Morning Glory","genre":"rock","views_m":700,"country":"UK"},

    # ── EDM ───────────────────────────────────────────────────
    {"title":"Levels",                "year":2011,"artist":"Avicii",            "release":"Single",                   "genre":"edm",       "views_m":1200,"country":"Sweden"},
    {"title":"Titanium",              "year":2011,"artist":"David Guetta ft. Sia","release":"Nothing but the Beat",  "genre":"edm",       "views_m":1900,"country":"France"},
    {"title":"Animals",               "year":2013,"artist":"Martin Garrix",     "release":"Single",                   "genre":"edm",       "views_m":1100,"country":"Netherlands"},
    {"title":"Stay The Night",        "year":2013,"artist":"Zedd ft. Hayley Williams","release":"Clarity (Album)",   "genre":"edm",       "views_m":600, "country":"Germany"},
    {"title":"Don't You Worry Child", "year":2012,"artist":"Swedish House Mafia","release":"Until Now (Album)",       "genre":"edm",       "views_m":900, "country":"Sweden"},
    {"title":"Wake Me Up",            "year":2013,"artist":"Avicii",            "release":"True (Album)",             "genre":"edm",       "views_m":1800,"country":"Sweden"},
    {"title":"Lean On",               "year":2015,"artist":"Major Lazer & DJ Snake","release":"Peace Is the Mission","genre":"edm",      "views_m":3000,"country":"USA"},
    {"title":"Faded",                 "year":2015,"artist":"Alan Walker",       "release":"Single",                   "genre":"edm",       "views_m":3400,"country":"Norway"},

    # ── Pop ───────────────────────────────────────────────────
    {"title":"Shape of You",          "year":2017,"artist":"Ed Sheeran",        "release":"÷ (Album)",               "genre":"pop",       "views_m":6100,"country":"UK"},
    {"title":"Uptown Funk",           "year":2014,"artist":"Mark Ronson ft. Bruno Mars","release":"Uptown Special", "genre":"pop",       "views_m":4500,"country":"USA"},
    {"title":"Bad Guy",               "year":2019,"artist":"Billie Eilish",     "release":"When We All Fall Asleep","genre":"pop",       "views_m":2800,"country":"USA"},
    {"title":"Anti-Hero",             "year":2022,"artist":"Taylor Swift",      "release":"Midnights (Album)",        "genre":"pop",       "views_m":800, "country":"USA"},
    {"title":"Flowers",               "year":2023,"artist":"Miley Cyrus",       "release":"Endless Summer Vacation", "genre":"pop",       "views_m":1200,"country":"USA"},
    {"title":"As It Was",             "year":2022,"artist":"Harry Styles",      "release":"Harry's House (Album)",   "genre":"pop",       "views_m":1700,"country":"UK"},
    {"title":"Stay",                  "year":2021,"artist":"The Kid LAROI & Justin Bieber","release":"Single",       "genre":"pop",       "views_m":2000,"country":"Australia/Canada"},
    {"title":"Unholy",                "year":2022,"artist":"Sam Smith ft. Kim Petras","release":"Single",           "genre":"pop",       "views_m":700, "country":"UK"},

    # ── Afro House ───────────────────────────────────────────
    {"title":"Stimela",               "year":2021,"artist":"Black Coffee",      "release":"We Dance Again (Album)",  "genre":"afrohouse", "views_m":50,  "country":"South Africa"},
    {"title":"Superman",              "year":2023,"artist":"Enoo Napa",         "release":"Single",                   "genre":"afrohouse", "views_m":15,  "country":"South Africa"},
    {"title":"You Need Me",           "year":2022,"artist":"Black Coffee ft. Maxine","release":"Single",             "genre":"afrohouse", "views_m":30,  "country":"South Africa"},
    {"title":"We Dance Again",        "year":2013,"artist":"Naughty Boy ft. Nile Rodgers","release":"Hotel Cabana", "genre":"afrohouse", "views_m":80,  "country":"UK"},

    # ── Reggaeton ─────────────────────────────────────────────
    {"title":"Gasolina",              "year":2004,"artist":"Daddy Yankee",      "release":"Barrio Fino (Album)",      "genre":"reggaeton", "views_m":1200,"country":"Puerto Rico"},
    {"title":"Despacito",             "year":2017,"artist":"Luis Fonsi ft. Daddy Yankee","release":"Vida (Album)",  "genre":"reggaeton", "views_m":8400,"country":"Puerto Rico"},
    {"title":"Con Calma",             "year":2019,"artist":"Daddy Yankee & Snow","release":"Single",                 "genre":"reggaeton", "views_m":2000,"country":"Puerto Rico"},
    {"title":"Tití Me Preguntó",      "year":2022,"artist":"Bad Bunny",         "release":"Un Verano Sin Ti",        "genre":"reggaeton", "views_m":800, "country":"Puerto Rico"},
    {"title":"Mayores",               "year":2017,"artist":"Becky G ft. Bad Bunny","release":"Single",               "genre":"reggaeton", "views_m":1500,"country":"USA/Puerto Rico"},

    # ── Latino / Latina ───────────────────────────────────────
    {"title":"La Bamba",              "year":1958,"artist":"Ritchie Valens",    "release":"Single",                   "genre":"latino",    "views_m":200, "country":"USA/Mexico"},
    {"title":"Hips Don't Lie",        "year":2006,"artist":"Shakira ft. Wyclef Jean","release":"She Wolf (Album)",  "genre":"latino",    "views_m":1400,"country":"Colombia"},
    {"title":"Waka Waka",             "year":2010,"artist":"Shakira",           "release":"She Wolf (Album)",         "genre":"latino",    "views_m":3500,"country":"Colombia"},
    {"title":"La Gozadera",           "year":2016,"artist":"Gente de Zona ft. Marc Anthony","release":"Single",     "genre":"latino",    "views_m":600, "country":"Cuba"},
    {"title":"Mi Gente",              "year":2017,"artist":"J Balvin & Willy William","release":"Vibras (Album)",    "genre":"latino",    "views_m":3200,"country":"Colombia"},
    {"title":"Hawái",                 "year":2020,"artist":"Maluma",            "release":"Papi Juancho (Album)",     "genre":"latina",    "views_m":1800,"country":"Colombia"},

    # ── Movie Soundtracks ─────────────────────────────────────
    {"title":"My Heart Will Go On",   "year":1997,"artist":"Celine Dion",       "release":"Titanic OST",             "genre":"soundtrack","views_m":2600,"country":"Canada"},
    {"title":"Eye of the Tiger",      "year":1982,"artist":"Survivor",          "release":"Rocky III OST",           "genre":"soundtrack","views_m":1500,"country":"USA"},
    {"title":"Circle of Life",        "year":1994,"artist":"Elton John",        "release":"The Lion King OST",       "genre":"soundtrack","views_m":900, "country":"UK"},
    {"title":"He's a Pirate",         "year":2003,"artist":"Klaus Badelt",      "release":"Pirates of the Caribbean","genre":"soundtrack","views_m":400, "country":"Germany"},
    {"title":"Interstellar Theme",    "year":2014,"artist":"Hans Zimmer",       "release":"Interstellar OST",        "genre":"soundtrack","views_m":550, "country":"Germany/USA"},
    {"title":"Time",                  "year":2010,"artist":"Hans Zimmer",       "release":"Inception OST",           "genre":"soundtrack","views_m":700, "country":"Germany/USA"},
    {"title":"Lose Yourself",         "year":2002,"artist":"Eminem",            "release":"8 Mile OST",              "genre":"soundtrack","views_m":3000,"country":"USA"},
    {"title":"Shallow",               "year":2018,"artist":"Lady Gaga & Bradley Cooper","release":"A Star Is Born", "genre":"soundtrack","views_m":2000,"country":"USA"},

    # ── 🇰🇪 KENYAN HIPHOP ─────────────────────────────────────
    {"title":"Melanin",               "year":2018,"artist":"Sauti Sol",         "release":"Afrikan Sauce (Album)",   "genre":"kenyan-hiphop","views_m":25,"country":"Kenya"},
    {"title":"Suzanna",               "year":2019,"artist":"Sauti Sol",         "release":"Midnight Train (Album)",  "genre":"kenyan-hiphop","views_m":30,"country":"Kenya"},
    {"title":"Midnight Train",        "year":2019,"artist":"Sauti Sol",         "release":"Midnight Train (Album)",  "genre":"kenyan-hiphop","views_m":15,"country":"Kenya"},
    {"title":"Nishike",               "year":2013,"artist":"Sauti Sol",         "release":"Sol Filosofia (Album)",   "genre":"kenyan-hiphop","views_m":10,"country":"Kenya"},
    {"title":"Extravaganza",          "year":2019,"artist":"Sauti Sol ft. Bensoul","release":"Midnight Train",       "genre":"kenyan-hiphop","views_m":18,"country":"Kenya"},
    {"title":"Nairobi",               "year":2020,"artist":"Matata",            "release":"Single",                   "genre":"kenyan-hiphop","views_m":8, "country":"Kenya"},
    {"title":"Nikumbuke",             "year":2022,"artist":"Nikita Kering",     "release":"Single",                   "genre":"kenyan-hiphop","views_m":5, "country":"Kenya"},
    {"title":"Maombi",                "year":2021,"artist":"Nikita Kering",     "release":"Single",                   "genre":"kenyan-hiphop","views_m":4, "country":"Kenya"},

    # ── 🇰🇪 KENYAN TRAP / DRILL ───────────────────────────────
    {"title":"Wamlambez",             "year":2019,"artist":"Sailors Gang",      "release":"Single",                   "genre":"kenyan-trap","views_m":20,"country":"Kenya"},
    {"title":"Teke Teke",             "year":2020,"artist":"Wakadinali",        "release":"Single",                   "genre":"kenyan-drill","views_m":12,"country":"Kenya"},
    {"title":"Kiboko Ya Moto",        "year":2021,"artist":"Wakadinali",        "release":"Single",                   "genre":"kenyan-drill","views_m":9, "country":"Kenya"},
    {"title":"Swagga",                "year":2022,"artist":"Wakadinali ft. Njerae","release":"Single",                "genre":"kenyan-drill","views_m":14,"country":"Kenya"},
    {"title":"Unavailable",           "year":2023,"artist":"Njerae",            "release":"Single",                   "genre":"kenyan-trap","views_m":7, "country":"Kenya"},
    {"title":"Lamba Lolo",            "year":2019,"artist":"Ethic Entertainment","release":"Single",                  "genre":"kenyan-trap","views_m":22,"country":"Kenya"},
    {"title":"Pandana",               "year":2022,"artist":"Buruklyn Boyz",     "release":"Single",                   "genre":"kenyan-drill","views_m":11,"country":"Kenya"},
    {"title":"Gari Ya Moshi",         "year":2021,"artist":"Buruklyn Boyz",     "release":"Boyz From Brooklyn EP",    "genre":"kenyan-drill","views_m":8, "country":"Kenya"},
    {"title":"Kula Hiyo",             "year":2021,"artist":"Buruklyn Boyz",     "release":"Single",                   "genre":"kenyan-drill","views_m":6, "country":"Kenya"},
    {"title":"Rhumba",                "year":2022,"artist":"Buruklyn Boyz",     "release":"Single",                   "genre":"kenyan-drill","views_m":5, "country":"Kenya"},
    {"title":"Waende",                "year":2023,"artist":"Matata",            "release":"Single",                   "genre":"kenyan-trap","views_m":4, "country":"Kenya"},
    {"title":"Niaje",                 "year":2022,"artist":"Matata",            "release":"Single",                   "genre":"kenyan-hiphop","views_m":3,"country":"Kenya"},
]

# ============================================================
#  SECTION 2 — GENRE ALIASES  (so user can type partial names)
# ============================================================
GENRE_ALIASES = {
    "rnb":["rnb","r&b","r n b","rhythm and blues"],
    "hiphop":["hiphop","hip hop","hip-hop","rap"],
    "soul":["soul","neo-soul","neosoul"],
    "classical":["classical","classic"],
    "orchestra":["orchestra","orchestral","symphonic","symphony"],
    "afrobeats":["afrobeats","afrobeat","afro beats","afro pop","afropop"],
    "amapiano":["amapiano","piano"],
    "trap":["trap"],
    "rock":["rock","hard rock","classic rock"],
    "edm":["edm","electronic","dance","house","techno","dubstep"],
    "pop":["pop","pop music"],
    "afrohouse":["afrohouse","afro house","afro-house"],
    "reggaeton":["reggaeton","regaeton","reggeton"],
    "latino":["latino","latin"],
    "latina":["latina","latin pop"],
    "soundtrack":["soundtrack","ost","movie","film score","score"],
    "kenyan-hiphop":["kenyan hiphop","kenyan hip hop","kenyan rap","ke hiphop","kenya hiphop"],
    "kenyan-trap":["kenyan trap","ke trap","kenya trap"],
    "kenyan-drill":["kenyan drill","ke drill","kenya drill"],
}

def resolve_genre(user_input):
    """Map user typed genre to canonical genre key."""
    ui = user_input.lower().strip()
    for canonical, aliases in GENRE_ALIASES.items():
        if ui in aliases or ui == canonical:
            return canonical
    # fuzzy fallback
    all_aliases = [(alias, canon) for canon, alist in GENRE_ALIASES.items() for alias in alist]
    best = process.extractOne(ui, [a[0] for a in all_aliases], scorer=fuzz.ratio)
    if best and best[1] >= 60:
        for alias, canon in all_aliases:
            if alias == best[0]:
                return canon
    return ui  # return as-is, may match nothing

# ============================================================
#  SECTION 3 — CACHE  (saves deep-search results locally)
# ============================================================
CACHE_FILE = os.path.expanduser("~/.musicdb_cache.json")

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def cache_key(query, mode):
    raw = f"{query}|{mode}|{datetime.now().strftime('%Y-%m-%d')}"
    return hashlib.md5(raw.encode()).hexdigest()

# ============================================================
#  SECTION 4 — MULTI-SOURCE LIVE SEARCH ENGINE
#  Sources: iTunes, MusicBrainz, Deezer, Last.fm, Spotify, AI
# ============================================================
import threading

# ── iTunes Search API (100% free, no key) ────────────────────
def search_itunes(query: str) -> list:
    """
    Hits Apple's iTunes API. Returns real songs with release
    year, artist, album, genre, artwork.
    Endpoint: https://itunes.apple.com/search
    """
    results = []
    try:
        url = "https://itunes.apple.com/search"
        params = {
            "term": query,
            "media": "music",
            "limit": 25,
            "entity": "song"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        for item in data.get("results", []):
            results.append({
                "title":   item.get("trackName", "Unknown"),
                "year":    item.get("releaseDate", "")[:4],
                "artist":  item.get("artistName", "Unknown"),
                "release": item.get("collectionName", "Single"),
                "genre":   item.get("primaryGenreName", "Unknown"),
                "views_m": round(item.get("trackTimeMillis", 0) / 1_000_000, 2),
                "country": item.get("country", "Unknown"),
                "source":  "iTunes"
            })
    except Exception as e:
        console.print(f"[dim red]iTunes error: {e}[/dim red]")
    return results


# ── Deezer API (free, no key needed) ─────────────────────────
def search_deezer(query: str) -> list:
    """
    Deezer's public search endpoint. Returns tracks with
    rank (popularity), artist, album, duration.
    Endpoint: https://api.deezer.com/search
    """
    results = []
    try:
        url = "https://api.deezer.com/search"
        params = {"q": query, "limit": 25}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        for item in data.get("data", []):
            results.append({
                "title":   item.get("title", "Unknown"),
                "year":    "N/A",
                "artist":  item.get("artist", {}).get("name", "Unknown"),
                "release": item.get("album", {}).get("title", "Single"),
                "genre":   query,   # Deezer free tier doesn't return genre
                "views_m": round(item.get("rank", 0) / 100_000, 2),
                "country": "Global",
                "source":  "Deezer"
            })
    except Exception as e:
        console.print(f"[dim red]Deezer error: {e}[/dim red]")
    return results


# ── MusicBrainz API (free, no key, open database) ────────────
def search_musicbrainz(query: str) -> list:
    """
    MusicBrainz is the world's largest open music encyclopedia.
    No key needed. Returns recordings with country + release date.
    Endpoint: https://musicbrainz.org/ws/2/recording
    """
    results = []
    try:
        url = "https://musicbrainz.org/ws/2/recording"
        params = {
            "query": query,
            "limit": 20,
            "fmt":   "json"
        }
        headers = {"User-Agent": "musicdb/1.0 (your@email.com)"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        for item in data.get("recordings", []):
            releases = item.get("releases", [{}])
            release  = releases[0] if releases else {}
            results.append({
                "title":   item.get("title", "Unknown"),
                "year":    release.get("date", "")[:4] or "N/A",
                "artist":  ", ".join(c["artist"]["name"] for c in item.get("artist-credit", [])),
                "release": release.get("title", "Single"),
                "genre":   "Various",
                "views_m": round(item.get("score", 0) / 10, 2),
                "country": release.get("country", "Unknown"),
                "source":  "MusicBrainz"
            })
    except Exception as e:
        console.print(f"[dim red]MusicBrainz error: {e}[/dim red]")
    return results


# ── Last.fm API (free key at last.fm/api) ────────────────────
def search_lastfm(query: str) -> list:
    """
    Last.fm gives you REAL listener/play counts — closest to
    actual 'views'. Get free key at: https://www.last.fm/api
    Set env var: export LASTFM_API_KEY=your_key
    """
    results = []
    api_key = os.environ.get("LASTFM_API_KEY", "")
    if not api_key:
        return []
    try:
        url = "https://ws.audioscrobbler.com/2.0/"
        params = {
            "method":  "track.search",
            "track":   query,
            "api_key": api_key,
            "format":  "json",
            "limit":   100
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        for item in data.get("results", {}).get("trackmatches", {}).get("track", []):
            listeners = int(item.get("listeners", 0))
            results.append({
                "title":   item.get("name", "Unknown"),
                "year":    "N/A",
                "artist":  item.get("artist", "Unknown"),
                "release": "Single",
                "genre":   query,
                "views_m": round(listeners / 1_000_000, 3),
                "country": "Global",
                "source":  "Last.fm"
            })
    except Exception as e:
        console.print(f"[dim red]Last.fm error: {e}[/dim red]")
    return results


# ── Spotify API (free app at developer.spotify.com) ──────────
def search_spotify(query: str) -> list:
    """
    Spotify returns a popularity score (0-100) and full metadata.
    Get free keys at: https://developer.spotify.com
    Set env vars:
      export SPOTIFY_CLIENT_ID=your_id
      export SPOTIFY_CLIENT_SECRET=your_secret
    """
    results = []
    client_id     = os.environ.get("SPOTIFY_CLIENT_ID", "")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return []
    try:
        # Step 1: Get access token
        token_resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=10
        )
        token = token_resp.json().get("access_token", "")
        if not token:
            return []

        # Step 2: Search tracks
        r = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": query, "type": "track", "limit": 25},
            timeout=10
        )
        data = r.json()
        for item in data.get("tracks", {}).get("items", []):
            results.append({
                "title":   item["name"],
                "year":    item["album"]["release_date"][:4],
                "artist":  ", ".join(a["name"] for a in item["artists"]),
                "release": item["album"]["name"],
                "genre":   "Various",
                "views_m": round(item.get("popularity", 0) / 10, 1),
                "country": "Global",
                "source":  "Spotify"
            })
    except Exception as e:
        console.print(f"[dim red]Spotify error: {e}[/dim red]")
    return results


# ── AI Engine stays as is (Claude with web_search) ───────────
# (keep your existing ai_deep_search() function here)
# ============================================================
#  UPGRADED SEARCH FUNCTIONS — Minimum 100 results guaranteed
# ============================================================

MIN_RESULTS = 100   # ← change this number anytime you want more

# ── iTunes — supports pagination via 'offset' ─────────────────
def search_itunes(query: str) -> list:
    results = []
    offset  = 0
    limit   = 50        # iTunes max per request is 200, we use 50 per page

    while len(results) < MIN_RESULTS:
        try:
            r = requests.get(
                "https://itunes.apple.com/search",
                params={
                    "term":   query,
                    "media":  "music",
                    "limit":  limit,
                    "offset": offset,
                    "entity": "song"
                },
                timeout=10
            )
            data  = r.json()
            items = data.get("results", [])
            if not items:
                break                   # no more pages, stop loop

            for item in items:
                results.append({
                    "title":   item.get("trackName",        "Unknown"),
                    "year":    item.get("releaseDate", "")[:4] or "N/A",
                    "artist":  item.get("artistName",       "Unknown"),
                    "release": item.get("collectionName",   "Single"),
                    "genre":   item.get("primaryGenreName", "Unknown"),
                    "views_m": 0,
                    "country": item.get("country",          "Unknown"),
                    "source":  "iTunes"
                })
            offset += limit             # move to next page

        except Exception as e:
            console.print(f"[dim red]iTunes error: {e}[/dim red]")
            break

    return results[:MIN_RESULTS]        # cap at exactly MIN_RESULTS


# ── Deezer — supports pagination via 'index' ──────────────────
def search_deezer(query: str) -> list:
    results = []
    index   = 0
    limit   = 50        # Deezer allows up to 100 per page

    while len(results) < MIN_RESULTS:
        try:
            r = requests.get(
                "https://api.deezer.com/search",
                params={"q": query, "limit": limit, "index": index},
                timeout=10
            )
            data  = r.json()
            items = data.get("data", [])
            if not items:
                break

            for item in items:
                results.append({
                    "title":   item.get("title",  "Unknown"),
                    "year":    "N/A",
                    "artist":  item.get("artist", {}).get("name", "Unknown"),
                    "release": item.get("album",  {}).get("title", "Single"),
                    "genre":   query,
                    "views_m": round(item.get("rank", 0) / 100_000, 2),
                    "country": "Global",
                    "source":  "Deezer"
                })
            index += limit              # next page

        except Exception as e:
            console.print(f"[dim red]Deezer error: {e}[/dim red]")
            break

    return results[:MIN_RESULTS]


# ── MusicBrainz — supports pagination via 'offset' ────────────
def search_musicbrainz(query: str) -> list:
    results = []
    offset  = 0
    limit   = 25        # MusicBrainz allows max 100 but 25 is safe
    headers = {"User-Agent": "musicdb/1.0 (your@email.com)"}

    while len(results) < MIN_RESULTS:
        try:
            r = requests.get(
                "https://musicbrainz.org/ws/2/recording",
                params={"query": query, "limit": limit, "offset": offset, "fmt": "json"},
                headers=headers,
                timeout=12
            )
            data  = r.json()
            items = data.get("recordings", [])
            if not items:
                break

            for item in items:
                releases = item.get("releases", [{}])
                release  = releases[0] if releases else {}
                results.append({
                    "title":   item.get("title", "Unknown"),
                    "year":    release.get("date", "")[:4] or "N/A",
                    "artist":  ", ".join(
                                   c["artist"]["name"]
                                   for c in item.get("artist-credit", [])
                                   if isinstance(c, dict) and "artist" in c
                               ),
                    "release": release.get("title", "Single"),
                    "genre":   "Various",
                    "views_m": round(item.get("score", 0) / 10, 2),
                    "country": release.get("country", "Unknown"),
                    "source":  "MusicBrainz"
                })
            offset += limit
            time.sleep(1)   # MusicBrainz rate limit: 1 request/sec

        except Exception as e:
            console.print(f"[dim red]MusicBrainz error: {e}[/dim red]")
            break

    return results[:MIN_RESULTS]


# ── Last.fm — supports pagination via 'page' number ───────────
def search_lastfm(query: str) -> list:
    results = []
    page    = 1
    limit   = 50
    api_key = os.environ.get("LASTFM_API_KEY", "")
    if not api_key:
        return []

    while len(results) < MIN_RESULTS:
        try:
            r = requests.get(
                "https://ws.audioscrobbler.com/2.0/",
                params={
                    "method":  "track.search",
                    "track":   query,
                    "api_key": api_key,
                    "format":  "json",
                    "limit":   limit,
                    "page":    page
                },
                timeout=10
            )
            data  = r.json()
            items = data.get("results", {}) \
                        .get("trackmatches", {}) \
                        .get("track", [])
            if not items:
                break

            for item in items:
                listeners = int(item.get("listeners", 0))
                results.append({
                    "title":   item.get("name",   "Unknown"),
                    "year":    "N/A",
                    "artist":  item.get("artist", "Unknown"),
                    "release": "Single",
                    "genre":   query,
                    "views_m": round(listeners / 1_000_000, 3),
                    "country": "Global",
                    "source":  "Last.fm"
                })
            page += 1

        except Exception as e:
            console.print(f"[dim red]Last.fm error: {e}[/dim red]")
            break

    return results[:MIN_RESULTS]


# ── Spotify — supports pagination via 'offset' ────────────────
def search_spotify(query: str) -> list:
    results       = []
    offset        = 0
    limit         = 50       # Spotify max per request is 50
    client_id     = os.environ.get("SPOTIFY_CLIENT_ID",     "")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return []

    # Get token once before the loop
    try:
        token_resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=10
        )
        token = token_resp.json().get("access_token", "")
        if not token:
            return []
    except Exception as e:
        console.print(f"[dim red]Spotify token error: {e}[/dim red]")
        return []

    while len(results) < MIN_RESULTS:
        try:
            r = requests.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": query, "type": "track", "limit": limit, "offset": offset},
                timeout=10
            )
            data  = r.json()
            items = data.get("tracks", {}).get("items", [])
            if not items:
                break

            for item in items:
                results.append({
                    "title":   item["name"],
                    "year":    item["album"]["release_date"][:4],
                    "artist":  ", ".join(a["name"] for a in item["artists"]),
                    "release": item["album"]["name"],
                    "genre":   "Various",
                    "views_m": round(item.get("popularity", 0) / 10, 1),
                    "country": "Global",
                    "source":  "Spotify"
                })
            offset += limit

            # Spotify hard cap is offset 1000
            if offset >= 1000:
                break

        except Exception as e:
            console.print(f"[dim red]Spotify error: {e}[/dim red]")
            break

    return results[:MIN_RESULTS]

# ── PARALLEL MULTI-SOURCE DEEP SEARCH ────────────────────────
def deep_search(query: str) -> list:
    """
    Runs ALL sources SIMULTANEOUSLY using threads.
    Each source searches in parallel, results merge at the end.
    This is what makes it fast despite hitting 5+ APIs.
    """
    cache = load_cache()
    ck    = cache_key(query, "deep")
    local = fast_search(query)   # instant local DB

    if ck in cache:
        console.print("[dim]  (cached AI results)[/dim]")
        external = cache[ck]
    else:
        console.print("[cyan]  🌐 Searching all sources in parallel...[/cyan]")
        bucket = []          # shared list all threads write into
        lock   = threading.Lock()

        def run(fn, q):
            res = fn(q)
            with lock:
                bucket.extend(res)

        # Launch all sources at the same time
        threads = [
            threading.Thread(target=run, args=(search_itunes,      query)),
            threading.Thread(target=run, args=(search_deezer,      query)),
            threading.Thread(target=run, args=(search_musicbrainz, query)),
            threading.Thread(target=run, args=(search_lastfm,      query)),
            threading.Thread(target=run, args=(search_spotify,     query)),
            threading.Thread(target=run, args=(ai_deep_search,     query)),
        ]
        for t in threads: t.start()
        for t in threads: t.join()   # wait for ALL to finish

        external = bucket
        cache[ck] = external
        save_cache(cache)

    # Merge local + external, deduplicate by title+artist
    seen     = {(s["title"].lower(), s["artist"].lower()) for s in local}
    combined = local.copy()
    for s in external:
        key = (str(s.get("title","")).lower(), str(s.get("artist","")).lower())
        if key not in seen:
            seen.add(key)
            combined.append(s)

    combined.sort(key=lambda x: float(x.get("views_m", 0) or 0), reverse=True)
    return combined
# ============================================================
#  SECTION 5 — DISPLAY TABLE
# ============================================================
def display_results(results: list, title: str):
    if not results:
        console.print(Panel("[red]No results found.[/red]", title="MusicDB"))
        return

    table = Table(
        title=f"🎵 {title}",
        box=box.ROUNDED,
        show_lines=True,
        style="bold white",
        header_style="bold cyan",
    )
    table.add_column("#",          style="dim",        width=4)
    table.add_column("Title",      style="bold yellow",width=28)
    table.add_column("Artist",     style="green",      width=22)
    table.add_column("Year",       style="cyan",       width=6)
    table.add_column("Release",    style="magenta",    width=25)
    table.add_column("Genre",      style="blue",       width=16)
    table.add_column("Views (M)",  style="red",        width=10)
    table.add_column("Country",    style="white",      width=12)

    for i, s in enumerate(results, 1):
        table.add_row(
            str(i),
            str(s.get("title","—")),
            str(s.get("artist","—")),
            str(s.get("year","—")),
            str(s.get("release","—")),
            str(s.get("genre","—")),
            str(s.get("views_m","—")),
            str(s.get("country","—")),
        )
    console.print(table)
    console.print(f"[dim]  Total results: {len(results)}[/dim]\n")

# ============================================================
#  SECTION 6 — FAST SEARCH
# ============================================================
def fast_search(query: str) -> list:
    """
    Searches local DB only. Matches genre, title, artist, country.
    Uses fuzzy matching for typos.
    """
    q = query.lower().strip()
    canon = resolve_genre(q)
    results = []

    # Phase 1: exact/canonical genre match
    for song in MUSIC_DB:
        g = song["genre"].lower()
        if g == canon or q in g:
            results.append(song)

    # Phase 2: fuzzy title or artist match
    if not results or len(results) < 3:
        for song in MUSIC_DB:
            score_t = fuzz.partial_ratio(q, song["title"].lower())
            score_a = fuzz.partial_ratio(q, song["artist"].lower())
            if score_t >= 70 or score_a >= 70:
                if song not in results:
                    results.append(song)

    # Phase 3: country match (e.g. "kenya")
    if not results:
        for song in MUSIC_DB:
            if q in song.get("country","").lower():
                results.append(song)

    # Sort by views descending
    results.sort(key=lambda x: x.get("views_m", 0), reverse=True)
    return results

# ============================================================
#  SECTION 7 — DEEP SEARCH
# ============================================================
def deep_search(query: str) -> list:
    """
    Fast search PLUS AI-powered web search via Claude API.
    Results are cached per day.
    """
    cache = load_cache()
    ck    = cache_key(query, "deep")

    local = fast_search(query)

    if ck in cache:
        console.print("[dim]  (using cached AI results from today)[/dim]")
        ai_results = cache[ck]
    else:
        console.print("[cyan]  🔍 Querying AI engine (Claude + web search)...[/cyan]")
        ai_results = ai_deep_search(query, "deep search")
        cache[ck] = ai_results
        save_cache(cache)

    # Merge, deduplicate by title+artist
    seen  = {(s["title"].lower(), s["artist"].lower()) for s in local}
    combined = local.copy()
    for s in ai_results:
        key = (str(s.get("title","")).lower(), str(s.get("artist","")).lower())
        if key not in seen:
            seen.add(key)
            combined.append(s)

    combined.sort(key=lambda x: float(x.get("views_m", 0)), reverse=True)
    return combined

# ============================================================
#  SECTION 8 — INTERACTIVE MENU
# ============================================================
BANNER = """
[bold cyan]
╔══════════════════════════════════════════════════════╗
║        🎵  M U S I C D B  — AI Music Search          ║
║  Genres: RnB · HipHop · Soul · Classical · Orchestra ║
║  Afrobeats · Amapiano · Trap · Rock · EDM · Pop      ║
║  Afro House · Reggaeton · Latino · Soundtracks        ║
║  🇰🇪 Kenyan HipHop · Trap · Drill                    ║
╚══════════════════════════════════════════════════════╝
[/bold cyan]
[yellow]Commands:[/yellow]
  [green]fast[/green]  <query>   — Fast search (local database, instant)
  [green]deep[/green]  <query>   — Deep search (local + AI + live web)
  [green]genres[/green]          — List all available genres
  [green]top[/green]             — Top 20 songs by views
  [green]kenya[/green]           — All Kenyan music
  [green]clear[/green]           — Clear cache
  [green]exit[/green]            — Quit
"""

def show_genres():
    t = Table(title="Available Genres", box=box.SIMPLE, header_style="bold magenta")
    t.add_column("Genre Key",   style="cyan")
    t.add_column("Also accepts", style="white")
    for canon, aliases in GENRE_ALIASES.items():
        t.add_row(canon, ", ".join(aliases[:4]))
    console.print(t)

def top_songs():
    top = sorted(MUSIC_DB, key=lambda x: x.get("views_m",0), reverse=True)[:20]
    display_results(top, "Top 20 Songs by Views")

def kenya_music():
    ke = [s for s in MUSIC_DB if "kenya" in s.get("country","").lower()
          or "kenyan" in s.get("genre","").lower()]
    display_results(ke, "Kenyan Music Catalog")

def clear_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        console.print("[green]Cache cleared.[/green]")
    else:
        console.print("[dim]No cache file found.[/dim]")

def interactive_mode():
    console.print(BANNER)
    while True:
        try:
            raw = console.input("[bold green]musicdb>[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye 🎵[/dim]")
            break

        if not raw:
            continue

        parts = raw.split(None, 1)
        cmd   = parts[0].lower()
        arg   = parts[1] if len(parts) > 1 else ""

        if cmd in ("exit", "quit", "q"):
            console.print("[dim]Goodbye 🎵[/dim]")
            break
        elif cmd == "fast":
            if not arg:
                console.print("[red]Usage: fast <genre or artist or title>[/red]")
            else:
                console.print(f"[cyan]⚡ Fast search: '{arg}'[/cyan]")
                t = time.time()
                r = fast_search(arg)
                console.print(f"[dim]  ({time.time()-t:.3f}s)[/dim]")
                display_results(r, f"Fast Search: {arg}")
        elif cmd == "deep":
            if not arg:
                console.print("[red]Usage: deep <genre or artist or title>[/red]")
            else:
                console.print(f"[magenta]🌐 Deep search: '{arg}'[/magenta]")
                t = time.time()
                r = deep_search(arg)
                console.print(f"[dim]  ({time.time()-t:.2f}s)[/dim]")
                display_results(r, f"Deep Search: {arg}")
        elif cmd == "genres":
            show_genres()
        elif cmd == "top":
            top_songs()
        elif cmd == "kenya":
            kenya_music()
        elif cmd == "clear":
            clear_cache()
        else:
            # treat whole line as a fast search
            console.print(f"[cyan]⚡ Auto fast search: '{raw}'[/cyan]")
            display_results(fast_search(raw), f"Search: {raw}")

# ============================================================
#  SECTION 9 — CLI  (command-line flags for scripting)
# ============================================================
def cli_mode():
    parser = argparse.ArgumentParser(
        prog="musicdb",
        description="AI-Powered Music Search Engine"
    )
    sub = parser.add_subparsers(dest="command")

    p_fast = sub.add_parser("fast",  help="Fast search local DB")
    p_fast.add_argument("query", nargs="+")

    p_deep = sub.add_parser("deep",  help="Deep search (AI + web)")
    p_deep.add_argument("query", nargs="+")

    sub.add_parser("genres", help="List all genres")
    sub.add_parser("top",    help="Top 20 songs by views")
    sub.add_parser("kenya",  help="All Kenyan music")
    sub.add_parser("clear",  help="Clear AI cache")

    args = parser.parse_args()

    if args.command == "fast":
        q = " ".join(args.query)
        display_results(fast_search(q), f"Fast: {q}")
    elif args.command == "deep":
        q = " ".join(args.query)
        display_results(deep_search(q), f"Deep: {q}")
    elif args.command == "genres":
        show_genres()
    elif args.command == "top":
        top_songs()
    elif args.command == "kenya":
        kenya_music()
    elif args.command == "clear":
        clear_cache()
    else:
        interactive_mode()

# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_mode()
    else:
        interactive_mode()
