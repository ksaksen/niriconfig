#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${HOME}/.dotfiles-backup/$(date +%Y%m%d-%H%M%S)"

link_file() {
    local source="$1"
    local target="$2"

    mkdir -p "$(dirname "$target")"

    if [ -e "$target" ] || [ -L "$target" ]; then
        mkdir -p "${BACKUP_DIR}/$(dirname "${target#${HOME}/}")"
        mv "$target" "${BACKUP_DIR}/${target#${HOME}/}"
    fi

    ln -s "$source" "$target"
    printf 'linked %s -> %s\n' "$target" "$source"
}

link_file "$ROOT/config/niri/config.kdl" "$HOME/.config/niri/config.kdl"
link_file "$ROOT/config/alacritty/alacritty.toml" "$HOME/.config/alacritty/alacritty.toml"
link_file "$ROOT/config/alacritty/colors-dark.toml" "$HOME/.config/alacritty/colors-dark.toml"
link_file "$ROOT/config/alacritty/colors-light.toml" "$HOME/.config/alacritty/colors-light.toml"
link_file "$ROOT/config/starship.toml" "$HOME/.config/starship.toml"
link_file "$ROOT/config/bashrc.d/90-starship.sh" "$HOME/.bashrc.d/90-starship.sh"
link_file "$ROOT/config/tmux" "$HOME/.config/tmux"
link_file "$ROOT/config/kanshi/config" "$HOME/.config/kanshi/config"
link_file "$ROOT/assets/wallpapers/italy-landscape_5120x1440.jpg" "$HOME/.local/share/wallpapers/italy-landscape_5120x1440.jpg"
link_file "$ROOT/config/waybar/config.jsonc" "$HOME/.config/waybar/config.jsonc"
link_file "$ROOT/config/waybar/style.css" "$HOME/.config/waybar/style.css"
link_file "$ROOT/config/waybar/docker-status.py" "$HOME/.config/waybar/docker-status.py"
link_file "$ROOT/config/waybar/update-status.py" "$HOME/.config/waybar/update-status.py"
link_file "$ROOT/config/waybar/colorscheme-status.py" "$HOME/.config/waybar/colorscheme-status.py"
link_file "$ROOT/config/waybar/display-status.py" "$HOME/.config/waybar/display-status.py"
link_file "$ROOT/config/waybar/power_menu.xml" "$HOME/.config/waybar/power_menu.xml"
link_file "$ROOT/config/kitty/kitty.conf" "$HOME/.config/kitty/kitty.conf"
link_file "$ROOT/scripts/idea-x11" "$HOME/.local/bin/idea-x11"
link_file "$ROOT/scripts/docker-status-terminal" "$HOME/.local/bin/docker-status-terminal"
link_file "$ROOT/scripts/cpu-status-terminal" "$HOME/.local/bin/cpu-status-terminal"
link_file "$ROOT/scripts/memory-status-terminal" "$HOME/.local/bin/memory-status-terminal"
link_file "$ROOT/scripts/update-status-terminal" "$HOME/.local/bin/update-status-terminal"
link_file "$ROOT/scripts/kill-window" "$HOME/.local/bin/kill-window"
link_file "$ROOT/scripts/cleanup-empty-workspaces" "$HOME/.local/bin/cleanup-empty-workspaces"
link_file "$ROOT/scripts/close-workspace" "$HOME/.local/bin/close-workspace"
link_file "$ROOT/scripts/workspace-gc" "$HOME/.local/bin/workspace-gc"
link_file "$ROOT/scripts/niri-set-wallpaper" "$HOME/.local/bin/niri-set-wallpaper"
link_file "$ROOT/scripts/color-scheme-toggle" "$HOME/.local/bin/color-scheme-toggle"
link_file "$ROOT/scripts/display-profile-switcher" "$HOME/.local/bin/display-profile-switcher"

# Initialize Alacritty color scheme (dark by default) if not already set
if [ ! -f "$HOME/.local/share/alacritty/colorscheme.toml" ]; then
    mkdir -p "$HOME/.local/share/alacritty"
    cp "$ROOT/config/alacritty/colors-dark.toml" "$HOME/.local/share/alacritty/colorscheme.toml"
fi

ensure_dnf_package() {
    local binary="$1"
    local package="$2"

    if command -v "$binary" >/dev/null 2>&1; then
        return
    fi

    if ! command -v dnf >/dev/null 2>&1; then
        printf '%s not found and dnf is unavailable, skipping install of %s\n' "$binary" "$package" >&2
        return
    fi

    printf '%s not found, installing %s via dnf...\n' "$binary" "$package"
    sudo dnf install -y "$package"
}

# Tray applets spawned by config/niri/config.kdl. Both packages are in
# Fedora's official repos, so install them automatically if missing.
ensure_dnf_package "nm-applet" "network-manager-applet"
ensure_dnf_package "blueman-applet" "blueman"

# JetBrains Toolbox is NOT in Fedora's official repos (installed manually
# from a JetBrains-provided .rpm), so it is intentionally not auto-installed
# here - the spawn-at-startup line for it in config.kdl is a no-op if missing.
if ! command -v jetbrains-toolbox >/dev/null 2>&1; then
    printf 'jetbrains-toolbox not found (not in Fedora repos) - hopper over, installer manuelt om ønskelig\n'
fi

printf 'backup directory: %s\n' "$BACKUP_DIR"
