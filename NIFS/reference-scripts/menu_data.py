"""Navigation data — loaded from datasets/content/chrome/chrome_navigation.json."""

from __future__ import annotations

from chrome_content_lib import get_navigation

_nav = get_navigation()

MAIN_NAV_ITEMS = _nav["main_nav"]
FOOTER_LINKS = _nav["footer_links"]
MEGA_POPULAR_LOCALES = _nav["mega_popular_locales"]
MEGA_REGION_LABELS = _nav["mega_region_labels"]
MEGA_MENU_ASIDE = _nav["mega_menu_aside"]
ROUTE_ALIASES = _nav["route_aliases"]
