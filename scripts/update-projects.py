import json
import urllib.request
import re
import os

USERNAME = "aymenhmaidiwastaken"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
BADGES_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "badges")


def make_badge_svg(text):
    """Create a for-the-badge style SVG with green border."""
    upper = text.upper()
    width = max(int(len(upper) * 9.5 + 24), 60)
    height = 28
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width+2}" height="{height+2}" viewBox="0 0 {width+2} {height+2}">
  <rect x="1" y="1" width="{width}" height="{height}" rx="3" fill="#0d1117" stroke="#00ff41" stroke-width="1"/>
  <text x="{(width+2)/2}" y="{height/2 + 5}" fill="#00ff41" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="10" font-weight="bold" text-anchor="middle" letter-spacing="1.1">{upper}</text>
</svg>'''

# Repos to exclude (e.g. the profile repo itself)
EXCLUDE = {f"{USERNAME}", f"{USERNAME.lower()}"}



def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated&type=owner"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def build_tree(repos):
    """Build the terminal tree + badge section."""
    filtered = [
        r for r in repos
        if not r["fork"]
        and r["name"] not in EXCLUDE
        and r["name"].lower() not in EXCLUDE
    ]
    # Sort by most recently pushed
    filtered.sort(key=lambda r: r["pushed_at"], reverse=True)

    count = len(filtered)
    tree_lines = [
        "```",
        "aymen@github:~$ tree ~/projects --info",
        "",
        "projects/",
        "\u2502",
    ]

    badges = []

    for i, repo in enumerate(filtered):
        name = repo["name"]
        desc = repo["description"] or "No description"
        if len(desc) > 65:
            desc = desc[:62] + "..."
        lang = repo["language"] or "Unknown"
        is_last = i == count - 1
        connector = "\u2514\u2500\u2500" if is_last else "\u251c\u2500\u2500"
        pipe = " " if is_last else "\u2502"

        tree_lines.append(f"{connector} {name}")
        tree_lines.append(f"{pipe}   \u251c\u2500\u2500 desc:  {desc}")
        tree_lines.append(f"{pipe}   \u2514\u2500\u2500 tech:  {lang}")
        if not is_last:
            tree_lines.append("\u2502")

    tree_lines.append("")
    tree_lines.append(f"{count} directories, \u221e lines of code")
    tree_lines.append("```")

    # Build badge links using local SVG files with green borders
    os.makedirs(BADGES_DIR, exist_ok=True)
    badge_lines = ['<div align="center">', ""]
    for repo in filtered:
        name = repo["name"]
        slug = name.lower().replace(" ", "-")
        svg_content = make_badge_svg(name)
        svg_path = os.path.join(BADGES_DIR, f"project-{slug}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        badge_lines.append(
            f'<a href="https://github.com/{USERNAME}/{name}"><img src="./assets/badges/project-{slug}.svg" alt="{name}"></a>'
        )
    badge_lines.append("")
    badge_lines.append("</div>")

    return count, "\n".join(tree_lines) + "\n\n" + "\n".join(badge_lines)


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
    count, content = build_tree(repos)
    update_readme(count, content)
    print(f"Updated README with {count} projects")


if __name__ == "__main__":
    main()
