"""
exporters.py - Compiles comic panels, illustrations, and narration into a PDF using FPDF.
Part of ComicCraft - AI Comic Story Creator using Gemini Models.
"""
import os
import time
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
EXPORTS_DIR = os.path.join(STATIC_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)


class ComicPDF(FPDF):
    def header(self):
        # Top banner with comic aesthetic
        self.set_fill_color(20, 24, 40)
        self.rect(0, 0, 210, 14, 'F')
        self.set_text_color(255, 215, 0)
        self.set_font('Helvetica', 'B', 10)
        self.set_xy(10, 3)
        self.cell(100, 8, "COMICCRAFT  |  AI Comic Story Creator", align='L')
        self.set_text_color(200, 210, 230)
        self.set_font('Helvetica', '', 8)
        self.set_xy(140, 3)
        self.cell(60, 8, "Powered by Gemini AI & Diffusers", align='R')
        self.ln(12)

    def footer(self):
        # Bottom page indicator
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(130, 140, 160)
        self.cell(0, 10, f"Page {self.page_no()}", align='C')


def save_pdf(layout: list, comic_title: str = "ComicCraft Comic Story") -> str:
    """
    Compiles comic layout and illustrations into a multi-page PDF using FPDF.
    Each panel is rendered onto its own page with its title, image, italic scene description,
    sound caption, and narration.
    Saves file to static/exports/ and returns the web-accessible path (e.g. /static/exports/comic_...).
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    output_path = os.path.join(EXPORTS_DIR, filename)

    pdf = ComicPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, panel in enumerate(layout):
        pdf.add_page()
        pdf.set_text_color(20, 20, 30)

        # Panel Title Box
        title = panel.get("title", f"Panel {i+1}")
        pdf.set_fill_color(240, 243, 250)
        pdf.set_draw_color(20, 24, 40)
        pdf.set_line_width(0.6)
        pdf.rect(15, 20, 180, 12, 'FD')

        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(15, 20, 35)
        pdf.set_xy(18, 22)
        pdf.cell(174, 8, title, align='L')

        # Comic Image
        img_web_path = panel.get("image_path", "")
        # Resolve filesystem path
        if img_web_path.startswith("/static/"):
            rel_path = img_web_path.replace("/static/", "")
            local_img_path = os.path.join(STATIC_DIR, rel_path)
        elif img_web_path.startswith("static/"):
            local_img_path = os.path.join(BASE_DIR, img_web_path)
        else:
            local_img_path = img_web_path

        current_y = 35
        if os.path.exists(local_img_path):
            try:
                # Border around image
                pdf.set_draw_color(10, 15, 25)
                pdf.set_line_width(0.8)
                pdf.rect(15, current_y, 180, 120, 'D')
                pdf.image(local_img_path, x=15.5, y=current_y + 0.5, w=179, h=119)
                current_y += 124
            except Exception as e:
                print(f"[PDF Export] Warning embedding image: {e}")
                current_y += 10
        else:
            pdf.set_xy(15, current_y)
            pdf.set_font('Helvetica', 'I', 11)
            pdf.cell(180, 20, f"[Illustration for Panel {i+1}]", align='C')
            current_y += 25

        # Scene Description (Italicized)
        scene_desc = panel.get("scene_description", "")
        if scene_desc:
            pdf.set_xy(15, current_y)
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(70, 80, 95)
            # Clean non-latin1 characters for basic FPDF standard font
            safe_scene = scene_desc.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(180, 5.5, safe_scene)
            current_y = pdf.get_y() + 4

        # Caption Box (ambient sound / setting)
        caption = panel.get("caption", "")
        if caption:
            pdf.set_fill_color(255, 245, 220)
            pdf.set_draw_color(220, 180, 50)
            pdf.set_line_width(0.4)
            cap_y = current_y
            pdf.rect(15, cap_y, 180, 9, 'FD')
            pdf.set_xy(18, cap_y + 1)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(140, 80, 10)
            safe_cap = caption.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(174, 7, safe_cap)
            current_y = cap_y + 13

        # Character Narration & Dialogue
        narration = panel.get("narration", "")
        if narration:
            pdf.set_fill_color(250, 252, 255)
            pdf.set_draw_color(50, 80, 150)
            pdf.set_line_width(0.5)

            box_start_y = current_y
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(20, 25, 40)
            safe_narration = narration.encode('latin-1', 'replace').decode('latin-1')

            # Render narration inside styled speech frame
            pdf.set_xy(18, box_start_y + 3)
            pdf.multi_cell(174, 5.5, safe_narration)
            box_end_y = pdf.get_y() + 3
            box_height = max(14, box_end_y - box_start_y)
            # Draw frame behind/around
            pdf.rect(15, box_start_y, 180, box_height, 'D')

    pdf.output(output_path)
    print(f"[PDF Exporter] Successfully compiled comic PDF to: {output_path}")
    return f"/static/exports/{filename}"


if __name__ == "__main__":
    test_layout = [{
        "panel_number": 1,
        "title": "Panel 1: The Whispering Woods",
        "image_path": "",
        "scene_description": "Finn stands at the edge of the mystical forest.",
        "caption": "*Wind rustles through luminescent leaves*",
        "narration": '"Here begins our greatest adventure yet," Finn whispers.'
    }]
    out = save_pdf(test_layout, "Test Adventure")
    print("Exported PDF:", out)
