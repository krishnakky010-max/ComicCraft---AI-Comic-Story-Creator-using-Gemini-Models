"""
image_generator.py - Generates distinct comic illustrations for each panel.
Combines fast AI text-to-image (Stable Diffusion / Flux) with dynamic multi-angle procedural comic composition.
Part of ComicCraft - AI Comic Story Creator using Gemini Models.
"""
import os
import re
import time
import math
import random
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PANELS_DIR = os.path.join(STATIC_DIR, "panels")
os.makedirs(PANELS_DIR, exist_ok=True)

_diffusers_pipe = None


def _sanitize_filename(prompt: str, max_length: int = 40) -> str:
    """Sanitizes an image prompt for filesystem-safe filename."""
    clean = re.sub(r'[^a-zA-Z0-9_\- ]', '', prompt).strip().lower()
    clean = re.sub(r'\s+', '_', clean)
    return clean[:max_length] or "comic_panel"


def _get_palette(art_style: str, panel_num: int):
    """Returns dynamic color palettes based on art style and dramatic panel arc."""
    style_lower = (art_style or "comic book").lower()

    # Panel-specific emotional lighting
    if panel_num == 1:  # Dawn / Exploration
        sky = [(25, 30, 70), (80, 50, 110), (220, 100, 80), (255, 190, 120)]
        accent = (255, 210, 80)
    elif panel_num == 2:  # Ominous / Shadowed / Tension
        sky = [(10, 15, 30), (20, 40, 55), (35, 70, 75), (50, 95, 85)]
        accent = (80, 255, 180)
    elif panel_num == 3:  # Cosmic Discovery / Glowing Relic
        sky = [(15, 10, 35), (45, 20, 70), (120, 40, 120), (200, 80, 160)]
        accent = (255, 240, 100)
    elif panel_num == 4:  # Climax / High-energy Combat
        sky = [(40, 10, 15), (140, 25, 30), (230, 80, 40), (255, 210, 60)]
        accent = (0, 230, 255)
    else:  # Panel 5: Golden Victory / Sunset
        sky = [(20, 25, 55), (90, 45, 95), (230, 110, 60), (255, 220, 130)]
        accent = (255, 235, 120)

    if "anime" in style_lower:
        accent = (255, 180, 220) if panel_num == 3 else accent
    elif "pixel" in style_lower:
        sky = [(c[0]//2, c[1]//2, c[2]//2) for c in sky]

    return sky, accent


def _draw_panel_1_arrival(draw, img, w, h, sky, accent, prompt):
    """Panel 1: Wide establishing landscape with winding path, character arriving on left."""
    # 1. Distant mountains
    pts = [(0, int(h * 0.65))]
    for x in range(0, w + 40, 30):
        mh = int(h * 0.5) + int(math.sin(x * 0.015) * 40 + math.cos(x * 0.03) * 20)
        pts.append((x, mh))
    pts.extend([(w, h), (0, h)])
    draw.polygon(pts, fill=(20, 25, 45, 220))

    # 2. Foreground terrain
    draw.polygon([(0, int(h * 0.7)), (w, int(h * 0.65)), (w, h), (0, h)], fill=(12, 15, 25, 255))

    # 3. Winding pathway vanishing into horizon
    path_pts = [
        (int(w * 0.15), h),
        (int(w * 0.35), h),
        (int(w * 0.55), int(h * 0.72)),
        (int(w * 0.5), int(h * 0.72))
    ]
    draw.polygon(path_pts, fill=(accent[0]//2, accent[1]//2, accent[2]//2, 150))

    # 4. Character on the left looking into the distance (Rule of Thirds)
    cx, cy = int(w * 0.22), int(h * 0.72)
    # Cloak / Torso
    draw.polygon([(cx - 15, cy - 80), (cx - 45, cy), (cx + 25, cy), (cx + 10, cy - 80)], fill=(10, 12, 20, 255))
    # Head looking right
    draw.ellipse([(cx - 10, cy - 105), (cx + 15, cy - 80)], fill=(10, 12, 20, 255))
    # Staff / Walking stick
    draw.line([(cx + 20, cy - 110), (cx + 28, cy)], fill=accent + (255,), width=4)

    # 5. Framing trees on edges
    draw.polygon([(0, 0), (70, 0), (35, int(h * 0.8)), (0, int(h * 0.8))], fill=(8, 10, 18, 255))
    draw.polygon([(w - 80, 0), (w, 0), (w, int(h * 0.7)), (w - 30, int(h * 0.7))], fill=(8, 10, 18, 255))


def _draw_panel_2_mystery(draw, img, w, h, sky, accent, prompt):
    """Panel 2: Deep foggy interior with glowing silhouettes / eyes peering from darkness."""
    # 1. Dark canopy / vertical silhouetted trees/pillars
    for tx in [60, 160, w - 180, w - 80, int(w * 0.45)]:
        tw = 35 + (tx % 20)
        draw.rectangle([(tx, 0), (tx + tw, h)], fill=(12, 14, 22, 255))
        # branches
        draw.line([(tx + 15, int(h * 0.3)), (tx - 50, int(h * 0.15))], fill=(12, 14, 22, 255), width=8)
        draw.line([(tx + 20, int(h * 0.4)), (tx + 80, int(h * 0.25))], fill=(12, 14, 22, 255), width=7)

    # 2. Glowing mysterious eyes / wisps in shadows
    random.seed(42)
    for _ in range(7):
        ex = random.randint(100, w - 100)
        ey = random.randint(int(h * 0.3), int(h * 0.65))
        draw.ellipse([(ex - 8, ey - 4), (ex - 2, ey + 4)], fill=accent + (230,))
        draw.ellipse([(ex + 4, ey - 4), (ex + 10, ey + 4)], fill=accent + (230,))

    # 3. Fog bands
    fog = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(fog)
    fdraw.ellipse([(w * 0.1, h * 0.55), (w * 0.9, h * 0.85)], fill=(30, 60, 70, 90))
    fog = fog.filter(ImageFilter.GaussianBlur(15))
    img.paste(Image.alpha_composite(img.convert("RGBA"), fog), (0, 0))
    draw = ImageDraw.Draw(img)

    # 4. Character in alert defensive crouch
    cx, cy = int(w * 0.5), int(h * 0.76)
    draw.polygon([(cx - 25, cy - 50), (cx - 40, cy), (cx + 35, cy), (cx + 20, cy - 50)], fill=(8, 10, 16, 255))
    draw.ellipse([(cx - 12, cy - 72), (cx + 12, cy - 50)], fill=(8, 10, 16, 255))
    # Glowing protective aura / weapon ready
    draw.line([(cx + 15, cy - 40), (cx + 45, cy - 65)], fill=accent + (255,), width=4)


def _draw_panel_3_discovery(draw, img, w, h, sky, accent, prompt):
    """Panel 3: Close-up low angle on central glowing relic / artifact with radiant light beams."""
    # 1. Altar / Pedestal in center
    ax, ay = int(w * 0.5), int(h * 0.72)
    draw.polygon([(ax - 90, h), (ax + 90, h), (ax + 60, ay), (ax - 60, ay)], fill=(15, 18, 30, 255))
    draw.rectangle([(ax - 70, ay - 12), (ax + 70, ay)], fill=(25, 30, 48, 255), outline=accent + (200,), width=2)

    # 2. Radiant Light Rays from Relic
    rx, ry = ax, ay - 45
    rays_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(rays_layer)
    for i in range(16):
        ang1 = (math.pi * 2 / 16) * i
        ang2 = ang1 + 0.18
        p1 = (rx + math.cos(ang1) * 700, ry + math.sin(ang1) * 700)
        p2 = (rx + math.cos(ang2) * 700, ry + math.sin(ang2) * 700)
        rdraw.polygon([(rx, ry), p1, p2], fill=accent + (45,))

    # Glowing aura
    rdraw.ellipse([(rx - 65, ry - 65), (rx + 65, ry + 65)], fill=accent + (160,))
    rdraw.ellipse([(rx - 30, ry - 30), (rx + 30, ry + 30)], fill=(255, 255, 255, 230))
    rays_layer = rays_layer.filter(ImageFilter.GaussianBlur(8))
    img.paste(Image.alpha_composite(img.convert("RGBA"), rays_layer), (0, 0))
    draw = ImageDraw.Draw(img)

    # 3. Crystal / Relic diamond
    draw.polygon([(rx, ry - 28), (rx + 20, ry), (rx, ry + 28), (rx - 20, ry)], fill=(255, 255, 255, 255), outline=accent, width=2)

    # 4. Character reaching out in awe from side
    cx, cy = int(w * 0.22), int(h * 0.8)
    draw.polygon([(cx - 20, cy - 90), (cx - 40, cy), (cx + 25, cy), (cx + 10, cy - 90)], fill=(10, 12, 20, 255))
    draw.ellipse([(cx - 8, cy - 115), (cx + 18, cy - 90)], fill=(10, 12, 20, 255))
    # Arm outstretched toward relic
    draw.line([(cx + 12, cy - 80), (rx - 35, ry + 15)], fill=(10, 12, 20, 255), width=8)


def _draw_panel_4_action(draw, img, w, h, sky, accent, prompt):
    """Panel 4: High-energy action clash, dynamic diagonal speedlines, leap & combat blast."""
    # 1. Comic Action Diagonal Speedlines
    cx, cy = int(w * 0.65), int(h * 0.4)
    lines_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(lines_layer)
    for i in range(45):
        ang = (math.pi * 2 / 45) * i
        lx = cx + math.cos(ang) * 900
        ly = cy + math.sin(ang) * 900
        thick = 2 if i % 2 == 0 else 6
        ldraw.line([(cx, cy), (lx, ly)], fill=(255, 255, 255, 75), width=thick)

    # 2. Explosive Impact Starburst
    star_pts = []
    points = 18
    for i in range(points * 2):
        r = 130 if i % 2 == 0 else 55
        ang = (math.pi / points) * i
        star_pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    ldraw.polygon(star_pts, fill=(255, 240, 50, 230), outline=(255, 70, 40, 255))

    lines_layer = lines_layer.filter(ImageFilter.GaussianBlur(2))
    img.paste(Image.alpha_composite(img.convert("RGBA"), lines_layer), (0, 0))
    draw = ImageDraw.Draw(img)

    # 3. Dynamic Leaping Character Striking across diagonally
    char_x, char_y = int(w * 0.35), int(h * 0.52)
    # Airborne torso & dynamic trailing cape
    draw.polygon([
        (char_x - 55, char_y + 40),
        (char_x - 110, char_y + 80),
        (char_x - 40, char_y - 20),
        (char_x + 20, char_y - 30)
    ], fill=(220, 30, 40, 255))
    # Torso angled forward
    draw.polygon([
        (char_x - 15, char_y - 40),
        (char_x + 25, char_y - 45),
        (char_x + 10, char_y + 15),
        (char_x - 20, char_y + 20)
    ], fill=(10, 12, 20, 255))
    draw.ellipse([(char_x + 15, char_y - 65), (char_x + 40, char_y - 40)], fill=(10, 12, 20, 255))
    # Striking sword / blast pointing straight into the impact point
    draw.line([(char_x + 25, char_y - 40), (cx - 10, cy + 5)], fill=(255, 255, 255, 255), width=6)
    draw.line([(char_x + 25, char_y - 40), (cx - 10, cy + 5)], fill=accent, width=3)


def _draw_panel_5_triumph(draw, img, w, h, sky, accent, prompt):
    """Panel 5: Panoramic victory summit shot, golden sunset, heroic pose overlooking land."""
    # 1. Grand mountain peak silhouette
    peak_x = int(w * 0.55)
    summit_pts = [
        (0, h),
        (int(w * 0.25), int(h * 0.75)),
        (peak_x, int(h * 0.52)),
        (int(w * 0.78), int(h * 0.7)),
        (w, int(h * 0.85)),
        (w, h)
    ]
    draw.polygon(summit_pts, fill=(15, 18, 32, 255))

    # 2. Glowing golden setting sun on the horizon
    sun_x, sun_y = int(w * 0.28), int(h * 0.38)
    sun_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sun_layer)
    sdraw.ellipse([(sun_x - 80, sun_y - 80), (sun_x + 80, sun_y + 80)], fill=(255, 220, 120, 210))
    sdraw.ellipse([(sun_x - 45, sun_y - 45), (sun_x + 45, sun_y + 45)], fill=(255, 255, 240, 255))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(10))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sun_layer), (0, 0))
    draw = ImageDraw.Draw(img)

    # 3. Flocks of distant birds / soaring creatures
    birds = [(sun_x + 90, sun_y - 60), (sun_x + 130, sun_y - 80), (sun_x + 160, sun_y - 50)]
    for bx, by in birds:
        draw.arc([(bx - 12, by - 6), (bx, by + 6)], 180, 360, fill=(30, 25, 45, 230), width=2)
        draw.arc([(bx, by - 6), (bx + 12, by + 6)], 180, 360, fill=(30, 25, 45, 230), width=2)

    # 4. Victorious Character standing on the peak, cape flowing in the wind
    cx, cy = peak_x, int(h * 0.52)
    # Billowing cape
    draw.polygon([(cx - 10, cy - 70), (cx - 75, cy - 40), (cx - 50, cy - 10), (cx, cy - 10)], fill=(200, 50, 50, 255))
    # Hero standing tall
    draw.polygon([(cx - 12, cy - 70), (cx + 12, cy - 70), (cx + 8, cy), (cx - 8, cy)], fill=(8, 10, 18, 255))
    draw.ellipse([(cx - 10, cy - 95), (cx + 10, cy - 70)], fill=(8, 10, 18, 255))
    # Raised fist / weapon held high in triumph
    draw.line([(cx + 8, cy - 65), (cx + 25, cy - 110)], fill=accent + (255,), width=4)
    draw.ellipse([(cx + 20, cy - 116), (cx + 30, cy - 104)], fill=(255, 255, 255, 255))


