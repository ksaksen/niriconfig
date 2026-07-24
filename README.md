# niriconfig

Personlig oppsett for et Niri-basert Linux-skrivebord: window manager, Waybar, terminal, prompt og en
håndfull hjelpescript. Ekstrahert fra et jobb-dotfiles-repo, renset for alt som var spesifikt for den
arbeidsgiveren — dette er ment for privat bruk.

## Innhold

- `config/niri/config.kdl`: window manager-oppsett (keybindings, workspace- og window-rules)
- `config/kanshi/config`: `home`-skjermprofil, kjører wallpaper-scriptet ved bytte
- `config/waybar/config.jsonc` + `style.css`: statuslinje-layout og styling
- `config/waybar/docker-status.py`: Waybar-modul for Docker-status
- `config/waybar/update-status.py`: Waybar-modul for Fedora-oppdateringer (`dnf`)
- `config/waybar/colorscheme-status.py`: Waybar-modul for lys/mørk-tema-indikator
- `config/waybar/display-status.py`: Waybar-modul som viser tilkoblede skjermer
- `config/waybar/power_menu.xml`: power-meny referert fra Waybar-konfigen
- `config/alacritty/`: terminal-oppsett + lys/mørke fargeskjema
- `config/kitty/kitty.conf`: alternativt terminal-oppsett
- `config/tmux/tmux.conf`: Catppuccin dark-tema, musestøtte
- `config/starship.toml` + `config/bashrc.d/90-starship.sh`: shell-prompt
- `config/sudoers.d/drm-rescan`: sudoers-regel som lar `%linuxdesktopusers`-gruppen trigge en DRM-hotplug-rescan uten passord (installeres ikke automatisk, se Merknader)
- `assets/wallpapers/italy-landscape_5120x1440.jpg`: wallpaper/lockscreen-bilde
- `scripts/niri-set-wallpaper`: setter wallpaper på aktiv `niri`-output via `swaybg`
- `scripts/display-profile-switcher`: fuzzel-meny for å bytte skjermprofil / restarte kanshi
- `scripts/color-scheme-toggle`: bytter lys/mørkt fargetema for GNOME + alacritty
- `scripts/workspace-gc` + `scripts/cleanup-empty-workspaces`: rydder automatisk bort tomme, navngitte workspaces
- `scripts/close-workspace`: lukker alle vinduer i fokusert workspace
- `scripts/kill-window`: lukker fokusert vindu via `niri`
- `scripts/idea-x11`: launcher for IntelliJ IDEA under XWayland
- `scripts/docker-status-terminal`, `cpu-status-terminal`, `memory-status-terminal`, `update-status-terminal`: live-oversikter åpnet fra Waybar-klikk

## Installer

```bash
./install.sh
```

Symlinker `config/` inn i `~/.config/` (pluss shell/script-filer til `~/.bashrc.d/` og `~/.local/bin/`),
og tar backup av eksisterende filer i `~/.dotfiles-backup/<timestamp>/`.

## Avhengigheter

Niri, Kanshi, Waybar, Alacritty (eller Kitty), Fuzzel, Swaylock, Brightnessctl, Wpctl, Jq, Python 3,
en Nerd Font (f.eks. CaskaydiaCove eller IosevkaTerm) for at prompt- og waybar-symboler skal vises riktig.

`niri` spawner også `nm-applet` (pakke: `network-manager-applet`) og `blueman-applet` (pakke: `blueman`)
for wifi-/bluetooth-ikoner i systray, siden niri ikke prosesserer XDG autostart-filer selv.
`install.sh` installerer disse to automatisk via `dnf` hvis de mangler. `jetbrains-toolbox` spawnes
også, men er ikke i Fedoras offisielle pakkebrønn og installeres derfor ikke automatisk — hopp over
den linja i `config/niri/config.kdl` hvis du ikke bruker JetBrains Toolbox.

## Nøkkel-keybindings (definert i `niri/config.kdl`)

| Binding | Handling |
|---------|----------|
| `Mod+T` | Åpne terminal |
| `Mod+D` | Fuzzel app-launcher |
| `Mod+F9` | Åpne IntelliJ IDEA (`idea-x11`) |
| `Super+Alt+L` / `Super+Alt+X` | Lås skjerm (`swaylock`) |
| `Super+Alt+A` | Bytt lys/mørkt fargetema |
| `Super+Alt+Q` | Lukk fokusert vindu og prosess |
| `Super+Alt+Shift+Q` | Lukk fokusert workspace |
| `Mod+Shift+S` | Områdeskjermbilde til utklippstavlen |

## Merknader

- `install.sh` linker wallpaper-/lockscreen-bildet til `~/.local/share/wallpapers/italy-landscape_5120x1440.jpg`.
- `niri` og `kanshi` bruker `~/.local/bin/niri-set-wallpaper` for å sette bakgrunn på aktiv skjerm, så `swaybg`, `niri` og `jq` må være installert.
- `niri` starter `waybar` og `kanshi` ved oppstart, samt `workspace-gc` som automatisk unnavngir tomme, inaktive workspaces.
- `kanshi/config` inneholder kun `home`-profilen med mine egne skjermmodeller/-oppløsninger — juster `output`-linjene (og evt. `scripts/display-profile-switcher`) til dine egne skjermer.
- `config/sudoers.d/drm-rescan` installeres ikke av `install.sh` (krever root). Kopier den manuelt om ønskelig: `sudo cp config/sudoers.d/drm-rescan /etc/sudoers.d/drm-rescan` — forutsetter at gruppen `linuxdesktopusers` finnes og at brukeren din er medlem.
