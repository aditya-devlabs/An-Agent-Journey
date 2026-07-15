import os
import re
import threading
from fnmatch import fnmatch
from concurrent.futures import ThreadPoolExecutor, as_completed
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field


class SearchCodeToolArgs(BaseModel):
    pattern: str = Field(description="Text or regex pattern to search for")
    path: str = Field(default=".", description="Directory or file to search in. Defaults to project root.")
    include: list[str] | None = Field(default=None, description="File patterns to include, e.g. ['*.ts', '*.tsx']")
    regex: bool = Field(default=False, description="If true, treat pattern as regex. Otherwise literal substring search.")
    ignore_case: bool = Field(default=False, description="Case-insensitive search.")
    context_lines: int = Field(default=0, description="Number of lines of context before and after each match.")
    max_results: int = Field(default=200, description="Maximum total matches to return.")
    max_matches_per_file: int = Field(default=50, description="Maximum matches per file.")


class SearchCodeTool(TOOL):
    name = "search_code"
    description = "Search file contents. Returns matching lines with file paths and line numbers. Use for finding code, functions, variables, or patterns across the project."

    args_schema = SearchCodeToolArgs

    SKIP_DIRS = {
        ".git", "node_modules", "__pycache__", ".next", ".opencode",
        "dist", "build", ".venv", "venv", "coverage", ".cache", ".turbo",
    }

    SKIP_FILES = {"pnpm-lock.yaml", "package-lock.json", "yarn.lock", ".DS_Store"}

    def _collect_files(self, root: str, include: list[str] | None) -> list[str]:
        files = []
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [
                d for d in dirnames
                if d not in self.SKIP_DIRS and (not d.startswith(".") or d == ".env")
            ]
            for fname in filenames:
                if fname in self.SKIP_FILES:
                    continue
                if include and not any(fnmatch(fname, pat) for pat in include):
                    continue
                files.append(os.path.join(dirpath, fname))
        return files

    def _search_file(self, rel_path: str, abs_path: str, compiled_re: re.Pattern | None, literal: str | None, ignore_case: bool, context_lines: int, max_matches_per_file: int, cancel: threading.Event) -> list[dict]:
        if cancel.is_set():
            return []
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return []

        matches = []
        for i, line in enumerate(lines):
            if cancel.is_set():
                break
            if len(matches) >= max_matches_per_file:
                break
            matched = False
            if literal is not None:
                target = line.lower() if ignore_case else line
                matched = literal in target
            elif compiled_re is not None:
                matched = bool(compiled_re.search(line))

            if matched:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                matches.append({
                    "file": rel_path,
                    "before": [l.rstrip("\n") for l in lines[start:i]],
                    "line": i + 1,
                    "content": line.rstrip("\n"),
                    "after": [l.rstrip("\n") for l in lines[i + 1:end]],
                })
        return matches

    async def execute(self, args: SearchCodeToolArgs):
        search_path = str(self.resolve_project_path(args.path))

        compiled_re = None
        literal = None
        if args.regex:
            try:
                flags = re.IGNORECASE if args.ignore_case else 0
                compiled_re = re.compile(args.pattern, flags)
            except re.error as e:
                raise ValueError(f"Invalid regex: {e}")
        else:
            literal = args.pattern.lower() if args.ignore_case else args.pattern

        files = self._collect_files(search_path, args.include)

        if not files:
            include_str = ", ".join(args.include) if args.include else "*"
            return {
                "success": True,
                "summary": f'Pattern "{args.pattern}" — no files found matching {include_str}',
                "matches": [],
                "total_matches": 0,
                "modified_files": [],
            }

        cancel = threading.Event()
        all_matches = []

        with ThreadPoolExecutor(max_workers=min(8, len(files))) as executor:
            futures = {
                executor.submit(
                    self._search_file,
                    os.path.relpath(f, self.project_root),
                    f, compiled_re, literal, args.ignore_case, args.context_lines,
                    args.max_matches_per_file, cancel,
                ): f
                for f in files
            }
            for future in as_completed(futures):
                result = future.result()
                all_matches.extend(result)
                if len(all_matches) >= args.max_results:
                    cancel.set()
                    break

        total_found = len(all_matches)
        all_matches = all_matches[:args.max_results]
        file_count = len({m["file"] for m in all_matches}) # good, set comprehension would tell us unique files only, list comprehension would have allowed the duplicate file name entries. Nice

        if total_found > len(all_matches):
            summary = f'Pattern "{args.pattern}" — Showing first {len(all_matches)} of {total_found} matches in {file_count} files'
        else:
            summary = f'Pattern "{args.pattern}" — {total_found} matches in {file_count} files'

        return {
            "success": True,
            "summary": summary,
            "matches": all_matches,
            "total_matches": total_found,
            "modified_files": [],
        }
