from pathlib import Path
from nextjs_agent.tools.base import TOOL
from nextjs_agent.config import PACKAGE_DIR
from pydantic import BaseModel


def _parse_yaml_front_matter(text: str) -> dict[str, str]:
    result = {}
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return result
    end = 1
    while end < len(lines) and lines[end].strip() != "---":
        end += 1
    i = 1
    while i < end:
        line = lines[i]
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val in (">", "|"):
                parts = []
                i += 1
                while i < end and lines[i].startswith((" ", "\t")):
                    parts.append(lines[i].strip())
                    i += 1
                result[key] = " ".join(parts)
                continue
            result[key] = val
        i += 1
    return result


class ListSkillsToolArgs(BaseModel):
    pass


class ListSkillsTool(TOOL):
    name = "list_skills"
    description = "List all available skills with their descriptions. Skills are reusable guides for common tasks like setting up auth, design patterns, performance optimization, etc."

    args_schema = ListSkillsToolArgs

    async def execute(self, args: ListSkillsToolArgs):
        skills_dir = PACKAGE_DIR / ".agents" / "skills"
        if not skills_dir.exists():
            return {"success": True, "summary": "No skills found.", "skills": [], "modified_files": []}

        skills = []
        for entry in sorted(skills_dir.iterdir()):
            if not entry.is_dir():
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text("utf-8")
            meta = _parse_yaml_front_matter(content)
            desc = meta.get("description", "")
            skills.append({
                "name": entry.name,
                "description": desc,
            })

        if not skills:
            return {"success": True, "summary": "No skills found.", "skills": [], "modified_files": []}

        names = ", ".join(s["name"] for s in skills)
        return {"success": True, "summary": f"Available skills: {names}", "skills": skills, "modified_files": []}
