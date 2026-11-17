#!/usr/bin/env python3
"""Build README.md, assets/skills.svg and site/index.html from profile.yaml.

Usage:
  python scripts/build.py          # validate and write the generated files
  python scripts/build.py --check  # validate and fail if generated files are out of date (CI on PRs)
"""
import html
import json
import pathlib
import sys

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEVEL_NAMES = {5: "Expert", 4: "Advanced", 3: "Proficient", 2: "Learning", 1: "Aware"}
STATUS_ICON = {"earned": "✅", "in progress": "🟡", "planned": "🗓️"}
GENERATED_NOTE = "<!-- Generated from profile.yaml by scripts/build.py. Edit profile.yaml, not this file. -->"


def load():
    data = yaml.safe_load((ROOT / "profile.yaml").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schema" / "profile.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(data, schema)
    return data


def esc(text):
    return html.escape(str(text), quote=True)


def skills_svg(skills):
    row, label_w, bar_w, pad = 40, 230, 440, 24
    height = pad * 2 + row * len(skills)
    width = label_w + bar_w + 140
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Skill levels by category">',
        f'<rect width="{width}" height="{height}" rx="14" fill="#1c1c24"/>',
    ]
    for i, s in enumerate(sorted(skills, key=lambda s: -s["level"])):
        y = pad + i * row
        filled = bar_w * s["level"] / 5
        color = "#3cc8ea" if s["level"] >= 4 else "#7a5cc4"
        parts += [
            f'<text x="{pad}" y="{y + 24}" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
            f'font-size="15" fill="#f4f4f7">{esc(s["category"])}</text>',
            f'<rect x="{label_w}" y="{y + 10}" width="{bar_w}" height="18" rx="9" fill="#2e2e3a"/>',
            f'<rect x="{label_w}" y="{y + 10}" width="{filled:.0f}" height="18" rx="9" fill="{color}"/>',
            f'<text x="{label_w + bar_w + 14}" y="{y + 24}" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
            f'font-size="14" fill="#b9bccb">{LEVEL_NAMES[s["level"]]}</text>',
        ]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def readme(d):
    p = d["person"]
    links = " · ".join(
        f"[{name}]({p[key]})" for key, name in (("linkedin", "LinkedIn"), ("github", "GitHub")) if p.get(key)
    )
    out = [GENERATED_NOTE, "", f"# {p['name']}", "", f"**{p['headline']}**", ""]
    meta = " · ".join(x for x in (p.get("location"), ", ".join(p.get("languages", [])), links) if x)
    out += [meta, "", d["summary"], ""]

    if d.get("highlights"):
        out += ["| " + " | ".join(f"**{h['value']}**" for h in d["highlights"]) + " |",
                "|" + "---|" * len(d["highlights"]),
                "| " + " | ".join(h["label"] for h in d["highlights"]) + " |", ""]

    out += ["## Skills", "", "![Skill levels by category](assets/skills.svg)", "",
            "| Area | Level | Tools and practices | Evidence |", "| --- | --- | --- | --- |"]
    for s in sorted(d["skills"], key=lambda s: -s["level"]):
        out.append(f"| **{s['category']}** | {LEVEL_NAMES[s['level']]} | {', '.join(s['items'])} | {s.get('evidence', '')} |")

    out += ["", "## Experience", "", "| Period | Company | Role | |", "| --- | --- | --- | --- |"]
    for e in d["experience"]:
        out.append(f"| {e['period']} | {e['company']} | {e['role']} | {e.get('summary', '')} |")

    if d.get("certifications"):
        out += ["", "## Certifications", ""]
        for c in d["certifications"]:
            year = f" ({c['year']})" if c.get("year") else ""
            out.append(f"- {STATUS_ICON[c['status']]} {c['name']}{year} · {c['status']}")

    out += ["", "---", "", "_This profile is maintained as code: edit `profile.yaml`, open a PR, "
            "and CI validates it and regenerates this page._", ""]
    return "\n".join(out)


