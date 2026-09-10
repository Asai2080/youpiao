# Multi-image Fusion Policy

Analyze every image separately before fusion. Fusion is semantic reconstruction, not a collage.

This policy is for routing and QA only. Do not translate it into a second fusion brief or append it to the generation prompt; the selected multi-image source prompt alone controls the generated composition.

Choose one real HERO unless the selected Style explicitly defines a different hero role. User-selected HERO overrides automatic ranking. Assign secondary, foreground, background, and connector roles by recognition value, structural completeness, silhouette complement, and spatial usefulness.

`NOT EVERY IMAGE MUST APPEAR`. Record unused images and the reason. Do not mechanically average coverage.

All retained elements must share:

- one perspective anchor and observation height;
- coherent relative scale;
- one lighting direction and color temperature;
- one atmospheric depth system;
- one print medium and aging treatment.

Do not make landmarks grow into each other, duplicate them, or preserve conflicting camera viewpoints. Geographic compression is allowed only for a Style that supports it and only inside a reliable common destination identity.

Images from different destinations may be fused when the user requests it, but do not describe them as one shared city. Build a union of the verified building, attraction, city, and place names extracted from every input image. Randomly select the primary title only from that pool and record its source image and evidence. Never invent a common city identity. If the pool is empty, stop at `BLOCKED_UNVERIFIED_PRIMARY_TITLE`.
