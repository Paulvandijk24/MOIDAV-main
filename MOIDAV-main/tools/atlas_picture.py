# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Take light and dark screenshots of an Atlas HTML page."""

import pathlib
import sys

from playwright.sync_api import sync_playwright

page_file, picture = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2])

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome")
    for theme, output in (
        ("light", picture),
        ("dark", picture.with_stem(f"{picture.stem}-dark")),
    ):
        context = browser.new_context(
            viewport={"width": 1400, "height": 800},
            device_scale_factor=2,
            color_scheme=theme,
            reduced_motion="reduce",
        )
        context.add_init_script("localStorage.setItem('atlas.code', '0')")
        page = context.new_page()
        page.goto(page_file.as_uri(), wait_until="networkidle")
        page.wait_for_function(
            "document.querySelectorAll('#scene g[data-id]').length > 0",
            timeout=120_000,
        )
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(500)
        page.screenshot(path=str(output))
        context.close()
    browser.close()