def _render_stylized_comic_art(prompt: str, art_style: str, panel_num: int, output_path: str):
    """
    Renders a completely unique comic panel illustration with distinct camera angles,
    scene framing, color palettes, and character poses for each of the 5 panels.
    """
    w, h = 768, 512
    sky_colors, accent = _get_palette(art_style, panel_num)

    # 1. Base Gradient Sky
    img = Image.new("RGBA", (w, h), sky_colors[0] + (255,))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / h
        if t < 0.33:
            local_t = t / 0.33
            c1, c2 = sky_colors[0], sky_colors[1]
        elif t < 0.66:
            local_t = (t - 0.33) / 0.33
            c1, c2 = sky_colors[1], sky_colors[2]
        else:
            local_t = (t - 0.66) / 0.34
            c1, c2 = sky_colors[2], sky_colors[3]

        r = int(c1[0] + (c2[0] - c1[0]) * local_t)
        g = int(c1[1] + (c2[1] - c1[1]) * local_t)
        b = int(c1[2] + (c2[2] - c1[2]) * local_t)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # 2. Render Panel Archetype based on panel_num
    if panel_num == 1:
        _draw_panel_1_arrival(draw, img, w, h, sky_colors, accent, prompt)
    elif panel_num == 2:
        _draw_panel_2_mystery(draw, img, w, h, sky_colors, accent, prompt)
    elif panel_num == 3:
        _draw_panel_3_discovery(draw, img, w, h, sky_colors, accent, prompt)
    elif panel_num == 4:
        _draw_panel_4_action(draw, img, w, h, sky_colors, accent, prompt)
    else:
        _draw_panel_5_triumph(draw, img, w, h, sky_colors, accent, prompt)

    draw = ImageDraw.Draw(img)

    # 3. Dynamic Halftone Dots layer (accentuated comic print effect)
    halftone_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(halftone_layer)
    grid = 18
    for gx in range(15, w, grid):
        for gy in range(15, h, grid):
            dot_rad = max(1, int(3 * (gy / h)))
            if (gx + gy) % 36 == 0:
                hdraw.ellipse([(gx - dot_rad, gy - dot_rad), (gx + dot_rad, gy + dot_rad)], fill=(255, 255, 255, 25))
    img = Image.alpha_composite(img, halftone_layer)
    draw = ImageDraw.Draw(img)

    # 4. Comic Panel Number Badge (Top-Left)
    draw.rectangle([(20, 20), (140, 56)], fill=(255, 220, 0, 245), outline=(0, 0, 0, 255), width=3)
    draw.text((32, 28), f"PANEL {panel_num}", fill=(10, 10, 10, 255))

    # 5. Art Style Badge (Top-Right)
    draw.rectangle([(w - 160, 20), (w - 20, 56)], fill=(15, 20, 35, 230), outline=(255, 220, 0, 255), width=2)
    draw.text((w - 150, 28), art_style[:14].upper(), fill=(255, 255, 255, 255))

    # 6. Comic Book Outer Border
    border_thick = 8
    draw.rectangle([(0, 0), (w - 1, h - 1)], outline=(10, 10, 15, 255), width=border_thick)
    draw.rectangle([(border_thick + 2, border_thick + 2), (w - border_thick - 3, h - border_thick - 3)],
                   outline=(255, 255, 255, 120), width=1)

    # Save finalized image
    img = img.convert("RGB")
    img.save(output_path, "PNG", quality=95)


