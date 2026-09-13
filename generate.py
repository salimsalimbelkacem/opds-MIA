import os
import html
from datetime import datetime, timezone
from urllib.parse import quote
from scraper import get_processed_ebooks_links

# OPDS namespaces
ATOM_NS = "http://www.w3.org/2005/Atom"
OPDS_NS = "http://opds-spec.org/2010/catalog"

def xml_escape(text: str) -> str:
    """Escape XML special characters."""
    return html.escape(str(text), quote=True)

def slugify(text: str) -> str:
    """Convert author/title to safe filename."""
    return "".join(c for c in text.lower().replace(" ", "-") if c.isalnum() or c == "-").strip("-")

def get_mime(format_ext: str) -> str:
    """Map file extension to MIME type."""
    return {
        "epub": "application/epub+zip",
        "pdf": "application/pdf",
        "mobi": "application/x-mobipocket-ebook",
        "azw3": "application/vnd.amazon.ebook"
    }.get(format_ext.lower(), "application/octet-stream")

def generate_opds_feed(books: list[dict], feed_title: str, feed_id: str, output_path: str, base_url: str):
    """Generate a single OPDS acquisition feed."""
    
    # Group books by title to combine formats (epub+pdf in one entry)
    works = {}
    for book in books:
        title = book["title"]
        if title not in works:
            works[title] = {
                "title": title,
                "author": book.get("author", "Unknown"),
                "formats": []
            }
        works[title]["formats"].append(book)
    
    # Build self href: absolute when base_url is set, relative otherwise
    basename = quote(os.path.basename(output_path))
    if base_url:
        self_href = f"{xml_escape(base_url.rstrip('/'))}/{basename}"
    else:
        self_href = basename
    # Build XML
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="{ATOM_NS}" xmlns:opds="{OPDS_NS}">
  <title>{xml_escape(feed_title)}</title>
  <id>urn:marxists:{xml_escape(feed_id)}</id>
  <updated>{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
  <link rel="self" type="application/atom+xml;profile=opds-catalog;kind=acquisition" href="{self_href}"/>
'''
    
    for title, work in works.items():
        work_id = slugify(title)
        author = work["author"]
        
        xml += f'''
  <entry>
    <title>{xml_escape(title)}</title>
    <id>urn:marxists:works:{xml_escape(work_id)}</id>
    <updated>{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
    <author>
      <name>{xml_escape(author)}</name>
    </author>
'''
        
        # Add acquisition links for each format
        for fmt in work["formats"]:
            mime = get_mime(fmt["format"])
            url = fmt["link"]
            xml += f'''    <link rel="http://opds-spec.org/acquisition/open-access" type="{mime}" href="{xml_escape(url)}"/>
'''
        
        # Add source link back to marxists.org (optional, but good practice)
        # Extract base marxists URL from first format
        if work["formats"]:
            source_url = work["formats"][0]["link"].rsplit("/", 1)[0] + "/"
            xml += f'''    <link rel="via" type="text/html" href="{xml_escape(source_url)}"/>
'''
        
        xml += '''  </entry>
'''
    
    xml += '''</feed>
'''
    
    # Write file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml)
    
    print(f"Generated: {output_path} ({len(works)} works)")

def generate_catalog(processed_links: list[dict], output_dir: str = "./opds", base_url: str = ""):
    """
    Generate complete OPDS catalog:
    - Root index (list of authors)
    - Individual author feeds
    """
    
    # Group by author
    authors = {}
    for book in processed_links:
        author = book.get("author", "Unknown")
        if author not in authors:
            authors[author] = []
        authors[author].append(book)
    
    # Generate root index
    if base_url:
        root_self_href = f"{xml_escape(base_url.rstrip('/'))}/index.xml"
    else:
        root_self_href = "index.xml"
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="{ATOM_NS}" xmlns:opds="{OPDS_NS}">
  <title>Marxists.org eBook Catalog</title>
  <id>urn:marxists:catalog:root</id>
  <updated>{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
  <link rel="self" type="application/atom+xml;profile=opds-catalog;kind=navigation" href="{root_self_href}"/>
'''
    
    for author in sorted(authors.keys()):
        author_slug = slugify(author)
        count = len(authors[author])
        if base_url:
            author_href = f"{xml_escape(base_url.rstrip('/'))}/{quote(author_slug)}.xml"
        else:
            author_href = f"{quote(author_slug)}.xml"
        xml += f'''
  <entry>
    <title>{xml_escape(author.title())}</title>
    <id>urn:marxists:authors:{xml_escape(author_slug)}</id>
    <updated>{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
    <link type="application/atom+xml;profile=opds-catalog;kind=acquisition" href="{author_href}"/>
    <content type="text">{count} works</content>
  </entry>
'''
    
    xml += '''</feed>
'''
    
    # Write root index
    os.makedirs(output_dir, exist_ok=True)
    index_path = os.path.join(output_dir, "index.xml")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Generated root index: {index_path}")
    
    # Generate individual author feeds
    for author, books in authors.items():
        author_slug = slugify(author)
        author_path = os.path.join(output_dir, f"{author_slug}.xml")
        generate_opds_feed(
            books=books,
            feed_title=f"Works by {author.title()}",
            feed_id=f"authors:{author_slug}",
            output_path=author_path,
            base_url=base_url
        )

if __name__ == "__main__":
    print("Fetching links from marxists.org...")
    links = get_processed_ebooks_links()
    print(f"Found {len(links)} format links")
    
    # Generate catalog
    # base_url can be set via BASE_URL env var for deployment (e.g. GitHub Pages)
    # e.g. BASE_URL=https://yourusername.github.io/marxists-opds
    base_url = os.environ.get("BASE_URL", "")
    if base_url:
        print(f"Using base_url: {base_url}")
    generate_catalog(links, output_dir="./opds", base_url=base_url)
    
    print(f"\nDone! Upload the './opds' folder to your static host.")
    print("In Librera: Network → Add Catalog → URL: https://yourdomain.com/opds/index.xml")
