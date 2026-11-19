#!/usr/bin/env python3
"""Check git commit, add, and push commands before they run."""

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

MESSAGE_RULE = (
    "Subject is an imperative English sentence with no trailing period and no type prefix. "
    "One blank line, then one sentence on why the step exists. "
    "Do not add Co-authored-by, Made-with, or any trailer that names Cursor."
)

CONVENTIONAL = re.compile(
    r"^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)"
    r"(\([^)]*\))?(!)?:\s",
    re.IGNORECASE,
)

CYRILLIC = re.compile(r"[\u0400-\u04FF]")

TRAILER = re.compile(r"^(co-authored-by|made-with)\s*:", re.IGNORECASE)

ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

SEPARATORS = {"&&", "||", ";", "|", "&"}

HEREDOC = re.compile(
    r"<<-?\s*['\"]?(\w+)['\"]?\n(.*?)\n\1\s*(?:\n|$)",
    re.DOTALL,
)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        emit({"permission": "allow"})
        return

    tool_input = data.get("tool_input") or {}

    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except json.JSONDecodeError:
            emit({"permission": "allow"})
            return

    command = tool_input.get("command") or data.get("command") or ""
    cwd = tool_input.get("working_directory") or data.get("cwd") or "."

    try:
        decision = decide(command, cwd, tool_input)
    except Exception:
        if is_commit_command(command):
            deny(
                "The commit hook failed closed. Fix the commit command and try again.",
                "Commit check failed closed.",
            )
            return

        emit({"permission": "allow"})
        return

    emit(decision)


def decide(command: str, cwd: str, tool_input: dict) -> dict:
    try:
        command = drop_forbidden_trailers(command)
        tokens = shlex_split(command)
    except ValueError:
        if is_commit_command(command):
            return deny_payload(
                "The commit command could not be parsed. Pass the message with -m or a heredoc.",
                "Commit command was not parsed.",
            )

        return {"permission": "allow"}

    push = segment_after(tokens, "push")

    if push is not None and is_force_push(push):
        return deny_payload("Do not force-push.", "Force-push is blocked.")

    commit = segment_after(tokens, "commit")

    if commit is None:
        return {"permission": "allow"}

    problem = commit_problem(command, commit, cwd)

    if problem is not None:
        return deny_payload(problem, "Commit was rejected.")

    prefix = author_prefix(cwd)

    if prefix is None:
        return deny_payload(
            "Set user.name and user.email in git config. The commit hook reads them and does not change git config.",
            "Git author is not configured.",
        )

    updated = dict(tool_input)
    updated["command"] = with_author(use_message_hook(command), prefix)

    if updated["command"] == command:
        return {"permission": "allow"}

    return {"permission": "allow", "updated_input": updated}


def commit_problem(command: str, segment: list[str], cwd: str) -> str | None:
    paths = commit_paths(segment, cwd)

    if paths is None:
        return "The index could not be read, so the commit was stopped."

    if spans_both_apps(paths):
        return "Keep apps/api and apps/web in separate commits."

    message = extract_message(command, segment, cwd)

    if message is None:
        return "Pass the message with -m or a heredoc. Do not open an editor."

    return message_problem(message)


def message_problem(message: str) -> str | None:
    if CYRILLIC.search(message):
        return f"The message must be English, with no Cyrillic. {MESSAGE_RULE}"

    lines = message.splitlines()

    if not lines or not lines[0].strip():
        return f"The subject is missing. {MESSAGE_RULE}"

    subject = lines[0].strip()

    if subject.endswith("."):
        return f"The subject has no trailing period. {MESSAGE_RULE}"

    if CONVENTIONAL.match(subject):
        return f"Do not use a type prefix such as feat: or fix:. {MESSAGE_RULE}"

    for line in lines:
        if TRAILER.match(line.strip()):
            return (
                "Do not add Co-authored-by, Made-with, or any trailer that names Cursor. "
                + MESSAGE_RULE
            )

    if len(lines) != 3 or lines[1].strip() != "" or not lines[2].strip():
        return f"Leave one blank line after the subject, then one sentence. {MESSAGE_RULE}"

    body = lines[2].strip()

    if not body.endswith(".") or body.count(".") != 1:
        return f"The body is one sentence on why the step exists. {MESSAGE_RULE}"

    return None


def extract_message(command: str, segment: list[str], cwd: str) -> str | None:
    bodies = [match.group(2) for match in HEREDOC.finditer(command)]
    flag_message = message_from_flags(segment)

    if bodies and (flag_message is None or "$(" in flag_message or "<<" in flag_message):
        return bodies[0] if len(bodies) == 1 else "\n\n".join(bodies)

    if flag_message is not None:
        return flag_message

    file_message = message_from_file(segment, cwd)

    if file_message is not None:
        return file_message

    if "--no-edit" in segment and "--amend" in segment:
        return head_message(cwd)

    return None


def message_from_flags(segment: list[str]) -> str | None:
    messages: list[str] = []
    index = 0

    while index < len(segment):
        token = segment[index]

        if token in ("-m", "--message") and index + 1 < len(segment):
            messages.append(segment[index + 1])
            index += 2
            continue

        if token.startswith("--message="):
            messages.append(token.split("=", 1)[1])
            index += 1
            continue

        index += 1

    if not messages:
        return None

    if len(messages) == 1:
        return messages[0]

    return "\n\n".join(messages)


def message_from_file(segment: list[str], cwd: str) -> str | None:
    path = flag_value(segment, "-F", "--file")

    if path is None:
        return None

    try:
        with open(path if path.startswith("/") else f"{cwd}/{path}", encoding="utf-8") as handle:
            return handle.read().rstrip("\n")
    except OSError:
        return None


