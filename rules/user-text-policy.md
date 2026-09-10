# User and Automatic Text Policy

Never ask whether the user wants text. Read the images and create an appropriate text plan automatically.

Text priority is:

```text
USER_TEXT
> VERIFIED_FACT_TEXT
> STYLE_DECORATIVE_TEXT
```

User text is preserved as supplied unless the user asks for editing. Automatic factual text must satisfy the Global Fact Policy. Decorative text must be unmistakably nonfactual and compatible with the selected Style.

Before automatic titling, create a verified-name candidate pool from every image. For a single image, choose the most specific eligible name from that image. For fusion, merge and deduplicate all eligible names and randomly choose only from that pool. Never synthesize a city or landmark name from visual style.

Do not add text merely to fill every visual slot. Empty is safer than invented. Do not repeat questions for information the user already supplied.
