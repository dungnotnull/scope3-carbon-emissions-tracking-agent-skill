#!/usr/bin/env python3
"""knowledge_updater.py - Scope 3 Carbon Emissions Tracking (idea 217).

Crawls GHG Protocol, SBTi, and emission-factor sources, extracts dated,
keyword-scored references, and appends deduplicated entries to
SECOND-KNOWLEDGE-BRAIN.md. Designed to run as a weekly self-update job.

Implementation notes:
- Pure standard library (urllib + html.parser) so it runs anywhere without
  optional deps; if the optional ``requests`` package is available it is used
  instead for richer timeout/redirect handling.
- Robust to network failures: every source is fetched with a timeout and a
  try/except so a single unreachable URL never aborts the run.
- Dedup by stable URL hash stored as an HTML comment marker in the brain file.
- A pluggable fetch backend makes it trivial to swap in crawl4ai for JS-heavy
  sites in production (see ``Backend``).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

BRAIN = Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"

SOURCES: dict[str, str] = {
    "ghg_protocol": "https://ghgprotocol.org/standards/scope-3-standard",
    "sbti": "https://sciencebasedtargets.org/resources",
    "defra": (
        "https://www.gov.uk/government/collections/"
        "government-conversion-factors-for-company-reporting"
    ),
    "epa": "https://www.epa.gov/climateleadership/ghg-emission-factors-hub",
    "cdp": "https://www.cdp.net/en/guidance",
    "ecoinvent": "https://ecoinvent.org/the-ecoinvent-database/",
    "exiobase": "https://www.exiobase.eu/",
}

KEYWORDS: list[str] = [
    "scope 3", "ghg protocol", "emission factor", "sbti", "carbon footprint",
    "value chain emissions", "abatement", "net zero", "spend-based",
    "activity-based", "1.5c", "science based", "eeio", "defra", "epa",
]

USER_AGENT = "scope3-carbon-tracking/1.0 (+knowledge-updater; python-urllib)"
TIMEOUT_SECONDS = 20


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class Entry:
    title: str
    url: str
    source: str
    year: int
    summary: str = ""
    retrieved: str = field(default_factory=lambda: date.today().isoformat())

    def to_line(self, url_hash: str) -> str:
        return (
            f"- {self.retrieved} - {self.title or '(untitled)'} "
            f"({self.source}, {self.year}) {self.url} <!--h:{url_hash}-->"
        )


# ---------------------------------------------------------------------------
# HTTP fetch backend (pluggable)
# ---------------------------------------------------------------------------
class Backend:
    """Minimal HTTP fetcher. Override ``fetch`` to use crawl4ai/requests."""

    def fetch(self, url: str, timeout: int = TIMEOUT_SECONDS) -> str | None:
        try:
            try:
                import requests  # type: ignore
            except ImportError:
                req = urllib.request.Request(
                    url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
                    charset = resp.headers.get_content_charset() or "utf-8"
                    return resp.read().decode(charset, errors="replace")
            else:
                r = requests.get(url, timeout=timeout,
                                 headers={"User-Agent": USER_AGENT}, allow_redirects=True)
                if r.ok:
                    return r.text
                return None
        except Exception as exc:  # network errors are non-fatal per-source
            print(f"[warn] {url} -> {exc}", file=sys.stderr)
            return None


# ---------------------------------------------------------------------------
# HTML link/title extractor
# ---------------------------------------------------------------------------
class _LinkExtractor(HTMLParser):
    """Collect (href, link_text) pairs and the page <title>."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.title: str = ""
        self._in_title = False
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True
        elif tag == "a":
            href = dict(attrs).get("href")
            if href:
                self._current_href = href
                self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._current_href is not None:
            text = re.sub(r"\s+", " ", "".join(self._current_text)).strip()
            if text:
                self.links.append((self._current_href, text))
            self._current_href = None
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_title and not self.title:
            self.title = re.sub(r"\s+", " ", data).strip()
        if self._current_href is not None:
            self._current_text.append(data)


def _absolute(base: str, href: str) -> str:
    return urllib.parse.urljoin(base, href)


