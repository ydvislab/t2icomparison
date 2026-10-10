"""Closed-model groups (product defaults). Every value marked VERIFY must be checked against the provider's
current documentation before the real run; model IDs and options change often.

Principle: use each API's defaults, and fix only what must be equal across groups: one image per request,
square output near 1024 px, no visible watermark, lossless PNG where offered. Record everything in meta.csv."""
import os

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
OUT = f"{DATA}/model_study/closed"
N_MAIN, N_CONTROL = 16, 16

GROUPS = {
    # OpenAI Image API (images.generate). No seed. The Image API does not revise prompts (only the Responses API
    # does), so this is the "no rewriting" condition by construction.
    "gpt_image": dict(
        provider="openai", key_env="OPENAI_API_KEY",
        model="gpt-image-2.5-sunburst",            # VERIFY: latest GPT image model ID
        params=dict(size="1024x1024", n=1, output_format="png"),  # quality / moderation left at API default
    ),
    # Google Gemini image model via google-genai (Interactions API). No seed. Images carry an invisible SynthID.
    "gemini_image": dict(
        provider="gemini", key_env="GEMINI_API_KEY",
        model="gemini-nano-banana-2.1",            # VERIFY: model ID; alternative gemini-3-pro-image
        params=dict(aspect_ratio="1:1", image_size="1K"),  # thinking level left at API default
    ),
    # ByteDance Seedream via Volcengine Ark. No seed (only seedream-3.0 supports it).
    "seedream": dict(
        provider="ark", key_env="ARK_API_KEY",
        model="doubao-seedream-5-0-260128",        # VERIFY: model ID (5.0 lite / pro)
        params=dict(size="2K", watermark=False, response_format="b64_json", output_format="png"),  # VERIFY: 1:1 size value
    ),
    # Optional second Seedream condition: prompt optimisation explicitly off, if the API allows disabling it.
    # Enable only after checking the docs; otherwise leave commented out and report rewriting as unknown.
    # "seedream_norewrite": dict(provider="ark", key_env="ARK_API_KEY", model="doubao-seedream-5-0-260128",
    #     params=dict(size="2K", watermark=False, response_format="b64_json", output_format="png",
    #                 optimize_prompt_options={"mode": "..."})),  # VERIFY
}
