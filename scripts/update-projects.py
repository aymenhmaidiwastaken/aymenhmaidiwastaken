import json
import urllib.request
import re
import os
import html

USERNAME = "aymenhmaidiwastaken"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
SVG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "projects-tree.svg")

# Repos to exclude (e.g. the profile repo itself)
EXCLUDE = {f"{USERNAME}", f"{USERNAME.lower()}"}

# Known frameworks/tools to detect from repo topics
# Manual framework overrides for repos without topics
REPO_TECH_OVERRIDE = {
    "Shopify-Seo": "Chrome Extension",
    "Css-Sniffer": "Chrome Extension",
    "linkedin-auto-connect": "Chrome Extension",
    "unsender-for-facebook": "Chrome Extension",
    "unsender-for-instagram": "Chrome Extension",
    "daily-country-search-trends": "Chrome Extension",
    "OpenBoil": "Next.js",
    "BoomAi": "Next.js",
    "Boomash": "Laravel",
    "seektalent": "Next.js",
    "Melkeya": "Next.js",
}

# Known frameworks/tools to detect from repo topics
FRAMEWORK_KEYWORDS = {
    "nextjs": "Next.js", "next": "Next.js",
    "react": "React", "reactjs": "React",
    "vue": "Vue.js", "vuejs": "Vue.js",
    "angular": "Angular", "angularjs": "Angular",
    "laravel": "Laravel",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "express": "Express", "expressjs": "Express",
    "nestjs": "NestJS",
    "nuxt": "Nuxt.js", "nuxtjs": "Nuxt.js",
    "svelte": "Svelte", "sveltekit": "SvelteKit",
    "tailwindcss": "Tailwind CSS", "tailwind": "Tailwind CSS",
    "nodejs": "Node.js", "node": "Node.js",
    "electron": "Electron",
    "chrome-extension": "Chrome Extension",
    "docker": "Docker",
}


def detect_tech(repo):
    """Detect framework/tech from overrides, topics, or language."""
    name = repo["name"]
    if name in REPO_TECH_OVERRIDE:
        return REPO_TECH_OVERRIDE[name]
    topics = repo.get("topics", [])
    for topic in topics:
        t = topic.lower()
        if t in FRAMEWORK_KEYWORDS:
            return FRAMEWORK_KEYWORDS[t]
    return repo.get("language") or "Unknown"


