# Reddit editorial radar — @polvo.ia

Read-only client for the Reddit Data API, published alongside our Data Access
Request so the request can be reviewed against the real implementation rather
than a description of it.

**Source:** [`radar_reddit.py`](radar_reddit.py) — this is the complete
Reddit-facing code. There is no other file that talks to Reddit.

## What it does

Once or twice a day it asks five AI-related subreddits for the top posts of
the week and reads four fields per post: **title, score, comment count,
permalink**. That tells the editor which AI topics are gaining traction, so
the account can decide what to research and cover in its own original
reporting.

| | |
|---|---|
| Endpoints used | `POST /api/v1/access_token`, `GET /r/{subreddit}/top` |
| Auth | `client_credentials` (application-only) |
| Subreddits | r/singularity, r/aivideo, r/StableDiffusion, r/OpenAI, r/artificial |
| Volume | ~50 requests/day (free tier allows 100 QPM) |

## What it cannot do

These are properties of the code, verifiable by reading it — not promises.

- **No writes.** There is no `POST`/`PUT`/`DELETE` to Reddit anywhere except
  the token request itself.
- **No user context.** `client_credentials` never acts on behalf of a Reddit
  account, so voting, commenting, posting, messaging and moderating are
  impossible by construction.
- **No storage.** Titles live in memory for one run and are discarded.
- **No republishing.** Reddit content never appears in our output. What leaves
  this tool is a decision about which *subject* to research from primary
  sources.
- **No model training.**

## About the account

[@polvo.ia](https://www.instagram.com/polvo.ia/) publishes short
Portuguese-language videos about artificial intelligence — one topic a day,
researched from primary sources and narrated originally, with the source
outlet credited.

- Site: https://selinbrasil.github.io/polvo-ia/
- Privacy policy: https://selinbrasil.github.io/polvo-ia/privacidade.html
- Terms: https://selinbrasil.github.io/polvo-ia/termos.html
- Contact: polvo.inteligenciaartificial@gmail.com
