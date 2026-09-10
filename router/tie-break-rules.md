# Router Tie-break Rules

Hard gates run before scoring. An ineligible Style cannot win, regardless of score. Ratio compatibility contributes at most ±5 points.

If the top score exceeds the runner-up by at least 12 points, select it. Otherwise apply these deterministic rules.

## Single image

Prefer the more specific supported structure:

1. real linear landmark → `STYLE_03`;
2. real locked civic building plus horizontal base → `STYLE_05`;
3. formal central heritage monument → `STYLE_02`;
4. multi-cultural heritage cityscape → `STYLE_04`;
5. rich city life with a strong HERO and transit/infrastructure → `STYLE_06`;
6. wide continuous city fabric with compositional corridors for swash geometry → `STYLE_07`;
7. otherwise → `STYLE_01`, but only when its complete source prompt is installed.

## Multi-image fusion

1. heritage monument plus heritage details → `MULTI_STYLE_02`;
2. nature/fauna/destination diversity → `MULTI_STYLE_03`;
3. vertical HERO ≥ 0.80 and monumentality ≥ 0.70 → `MULTI_STYLE_05`;
4. vertical HERO plus transit, foreground framing, and directional counterbalance → `MULTI_STYLE_06`;
5. balanced HERO + secondary + skyline + transit → `MULTI_STYLE_04`;
6. otherwise → `MULTI_STYLE_01`.

If the winning Style is unavailable, do not silently choose a different Style merely to avoid a missing Prompt. Return compatibility review or `blocked_missing_prompt`.

User Style override bypasses automatic ranking but not compatibility or fact checks. User HERO override preserves that HERO and recalculates compatibility without substituting a different subject.