def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated&type=owner"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def generate_tree_svg(projects):
    """Generate an animated SVG tree with cascading reveal effect."""
    n = len(projects)
    font_size = 13
    line_h = 26
    pad_x = 24
    pad_y = 40
    branch_x = pad_x + 12
    branch_h_len = 22
    text_x = branch_x + branch_h_len + 10

    max_name_len = max(len(p[0]) for p in projects)
    width = max(int(text_x + max_name_len * 8.2 + pad_x), 500)

    header_lines = 3
    footer_lines = 3  # blank + count + cursor prompt
    total_lines = header_lines + n + footer_lines
    height = int(pad_y + total_lines * line_h + 20)

    cmd_y = pad_y + line_h
    dir_y = cmd_y + line_h * 1.8

    def proj_y(i):
        return dir_y + (i + 1) * line_h

    footer_y = proj_y(n - 1) + line_h * 1.5

    vline_y1 = dir_y + 8
    vline_y2 = proj_y(n - 1)
    vline_len = vline_y2 - vline_y1

    tree_start = 1.1
    stagger = 0.22
    branch_dur = 0.25
    name_dur = 0.3
    vline_dur = n * stagger

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    lines.append('<defs>')
    lines.append('  <filter id="glow">')
    lines.append('    <feGaussianBlur stdDeviation="2" result="blur"/>')
    lines.append('    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>')
    lines.append('  </filter>')
    lines.append('</defs>')
    lines.append('<style>')
    lines.append('  @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }')
    lines.append('  @keyframes slideIn { from { opacity: 0; transform: translateX(-8px) } to { opacity: 1; transform: translateX(0) } }')
    lines.append(f'  @keyframes drawV {{ from {{ stroke-dashoffset: {vline_len:.0f} }} to {{ stroke-dashoffset: 0 }} }}')
    lines.append(f'  @keyframes drawH {{ from {{ stroke-dashoffset: {branch_h_len} }} to {{ stroke-dashoffset: 0 }} }}')
    lines.append('  .cmd { opacity: 0; animation: fadeIn 0.5s ease 0s forwards }')
    lines.append(f'  .dir {{ opacity: 0; animation: fadeIn 0.4s ease 0.6s forwards }}')
    lines.append(f'  .vline {{ stroke-dasharray: {vline_len:.0f}; stroke-dashoffset: {vline_len:.0f}; animation: drawV {vline_dur:.2f}s ease {tree_start}s forwards }}')

    for i in range(n):
        d = tree_start + i * stagger
        nd = d + branch_dur
        lines.append(f'  .hline-{i} {{ stroke-dasharray: {branch_h_len}; stroke-dashoffset: {branch_h_len}; animation: drawH {branch_dur}s ease {d:.2f}s forwards }}')
        lines.append(f'  .name-{i} {{ opacity: 0; animation: slideIn {name_dur}s ease {nd:.2f}s forwards }}')

    fd = tree_start + n * stagger + 0.4
    cursor_delay = fd + 0.6
    lines.append(f'  .footer {{ opacity: 0; animation: fadeIn 0.6s ease {fd:.2f}s forwards }}')
    lines.append(f'  .cursor {{ opacity: 0; animation: fadeIn 0.1s ease {cursor_delay:.2f}s forwards }}')
    lines.append(f'  .cursor rect {{ animation: blink 1s step-end infinite {cursor_delay:.2f}s }}')
    lines.append('  @keyframes blink { 0%, 100% { opacity: 1 } 50% { opacity: 0 } }')
    lines.append("  text { font-family: 'JetBrains Mono','Fira Code','Courier New',monospace }")
    lines.append('</style>')

    lines.append(f'<rect width="{width}" height="{height}" rx="10" fill="#0d1117"/>')
    lines.append(f'<rect width="{width}" height="{height}" rx="10" fill="none" stroke="#00ff41" stroke-width="0.5" opacity="0.3"/>')

    lines.append('<circle cx="18" cy="16" r="5" fill="#ff5f56"/>')
    lines.append('<circle cx="34" cy="16" r="5" fill="#ffbd2e"/>')
    lines.append('<circle cx="50" cy="16" r="5" fill="#27c93f"/>')

    lines.append(f'<text x="{pad_x}" y="{cmd_y}" fill="#4a9f4a" font-size="12" class="cmd">aymen@github</text>')
    cmd2_x = pad_x + 12 * 7.2
    lines.append(f'<text x="{cmd2_x}" y="{cmd_y}" fill="#555" font-size="12" class="cmd">:</text>')
    cmd3_x = cmd2_x + 7.2
    lines.append(f'<text x="{cmd3_x}" y="{cmd_y}" fill="#3a7abf" font-size="12" class="cmd">~</text>')
    cmd4_x = cmd3_x + 7.2
    lines.append(f'<text x="{cmd4_x}" y="{cmd_y}" fill="#ccc" font-size="12" class="cmd">$ tree ~/projects</text>')

    lines.append(f'<text x="{pad_x}" y="{dir_y}" fill="#00ff41" font-size="{font_size}" font-weight="bold" class="dir" filter="url(#glow)">projects/</text>')

    lines.append(f'<line x1="{branch_x}" y1="{vline_y1}" x2="{branch_x}" y2="{vline_y2}" stroke="#00ff41" stroke-width="1.5" opacity="0.6" class="vline"/>')

    for i, (name, desc, _full_desc, tech) in enumerate(projects):
        is_last = i == n - 1
        by = proj_y(i)

        hx1 = branch_x
        hx2 = branch_x + branch_h_len
        lines.append(f'<line x1="{hx1}" y1="{by}" x2="{hx2}" y2="{by}" stroke="#00ff41" stroke-width="1.5" opacity="0.6" class="hline-{i}"/>')

        if is_last:
            lines.append(f'<line x1="{branch_x}" y1="{by - 4}" x2="{branch_x}" y2="{by}" stroke="#00ff41" stroke-width="1.5" opacity="0.6" class="hline-{i}"/>')

        ax = hx2
        lines.append(f'<circle cx="{ax}" cy="{by}" r="2" fill="#00ff41" opacity="0" class="name-{i}"/>')

        esc_name = html.escape(name)
        lines.append(f'<text x="{text_x}" y="{by + 4}" fill="#00ff41" font-size="{font_size}" class="name-{i}" filter="url(#glow)">{esc_name}</text>')

    lines.append(f'<text x="{pad_x}" y="{footer_y}" fill="#555" font-size="11" class="footer">{n} repositories, \u221e lines of code</text>')

    # Blinking cursor on a new prompt line
    cursor_y = footer_y + line_h
    lines.append(f'<text x="{pad_x}" y="{cursor_y}" fill="#4a9f4a" font-size="12" class="cursor">aymen@github</text>')
    c2x = pad_x + 12 * 7.2
    lines.append(f'<text x="{c2x}" y="{cursor_y}" fill="#555" font-size="12" class="cursor">:</text>')
    c3x = c2x + 7.2
    lines.append(f'<text x="{c3x}" y="{cursor_y}" fill="#3a7abf" font-size="12" class="cursor">~</text>')
    c4x = c3x + 7.2
    lines.append(f'<text x="{c4x}" y="{cursor_y}" fill="#ccc" font-size="12" class="cursor">$</text>')
    c5x = c4x + 14
    lines.append(f'<g class="cursor"><rect x="{c5x}" y="{cursor_y - 11}" width="8" height="14" fill="#00ff41"/></g>')

    lines.append('</svg>')
    return '\n'.join(lines)