def _try_ai_image_generation(prompt: str, art_style: str, panel_num: int, output_path: str) -> bool:
    """
    Attempts fast, real AI image generation via Pollinations AI (running Stable Diffusion / Flux)
    with a short timeout so user experience stays fast. Returns True on success, False on fallback.
    """
    try:
        # Create an enriched comic-style prompt
        enhanced_prompt = f"{prompt}, {art_style} comic illustration, vivid graphic novel artwork, cinematic lighting, sharp ink outlines, panel {panel_num}"
        encoded_prompt = requests.utils.quote(enhanced_prompt)
        # Using 5 second timeout to prevent stalling
        seed = int(time.time()) % 100000 + panel_num * 53
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=512&seed={seed}&nologo=true"
        
        response = requests.get(url, timeout=6)
        if response.status_code == 200 and len(response.content) > 10000:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"[AI Generator] Successfully fetched online AI illustration for panel {panel_num} ({len(response.content)} bytes)")
            return True
    except Exception as e:
        # Network slow, timeout, or offline - quickly fallback
        pass
    return False


def generate_image(prompt: str, art_style: str = "comic book", panel_num: int = 1) -> str:
    """
    Generates a unique comic-style illustration for the given panel.
    1. If USE_DIFFUSERS=1 and GPU available, uses local Stable Diffusion pipeline.
    2. Tries fast online AI text-to-image with strict timeout.
    3. Falls back to distinct 5-panel procedural comic artist composition.
    Returns relative web path (e.g. '/static/panels/...').
    """
    slug = _sanitize_filename(prompt, max_length=24)
    timestamp = int(time.time() * 1000)
    filename = f"panel_{panel_num}_{timestamp}_{slug}.png"
    filepath = os.path.join(PANELS_DIR, filename)

    # 1. Local Diffusers Pipeline (if explicitly configured)
    use_diffusers = os.getenv("USE_DIFFUSERS", "0").strip() == "1"
    if use_diffusers:
        try:
            import torch
            from diffusers import StableDiffusionPipeline

            global _diffusers_pipe
            if _diffusers_pipe is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model_id = "runwayml/stable-diffusion-v1-5"
                _diffusers_pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32
                )
                _diffusers_pipe.to(device)

            result = _diffusers_pipe(
                prompt=f"{prompt}, {art_style} style, comic panel",
                num_inference_steps=20
            )
            result.images[0].save(filepath)
            return f"/static/panels/{filename}"
        except Exception as e:
            print(f"[Diffusers] Pipeline bypassed: {e}")

    # 2. Fast AI image generation
    if _try_ai_image_generation(prompt, art_style, panel_num, filepath):
        return f"/static/panels/{filename}"

    # 3. High-quality distinct 5-panel composition renderer
    _render_stylized_comic_art(prompt, art_style, panel_num, filepath)
    print(f"[Image Generator] Rendered distinct panel {panel_num} layout to {filepath}")
    return f"/static/panels/{filename}"


if __name__ == "__main__":
    for p in range(1, 6):
        path = generate_image(f"Scene for panel {p}", "Comic Book", p)
        print(f"Generated panel {p} -> {path}")
