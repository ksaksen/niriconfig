# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo purpose

Personal dotfiles for a Niri (Wayland compositor) desktop: window manager config, Waybar status bar,
terminal emulators, shell prompt, and a handful of helper scripts. Extracted from a work dotfiles repo
and scrubbed of anything employer-specific — this is for private use. There is no build step; files
are symlinked into place and take effect the next time the relevant program (re)starts.

## Installing / applying changes

```bash
./install.sh
```

Symlinks everything under `config/` into `~/.config/` (plus shell/script files into `~/.bashrc.d/` and
`~/.local/bin/`), backing up any pre-existing files into `~/.dotfiles-backup/<timestamp>/` first.
Since files are symlinked, edits under this repo take effect immediately — no re-run of `install.sh`
needed after the first install, except when *adding a new file* that needs a new symlink (update
`install.sh` in that case).

There is no test suite. Verifying a change means:
- `niri validate` (or reload niri: `Mod+Shift+E`-adjacent reload, or restart niri) after editing `config/niri/config.kdl` — niri will refuse to load a malformed KDL config.
- `killall waybar && waybar &` (or send `pkill -RTMIN+12 waybar` for scripts that already listen for that signal) after editing `config/waybar/*`.
- Run a waybar Python module directly (e.g. `python3 config/waybar/docker-status.py`) to sanity-check its JSON output before wiring it into `config.jsonc`.
- `kanshictl reload` after editing `config/kanshi/config`.

## Architecture

**`config/niri/config.kdl`** is the single window-manager config (KDL format). It starts from niri's
upstream default/example config and layers custom `binds`, `window-rule`s, and `spawn-at-startup`
lines on top — when editing, preserve the extensive inline comments that document each stock section,
and add new custom behavior near the existing custom lines rather than scattered throughout. Notable
startup chain: niri spawns `niri-set-wallpaper`, `workspace-gc`, `waybar`, and `kanshi` directly via
`spawn-at-startup`.

**Multi-monitor handling is split between two layers on purpose**: `config/niri/config.kdl` only
configures the built-in laptop panel (`eDP-1`) by name. External monitors are *not* referenced by
connector name in niri config (connector names like `DP-4` are unstable across reboots/cable changes);
instead `config/kanshi/config` matches external outputs by monitor make/model string and handles their
mode/position/scale. `scripts/display-profile-switcher` is a fuzzel-driven front-end over `kanshictl`
for switching/reloading kanshi profiles, with a Python fallback (`apply_home`) that drives the same
result directly via `niri msg output ...` if kanshi's own profile match fails.

**Event-stream daemon pattern**: anything that needs to react to niri state changes reliably —
regardless of how long niri itself takes to become ready at boot — is written as a long-lived loop
around `niri msg event-stream`, not a one-shot script with a sleep/retry budget (a one-shot script
raced against niri's startup timing is fragile and hardware-dependent; see git history on
`niri-set-wallpaper` for what that failure mode looked like in practice). `workspace-gc` and
`niri-set-wallpaper` are both spawned once at startup and loop forever: reconnect to
`event-stream` with a 1s backoff if it drops, and re-run their action on every event. Follow this
pattern for anything new that depends on live niri/output state.

- `workspace-gc` invokes `cleanup-empty-workspaces` on every event to unset names on workspaces that
  are empty and not focused/active. `close-workspace` is the interactive counterpart — it closes every
  window in the focused workspace (via repeated `niri msg action focus-window` + `close-window`,
  polling until the window list stabilizes since some apps prompt on close) and then invokes
  `cleanup-empty-workspaces` itself. These three scripts shell out to `niri msg --json ...` and parse
  the result with inline Python (`python3 -c '...'`) rather than `jq`, for structured filtering logic.
- `niri-set-wallpaper` re-derives the enabled-output set (`niri msg -j outputs`, via `jq`) on every
  event and only kills/relaunches `swaybg` when that set actually changed (or `swaybg` isn't running) —
  not on every event — to avoid a visible wallpaper flash on unrelated niri activity. One `swaybg`
  process is launched with one `-o`/`-i`/`-m` group per output rather than one process per output,
  since separate per-output processes each log spurious "could not find config for output" warnings
  for every *other* output they didn't get.

**Waybar modules** (`config/waybar/*.py`) are standalone scripts invoked by Waybar per its
`config.jsonc` `custom/*` module definitions — each prints one JSON line (text/tooltip/class) per
invocation and is otherwise stateless. `colorscheme-status.py` reflects state written by
`scripts/color-scheme-toggle` (`~/.local/state/colorscheme`), which is the single source of truth for
light/dark mode: it toggles GNOME's `color-scheme` gsetting, swaps the Alacritty color file, and
signals waybar (`pkill -RTMIN+12 waybar`) to refresh. When adding a new Waybar module, follow the
existing pattern (read-only, JSON-on-stdout, no persistent state) rather than introducing a daemon.

**Terminal/shell configs are static and mostly config-only**: `config/alacritty/`,
`config/kitty/kitty.conf`, `config/tmux/tmux.conf`, `config/starship.toml`, and
`config/bashrc.d/90-starship.sh` have no custom scripting beyond what's in those files directly.

**`config/sudoers.d/drm-rescan`** is intentionally *not* linked by `install.sh` (it requires root) —
document any changes to it in README.md's Merknader section rather than adding it to the install
script's symlink list.

## Conventions

- Scripts are Bash (`set -euo pipefail`, `#!/usr/bin/env bash`) or Python 3 (`#!/usr/bin/env python3`); no other runtimes are used.
- Bash scripts that shell out to `niri msg --json` and need to filter/reshape the JSON do so with inline `python3 -c '...'` rather than adding a `jq` dependency for anything beyond trivial field extraction (`niri-set-wallpaper` uses `jq -r` for its one simple filter: enabled output names).
- Scripts check `command -v <tool>` and exit with a message on `stderr` when a required binary is missing, rather than failing silently or with a raw error.
- README.md (in Norwegian) is the canonical file-by-file description of this repo, the install behavior, dependencies, and key keybindings — keep it in sync when adding/removing files or changing keybindings, rather than duplicating that content here.
