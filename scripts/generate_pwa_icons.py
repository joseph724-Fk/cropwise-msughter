from pathlib import Path
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "static" / "icons"

SOURCE = ICON_DIR / "cropwise-icon.svg"

sizes = [72, 96, 128, 144, 152, 192, 384, 512]

for size in sizes:
    output = ICON_DIR / f"cropwise-icon-{size}.png"
    cairosvg.svg2png(
        url=str(SOURCE),
        write_to=str(output),
        output_width=size,
        output_height=size,
    )
    print(f"Generated {output}")

print("Done generating PWA icons.")