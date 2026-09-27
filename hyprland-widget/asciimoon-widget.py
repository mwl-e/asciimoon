#!/usr/bin/env python3
"""ASCIIMoon desktop widget for Hyprland (and other wlroots-style compositors).

Shows widget.html in a transparent WebKitGTK view that sits on a
wlr-layer-shell surface, so it behaves like a desktop widget instead of a
normal window.

Dependencies (Arch): python-gobject gtk3 gtk-layer-shell webkit2gtk-4.1
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import urlencode

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
try:
    gi.require_version("WebKit2", "4.1")
except ValueError:
    gi.require_version("WebKit2", "4.0")

from gi.repository import Gdk, GLib, Gtk, WebKit2  # noqa: E402

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell  # noqa: E402
except (ValueError, ImportError):
    GtkLayerShell = None

HERE = Path(__file__).resolve().parent
DATA_DIR = Path(GLib.get_user_data_dir()) / "asciimoon-widget"
CACHE_DIR = Path(GLib.get_user_cache_dir()) / "asciimoon-widget"

POSITIONS = {
    "top-left": ("top", "left"),
    "top": ("top",),
    "top-right": ("top", "right"),
    "left": ("left",),
    "center": (),
    "right": ("right",),
    "bottom-left": ("bottom", "left"),
    "bottom": ("bottom",),
    "bottom-right": ("bottom", "right"),
}


def parse_args():
    parser = argparse.ArgumentParser(description="ASCIIMoon desktop widget")
    parser.add_argument("--position", choices=POSITIONS, default="top-right")
    parser.add_argument("--margin", type=int, default=24, help="gap to the screen edge in px")
    parser.add_argument("--width", type=int, default=320)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument(
        "--layer",
        choices=["background", "bottom", "top", "overlay"],
        default="bottom",
        help="bottom = under windows (desktop widget), top = above windows",
    )
    parser.add_argument("--monitor", type=int, default=None, help="monitor index (default: focused)")
    parser.add_argument("--lat", type=float, help="default latitude (the pin button overrides it)")
    parser.add_argument("--lon", type=float, help="default longitude")
    parser.add_argument("--name", help="label for the default location")
    parser.add_argument("--tz", help="IANA timezone for the default location, e.g. Europe/Oslo")
    parser.add_argument("--debug", action="store_true", help="enable the WebKit inspector")
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="open as a normal window (for testing or non-layer-shell setups)",
    )
    return parser.parse_args()


def setup_layer_shell(window, args):
    if GtkLayerShell is None or not GtkLayerShell.is_supported():
        print(
            "asciimoon-widget: gtk-layer-shell is unavailable, falling back to a normal window",
            file=sys.stderr,
        )
        return

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.set_namespace(window, "asciimoon")
    GtkLayerShell.set_layer(window, getattr(GtkLayerShell.Layer, args.layer.upper()))

    for edge_name in POSITIONS[args.position]:
        edge = getattr(GtkLayerShell.Edge, edge_name.upper())
        GtkLayerShell.set_anchor(window, edge, True)
        GtkLayerShell.set_margin(window, edge, args.margin)

    # KEYBOARD FOCUS ONLY WHEN CLICKED, SO YOU CAN TYPE A LOCATION IN THE PIN PANEL
    if hasattr(GtkLayerShell, "set_keyboard_mode"):
        GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.ON_DEMAND)
    else:
        GtkLayerShell.set_keyboard_interactivity(window, True)

    if args.monitor is not None:
        monitor = Gdk.Display.get_default().get_monitor(args.monitor)
        if monitor is not None:
            GtkLayerShell.set_monitor(window, monitor)


def build_webview(debug=False):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # PERSISTENT STORAGE SO THE PINNED LOCATION SURVIVES RESTARTS
    manager = WebKit2.WebsiteDataManager(
        base_data_directory=str(DATA_DIR),
        base_cache_directory=str(CACHE_DIR),
    )
    context = WebKit2.WebContext.new_with_website_data_manager(manager)
    webview = WebKit2.WebView.new_with_context(context)

    settings = webview.get_settings()
    settings.set_enable_html5_local_storage(True)
    settings.set_allow_file_access_from_file_urls(True)
    settings.set_enable_developer_extras(debug)

    # TRANSPARENT PAGE BACKGROUND, THE WIDGET DRAWS ITS OWN ROUNDED PANEL
    webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))

    def on_permission_request(_view, request):
        # ONLY THE "DETECT" BUTTON'S GEOLOCATION REQUEST IS ALLOWED
        if isinstance(request, WebKit2.GeolocationPermissionRequest):
            request.allow()
        else:
            request.deny()
        return True

    webview.connect("permission-request", on_permission_request)
    return webview


def main():
    args = parse_args()

    window = Gtk.Window(title="ASCIIMoon")
    window.set_default_size(args.width, args.height)
    window.set_size_request(args.width, args.height)
    window.set_app_paintable(True)
    visual = window.get_screen().get_rgba_visual()
    if visual is not None:
        window.set_visual(visual)

    if not args.windowed:
        setup_layer_shell(window, args)

    webview = build_webview(args.debug)
    window.add(webview)

    query = {}
    if args.lat is not None and args.lon is not None:
        query = {"lat": args.lat, "lon": args.lon}
        if args.name:
            query["name"] = args.name
        if args.tz:
            query["tz"] = args.tz
    url = (HERE / "widget.html").as_uri()
    if query:
        url += "?" + urlencode(query)
    webview.load_uri(url)

    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
