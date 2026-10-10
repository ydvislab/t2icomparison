# Closed-model generation (product defaults)

Groups C1–C3 in `docs/PLAN.md` §4. Run locally: no GPU is needed. API keys are read from environment variables only and must never be written into files in this repository.

| Group | Provider | Model (VERIFY before running) | Key variable | SDK |
|---|---|---|---|---|
| `gpt_image` | OpenAI Image API | `gpt-image-2.5-sunburst` | `OPENAI_API_KEY` | `pip install openai` |
| `gemini_image` | Google Gemini (Interactions API) | `gemini-nano-banana-2.1` | `GEMINI_API_KEY` | `pip install google-genai` |
| `seedream` | ByteDance Seedream (Volcengine Ark) | `doubao-seedream-5-0-260128` | `ARK_API_KEY` | `pip install volcengine-python-sdk[ark]` |

Each group generates 24 main prompts × 16 plus 6 control prompts × 16, which is 480 images (`../prompts.py`, `docs/PROMPTS.md`).

## Workflow
1. **Check settings** in `config.py` against each provider's current documentation: the model ID, the 1:1 size value, and whether prompt rewriting can be switched off (Seedream `optimize_prompt_options`). Update the values marked `VERIFY`.
2. **Set keys** in your shell for the current session only, for example in PowerShell:
   ```
   $env:OPENAI_API_KEY = "..."
   ```
3. **Dry run** (no API calls; prints the settings and the first jobs):
   ```
   python gen_closed.py gpt_image --dry-run
   ```
4. **Smoke test** with 2 images per group. Open the images and `meta.csv`, and check the size, that there is no visible watermark, and the recorded model and parameters:
   ```
   python gen_closed.py gpt_image --limit 2
   ```
5. **Full run** per group. The script is resumable: rerunning skips finished jobs and retries failed ones.
   ```
   python gen_closed.py gpt_image
   ```
6. **Record** the run dates and any refusals or failures, which are logged as `FAILED` and skipped. Do not regenerate refused prompts with different wording.
7. **Hand over:** copy `$T2IC_DATA/model_study/closed/` (default `~/va4ext/model_study/closed/`, about 1,440 images) to the server's `T2IC_DATA` at `/mnt/data/t2icomparison/data/model_study/closed/`. This transfer goes over the local connection; at about 1–3 MB per PNG it is roughly 1.5–4 GB.

## Output
`<group>/<job>.png` plus `<group>/meta.csv` with the columns job, kind (main/control), category, subject, prompt, k, group, provider, model, params, returned_model, revised_prompt, request_id, utc, seconds and file. Job IDs match the open-model groups (`m<prompt>_<k>`, `c<n>_<k>`), so the analysis treats every group the same way.

## Review checklist
- [ ] The model IDs are the current versions you intend to report, and the API's returned model name is recorded.
- [ ] One image per request (`n=1`); no prompt prefix, suffix or system text is added.
- [ ] Square output near 1K on all three providers; sizes are recorded in `params`.
- [ ] Visible watermarks are off (Seedream `watermark=False`); Gemini's invisible SynthID cannot be turned off and is noted.
- [ ] Prompt rewriting: OpenAI Image API does not rewrite (only the Responses API does). Gemini always runs a thinking step, which is left at the API default and noted. For Seedream, record whether optimisation is on, and add the `seedream_norewrite` condition if it can be disabled.
- [ ] No seeds are available. The 16 samples per prompt are independent requests, and providers may cache identical requests. Check that the images for one prompt are not byte-identical.
- [ ] The run dates are recorded, because services change silently.
- [ ] Keys appear only in environment variables, never in files or commits.

## Notes for the paper
- Closed-model groups are **product defaults**: settings are undeclared, so the system marks them "cannot attribute". Report location and spread only.
- Cite the API model name and the date range of the run.
