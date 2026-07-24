#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess


UPDATE_ICON = "󰏗"
PACKAGE_LINE = re.compile(r"^\S+\s+\S+\s+\S+$")


def emit(payload: dict) -> None:
    print(json.dumps(payload))


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    base_args = ["dnf", "--cacheonly", "--setopt=logdir=/tmp", "-q"]
    env = {
        **os.environ,
        "XDG_CACHE_HOME": "/tmp",
        "TMPDIR": "/tmp",
    }
    return subprocess.run(
        base_args + args,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def parse_package_lines(output: str) -> list[str]:
    packages = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Last metadata expiration check:"):
            continue
        if line in {"Obsoleting Packages", "Security notice(s)"}:
            continue
        if PACKAGE_LINE.match(line):
            packages.append(line)
    return packages


def main() -> None:
    if shutil.which("dnf") is None:
        emit(
            {
                "text": f"{UPDATE_ICON} n/a",
                "class": ["updates", "missing"],
                "tooltip": "dnf not found in PATH",
            }
        )
        return

    updates = run_command(["check-update"])
    if updates.returncode not in {0, 100}:
        stderr = updates.stderr.strip() or "dnf check-update failed"
        emit(
            {
                "text": f"{UPDATE_ICON} err",
                "class": ["updates", "error"],
                "tooltip": stderr,
            }
        )
        return

    all_updates = parse_package_lines(updates.stdout)

    security = run_command(["updateinfo", "list", "updates", "security"])
    security_updates = []
    if security.returncode == 0:
        security_updates = parse_package_lines(security.stdout)

    total_count = len(all_updates)
    security_count = len(security_updates)

    if security_count > 0:
        text = f"{UPDATE_ICON} {total_count} !"
        classes = ["updates", "security"]
    elif total_count > 0:
        text = f"{UPDATE_ICON} {total_count}"
        classes = ["updates", "pending"]
    else:
        text = f"{UPDATE_ICON} 0"
        classes = ["updates", "none"]

    tooltip_lines = [f"Updates available: {total_count}"]
    if security_count > 0:
        tooltip_lines.append(f"Security updates: {security_count}")

    if security_updates:
        tooltip_lines.append("")
        tooltip_lines.append("Security:")
        tooltip_lines.extend(security_updates[:12])
        if len(security_updates) > 12:
            tooltip_lines.append(f"... and {len(security_updates) - 12} more")

    if all_updates:
        tooltip_lines.append("")
        tooltip_lines.append("All updates:")
        tooltip_lines.extend(all_updates[:12])
        if len(all_updates) > 12:
            tooltip_lines.append(f"... and {len(all_updates) - 12} more")

    emit(
        {
            "text": text,
            "class": classes,
            "tooltip": "\n".join(tooltip_lines),
        }
    )


if __name__ == "__main__":
    main()
