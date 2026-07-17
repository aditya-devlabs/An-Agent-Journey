from nextjs_agent.tools.base import TOOL
from nextjs_agent.config import PACKAGE_DIR
from pydantic import Field, BaseModel


class ReadSkillToolArgs(BaseModel):
    skill_name: str = Field(description="Name of the skill to read. Use list_skills to see available skill names.")


class ReadSkillTool(TOOL):
    name = "read_skill"
    description = "Read the full content of a skill. Use list_skills first to find available skills."

    args_schema = ReadSkillToolArgs

    async def execute(self, args: ReadSkillToolArgs):
        skills_dir = PACKAGE_DIR / ".agents" / "skills"
        skill_path = skills_dir / args.skill_name / "SKILL.md"

        if not skill_path.exists():
            return {"success": False, "summary": f"Skill '{args.skill_name}' not found.", "content": "", "modified_files": []}

        content = skill_path.read_text("utf-8")
        return {"success": True, "summary": f"Read skill: {args.skill_name}", "content": content, "modified_files": []}
