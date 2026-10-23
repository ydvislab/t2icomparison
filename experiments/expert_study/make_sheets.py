"""Moderator sheets for the expert sessions (docs/EXPERT_SESSION.md, fixed 2026-10-19, revised 2026-10-23).
One sheet per expert (E1-E5) and one for the pilot (P, run in E1's order). The sheets hold the setup and the wording read
to the expert, never the expected answers. Sessions are held in Chinese, so the read-aloud text is given in Chinese
with the English original.
Usage: python make_sheets.py   (writes docs/expert_sheets/{P,E1..E5}.md and docs/expert_sheets/sessions_template.csv)"""
import csv, os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "docs", "expert_sheets")

# counterbalancing, EXPERT_SESSION.md section 2: first condition and the tool cases for T1-T4
ORDER = {"P": ("tool", "aaaa"), "E1": ("tool", "aaaa"), "E2": ("baseline", "bbbb"), "E3": ("tool", "baba"),
         "E4": ("baseline", "abab"), "E5": ("tool", "aabb")}
OTHER = {"a": "b", "b": "a"}

CASES = {
    ("T1", "a"): dict(A="klein-base 4B · CFG 1", B="klein-base 4B · CFG 4", aspect="saturation", subject="(any)",
                      zh="klein-base 4B 的 guidance 从 1 提高到 4 时，【饱和度】是整体移动了、变得更集中了，还是两者都有？请指出能说服你的图片。",
                      en="When klein-base 4B guidance goes from 1 to 4, does saturation move, tighten, or both? Show the images that convince you."),
    ("T1", "b"): dict(A="klein-base 4B · CFG 1", B="klein-base 4B · CFG 4", aspect="medium", subject="(any)",
                      zh="klein-base 4B 的 guidance 从 1 提高到 4 时，【媒介（照片 ↔ 绘画/插画）】是整体移动了、变得更集中了，还是两者都有？请指出能说服你的图片。",
                      en="When klein-base 4B guidance goes from 1 to 4, does medium move, tighten, or both? Show the images that convince you."),
    ("T2", "a"): dict(A="SDXL", B="SDXL-Turbo", aspect="saturation", subject="(any)",
                      zh="整体来看，从 SDXL 到 SDXL-Turbo，【饱和度】有没有变化？这对每个主题都成立吗？请说出往两个方向变化的主题。",
                      en="Overall, does SDXL → SDXL-Turbo change saturation? Is that true for every subject? Name subjects that go each way."),
    ("T2", "b"): dict(A="SD 1.5", B="klein-base 4B · CFG 4", aspect="saturation", subject="(any)",
                      zh="整体来看，从 SD 1.5 到 klein-base 4B · CFG 4，【饱和度】有没有变化？这对每个主题都成立吗？请说出往两个方向变化的主题。",
                      en="Overall, does SD 1.5 → klein-base 4B CFG 4 change saturation? Is that true for every subject? Name subjects that go each way."),
    ("T3", "a"): dict(A="Qwen-Image · CFG 1", B="Qwen-Image · CFG 4", aspect="tone", subject="(any)",
                      zh="这里有一条结论：“把 Qwen-Image 的 guidance 从 1 提高到 4，会让它的色调更现代。”这条结论可信吗？为什么？",
                      en="Here is a reading: \"Raising Qwen-Image's guidance from 1 to 4 makes its tone more modern.\" Can it be trusted? Why or why not?"),
    ("T3", "b"): dict(A="SDXL", B="SDXL-Turbo", aspect="background", subject="(any)",
                      zh="这里有一条结论：“把 SDXL 蒸馏成 SDXL-Turbo，会让一些主题的背景更繁杂、另一些主题的背景更简洁。”这条结论可信吗？为什么？",
                      en="Here is a reading: \"Distilling SDXL into SDXL-Turbo makes backgrounds busier for some subjects and plainer for others.\" Can it be trusted? Why or why not?"),
    ("T4", "a"): dict(A="SDXL", B="SDXL-Turbo", aspect="(leave as is)", subject="a restaurant",
                      zh="一个 VLM 看了 A 组 8 张和 B 组 8 张“a restaurant”的图片后说：“B 组的图有更多细致的建筑元素，比如拱形窗和华丽的线脚，这些在 A 组中不太突出。”这句话对吗？请给出证据。",
                      en="A VLM looked at 8 images of A and 8 of B (\"a restaurant\") and said: \"Set B images include more detailed architectural elements such as arched windows and ornate moldings, which are less prominent in set A.\" Is it correct? Show the evidence."),
    ("T4", "b"): dict(A="SDXL", B="SDXL-Turbo", aspect="(leave as is)", subject="a car",
                      zh="一个 VLM 看了 A 组 8 张和 B 组 8 张“a car”的图片后说：“B 组的图色调更偏棕褐（sepia），配色更灰暗。”这句话对吗？请给出证据。",
                      en="A VLM looked at 8 images of A and 8 of B (\"a car\") and said: \"Set B images have a more sepia tone and muted color palette.\" Is it correct? Show the evidence."),
}

PAGE = {"tool": "audit/index.html", "baseline": "audit/baseline.html"}
SETUP = {"tool": "In the header: left selector = A, right selector = B; aspect buttons on the right. Subject: selector in panel D.",
         "baseline": "Selectors at the top: A, B, subject, aspect."}
