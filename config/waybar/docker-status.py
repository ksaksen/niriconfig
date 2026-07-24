#!/usr/bin/env python3
import json
import shutil
import subprocess


DOCKER_ICON = "󰡨"
MAX_INLINE_NAMES = 2
MAX_TOOLTIP_CONTAINERS = 8
MAX_TOOLTIP_STOPPED = 6


def emit(payload: dict) -> None:
    print(json.dumps(payload))


def main() -> None:
    if shutil.which("docker") is None:
        emit(
            {
                "text": f"{DOCKER_ICON} n/a",
                "class": ["docker", "missing"],
                "tooltip": "docker not found in PATH",
            }
        )
        return

    result = subprocess.run(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}\t{{.Image}}\t{{.Status}}",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip() or "docker daemon unavailable"
        emit(
            {
                "text": f"{DOCKER_ICON} err",
                "class": ["docker", "error"],
                "tooltip": stderr,
            }
        )
        return

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    containers = []
    for line in lines:
        parts = line.split("\t", 2)
        name = parts[0] if len(parts) > 0 else ""
        image = parts[1] if len(parts) > 1 else ""
        status = parts[2] if len(parts) > 2 else ""
        containers.append(
            {
                "name": name,
                "image": image,
                "status": status,
                "cpu": "?",
                "mem": "?",
            }
        )

    count = len(containers)

    if count == 0:
        containers = []

    stats = subprocess.run(
        [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}",
        ],
        capture_output=True,
        text=True,
    )
    if stats.returncode == 0:
        stats_by_name = {}
        for line in stats.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t", 2)
            if len(parts) < 3:
                continue
            stats_by_name[parts[0]] = {"cpu": parts[1], "mem": parts[2]}

        for container in containers:
            if container["name"] in stats_by_name:
                container["cpu"] = stats_by_name[container["name"]]["cpu"]
                container["mem"] = stats_by_name[container["name"]]["mem"]

    stopped = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            "status=exited",
            "--filter",
            "status=dead",
            "--filter",
            "status=restarting",
            "--format",
            "{{.Names}}\t{{.Image}}\t{{.Status}}",
        ],
        capture_output=True,
        text=True,
    )
    stopped_containers = []
    if stopped.returncode == 0:
        for line in stopped.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t", 2)
            name = parts[0] if len(parts) > 0 else ""
            image = parts[1] if len(parts) > 1 else ""
            status = parts[2] if len(parts) > 2 else ""
            stopped_containers.append({"name": name, "image": image, "status": status})

    problem_containers = []
    for container in stopped_containers:
        status = container["status"].lower()
        if "exited (" in status or "dead" in status or "restarting" in status:
            problem_containers.append(container)

    if count == 0 and not problem_containers:
        emit(
            {
                "text": f"{DOCKER_ICON} 0",
                "class": ["docker", "empty"],
                "tooltip": "No running containers",
            }
        )
        return

    if count == 0:
        text = f"{DOCKER_ICON} Docker !"
    elif problem_containers:
        text = f"{DOCKER_ICON} Docker !"
    else:
        text = f"{DOCKER_ICON} Docker"

    tooltip_lines = [f"Running containers: {count}", ""]
    for container in containers[:MAX_TOOLTIP_CONTAINERS]:
        tooltip_lines.append(
            f"{container['name']} [{container['image']}] | {container['status']} | CPU {container['cpu']} | MEM {container['mem']}"
        )

    if count > MAX_TOOLTIP_CONTAINERS:
        tooltip_lines.append("")
        tooltip_lines.append(f"... and {count - MAX_TOOLTIP_CONTAINERS} more")

    if problem_containers:
        if count > 0:
            tooltip_lines.append("")
        tooltip_lines.append("Problem containers:")
        tooltip_lines.append("")
        for container in problem_containers[:MAX_TOOLTIP_STOPPED]:
            tooltip_lines.append(
                f"{container['name']} [{container['image']}] | {container['status']}"
            )
        if len(problem_containers) > MAX_TOOLTIP_STOPPED:
            tooltip_lines.append("")
            tooltip_lines.append(
                f"... and {len(problem_containers) - MAX_TOOLTIP_STOPPED} more"
            )

    emit(
        {
            "text": text,
            "class": ["docker", "running" if count > 0 else "empty", "warning" if problem_containers else "ok"],
            "tooltip": "\n".join(line for line in tooltip_lines if line is not None).strip(),
        }
    )


if __name__ == "__main__":
    main()
