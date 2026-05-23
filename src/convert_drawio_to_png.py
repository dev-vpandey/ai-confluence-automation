#!/usr/bin/env python3
"""
Convert Draw.io (.drawio) files to PNG
Uses a simple approach: load diagram in viewer mode and capture the SVG/canvas
"""

import sys
import time
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

def convert_drawio_to_png(drawio_path, png_path=None):
    """
    Convert a .drawio file to PNG using diagrams.net viewer

    Args:
        drawio_path: Path to .drawio file
        png_path: Output PNG path (default: same name as drawio)
    """
    drawio_path = Path(drawio_path).absolute()

    if not drawio_path.exists():
        print(f"❌ File not found: {drawio_path}")
        return False

    if png_path is None:
        png_path = drawio_path.with_suffix('.png')
    else:
        png_path = Path(png_path)

    print(f"Converting: {drawio_path.name}")
    print(f"Output: {png_path.name}")

    # Read and encode the diagram content
    with open(drawio_path, 'rb') as f:
        diagram_bytes = f.read()

    diagram_b64 = base64.b64encode(diagram_bytes).decode('utf-8')

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Use diagrams.net with embedded data
        print("Loading diagram in viewer...")
        viewer_url = f"https://viewer.diagrams.net/?lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=#R{diagram_b64}"

        page.goto(viewer_url, wait_until='networkidle', timeout=60000)

        # Wait for diagram to render
        time.sleep(5)

        # Find the diagram container and take screenshot
        print("Capturing diagram...")
        try:
            # Try to find the SVG container
            svg_container = page.locator('div.geEditor svg').first
            svg_container.wait_for(timeout=10000)

            # Get bounding box and screenshot just that area
            box = svg_container.bounding_box()
            if box:
                page.screenshot(
                    path=str(png_path),
                    clip={
                        'x': max(0, box['x'] - 10),
                        'y': max(0, box['y'] - 10),
                        'width': box['width'] + 20,
                        'height': box['height'] + 20
                    }
                )
            else:
                # Fallback to full diagram container
                page.screenshot(path=str(png_path), full_page=False)

        except Exception as e:
            print(f"Note: Using fallback capture method ({e})")
            # Try alternative selectors
            try:
                container = page.locator('div.geDiagramContainer').first
                container.screenshot(path=str(png_path))
            except:
                # Last resort: full page
                page.screenshot(path=str(png_path), full_page=True)

        browser.close()

    if png_path.exists():
        file_size_kb = png_path.stat().st_size / 1024

        # Check if file is too small (likely blank/error)
        if file_size_kb < 5:
            print(f"\n⚠️  Warning: Output file is very small ({file_size_kb:.1f} KB)")
            print(f"   The diagram may not have rendered correctly")
            return False

        print(f"\n✅ SUCCESS!")
        print(f"   {png_path.name} ({file_size_kb:.1f} KB)")
        return True
    else:
        print(f"\n❌ Failed to create: {png_path}")
        return False

def batch_convert(directory="."):
    """Convert all .drawio files in a directory to PNG"""
    directory = Path(directory)
    drawio_files = list(directory.glob("*.drawio"))

    if not drawio_files:
        print(f"No .drawio files found in {directory}")
        return

    print(f"Found {len(drawio_files)} diagram(s) to convert:\n")

    success_count = 0
    for drawio_file in drawio_files:
        try:
            if convert_drawio_to_png(drawio_file):
                success_count += 1
            print()
        except Exception as e:
            print(f"❌ Error converting {drawio_file.name}: {e}\n")

    print(f"\n{'='*60}")
    print(f"Converted {success_count}/{len(drawio_files)} diagrams successfully")
    print(f"{'='*60}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_drawio_to_png.py DRAWIO_FILE [OUTPUT_PNG]")
        print("       python convert_drawio_to_png.py --batch [DIRECTORY]")
        print("\nExamples:")
        print("  python convert_drawio_to_png.py architecture.drawio")
        print("  python convert_drawio_to_png.py architecture.drawio output.png")
        print("  python convert_drawio_to_png.py --batch")
        print("  python convert_drawio_to_png.py --batch /path/to/diagrams/")
        sys.exit(1)

    if sys.argv[1] == '--batch':
        directory = sys.argv[2] if len(sys.argv) > 2 else "."
        batch_convert(directory)
    else:
        drawio_file = sys.argv[1]
        png_file = sys.argv[2] if len(sys.argv) > 2 else None

        success = convert_drawio_to_png(drawio_file, png_file)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
