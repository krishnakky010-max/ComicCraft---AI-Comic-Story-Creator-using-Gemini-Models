"""
test_pipeline.py - Verifies the full ComicCraft generation pipeline end-to-end.
"""
import os
import sys

from gemini_flash import generate_outline
from gemini_pro import generate_story
from image_generator import generate_image
from layout_builder import build_comic_layout
from exporters import save_pdf

def test_full_flow():
    print("[1/5] Testing Gemini Flash Outline Generation...")
    outline = generate_outline(
        prompt="A brave fox exploring an enchanted forest",
        character_name="Finn",
        setting="Enchanted Forest",
        tone="Dramatic",
        art_style="Comic Book"
    )
    assert len(outline) == 5, f"Expected 5 panels, got {len(outline)}"
    print(f"  -> Generated {len(outline)} panels outline.")

    print("[2/5] Testing Gemini Pro Story & Dialogue Generation...")
    story = generate_story(
        outline=outline,
        character_name="Finn",
        setting="Enchanted Forest",
        tone="Dramatic"
    )
    assert len(story) >= 1, "Expected story narration"
    print(f"  -> Generated {len(story)} story panels.")

    print("[3/5] Testing Illustration Generation for 5 panels...")
    image_paths = []
    for i, p in enumerate(outline):
        path = generate_image(p["image_prompt"], art_style="Comic Book", panel_num=i+1)
        image_paths.append(path)
        print(f"  -> Panel {i+1} image created: {path}")

    print("[4/5] Testing Layout Binding...")
    layout = build_comic_layout(outline, story, image_paths)
    assert len(layout) == 5, f"Expected 5 layout items, got {len(layout)}"
    print(f"  -> Layout successfully bound with {len(layout)} panels.")

    print("[5/5] Testing PDF Compilation & Export...")
    pdf_path = save_pdf(layout, comic_title="Finn's Enchanted Adventure")
    print(f"  -> PDF generated: {pdf_path}")

    # Check that PDF exists on disk
    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_pdf = os.path.join(base_dir, pdf_path.lstrip("/").replace("/", os.sep))
    assert os.path.exists(local_pdf), f"PDF file does not exist at {local_pdf}"
    print(f"  -> PDF Verified on disk! Size: {os.path.getsize(local_pdf)} bytes")

    print("\nALL 5 PIPELINE STEPS PASSED SUCCESSFULLY! COMICCRAFT CORE IS 100% OPERATIONAL!")

if __name__ == "__main__":
    test_full_flow()
