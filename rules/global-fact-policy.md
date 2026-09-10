# Global Fact Policy

Factual accuracy outranks Style DNA and decoration.

Allowed factual text must be supported by at least one of:

- explicit user-provided text;
- text visibly present in the input image;
- high-confidence image identification with recorded evidence;
- a reliable external source when verification is authorized and performed.

Without reliable support, do not generate factual text. This especially covers years, dates, denominations, currency, serial numbers, anniversaries, coordinates, official emblems, postal authorities, building names, and historical events.

The primary title must exist in the recorded verified-name candidate pool. A country name is never allowed as the primary title. Architectural style, cultural appearance, resemblance, and general geographic association are not identity evidence. If no eligible identity can be verified, stop instead of inventing a title or falling back to the country.

A visual slot may remain empty or use clearly nonfactual Style decoration. Never convert uncertainty into a plausible-looking fact. Record verification type and confidence in the analysis and text plan.
