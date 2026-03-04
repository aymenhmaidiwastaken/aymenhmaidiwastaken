import json
import urllib.request
import re
import os

USERNAME = "aymenhmaidiwastaken"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

# Repos to exclude (e.g. the profile repo itself)
EXCLUDE = {f"{USERNAME}", f"{USERNAME.lower()}"}

# Emoji mapping by dominant language or topic
LANG_EMOJI = {
    "Python": "\U0001f40d",
    "JavaScript": "\U0001f525",
    "TypeScript": "\U0001f3af",
    "PHP": "\U0001f4e6",
    "Vue": "\U0001f4ca",
    "C": "\u2699\ufe0f",
    "C++": "\u2699\ufe0f",
    "HTML": "\U0001f310",
    "CSS": "\U0001f3a8",
    "SCSS": "\U0001f3a8",
    "Shell": "\U0001f4bb",
    "Jupyter Notebook": "\U0001f4d3",
}
DEFAULT_EMOJI = "\U0001f4c2"


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
        emoji = LANG_EMOJI.get(lang, DEFAULT_EMOJI)
        is_last = i == count - 1
        connector = "\u2514\u2500\u2500" if is_last else "\u251c\u2500\u2500"
        pipe = " " if is_last else "\u2502"

        tree_lines.append(f"{connector} {emoji} {name}")
        tree_lines.append(f"{pipe}   \u251c\u2500\u2500 desc:  {desc}")
        tree_lines.append(f"{pipe}   \u2514\u2500\u2500 tech:  {lang}")
        if not is_last:
            tree_lines.append("\u2502")

    tree_lines.append("")
    tree_lines.append(f"{count} directories, \u221e lines of code")
    tree_lines.append("```")

    # Build badge links
    badge_lines = ['<div align="center">', ""]
    for repo in filtered:
        name = repo["name"]
        lang = repo["language"] or "Unknown"
        emoji = LANG_EMOJI.get(lang, DEFAULT_EMOJI)
        safe_name = name.replace("-", "--")
        badge_lines.append(
            f'<a href="https://github.com/{USERNAME}/{name}">\n'
            f'  <img src="https://img.shields.io/badge/{emoji}%20{safe_name}-0d1117?style=for-the-badge&logoColor=00ff41" alt="{name}"/>\n'
            f"</a>"
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

    # Update repo count in whoami section
    new_readme = re.sub(
        r"(<!-- REPO-COUNT -->)\d+(<!-- /REPO-COUNT -->)",
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
