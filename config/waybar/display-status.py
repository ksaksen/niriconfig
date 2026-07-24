#!/usr/bin/env python3
import json
import subprocess


def get_outputs():
    try:
        result = subprocess.run(
            ["niri", "msg", "--json", "outputs"],
            capture_output=True, text=True, timeout=3
        )
        return json.loads(result.stdout)
    except Exception:
        return None


def is_internal(name):
    return name.startswith("eDP")


def short_label(info):
    make = info.get("make", "")
    model = info.get("model", "")
    if "Samsung" in make:
        return f"Samsung {model}"
    if "Sharp" in make:
        return "Laptop"
    return info.get("name", "Ukjent")


def main():
    outputs = get_outputs()
    if outputs is None:
        print(json.dumps({
            "text": "󰍵",
            "tooltip": "Feil: kan ikke hente skjerminfo",
            "class": "error"
        }))
        return

    external = {n: v for n, v in outputs.items() if not is_internal(n)}
    active_external = {n: v for n, v in external.items() if v.get("logical") is not None}
    inactive_external = {n: v for n, v in external.items() if v.get("logical") is None}

    lines = []
    for name, info in outputs.items():
        lbl = short_label(info)
        mode_idx = info.get("current_mode")
        logical = info.get("logical")
        if logical is not None and mode_idx is not None:
            m = info["modes"][mode_idx]
            lines.append(f"● {lbl}: {m['width']}x{m['height']}")
        else:
            lines.append(f"○ {lbl}: av")

    lines.append("")
    lines.append("Klikk: bytt kanshi-profil")
    tooltip = "\n".join(lines)

    if inactive_external:
        text = "󰍵"
        css_class = "warning"
    elif active_external:
        text = "󰍺"
        css_class = "ok"
    else:
        text = "󰍹"
        css_class = "laptop-only"

    print(json.dumps({"text": text, "tooltip": tooltip, "class": css_class}))


if __name__ == "__main__":
    main()
