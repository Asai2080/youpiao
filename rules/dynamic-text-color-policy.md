# Dynamic Text Color Policy

The image determines which colors exist. The selected Style determines what each color is used for.

The color analyzer may only return candidates in these groups:

- `STRUCTURAL_DARK`
- `ARCHITECTURAL_MATERIAL`
- `IDENTITY_ACCENT`
- `ENVIRONMENT_COLOR`
- `WARM_ACCENT`
- `LIGHT_COLOR`

It must not choose the final title color. Resolve title, secondary, accent, and knockout roles from the selected Style Card.

Never copy a raw photo RGB value directly. Convert the chosen candidate through:

```text
DESATURATION
+ DARKENING
+ GREYING
+ INK OXIDATION
+ PAPER ABSORPTION
+ PRINT AGING
```

Prefer stable colors repeated across meaningful regions, not a single darkest pixel or accidental bright object. When contrast is insufficient, preserve hue first, then adjust lightness and ink density, then use the Style's paper knockout. Do not solve contrast by randomly changing hue.

