"""Read-only editorial radar for @polvo.ia — Reddit Data API client.

This is the complete Reddit-facing code of the tool described in our Data
Access Request. It is published so the request can be reviewed against the
actual implementation instead of a description.

WHAT IT DOES
------------
Once or twice a day it asks five AI-related subreddits for the top posts of
the week, and reads four fields per post: title, score, comment count and
permalink. That tells the editor which AI topics are gaining traction, so the
account can decide what to cover in its own original reporting.

WHAT IT DOES NOT DO — and cannot, by construction
-------------------------------------------------
* No writes. There is no POST/PUT/DELETE call to Reddit anywhere in this file.
  The only Reddit request besides the token is a GET to /r/{sub}/top.
* No user context. Authentication is `client_credentials` (application-only),
  so the client is never acting on behalf of any Reddit account. It cannot
  vote, comment, post, message, or moderate.
* No storage. Titles are held in memory for the duration of one run and
  discarded. Nothing is written to disk or to a database.
* No republishing. Reddit content is never reproduced in our output. What
  leaves this tool is a decision about which SUBJECT to research from primary
  sources.
* No model training. None of this data trains anything.

VOLUME
------
Five subreddits, one request each, once or twice a day: about 50 requests per
day at the maximum. The free tier allows 100 queries per minute.

CONTACT
-------
polvo.inteligenciaartificial@gmail.com
https://selinbrasil.github.io/polvo-ia/
"""

import os
import sys
import time

import requests

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "").strip()

# Reddit asks for platform:app-id:version (by /u/username).
AGENTE = "windows:polvoia-radar:v1.0 (by /u/polvoia)"

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API = "https://oauth.reddit.com"

SUBS = ["singularity", "aivideo", "StableDiffusion", "OpenAI", "artificial"]

_cache = {"token": None, "expira": 0}


def token() -> str:
    """Application-only token. Valid for one hour, no refresh token issued."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise SystemExit("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.")
    if _cache["token"] and time.time() < _cache["expira"] - 60:
        return _cache["token"]

    r = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET),
                      data={"grant_type": "client_credentials"},
                      headers={"User-Agent": AGENTE}, timeout=40)
    r.raise_for_status()
    d = r.json()
    _cache["token"] = d["access_token"]
    _cache["expira"] = time.time() + int(d.get("expires_in", 3600))
    return _cache["token"]


def top_da_semana(sub: str, limite: int = 25) -> list[dict]:
    """GET /r/{sub}/top — the only Reddit endpoint this tool ever calls."""
    r = requests.get(f"{API}/r/{sub}/top",
                     params={"t": "week", "limit": limite},
                     headers={"Authorization": f"Bearer {token()}",
                              "User-Agent": AGENTE}, timeout=40)
    r.raise_for_status()

    saida = []
    for filho in r.json().get("data", {}).get("children", []):
        p = filho["data"]
        # Exactly four fields. Nothing else is read, kept or passed along.
        saida.append({
            "titulo": p.get("title", ""),
            "votos": p.get("ups", 0),
            "comentarios": p.get("num_comments", 0),
            "link": f"https://www.reddit.com{p.get('permalink', '')}",
        })
    return saida


def varrer() -> list[dict]:
    achados = []
    for sub in SUBS:
        try:
            for p in top_da_semana(sub):
                achados.append({**p, "sub": sub})
        except requests.HTTPError as erro:
            print(f"  r/{sub}: {erro}", file=sys.stderr)
    achados.sort(key=lambda a: -a["votos"])
    return achados


if __name__ == "__main__":
    for p in varrer()[:15]:
        print(f"{p['votos']:>6} ups  r/{p['sub']:16} {p['titulo'][:60]}")
        print(f"        {p['link']}")