def head_message(cwd: str) -> str | None:
    result = git(cwd, ["log", "-1", "--format=%B"])

    if result is None:
        return None

    return result.rstrip("\n")


def commit_paths(segment: list[str], cwd: str) -> list[str] | None:
    if "--" in segment:
        return [path for path in segment[segment.index("--") + 1 :] if path]

    staged = git(cwd, ["diff", "--cached", "--name-only"])

    if staged is None:
        return None

    paths = [line for line in staged.splitlines() if line]

    if "-a" in segment or "--all" in segment:
        unstaged = git(cwd, ["diff", "--name-only"])

        if unstaged is None:
            return None

        paths.extend(line for line in unstaged.splitlines() if line)

    return paths


def spans_both_apps(paths: list[str]) -> bool:
    normalized = [normalize_path(path) for path in paths]
    api = any(path == "apps/api" or path.startswith("apps/api/") for path in normalized)
    web = any(path == "apps/web" or path.startswith("apps/web/") for path in normalized)

    return api and web


def normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")

    while normalized.startswith("./"):
        normalized = normalized[2:]

    return normalized.lstrip("/")


def is_force_push(segment: list[str]) -> bool:
    for token in segment:
        if token in ("-f", "--force", "--force-with-lease", "--force-if-includes"):
            return True

        if token.startswith("+") and not token.startswith("++"):
            return True

    return False


def is_commit_command(command: str) -> bool:
    return re.search(r"(^|[\s;&|])git\s+commit\b", command) is not None


def segment_after(tokens: list[str], name: str) -> list[str] | None:
    for start in command_starts(tokens):
        index = skip_exports(tokens, start)

        if index >= len(tokens):
            continue

        if tokens[index] != "git" and not tokens[index].endswith("/git"):
            continue

        cursor = index + 1

        while cursor < len(tokens):
            if tokens[cursor] in ("-C", "-c", "--git-dir", "--work-tree") and cursor + 1 < len(tokens):
                cursor += 2
                continue

            if tokens[cursor].startswith("-"):
                cursor += 1
                continue

            break

        if cursor >= len(tokens) or tokens[cursor] != name:
            continue

        segment: list[str] = []
        end = cursor + 1

        while end < len(tokens) and tokens[end] not in SEPARATORS:
            segment.append(tokens[end])
            end += 1

        return segment

    return None


def command_starts(tokens: list[str]) -> list[int]:
    starts = [0]

    for index, token in enumerate(tokens):
        if token in SEPARATORS:
            starts.append(index + 1)

    return starts


def skip_exports(tokens: list[str], index: int) -> int:
    while index < len(tokens):
        if ASSIGNMENT.match(tokens[index]):
            index += 1
            continue

        if tokens[index] == "export":
            index += 1

            while index < len(tokens) and ASSIGNMENT.match(tokens[index]):
                index += 1

            continue

        break

    return index


def flag_value(segment: list[str], short: str, long: str) -> str | None:
    index = 0

    while index < len(segment):
        token = segment[index]

        if token in (short, long) and index + 1 < len(segment):
            return segment[index + 1]

        if token.startswith(f"{long}="):
            return token.split("=", 1)[1]

        index += 1

    return None


def author_prefix(cwd: str) -> str | None:
    name = config_value(cwd, "user.name")
    email = config_value(cwd, "user.email")

    if name is None or email is None:
        return None

    return (
        "export "
        f"GIT_AUTHOR_NAME={shlex.quote(name)} "
        f"GIT_AUTHOR_EMAIL={shlex.quote(email)} "
        f"GIT_COMMITTER_NAME={shlex.quote(name)} "
        f"GIT_COMMITTER_EMAIL={shlex.quote(email)}"
    )


def config_value(cwd: str, key: str) -> str | None:
    output = git(cwd, ["config", "--get", key])

    if output is None:
        return None

    value = output.strip()

    if not value:
        return None

    return value


TRAILER_FLAG = re.compile(
    r"""--trailer(?:=("[^"]*"|'[^']*'|\S+)|[ \t]+("[^"]*"|'[^']*'|\S+))"""
)


def drop_forbidden_trailers(command: str) -> str:
    def replace(match: re.Match[str]) -> str:
        raw = match.group(1) or match.group(2)
        value = raw[1:-1] if raw[:1] in {"'", '"'} else raw

        if is_forbidden_trailer(value):
            return ""

        return match.group(0)

    return TRAILER_FLAG.sub(replace, command)


def is_forbidden_trailer(value: str) -> bool:
    return TRAILER.match(value.strip()) is not None


def use_message_hook(command: str) -> str:
    hooks = shlex.quote(str(Path(__file__).resolve().parent / "git"))
    git_word = re.compile(r"(?:(?<=\s)|^)((?:[\w./-]+/)?git)(?=\s)")

    def replace(match: re.Match[str]) -> str:
        word = match.group(1)
        rest = command[match.end() :]
        head = re.split(r"\s*(?:&&|\|\||;)\s*", rest, maxsplit=1)[0]

        if re.search(r"(^|\s)commit(?=\s|$)", head) is None:
            return word

        return f"{word} -c core.hooksPath={hooks}"

    return git_word.sub(replace, command)


def with_author(command: str, prefix: str) -> str:
    if prefix in command:
        return command

    return f"{prefix}\n{command}"


def git(cwd: str, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    return result.stdout


def shlex_split(command: str) -> list[str]:
    return shlex.split(command, posix=True)


def deny(agent_message: str, user_message: str) -> None:
    emit(deny_payload(agent_message, user_message))


def deny_payload(agent_message: str, user_message: str) -> dict:
    return {
        "permission": "deny",
        "user_message": user_message,
        "agent_message": agent_message,
    }


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
