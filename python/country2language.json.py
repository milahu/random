#!/usr/bin/env python3

# map country codes (ISO 3166) to language codes (ISO 639)
# https://github.com/georgkrause/langcodes/issues/16

# https://gist.github.com/missinglink/ebe8ba69e58dbdfb47750f6079364ecc
json_url = "https://gist.github.com/missinglink/ebe8ba69e58dbdfb47750f6079364ecc/raw/05e59101780aa4b21995af0432d12a45fbac54d2/codes.json"
json_path = "country2language.json"

import os
import json
import langcodes

if not os.path.exists(json_path):
    import urllib.request
    urllib.request.urlretrieve(json_url, json_path)

with open(json_path) as f:
    country2language = json.load(f)

map_lang4country = dict()
collisions = list()
for country, lang in country2language.items():
    country = country.lower()
    lang = lang.split(",")[0].split("-")[0]
    if country == lang:
        continue
    if lang == "":
        # "AQ": "", # Antarctica
        # "BV": "", # Bouvet Island
        # "HM": "", # Heard Island and McDonald Islands
        continue
    try:
        langcodes.Language.get(country).to_alpha3(variant='B')
        # collision between country codes and language codes
        collisions.append(country)
    except LookupError:
        map_lang4country[country] = lang

print("map_lang4country", json.dumps(map_lang4country))
print("collisions", json.dumps(collisions))

###

map_lang4country = {
    "ad": "ca", "ag": "en", "ai": "en", "al": "sq", "ao": "pt", "at": "de",
    "au": "en", "aw": "nl", "ax": "sv", "bb": "en", "bd": "bn", "bf": "fr",
    "bj": "fr", "bl": "fr", "bq": "nl", "bt": "dz", "bw": "en", "by": "be",
    "bz": "en", "cc": "ms", "cd": "fr", "cf": "fr", "cg": "fr", "ci": "fr",
    "ck": "en", "cl": "es", "cm": "en", "cn": "zh", "cw": "nl", "cx": "en",
    "cz": "cs", "dj": "fr", "dk": "da", "dm": "en", "do": "es", "ec": "es",
    "eg": "ar", "eh": "ar", "er": "aa", "fk": "en", "fm": "en", "gb": "en",
    "ge": "ka", "gf": "fr", "gg": "en", "gh": "en", "gi": "en", "gm": "en",
    "gp": "fr", "gq": "es", "gr": "el", "gs": "en", "gt": "es", "gw": "pt",
    "gy": "en", "hk": "zh", "hn": "es", "il": "he", "im": "en", "iq": "ar",
    "ir": "fa", "je": "en", "jm": "en", "jo": "ar", "jp": "ja", "ke": "en",
    "kh": "km", "kp": "ko", "kz": "kk", "lc": "en", "lk": "si", "lr": "en",
    "ls": "en", "ly": "ar", "ma": "ar", "mc": "fr", "md": "ro", "me": "sr",
    "mf": "fr", "mm": "my", "mp": "fil", "mq": "fr", "mu": "en", "mv": "dv",
    "mw": "ny", "mx": "es", "mz": "pt", "nc": "fr", "nf": "en", "ni": "es",
    "np": "ne", "nu": "niu", "nz": "en", "pe": "es", "pf": "fr", "pg": "en",
    "ph": "tl", "pk": "ur", "pm": "fr", "pn": "en", "pr": "en", "pw": "pau",
    "py": "es", "qa": "ar", "re": "fr", "rs": "sr", "sb": "en", "sj": "no",
    "sx": "nl", "sy": "ar", "sz": "en", "tc": "en", "td": "fr", "tf": "fr",
    "tj": "tg", "tm": "tk", "tv": "tvl", "tz": "sw", "ua": "uk", "um": "en",
    "us": "en", "uy": "es", "va": "la", "vc": "en", "vg": "en", "vn": "vi",
    "vu": "bi", "wf": "wls", "ws": "sm", "xk": "sq", "ye": "ar", "yt": "fr",
    "zm": "en", "zw": "en"
}

def lang4country(country):
    try:
        return map_lang4country[country]
    except KeyError:
        return country

assert lang4country("jp") == "ja"
assert lang4country("cz") == "cs"
