"""
gemini_flash.py - Generates structured 5-panel comic outline using Gemini Flash.
Part of ComicCraft - AI Comic Story Creator using Gemini Models.
"""
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Check for Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def _get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai
    except Exception as e:
        print(f"Warning: Could not configure google.generativeai: {e}")
        return None


def _fallback_outline(prompt: str, character_name: str, setting: str, tone: str, art_style: str) -> list:
    """High-quality procedural fallback when Gemini API key is not yet set or offline."""
    char = character_name.strip() if character_name else "The Protagonist"
    loc = setting.strip() if setting else "an uncharted realm"
    t = tone.strip() if tone else "adventurous"
    style = art_style.strip() if art_style else "comic book"

    return [
        {
            "panel_number": 1,
            "title": f"Panel 1: The Journey Begins in {loc.title()}",
            "scene_description": f"The story opens as {char} surveys the breathtaking horizon of {loc}, preparing for the unexpected trial ahead.",
            "image_prompt": f"{style} style: {char} standing at the threshold of {loc}, looking forward with determination, dramatic cinematic lighting, wide establishing shot, high detail comic art."
        },
        {
            "panel_number": 2,
            "title": f"Panel 2: Whispers in the Shadows",
            "scene_description": f"Deep within {loc}, an enigmatic presence reveals itself. The atmosphere turns intensely {t} as {char} senses a looming challenge.",
            "image_prompt": f"{style} style: {char} in {loc} looking warily at glowing mysterious silhouettes emerging from the shadows, medium shot, atmospheric shadows, {t} mood."
        },
        {
            "panel_number": 3,
            "title": "Panel 3: The Turning Point",
            "scene_description": f"{char} confronts the mystery head-on, uncovering a hidden artifact that pulses with strange energy.",
            "image_prompt": f"{style} style: {char} discovering a radiant glowing relic in {loc}, light reflecting on their face, dynamic perspective, vibrant colors, comic panel artwork."
        },
        {
            "panel_number": 4,
            "title": "Panel 4: Clash of Resolve",
            "scene_description": f"A pulse of mystical force erupts! {char} takes a bold, decisive stand against the shifting forces of {loc}.",
            "image_prompt": f"{style} style: dynamic action shot of {char} unleashing power or leaping across terrain in {loc}, motion lines, intense expression, vivid comic book coloring."
        },
        {
            "panel_number": 5,
            "title": "Panel 5: Dawn of a New Legend",
            "scene_description": f"With the trial overcome, {char} stands triumphant as the first light breaks through {loc}, heralding a new destiny.",
            "image_prompt": f"{style} style: {char} smiling triumphantly in {loc} at sunrise, heroic pose, warm golden hour rays, beautiful comic cover quality finish."
        }
    ]


def generate_outline(prompt: str, character_name: str = "Hero", setting: str = "Forest", tone: str = "Dramatic", art_style: str = "Comic Book") -> list:
    """
    Uses Gemini Flash (gemini-1.5-flash) to generate a structured 5-panel comic outline.
    Returns a list of 5 dictionaries containing panel_number, title, scene_description, image_prompt.
    """
    genai = _get_gemini_client()

    if not genai:
        print("[Gemini Flash] No GEMINI_API_KEY detected. Using intelligent built-in outline generator.")
        return _fallback_outline(prompt, character_name, setting, tone, art_style)

    system_instruction = (
        "You are an expert comic book creator and storyboard artist. "
        "Generate a structured 5-panel comic strip outline based on the user's premise. "
        "Return ONLY valid JSON format containing a list of 5 panel objects. "
        "Each object must have these exact keys:\n"
        "- panel_number: integer (1 to 5)\n"
        "- title: short catchy panel title (e.g., 'Panel 1: The Whispering Woods')\n"
        "- scene_description: 1-2 sentences describing the physical setting and action\n"
        "- image_prompt: a vivid text-to-image prompt suitable for Stable Diffusion, specifying the character appearance, action, art style, and lighting."
    )

    user_message = f"""
Create a 5-panel comic outline:
- Story Prompt: {prompt}
- Main Character: {character_name}
- Setting: {setting}
- Story Tone: {tone}
- Preferred Art Style: {art_style}

Format output as pure JSON array:
[
  {{
    "panel_number": 1,
    "title": "Panel 1: ...",
    "scene_description": "...",
    "image_prompt": "..."
  }},
  ...
]
"""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(
            f"{system_instruction}\n\n{user_message}",
            generation_config={"temperature": 0.7, "max_output_tokens": 1500}
        )
        text = response.text.strip()
        # Clean any markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        outline = json.loads(text)
        if isinstance(outline, list) and len(outline) >= 1:
            # Ensure 5 panels format
            return outline[:5]
    except Exception as e:
        print(f"[Gemini Flash] API call failed: {e}. Falling back to default outline generator.")

    return _fallback_outline(prompt, character_name, setting, tone, art_style)


if __name__ == "__main__":
    test_res = generate_outline("A brave fox exploring an enchanted forest", "Finn", "Enchanted Forest", "Dramatic", "Anime")
    print(f"Generated {len(test_res)} panels.")
    print(json.dumps(test_res, indent=2))
