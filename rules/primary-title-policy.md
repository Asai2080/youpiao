# Primary Title Policy

The main stamp title must come from a verified name candidate extracted before generation. Never infer a place from architectural style, cultural appearance, visual similarity, country, or general knowledge alone.

Eligible candidate evidence is limited to:

- a name explicitly provided by the user;
- clearly readable text or signage in the image;
- a reliably verified image identity or metadata record;
- a reliable external source when verification is authorized and performed.

For one image, prefer the most specific supported object in this order:

1. attraction or building name;
2. city name.

A country name must never be the primary title. It may appear only as small secondary text, a postmark, or Footer content when the selected Style permits it.

If no attraction, building, or city can be identified with reliable evidence, do not invent one and do not fall back to a country name. Stop at `BLOCKED_UNVERIFIED_PRIMARY_TITLE` and request only the missing identity.

For a fusion image, merge and deduplicate eligible candidates from all input images. The primary title must be selected randomly from that complete verified pool. Randomness applies only to title selection, never to Style routing. A selected or rendered title outside the pool is an automatic failure.

This policy is represented inside every active portrait v3 and landscape v4 Style source prompt. It is also a routing and QA gate; it must never be appended separately at generation time.
