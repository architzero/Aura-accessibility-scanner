import os
import requests
import json
import colorsys
import textstat # <--- Added import
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup # <--- Added import

from services.suggestions import SUGGESTION_MAP
from transformers import BlipProcessor, BlipForConditionalGeneration

# --- AI Model Setup ---
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
# --------------------

os.makedirs("screenshots", exist_ok=True)

# --- Contrast Ratio and Color Functions ---
def get_relative_luminance(rgb: tuple) -> float:
    r, g, b = [x / 255.0 for x in rgb]
    def srgb_to_linear(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r_lin = srgb_to_linear(r)
    g_lin = srgb_to_linear(g)
    b_lin = srgb_to_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

def get_contrast_ratio(rgb1: tuple, rgb2: tuple) -> float:
    l1 = get_relative_luminance(rgb1)
    l2 = get_relative_luminance(rgb2)
    return (l1 + 0.05) / (l2 + 0.05) if l1 > l2 else (l2 + 0.05) / (l1 + 0.05)

def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def suggest_contrast_fix(fg_hex, bg_hex, required_ratio=4.5):
    fg_rgb = hex_to_rgb(fg_hex)
    bg_rgb = hex_to_rgb(bg_hex)
    fg_h, fg_l, fg_s = colorsys.rgb_to_hls(fg_rgb[0]/255, fg_rgb[1]/255, fg_rgb[2]/255)
    bg_l = colorsys.rgb_to_hls(bg_rgb[0]/255, bg_rgb[1]/255, bg_rgb[2]/255)[1]
    step = 0.01 if bg_l < 0.5 else -0.01
    new_fg_l = fg_l
    for _ in range(100):
        new_fg_l = max(0, min(1, new_fg_l + step))
        new_fg_rgb_norm = colorsys.hls_to_rgb(fg_h, new_fg_l, fg_s)
        new_fg_rgb = (new_fg_rgb_norm[0] * 255, new_fg_rgb_norm[1] * 255, new_fg_rgb_norm[2] * 255)
        if get_contrast_ratio(new_fg_rgb, bg_rgb) >= required_ratio:
            return rgb_to_hex(new_fg_rgb_norm)
    return None

# --- Alt Text AI Function ---
def generate_alt_text(image_url: str) -> str:
    try:
        response = requests.get(image_url, stream=True, timeout=5)
        response.raise_for_status()
        raw_image = Image.open(BytesIO(response.content)).convert("RGB")
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        print(f"Could not generate alt text for {image_url}: {e}")
        return ""

# --- New Readability AI Function ---
def check_readability(soup: BeautifulSoup) -> List[str]:
    """Analyzes text in <p> tags for reading complexity."""
    suggestions = []
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text()
        # Analyze only paragraphs with a meaningful amount of text
        if len(text.split()) > 25:
            grade = textstat.flesch_kincaid_grade(text)
            if grade > 10:
                preview = (text[:80] + '...') if len(text) > 80 else text
                suggestion = (f"AI Suggestion for readability: The paragraph starting with \"{preview}\" "
                              f"has a high reading grade level ({grade:.1f}). Consider simplifying the language.")
                suggestions.append(suggestion)
    return suggestions

def scan_website(url: str, project_id: str) -> Dict:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle")
            html_content = page.content() # Get HTML for readability check
            
            page.add_script_tag(path="static/axe.min.js")
            axe_results = page.evaluate("axe.run(document, { iframes: true })")
            
            screenshot_path = f"screenshots/{project_id}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            
            issues, generic_suggestions, ai_suggestions = [], [], []

            for violation in axe_results.get("violations", []):
                violation_id = violation["id"]
                if violation_id in SUGGESTION_MAP:
                    generic_suggestions.append(f"Suggestion for '{violation_id}': {SUGGESTION_MAP[violation_id]}")
                
                for node in violation["nodes"]:
                    issues.append({ "element": node["html"], "description": violation["description"], "guideline": violation_id })
                    
                    if violation_id == "image-alt":
                        img_element = page.locator(node["target"][0]).first
                        img_src = img_element.get_attribute("src")
                        if img_src:
                            full_img_url = urljoin(url, img_src)
                            generated_text = generate_alt_text(full_img_url)
                            if generated_text:
                                ai_suggestions.append(f"AI Suggestion for '{img_src}': Consider this alt text: '{generated_text}'")
                    
                    if violation_id == "color-contrast":
                        data = node.get("any", [{}])[0].get("data", {})
                        fg_color, bg_color = data.get("fgColor"), data.get("bgColor")
                        if fg_color and bg_color:
                            new_color = suggest_contrast_fix(fg_color, bg_color)
                            if new_color:
                                ai_suggestions.append(f"AI Suggestion for contrast: For the element '{node['html']}', try changing the text color from {fg_color} to {new_color}.")
            
            # --- Call the Readability Check ---
            soup = BeautifulSoup(html_content, "html.parser")
            readability_suggestions = check_readability(soup)
            ai_suggestions.extend(readability_suggestions)

        except Exception as e:
            browser.close()
            raise RuntimeError(f"Failed to load or scan page {url}: {e}")
        finally:
            browser.close()

    return {
        "issues": issues,
        "genericSuggestions": list(set(generic_suggestions)),
        "aiSuggestions": ai_suggestions,
        "screenshot_url": screenshot_path
    }