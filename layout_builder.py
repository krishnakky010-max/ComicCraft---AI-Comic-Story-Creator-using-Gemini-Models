"""
layout_builder.py - Organizes generated illustrations, outlines, and story into structured comic layout.
Part of ComicCraft - AI Comic Story Creator using Gemini Models.
"""

def build_comic_layout(outline: list, story: list, image_paths: list) -> list:
    """
    Combines the structured outline from Gemini Flash, the story/dialogue from Gemini Pro,
    and the generated illustration paths into a unified comic layout.

    Returns a list of dictionaries:
    [
        {
            "panel_number": 1,
            "title": "Panel 1: Title",
            "image_path": "/static/panels/...",
            "scene_description": "...",
            "caption": "...",
            "narration": "...",
            "image_prompt": "..."
        },
        ...
    ]
    """
    layout = []
    total_panels = len(outline)

    for i in range(total_panels):
        panel_data = outline[i]
        panel_num = panel_data.get("panel_number", i + 1)
        title = panel_data.get("title", f"Panel {panel_num}")
        scene_desc = panel_data.get("scene_description", "")
        img_prompt = panel_data.get("image_prompt", "")

        # Match story by panel_number or index
        matched_story = None
        if isinstance(story, list):
            for s in story:
                if isinstance(s, dict) and s.get("panel_number") == panel_num:
                    matched_story = s
                    break
            if not matched_story and i < len(story):
                matched_story = story[i]

        caption = ""
        narration = ""
        if isinstance(matched_story, dict):
            caption = matched_story.get("caption", "")
            narration = matched_story.get("narration", "")
        elif isinstance(matched_story, str):
            narration = matched_story

        # Match image path
        img_path = image_paths[i] if i < len(image_paths) else ""

        layout.append({
            "panel_number": panel_num,
            "title": title,
            "image_path": img_path,
            "scene_description": scene_desc,
            "caption": caption,
            "narration": narration,
            "image_prompt": img_prompt
        })

    return layout


if __name__ == "__main__":
    sample_outline = [{"panel_number": 1, "title": "Panel 1: Start", "scene_description": "A quiet grove", "image_prompt": "trees"}]
    sample_story = [{"panel_number": 1, "caption": "*Birds chirp*", "narration": "Finn begins his walk."}]
    sample_imgs = ["/static/panels/panel_1.png"]
    res = build_comic_layout(sample_outline, sample_story, sample_imgs)
    print("Sample layout:", res)
