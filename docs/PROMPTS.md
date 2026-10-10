# Prompt set for the model study (final, 2026-10-10)

Status: approved by the owner on 2026-10-10. Nothing has been generated with it yet. This set has 24 prompts (v1 had 30). It removes prompts that are open to dispute (abstract concepts, groups of people, scenes with cultural or emotional connotations) and keeps subjects where many aspects are genuinely open.

## Principles
1. **Minimal and underspecified.** Each prompt names only the subject: no words for medium, lighting, framing, colour, quality or style.
2. **Uncontroversial.** Everyday subjects only: no abstract concepts, demographic groups, children, religious or cultural events, brands, real people, or text rendering.
3. **Defaults must be visible.** Each subject leaves most of the 15 aspects open: it could plausibly be shown day or night, as a photo or a painting, close or far, warm or cool, plain or busy. Subjects that fix many aspects by themselves are avoided.
4. **Keep the 12 earlier subjects** (marked ●) so that the study can be checked against the pilot findings on the same subjects. The pilot images themselves are not reused: the study regenerates every group with its own settings (e.g. SD1.5 at 50 steps instead of 25, SDXL-Turbo at 1 step instead of 4, klein at 1024² instead of 768²) and a new seed list.
5. **Balanced categories:** 6 categories × 4 prompts. A finding is reported for a model only if it holds in most categories; otherwise it is reported as category-specific.
6. **Prompt-implied aspects are excluded per prompt** (e.g. in/out for "a kitchen") from location and spread statistics.

## Main set (24 prompts)
| # | Category | Prompt | Excluded aspects |
|---|---|---|---|
| 1 | People | a doctor ● | — |
| 2 | People | a person reading a book ● | — |
| 3 | People | a musician | — |
| 4 | People | a traveler | — |
| 5 | Animals | a dog ● | — |
| 6 | Animals | a bird on a branch ● | — |
| 7 | Animals | a cat | — |
| 8 | Animals | a horse | — |
| 9 | Objects | a car ● | — |
| 10 | Objects | a cup of coffee ● | — |
| 11 | Objects | a bicycle ● | — |
| 12 | Objects | a bowl of fruit | — |
| 13 | Indoor scenes | a kitchen ● | in/out |
| 14 | Indoor scenes | a living room ● | in/out |
| 15 | Indoor scenes | a library | in/out |
| 16 | Indoor scenes | a restaurant | in/out |
| 17 | Outdoor scenes | a house ● | — (inside or outside both plausible) |
| 18 | Outdoor scenes | a city street ● | in/out |
| 19 | Outdoor scenes | a mountain ● | in/out |
| 20 | Outdoor scenes | a beach | in/out |
| 21 | Activity scenes | a market | — |
| 22 | Activity scenes | a train station | — |
| 23 | Activity scenes | a birthday party | — |
| 24 | Activity scenes | a picnic | in/out |

Category roles:
- **People:** the subject is a person whose demographics are not measured (out of scope, stated as a limitation). These prompts show framing, setting and lighting defaults for portraits.
- **Objects:** classic still-life and product-shot defaults (centred, plain background, shallow depth of field).
- **Activity scenes:** many elements per scene, so they show defaults for time of day, crowd and clutter, and mood.

## Control set (6 prompts, not part of the main statistics)
Each control specifies one aspect value on a main-set subject. Controls are used to (1) check that the aspect measurement moves in the expected direction for every model, and (2) measure how far each model moves away from its default when asked.

| # | Prompt | Aspect and expected direction |
|---|---|---|
| C1 | a house at night | time → night |
| C2 | a black and white photograph of a dog | saturation → muted; medium → photo |
| C3 | an oil painting of a cup of coffee | medium → painting |
| C4 | a close-up of a bicycle | shot → close-up |
| C5 | a kitchen in warm golden light | light → warm |
| C6 | a city street seen from above | angle → high angle |

## Sample sizes and image counts
| Groups | Prompts | Seeds | Images |
|---|---|---|---|
| Open models and settings (about 10 groups) | 24 main + 6 control | 32 main, 16 control | about 10 × (768 + 96) ≈ 8,600 |
| Closed models (3) | 24 main + 6 control | 16 | 3 × 480 = 1,440 API calls |

- One fixed seed list per prompt, shared by all open-model groups.
- Closed models: record the API model name, version and date. Turn prompt rewriting off where the API allows it, and run a second condition with rewriting on where it can be toggled.