def build_content(repos):
    """Build the SVG tree + details dropdowns section."""
    filtered = [
        r for r in repos
        if not r["fork"]
        and r["name"] not in EXCLUDE
        and r["name"].lower() not in EXCLUDE
    ]
    filtered.sort(key=lambda r: r["pushed_at"], reverse=True)

    count = len(filtered)

    # Prepare project data for SVG
    projects = []
    for repo in filtered:
        name = repo["name"]
        full_desc = repo["description"] or "No description"
        short_desc = full_desc[:77] + "..." if len(full_desc) > 80 else full_desc
        tech = detect_tech(repo)
        projects.append((name, short_desc, full_desc, tech))

    # Generate and save the SVG
    svg_content = generate_tree_svg(projects)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Build the README section
    section_lines = [
        '<div align="center">',
        '  <a href="https://github.com/aymenhmaidiwastaken">',
        '    <img src="./assets/projects-tree.svg" width="500" alt="Projects Tree"/>',
        '  </a>',
        '</div>',
        '',
        '<br/>',
        '',
    ]

    for name, _short_desc, full_desc, tech in projects:
        section_lines.append('<details>')
        section_lines.append(f'<summary><code>{name}</code> \u2014 {tech}</summary>')
        section_lines.append('<br/>')
        section_lines.append('')
        section_lines.append(f'> {full_desc}')
        section_lines.append('')
        section_lines.append(f'[![View Repo](https://img.shields.io/badge/View_Repo-0d1117?style=for-the-badge&logoColor=00ff41)](https://github.com/{USERNAME}/{name})')
        section_lines.append('</details>')
        section_lines.append('')

    return count, "\n".join(section_lines).rstrip()


def update_readme(count, content):
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = r"(<!-- PROJECTS-START -->).*?(<!-- PROJECTS-END -->)"
    replacement = f"\\1\n{content}\n\\2"
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    # Update repo count in whoami section (inside code block)
    new_readme = re.sub(
        r"(Packages\s+)\d+(\s+\(github\))",
        f"\\g<1>{count}\\g<2>",
        new_readme,
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme)


def main():
    repos = fetch_repos()
    count, content = build_content(repos)
    update_readme(count, content)
    print(f"Updated README with {count} projects")


if __name__ == "__main__":
    main()
