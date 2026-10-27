"""Compose the screenshot figures of the PacificVis paper (Figs. 4-6) from the shots of shots.mjs.
Usage: python make_figures.py   (reads figures/*.png at 3360 x 2000, writes figures/fig4_interface.png, fig5_cases_61_62.png,
fig6_cases_63_64.png at about 300 dpi for a 7-inch full-width figure).
Crop boxes are in screenshot pixels (viewport 1680 x 1000 at device scale 2); the panel letters A-E come from the tool."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
S = 2  # device scale of the shots
# panels in viewport pixels (x0, y0, x1, y1)
PANEL = {"A": (14, 53, 779, 624), "B": (785, 53, 1352, 624), "C": (14, 630, 779, 987), "D": (785, 630, 1352, 987),
         "E_sat": (1359, 53, 1666, 237), "E_medium": (1359, 246, 1666, 424), "E_shot": (1359, 432, 1666, 613),
         "E_tone": (1359, 622, 1666, 802), "E_bg": (1359, 810, 1666, 987)}
INK, MUTED, BG = (11, 18, 32), (90, 100, 118), (255, 255, 255)


def font(size, bold=False):
    for f in (["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]):
        for d in ("C:/Windows/Fonts", "/usr/share/fonts/truetype/dejavu", ""):
            try:
                return ImageFont.truetype(os.path.join(d, f) if d else f, size)
            except OSError:
                pass
    return ImageFont.load_default()


def crop(shot, key):
    x0, y0, x1, y1 = PANEL[key]
    return Image.open(os.path.join(FIG, shot + ".png")).convert("RGB").crop((x0 * S, y0 * S, x1 * S, y1 * S))


def fit_h(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def fit_w(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def hcat(ims, gap=24):
    h = max(i.height for i in ims)
    out = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), h), BG)
    x = 0
    for i in ims:
        out.paste(i, (x, 0)); x += i.width + gap
    return out


def vcat(ims, gap=24):
    w = max(i.width for i in ims)
    out = Image.new("RGB", (w, sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for i in ims:
        out.paste(i, (0, y)); y += i.height + gap
    return out


def titled(im, text, size=44, sub=None):
    """A sub-figure with its tag line above: '(a) text' in ink, an optional note in muted grey."""
    pad = round(size * 1.6)
    out = Image.new("RGB", (im.width, im.height + pad), BG)
    d = ImageDraw.Draw(out)
    d.text((4, 4), text, fill=INK, font=font(size, True))
    if sub:
        w = d.textlength(text, font=font(size, True))
        d.text((w + 24, 4 + size * 0.08), sub, fill=MUTED, font=font(round(size * .9)))
    out.paste(im, (0, pad))
    return out


def frame(im, c=(220, 226, 235), w=3):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width - 1, im.height - 1], outline=c, width=w)
    return im


def save(im, name, width=3000):
    im = fit_w(im, width) if im.width > width else im
    im.save(os.path.join(FIG, name), dpi=(int(width / 7), int(width / 7)))
    print(name, im.size)


def main():
    # Fig. 4: the interface, whole screen
    save(frame(Image.open(os.path.join(FIG, "interface_klein_chain.png")).convert("RGB")), "fig4_interface.png")

    # Fig. 5, case 6.1: the same view under CLIP and SigLIP 2; the maps side by side, then the medium and tone scatters
    maps = hcat([titled(crop("case61_clip_medium", "A"), "CLIP", size=40), titled(crop("case61_siglip_medium", "A"), "SigLIP 2", size=40)], gap=36)
    cards = hcat([crop("case61_clip_medium", "E_medium"), crop("case61_clip_medium", "E_tone"),
                  crop("case61_siglip_medium", "E_medium"), crop("case61_siglip_medium", "E_tone")], gap=12)
    save(vcat([maps, fit_w(cards, maps.width)], gap=24), "fig5_case61.png")

    # Fig. 6: (a) case 6.2, SDXL -> Turbo on saturation: the scatter with subjects on both sides of the pooled diamond and
    #             the image lanes of one subject each way, in one strip;
    #         (b) case 6.3, the rewriter's background effect on a failed axis, with its images
    W = 3000
    horse = titled(crop("case62_turbo_horse", "C"), "a horse: Turbo more vivid", size=48)
    bird = titled(crop("case62_turbo_bird", "C"), "a bird on a branch: Turbo more muted", size=48)
    card = titled(crop("case62_turbo_horse", "E_sat"), "subjects on both sides", size=24)
    a = titled(fit_w(hcat([fit_h(card, horse.height), horse, bird], gap=24), W), "(a) Case 6.2: SDXL → SDXL-Turbo, saturation",
               sub="pooled +0.17; 7 subjects turn muted against it")
    e = vcat([crop("case63_rewrite_bg", "E_bg"), crop("case63_rewrite_bg", "E_medium")], gap=12)
    c = crop("case63_rewrite_bg", "C")
    b = titled(fit_w(hcat([fit_h(e, c.height), c], gap=24), W), "(b) Case 6.3: FLUX.2 dev → FLUX.2 rewrite",
               sub="background, not validated on rewritten images; a picnic")
    save(vcat([a, b], gap=60), "fig6_cases_62_63.png")

    # Fig. 7 (one column), case 6.4: a VLM statement about SDXL -> Turbo traced to the measurement, the subject and its images
    save(frame(crop("case64_trail", "A")), "fig7_case64.png", width=1500)

    # ---- draft 4 (system paper): design components, case 1 (distillation), case 2 (language claims) ----
    PANEL.update({"E_u1": (1359, 727, 1666, 851), "E_u2": (1359, 863, 1666, 987)})
    W = 3000
    def row(items, h=None):
        h = h or max(i.height for i in items)
        return hcat([fit_h(i, h) for i in items], gap=28)
    # Fig. 3, design components: (a) contrast scatter with margins, intervals and set members; (b) subject matrix with
    # per-member shift columns and reversals; (c) the same seeds through the set; (d) VLM statements with verdicts;
    # (e) the audit trail of one claim; (f) aspects defined in words, marked until checked
    def fill_row(items, gap=28, size=34):
        """Scale the crops to one height so the row is exactly W wide, then title each at the same size."""
        h = round((W - gap * (len(items) - 1)) / sum(im.width / im.height for im, _ in items))
        return hcat([titled(fit_h(im, h), lab, size=size) for im, lab in items], gap=gap)
    r1 = fill_row([(crop("interface_klein_chain", "E_sat"), "(a) shift × spread, margins, members"),
                   (crop("case62_turbo_horse", "B"), "(b) subjects × configurations"),
                   (crop("interface_klein_chain", "D"), "(c) the same seeds through the set")])
    r2 = fill_row([(crop("case64_statements", "A"), "(d) VLM statements, live verdicts"),
                   (crop("case64_trail", "A"), "(e) audit trail of one claim"),
                   (vcat([crop("case65_night", "E_u1"), crop("case65_night", "E_u2")], gap=10), "(f) aspects defined in words")])
    save(vcat([r1, r2], gap=40), "fig3_design.png")
    # Fig. 4, case 1 (auditing distillation): the klein chain under CLIP and SigLIP 2; SDXL -> Turbo reversals with images
    maps = hcat([titled(crop("case61_clip_medium", "A"), "CLIP", size=40), titled(crop("case61_siglip_medium", "A"), "SigLIP 2", size=40)], gap=36)
    top = titled(fit_w(maps, W), "(a) klein-base 4B: guidance 1 → 4 → distilled, medium",
                 sub="narrowing under both encoders; the shift only under SigLIP 2")
    horse = titled(crop("case62_turbo_horse", "C"), "a horse: Turbo more vivid", size=48)
    bird = titled(crop("case62_turbo_bird", "C"), "a bird on a branch: Turbo more muted", size=48)
    card = titled(crop("case62_turbo_horse", "E_sat"), "subjects on both sides", size=24)
    bot = titled(fit_w(hcat([fit_h(card, horse.height), horse, bird], gap=24), W), "(b) SDXL → SDXL-Turbo, saturation",
                 sub="pooled +0.17; subjects turn both ways")
    save(vcat([top, bot], gap=50), "fig4_case1.png")
    # Fig. 5, case 2 (auditing language claims): the rewriter's strongest effect on a failed axis; aspects defined in words
    e1 = vcat([crop("case63_rewrite_bg", "E_bg"), crop("case63_rewrite_bg", "E_medium")], gap=12)
    c1 = crop("case63_rewrite_bg", "C")
    r1 = titled(fit_w(hcat([fit_h(e1, c1.height), c1], gap=24), W), "(a) FLUX.2 dev → FLUX.2 rewrite",
                sub="background is not validated on rewritten images; a picnic")
    e2 = vcat([crop("case65_night", "E_u1"), crop("case65_night", "E_u2")], gap=12)
    c2 = crop("case65_night", "C")
    r2 = titled(fit_w(hcat([fit_h(e2, c2.height), c2], gap=24), W), "(b) two aspects defined in words on the klein chain",
                sub="daylight ↔ night; simple ↔ intricate (a VLM proposal people rejected)")
    save(vcat([r1, r2], gap=50), "fig5_case2.png")

    # Fig. 8 (one column), case 6.5: two aspects defined in words on the klein chain (from case65.mjs), both marked
    # not validated; their scatters and the image lane of one subject. With seven aspects the E cards are shorter.
    if os.path.exists(os.path.join(FIG, "case65_night.png")):
        PANEL.update({"E_u1": (1359, 727, 1666, 851), "E_u2": (1359, 863, 1666, 987)})
        cards = hcat([crop("case65_night", "E_u1"), crop("case65_night", "E_u2")], gap=12)
        lane = crop("case65_night", "C")
        save(vcat([fit_w(cards, lane.width), lane], gap=16), "fig8_case65.png", width=1500)

if __name__ == "__main__":
    main()
