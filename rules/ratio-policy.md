# Output Ratio Policy

The output uses one of two fixed orientation contracts:

```text
PORTRAIT = 2:3, 1024 × 1536 PX
LANDSCAPE = 3:2, 1536 × 1024 PX
ASK_USER_FOR_ORIENTATION_WHEN_MISSING = TRUE
ASK_USER_FOR_CUSTOM_RATIO = FALSE
```

When the user has not specified an orientation, ask only: `横版还是竖版？` Do not ask for a numeric ratio or custom dimensions. Do not repeat the question when the user already supplied an orientation.

Map `竖版` / portrait to 2:3 at 1024×1536 px. Map `横版` / landscape to 3:2 at 1536×1024 px. No other ratio or dimensions are supported unless the user explicitly changes the Skill specification again.

Do not append ratio or dimension instructions to the selected source prompt. Apply native generation parameters outside prompt text when available; otherwise normalize the completed stamp proportionally during transparent-background post-processing.

For multiple images, also ask for fusion versus independent generation when that choice is missing. Orientation compatibility may contribute at most ±5 router points; it must not drive Style selection.

After selection, adapt composition in this order:

```text
PRESERVE HERO
> RECOMPOSE
> EXTEND ENVIRONMENT
> CROP
```

Never solve a ratio mismatch by simple center-cropping the HERO. Preserve at least 95% of identity-defining shape, structure, and landmark details.
