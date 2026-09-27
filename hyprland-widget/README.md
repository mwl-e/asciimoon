ASCIIMoon Hyprland Widget
=========================

A desktop widget version of ASCIIMoon for Hyprland. It shows the same ASCII art moon, and adds a location pin. Once you pin a location, the widget shows:

- **The moon turned the way it looks from where you are.** Two angles are applied:
  - the *bright-limb position angle*, which says which side of the moon the sun lights, and
  - the *parallactic angle*, which says how your "up" is tilted against celestial north.

  So a waxing crescent is lit on the right in London and on the left in Sydney. Near the equator it looks like a "boat". The moon also tilts as it rises and sets, and it dims when it is below your horizon.
- **Where you are in the day/night cycle:** Daytime, Golden hour, Civil, Nautical or Astronomical twilight (dawn or dusk), or Night. The panel's colour follows the sky, and a 24-hour ASCII timeline marks the current time with `^`.
- Sunrise and sunset, moonrise and moonset, and the moon's current altitude.

Without a location the moon is shown north-up, as on the website.

The widget is `widget.html`, a self-contained page that loads its own copy of SunCalc so it works offline. `asciimoon-widget.py` shows that page in a transparent WebKitGTK view on a `wlr-layer-shell` surface, so Hyprland treats it as a widget and not as a tiled window.

Install
-------

Arch / Manjaro:

```sh
sudo pacman -S python-gobject gtk3 gtk-layer-shell webkit2gtk-4.1
./install.sh
```

Fedora: `sudo dnf install python3-gobject gtk3 gtk-layer-shell webkit2gtk4.1`<br>
Debian/Ubuntu: `sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-gtklayershell-0.1 gir1.2-webkit2-4.1`

Then add it to `~/.config/hypr/hyprland.conf`:

```ini
exec-once = ~/.local/bin/asciimoon-widget --position top-right
```

Optional: to blur the area behind the widget, add a layer rule for the `asciimoon` namespace. The rule syntax changes between Hyprland releases, so check the wiki for your version. On older releases it is:

```ini
layerrule = blur, asciimoon
layerrule = ignorezero, asciimoon
```

Setting your location
---------------------

Click the **pin** button in the top-right corner of the widget. Then do one of these:

- type a city name (for example `Oslo`), which is looked up with Open-Meteo's free geocoder. This also sets the correct timezone for the times shown.
- type coordinates such as `59.91, 10.75` (south and west are negative). No network is needed, and times are shown in your system timezone.
- click **Detect** to ask the system for your location. This needs `geoclue` to be running.

The location is saved in `~/.local/share/asciimoon-widget`. **Clear** returns to the north-up view.

You can also give a default location on the command line. The pin overrides it:

```sh
asciimoon-widget --lat 59.91 --lon 10.75 --name Oslo --tz Europe/Oslo
```

Options
-------

| Flag | Default | |
| --- | --- | --- |
| `--position` | `top-right` | `top-left`, `top`, `top-right`, `left`, `center`, `right`, `bottom-left`, `bottom`, `bottom-right` |
| `--margin` | `24` | gap to the screen edge, in px |
| `--width` / `--height` | `320` / `480` | widget size |
| `--layer` | `bottom` | `background`/`bottom` = under your windows, `top`/`overlay` = above them |
| `--monitor` | focused | monitor index |
| `--windowed` | off | open as a normal window, for testing |
| `--debug` | off | enable the WebKit inspector (Ctrl+Shift+I) |

You can also open `widget.html` directly in a browser to try it out.

Credits
-------

- Moon calculations: [SunCalc](https://github.com/mourner/suncalc) by Vladimir Agafonkin, BSD-2-Clause (see `vendor/SUNCALC-LICENSE`).
- Geocoding: [Open-Meteo](https://open-meteo.com/en/docs/geocoding-api).
- Moon ASCII art: made from NASA's Galileo photo [PIA00405](https://images.nasa.gov/details-PIA00405), as on the main site.
