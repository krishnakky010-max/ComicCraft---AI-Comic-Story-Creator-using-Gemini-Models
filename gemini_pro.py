"""
gemini_pro.py - Generates rich narration, character dialogue, and sound captions using Gemini Pro.
Part of ComicCraft - AI Comic Story Creator using Gemini Models.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

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


def _fallback_story(outline: list, character_name: str, setting: str, tone: str) -> list:
    """Rich fallback story generator when Gemini Pro API is offline."""
    char = character_name.strip() if character_name else "Hero"
    tone_lower = (tone or "dramatic").lower()

    if "funny" in tone_lower or "light" in tone_lower:
        dialogues = [
            (f"*Birds chirp sarcastically in the treetops*", f'"{char}, master explorer, ready to conquer... wait, did I leave the oven on?" {char} mutters.'),
            (f"*Rustle! Crackle!*", f'"Hello? If you\'re a goblin, I must warn you—I know karate. Well, I watched a documentary once!" yells {char}.'),
            (f"*BZZZT! A sudden glittery flash*", f'"A glowing magical rock? Don\'t touch it, {char}. Definitely don\'t touch it... oops, I touched it."'),
            (f"*SWOOSH! The ground spins*", f'"Whoa! Flying without wings! Ten out of ten for style, zero out of ten for landing predictability!"'),
            (f"*Golden sunshine sparkles*", f'"We survived! Another glorious day saved by sheer luck and undeniable charm!" {char} grins proudly.')
        ]
    else:
        dialogues = [
            (f"*The cold wind sighs through {setting}*", f'"{char}, keep your focus. The ancient tales whispered of this day," {char} murmurs, stepping forward with unwavering grit.'),
            (f"*Low, rumbling vibration beneath the earth*", f'"Something is awake here. Something that hasn\'t breathed in centuries." {char}\'s pulse quickens.'),
            (f"*Humming pulse of ancient celestial energy*", f'"The Seal of Eternity... it is still intact! If I can harness this, we might yet turn the tide."'),
            (f"*Thunderous shockwave rocks the horizon*", f'"I won\'t back down! Not now, not ever!" {char} shouts into the blazing vortex.'),
            (f"*Serene silence falls across the dawn*", f'"The shadow has passed. A new chapter begins for us all," {char} breathes, looking toward the dawn.')
        ]

    stories = []
    for i, panel in enumerate(outline):
        cap, nar = dialogues[i % len(dialogues)]
        stories.append({
            "panel_number": panel.get("panel_number", i + 1),
            "caption": cap,
            "narration": nar
        })
    return stories


def generate_story(outline: list, character_name: str = "Hero", setting: str = "Forest", tone: str = "Dramatic") -> list:
    """
    Uses Gemini Pro (gemini-1.5-pro) to expand panel outlines into full comic-style story,
    creating atmospheric captions and vivid character dialogues for each panel.
    Returns a list of dictionaries with panel_number, caption, narration.
    """
    genai = _get_gemini_client()

    if not genai:
        print("[Gemini Pro] No GEMINI_API_KEY detected. Using intelligent built-in dialogue generator.")
        return _fallback_story(outline, character_name, setting, tone)

    prompt_panels = "\n".join([
        f"Panel {p.get('panel_number', i+1)}: Title: {p.get('title')}, Scene: {p.get('scene_description')}"
        for i, p in enumerate(outline)
    ])

    user_prompt = f"""
You are a master comic book scriptwriter.
Expand the following 5-panel comic outline into immersive comic narration, sound captions, and character dialogue.
Main Character: {character_name}
Setting: {setting}
Tone: {tone}

Outline:
{prompt_panels}

Return ONLY a JSON array with exactly {len(outline)} items matching this structure:
[
  {{
    "panel_number": 1,
    "caption": "*Atmospheric sound or setting note*",
    "narration": "Character actions, internal thoughts, or spoken dialogue"
  }},
  ...
]
"""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(
            user_prompt,
            generation_config={"temperature": 0.8, "max_output_tokens": 1500}
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        stories = json.loads(text)
        if isinstance(stories, list) and len(stories) >= 1:
            return stories
    except Exception as e:
        print(f"[Gemini Pro] API call failed: {e}. Falling back to default story generator.")

    return _fallback_story(outline, character_name, setting, tone)


if __name__ == "__main__":
    from gemini_flash import generate_outline
    test_outline = generate_outline("A brave fox exploring an enchanted forest", "Finn", "Enchanted Forest", "Dramatic", "Anime")
    test_story = generate_story(test_outline, "Finn", "Enchanted Forest", "Dramatic")
    print("Generated Story:")
    print(json.dumps(test_story, indent=2))
