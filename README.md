# opds-MIA — OPDS Catalog for the Marxists Internet Archive

An [OPDS](https://opds-spec.org/) (Open Publication Distribution System) catalog for the free ebooks hosted at [marxists.org/ebooks](https://www.marxists.org/ebooks/). It scrapes all `epub`/`pdf` links, groups them by author, and generates a static navigable catalog you can add directly to any OPDS-compatible reader.

**Hosted catalog (GitHub Pages):**

```
https://salimsalimbelkacem.github.io/opds-MIA/index.xml
```

No installation required — just add the URL above to your reader.

Rebuilt automatically every Monday at 06:00 UTC and on every push to `main` via GitHub Actions. Last build included **~418 files** across **69 authors** (e.g. Marx, Lenin, Luxemburg, Trotsky, Gramsci, etc.).

## What you get

- `index.xml` — navigation feed listing all authors (69 entries)
- `{author}.xml` — acquisition feed per author (e.g. `marx.xml`, `lenin.xml`, `luxemburg.xml`) with open-access download links for each format (`application/epub+zip`, `application/pdf`)
- Absolute URLs when deployed (`https://salimsalimbelkacem.github.io/opds-MIA/{author}.xml`), relative for local builds
- Each work groups `epub` + `pdf` under one entry with `rel="http://opds-spec.org/acquisition/open-access"` links and a `rel="via"` back to marxists.org

## How to use

### Generic (any OPDS client)

1. Copy the catalog URL:
   `https://salimsalimbelkacem.github.io/opds-MIA/index.xml`
2. In your reader, find **Add Catalog / Add OPDS / Network Library / OPDS Catalog**.
3. Paste the URL as catalog URL, title it e.g. `MIA` or `marxists.org`.
4. Browse `MIA → Author → Work → Download epub/pdf`.

### App-specific

**Librera Reader (Android) — recommended**
1. `Library` → `⋮` → `Add Catalog` / `Network` → `Add Catalog`
2. Name: `MIA`, URL: `https://salimsalimbelkacem.github.io/opds-MIA/index.xml`
3. Open the new catalog, browse by author, tap a title → choose `epub` or `pdf` to download/open.

**KOReader (Android / Kobo / Kindle)**
1. `Menu` → `Search` → `OPDS catalog` (or `File browser` → `Add new OPDS catalog` depending on version)
2. Add `https://salimsalimbelkacem.github.io/opds-MIA/index.xml`
3. Browse and long-press a format link to download.

**Moon+ Reader (Android)**
1. `My Shelf` → `⋮` → `OPDS Catalog` / `Net Library`
2. `+` → paste `https://salimsalimbelkacem.github.io/opds-MIA/index.xml`
3. Browse → download.

**Thorium Reader (Windows / macOS / Linux)**
1. `File` → `Add OPDS feed` / `OPDS Catalogs` → `Add feed`
2. Paste the URL, open the feed, download epub.

**Calibre**
1. *Calibre itself is not an OPDS client*, but you can use the [Calibre OPDS plugins](https://manual.calibre-ebook.com/) or fetch via a reader. Alternatively download directly: open the catalog URL in a browser, navigate to an author feed, click the `href` for the desired format.

> Tip: If your app asks for OPDS version, choose **OPDS 1.2 / Atom** (this catalog is `profile=opds-catalog;kind=navigation` + `kind=acquisition`). Authentication is not required.

### Troubleshooting

- **404 on `bordiga.xml` / author feed:** ensure you use the full `index.xml` URL with `/opds-MIA/` prefix, not `https://salimsalimbelkacem.github.io/bordiga.xml`. The catalog now serves absolute URLs (fixed in `generate.py:131`).
- **Empty catalog:** GitHub Pages needs `Settings → Pages → Source: GitHub Actions` enabled. Builds run weekly; trigger manually via `Actions → Build and Deploy OPDS → Run workflow`.
- **Reader shows no downloads:** some readers hide `open-access` links behind a details page — tap the title to reveal `epub`/`pdf`.

## Local development

```bash
git clone https://github.com/salimsalimbelkacem/opds-MIA.git
cd opds-MIA
pip install -r requirements.txt  # requests, beautifulsoup4
python generate.py               # -> ./opds/index.xml + ./{author}.xml

# For Pages-like absolute URLs:
BASE_URL="https://salimsalimbelkacem.github.io/opds-MIA" python generate.py
```

- `scraper.py:5` — `get_all_ebooks_links()` + `get_processed_ebooks_links()` scrape `https://www.marxists.org/ebooks/`
- `generate.py:99` — `generate_catalog()` groups by author, writes root navigation feed
- `generate.py:28` — `generate_opds_feed()` writes per-author acquisition feeds
- Output: `./opds/` (gitignored, deployed as Pages artifact via `actions/upload-pages-artifact@v3`)

## Automation

`.github/workflows/pages.yml`:
- `push` to `main`, `workflow_dispatch`, weekly `cron: "0 6 * * 1"` (Monday 06:00 UTC)
- `setup-python@v5` (3.11, `cache: pip` via `requirements.txt`), `configure-pages@v5` → `BASE_URL`, `generate.py`, `upload-pages-artifact` (`./opds`), `deploy-pages@v4`

## Credits

- Source ebooks: [Marxists Internet Archive](https://www.marxists.org/) — all texts are free / public domain or used with permission per MIA licensing.
- OPDS spec: https://opds-spec.org/ / https://specs.opds.io/

## License

No additional restrictions on the catalog itself; ebook files retain their original MIA licenses.