TRAIN_SHOW = {
    "tool": ["header: A, B, the declared settings that differ (chip next to + compare), the aspect buttons (struck through = not validated by people for this pair)",
             "panel A, map (◎): where each configuration settles (x) and how tightly (y); click = choose B, shift-click = add to the comparison set; zoom with the wheel",
             "panel E: the contrast scatter of every aspect, one dot per subject; the shaded band is the margin; the diamond is the pooled contrast",
             "panel B: subjects × configurations; panel C: the images of one subject placed on the aspect axis (A above, B below)",
             "panel D: the same seed in A and B (trajectories)",
             "panel A, ❝: the VLM statements about the pair, coloured by the audit's verdict; clicking one selects its aspect and subject",
             "panel A, ⛓: the audit trail of one claim"],
    "baseline": ["selectors A, B, subject, aspect; the settings table and the human-validation table",
                 "the pooled table: shift and spread with 90% intervals, and whether the aspect is validated",
                 "the per-subject box plots of the chosen aspect",
                 "the image grid of the chosen subject, sortable by seed or by aspect score",
                 "the section 'Rewritten prompts and VLM statements for this pair' at the bottom"]}

HEAD = ["expert", "condition", "order", "task", "case", "answer", "correct", "evidence", "confidence", "seconds", "notes"]


def trial_block(cond, order, task, case):
    c = CASES[(task, case)]
    return f"""#### {task} (case {case})
- **Set up before reading** ({SETUP[cond]}): A = `{c['A']}`, B = `{c['B']}`, aspect = `{c['aspect']}`, subject = `{c['subject']}`. Start the timer when you finish reading.
- **Read aloud:** {c['zh']}
- *English original:* {c['en']}
- **Record:**

| answer | evidence cited (views, images, subjects) | confidence 1–5 | seconds | notes |
|---|---|---|---|---|
| | | | | |
"""


def sheet(e):
    first, tool_cases = ORDER[e]
    second = "baseline" if first == "tool" else "tool"
    cases = {"tool": dict(zip(["T1", "T2", "T3", "T4"], tool_cases)),
             "baseline": {t: OTHER[k] for t, k in zip(["T1", "T2", "T3", "T4"], tool_cases)}}
    title = "Pilot session (order of E1; answers are not analysed)" if e == "P" else f"Session sheet {e}"
    s = [f"# {title}", "",
         f"First condition: **{first}**, then **{second}**. Tasks within a condition run T1 → T4. Up to about 75 minutes.", "",
         "Expected answers are not on this sheet (they are in `docs/EXPERT_SESSION.md` and are not shown to the expert).", "",
         "## Before the session",
         "- The expert has unzipped `expert_offline_package.zip` and has Chrome or Edge; screen sharing and recording work.",
         "- Consent form signed under the approved ethics protocol.",
         "- The expert should not open either page before you ask.", "",
         "## 0. Consent and background (3 min)",
         "- **Read aloud:** 这次测试大约 75 分钟。我们会请你用两个页面完成几道判断题，没有标准的操作方式，请边做边把想法说出来。我们评价的是工具，不是你。全程录屏，记录中不出现你的名字。",
         "- **Record:** role; years in imaging or graphics research; years with generative image models; experience with CLIP-based metrics (none / some / regular); prior involvement with this project (none / saw a demo / contributed).", ""]
    order = 0
    for part, cond in ((1, first), (2, second)):
        s += [f"## Part {part}: {cond} (open `{PAGE[cond]}`)", "",
              f"### Training (up to 8 min, not scored)",
              f"- **Set up:** A = `klein 4B`, B = `klein 4B · FLUX.2 rewrite`, aspect = `saturation`, subject = `a kitchen`.",
              "- **Show, in this order:**"]
        s += [f"  {i + 1}. {x}" for i, x in enumerate(TRAIN_SHOW[cond])]
        s += ["- Let the expert try one free question on this case; answer questions about what a view shows, not about what the case means.", "",
              "### Tasks (about 6 min each; at 8 min ask for a final answer)",
              "- Remind the expert once: 请边做边说出你在看什么、为什么这样判断。",
              "- If the expert asks what a view means, repeat only what was said in training. Give no hint about the answer.", ""]
        for t in ["T1", "T2", "T3", "T4"]:
            order += 1
            s.append(trial_block(cond, order, t, cases[cond][t]))
    s += ["## Interview (8 min)",
          "1. 哪些结论如果只看表格和图片网格，你可能会判断错？为什么？ — *Which reading would you have got wrong with the table and grid alone? Why?*",
          "2. 你什么时候去看了原图？看图改变了你的答案吗？ — *When did you go to the images, and did that change your answer?*",
          "3. 你会相信 VLM 对两个模型差别的描述吗？需要核对什么？ — *Would you trust a VLM's description of how two models differ? What would you need to check?*",
          "4. 如果要审计你自己的模型或设置改动，你还需要什么？ — *What would you need to audit your own model or setting changes?*",
          "5. 工具里哪里不清楚或者容易误导？ — *What in the tool is unclear or misleading?*", "",
          "## After the session",
          f"- Copy the eight records into `results/expert_study/sessions.csv` (rows for {e} are in `sessions_template.csv`); leave `correct` empty for the judges.",
          "- Keep the screen recording outside the repository. Note interview answers in your own words, without names.", ""]
    return "\n".join(s), cases, first, second


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for e in ORDER:
        text, cases, first, second = sheet(e)
        open(os.path.join(OUT, f"{e}.md"), "w", encoding="utf-8").write(text)
        n = 0
        for cond in (first, second):
            for t in ["T1", "T2", "T3", "T4"]:
                n += 1
                rows.append(dict(expert=e, condition=cond, order=n, task=t, case=cases[cond][t]))
    with open(os.path.join(OUT, "sessions_template.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, HEAD); w.writeheader(); w.writerows(rows)
    print("sheets:", ", ".join(ORDER), "->", OUT)


if __name__ == "__main__":
    main()