def _infer_year(text: str) -> int:
    """Pull the most plausible 4-digit year (>=2010) from text, else today."""
    now = datetime.now(timezone.utc).year
    years = [int(y) for y in re.findall(r"\b(20[1-2]\d)\b", text)]
    return max(years) if years and max(years) <= now else now


# ---------------------------------------------------------------------------
# Entry construction
# ---------------------------------------------------------------------------
def _entries_from_page(source_name: str, base_url: str, html_text: str) -> list[Entry]:
    parser = _LinkExtractor()
    try:
        parser.feed(html_text)
    except Exception:
        pass
    page_title = html.unescape(parser.title or source_name)
    out: list[Entry] = []
    seen_urls: set[str] = set()
    for href, text in parser.links:
        full = _absolute(base_url, href)
        if not full.startswith(("http://", "https://")):
            continue
        # only keep topical links (skip nav/footer boilerplate) - heuristic by
        # requiring the link text or page title to mention a keyword or be long.
        lc = (text + " " + page_title).lower()
        topical = any(k in lc for k in KEYWORDS) or len(text) > 12
        if not topical:
            continue
        if full in seen_urls:
            continue
        seen_urls.add(full)
        out.append(
            Entry(
                title=html.unescape(text)[:200],
                url=full,
                source=source_name,
                year=_infer_year(text + " " + page_title),
                summary=page_title[:160],
            )
        )
    return out


def fetch_entries(backend: Backend | None = None) -> list[Entry]:
    """Fetch all configured SOURCES and return scored, keyword-relevant entries."""
    backend = backend or Backend()
    entries: list[Entry] = []
    for source_name, url in SOURCES.items():
        html_text = backend.fetch(url)
        if html_text:
            entries.extend(_entries_from_page(source_name, url, html_text))
    return entries


# ---------------------------------------------------------------------------
# Scoring & dedup
# ---------------------------------------------------------------------------
def score(e: Entry) -> float:
    t = (e.title + " " + e.summary).lower()
    keyword_hits = sum(k in t for k in KEYWORDS)
    recency = 1.0 if e.year >= date.today().year - 1 else 0.5
    return keyword_hits * recency


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]


def _existing_hashes(text: str) -> set[str]:
    return set(re.findall(r"<!--h:([0-9a-f]{12})-->", text))


# ---------------------------------------------------------------------------
# Brain append (dedup by URL hash)
# ---------------------------------------------------------------------------
def append_entries(entries: Iterable[Entry], brain: Path = BRAIN) -> int:
    if not brain.exists():
        print(f"[warn] brain file not found: {brain}", file=sys.stderr)
        return 0
    text = brain.read_text(encoding="utf-8")
    seen = _existing_hashes(text)
    lines: list[str] = []
    added = 0
    for e in sorted(entries, key=score, reverse=True):
        if not e.url:
            continue
        h = _url_hash(e.url)
        if h in seen:
            continue
        lines.append(e.to_line(h))
        seen.add(h)
        added += 1
    if added:
        # Append under a dated update-log section so the brain stays auditable.
        header = f"\n## Knowledge Update - {date.today().isoformat()}\n"
        block = header + "\n".join(lines) + "\n"
        brain.write_text(text.rstrip() + "\n" + block, encoding="utf-8")
    return added


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _cmd_run(args: argparse.Namespace) -> int:
    backend = Backend()
    if args.dry_run:
        entries = fetch_entries(backend)
        print(json.dumps(
            [e.__dict__ for e in sorted(entries, key=score, reverse=True)],
            indent=2, ensure_ascii=False,
        ))
        print(f"[dry-run] {len(entries)} candidate entries (not written).")
        return 0
    n = append_entries(fetch_entries(backend), BRAIN)
    print(f"[217] appended {n} entries to {BRAIN.name}")
    return 0


def _cmd_list_sources(_args: argparse.Namespace) -> int:
    for name, url in SOURCES.items():
        print(f"{name:14s} {url}")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="knowledge_updater",
        description="Crawl Scope 3 / SBTi / emission-factor sources and update the brain.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("run", help="Fetch sources and append deduplicated entries.")
    pr.add_argument("--dry-run", action="store_true", help="Print candidates without writing.")
    pr.set_defaults(func=_cmd_run)
    pl = sub.add_parser("sources", help="List configured source URLs.")
    pl.set_defaults(func=_cmd_list_sources)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