def site(d):
    p = d["person"]
    hl = "".join(
        f'<div class="hl"><b>{esc(h["value"])}</b><span>{esc(h["label"])}</span></div>' for h in d.get("highlights", [])
    )
    sk = "".join(
        f'<div class="card"><div class="row"><h3>{esc(s["category"])}</h3><em>{LEVEL_NAMES[s["level"]]}</em></div>'
        f'<div class="bar"><i style="width:{s["level"] * 20}%"></i></div>'
        f'<p class="chips">{"".join(f"<span>{esc(i)}</span>" for i in s["items"])}</p>'
        f'<p class="ev">{esc(s.get("evidence", ""))}</p></div>'
        for s in sorted(d["skills"], key=lambda s: -s["level"])
    )
    ex = "".join(
        f'<li><time>{esc(e["period"])}</time><div><b>{esc(e["role"])}</b> · {esc(e["company"])}'
        f'<p>{esc(e.get("summary", ""))}</p></div></li>'
        for e in d["experience"]
    )
    links = "".join(
        f'<a href="{esc(p[k])}">{n}</a>' for k, n in (("linkedin", "LinkedIn"), ("github", "GitHub")) if p.get(k)
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p['name'])} · DevOps profile</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
:root{{--bg:#1c1c24;--card:#262632;--line:#3a3a4a;--text:#f4f4f7;--muted:#b9bccb;--cyan:#3cc8ea;--purple:#7a5cc4}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 'IBM Plex Sans',Arial,sans-serif}}
main{{max-width:1080px;margin:0 auto;padding:56px 16px}}h1,h2,h3{{font-family:'Space Grotesk',Arial,sans-serif;margin:0}}
h1{{font-size:clamp(36px,6vw,56px)}}.head p{{color:var(--muted);margin:8px 0}}.tag{{color:var(--cyan);font-weight:600}}
.links a{{color:var(--cyan);margin-right:16px}}h2{{font-size:28px;margin:48px 0 16px}}
.hls{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:32px}}
.hl{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}}.hl b{{display:block;font:700 32px 'Space Grotesk',Arial;color:var(--cyan)}}.hl span{{color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}}.row{{display:flex;justify-content:space-between;align-items:baseline;gap:8px}}
.row em{{color:var(--muted);font-style:normal;font-size:14px}}.bar{{height:8px;background:#2e2e3a;border-radius:4px;margin:12px 0}}.bar i{{display:block;height:100%;background:linear-gradient(90deg,var(--purple),var(--cyan));border-radius:4px}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:0}}.chips span{{background:#1c1c24;border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:13px}}
.ev{{color:var(--muted);font-size:14px;margin:12px 0 0}}
ol{{list-style:none;padding:0;margin:0;border-left:2px solid var(--line)}}li{{display:grid;grid-template-columns:140px 1fr;gap:16px;padding:12px 0 12px 20px}}
li time{{color:var(--cyan);font-weight:600}}li p{{color:var(--muted);margin:4px 0 0}}
@media(max-width:600px){{li{{grid-template-columns:1fr;gap:4px}}}}
footer{{color:var(--muted);font-size:14px;margin-top:56px}}
</style></head><body><main>
<section class="head"><h1>{esc(p['name'])}</h1><p class="tag">{esc(p['headline'])}</p>
<p>{esc(p.get('location', ''))}</p><p class="links">{links}</p><p>{esc(d['summary'])}</p></section>
<div class="hls">{hl}</div>
<h2>Skills</h2><div class="grid">{sk}</div>
<h2>Experience</h2><ol>{ex}</ol>
<footer>Maintained as code: generated from profile.yaml.</footer>
</main></body></html>
"""


def main():
    check = "--check" in sys.argv
    data = load()
    outputs = {
        ROOT / "README.md": readme(data),
        ROOT / "assets" / "skills.svg": skills_svg(data["skills"]),
        ROOT / "site" / "index.html": site(data),
    }
    stale = []
    for path, content in outputs.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            stale.append(path.relative_to(ROOT))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if check and stale:
        sys.exit(f"Out of date: {', '.join(map(str, stale))}. Run: python scripts/build.py")
    print("profile.yaml valid;", "updated: " + ", ".join(map(str, stale)) if stale else "nothing to update")


if __name__ == "__main__":
    main()
