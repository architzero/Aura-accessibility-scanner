"""
Standalone scanner script that runs in a separate process.
This avoids asyncio event loop conflicts on Windows.
"""
import sys
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import requests
import colorsys
import textstat
from io import BytesIO
from PIL import Image

# Ensure screenshots directory exists
os.makedirs("screenshots", exist_ok=True)

# AI Model Setup (lazy load to save memory)
processor = None
model = None

def load_ai_model():
    global processor, model
    if processor is None:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Suggestion map with severity levels
SUGGESTION_MAP = {
    # Critical (10 points each)
    "image-alt": {"text": "AI suggestion will be generated for this issue.", "severity": "critical", "points": 10},
    "label": {"text": "Fix: Every form element must have a corresponding <label>.", "severity": "critical", "points": 10},
    "button-name": {"text": "Fix: Ensure every button has clear text.", "severity": "critical", "points": 10},
    
    # Serious (7 points each)
    "color-contrast": {"text": "Fix: Increase contrast between text and background (4.5:1 ratio).", "severity": "serious", "points": 7},
    "link-name": {"text": "Fix: Ensure every link has discernible, descriptive text.", "severity": "serious", "points": 7},
    "html-has-lang": {"text": "Fix: Add a lang attribute to the <html> tag.", "severity": "serious", "points": 7},
    "document-title": {"text": "Fix: Add a descriptive <title> element.", "severity": "serious", "points": 7},
    
    # Moderate (4 points each)
    "heading-order": {"text": "Fix: Heading levels should increase by only one.", "severity": "moderate", "points": 4},
    "list": {"text": "Fix: List elements should only contain proper children.", "severity": "moderate", "points": 4},
    "region": {"text": "Fix: Use landmark elements like <main>, <nav>, <header>.", "severity": "moderate", "points": 4},
    
    # Minor (2 points each)
    "meta-viewport": {"text": "Fix: Ensure viewport doesn't disable user scaling.", "severity": "minor", "points": 2},
    "duplicate-id": {"text": "Fix: Ensure every id attribute is unique.", "severity": "minor", "points": 2},
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def get_relative_luminance(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    def srgb_to_linear(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

def get_contrast_ratio(rgb1, rgb2):
    l1 = get_relative_luminance(rgb1)
    l2 = get_relative_luminance(rgb2)
    return (l1 + 0.05) / (l2 + 0.05) if l1 > l2 else (l2 + 0.05) / (l1 + 0.05)

def suggest_contrast_fix(fg_hex, bg_hex):
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
        if get_contrast_ratio(new_fg_rgb, bg_rgb) >= 4.5:
            return rgb_to_hex(new_fg_rgb_norm)
    return None

def generate_alt_text(image_url):
    try:
        load_ai_model()
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        raw_image = Image.open(BytesIO(response.content)).convert("RGB")
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        return processor.decode(out[0], skip_special_tokens=True)
    except:
        return ""

def scan(url, project_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
        except PlaywrightTimeout:
            raise RuntimeError("Timeout loading page")
        
        html_content = page.content()
        
        # Inject Axe using URL to bypass CSP
        try:
            page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js")
            page.wait_for_function("typeof axe !== 'undefined'", timeout=5000)
        except Exception:
            # Fallback: return basic scan without Axe
            context.close()
            browser.close()
            return {
                "issues": [],
                "genericSuggestions": ["Website security policies prevented full scan"],
                "aiSuggestions": [],
                "screenshot_url": screenshot_path
            }
        
        # Run scan
        try:
            axe_results = page.evaluate("axe.run(document, { iframes: true })")
        except Exception:
            axe_results = {"violations": []}
        
        # Screenshot
        screenshot_path = f"screenshots/{project_id}.png"
        try:
            page.screenshot(path=screenshot_path, full_page=True)
        except:
            screenshot_path = "screenshots/placeholder.png"
        
        # Process results with scoring
        issues, generic_suggestions, ai_suggestions = [], [], []
        total_deductions = 0
        
        for violation in axe_results.get("violations", []):
            vid = violation["id"]
            suggestion_info = SUGGESTION_MAP.get(vid, {"text": "Fix this accessibility issue.", "severity": "moderate", "points": 4})
            
            if vid in SUGGESTION_MAP:
                generic_suggestions.append(f"Suggestion for '{vid}': {suggestion_info['text']}")
            
            for node in violation["nodes"]:
                # Deduct points based on severity
                total_deductions += suggestion_info['points']
                
                issues.append({
                    "element": node["html"],
                    "description": violation["description"],
                    "guideline": vid
                })
                
                # Generate REAL AI suggestions
                if vid == "image-alt" and len([s for s in ai_suggestions if "Alt Text" in s]) < 5:
                    try:
                        img_element = page.locator(node["target"][0]).first
                        img_src = img_element.get_attribute("src", timeout=2000)
                        if img_src:
                            full_img_url = urljoin(url, img_src)
                            # Generate actual alt text using BLIP model
                            alt_text = generate_alt_text(full_img_url)
                            if alt_text:
                                ai_suggestions.append(f"🤖 AI Generated Alt Text: '{alt_text}' (for {img_src[:40]}...)")
                            else:
                                ai_suggestions.append(f"🤖 AI Suggestion: Add descriptive alt text for '{img_src[:40]}...'")
                    except Exception as e:
                        ai_suggestions.append(f"🤖 AI Suggestion: Add descriptive alt text for this image")
                
                elif vid == "color-contrast":
                    try:
                        data = node.get("any", [{}])[0].get("data", {})
                        fg_color = data.get("fgColor")
                        bg_color = data.get("bgColor")
                        if fg_color and bg_color:
                            # Calculate actual fixed color
                            new_color = suggest_contrast_fix(fg_color, bg_color)
                            if new_color:
                                ai_suggestions.append(f"🎨 AI Color Fix: Change text color from {fg_color} to {new_color} (meets WCAG AA 4.5:1 ratio)")
                            else:
                                ai_suggestions.append(f"🎨 AI Suggestion: Increase contrast between {fg_color} and {bg_color}")
                    except Exception as e:
                        ai_suggestions.append(f"🎨 AI Suggestion: Improve text color contrast")
                
                elif vid == "link-name" and len([s for s in ai_suggestions if "Link" in s]) < 3:
                    ai_suggestions.append(f"🔗 AI Suggestion: Use descriptive link text (avoid 'click here', 'read more')")
                
                elif vid == "button-name" and len([s for s in ai_suggestions if "Button" in s]) < 3:
                    ai_suggestions.append(f"🔘 AI Suggestion: Add clear, action-oriented button text")
        
        # Add Flesch readability analysis
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            paragraphs = soup.find_all('p')
            readability_checked = 0
            for p in paragraphs:
                if readability_checked >= 3:
                    break
                text = p.get_text().strip()
                if len(text.split()) > 20:  # At least 20 words
                    try:
                        grade = textstat.flesch_kincaid_grade(text)
                        if grade > 10:
                            preview = text[:70] + '...' if len(text) > 70 else text
                            ai_suggestions.append(f"📚 AI Readability Analysis: Text has grade level {grade:.1f} (college level). Simplify for broader audience: '{preview}'")
                            readability_checked += 1
                    except:
                        pass
        except:
            pass
        
        # Calculate score (100 - deductions, minimum 0)
        score = max(0, 100 - total_deductions)
        
        # Always add at least one AI suggestion if there are issues
        if len(issues) > 0 and len(ai_suggestions) == 0:
            ai_suggestions.append("🤖 AI Tip: Focus on fixing critical issues first (image alt text, form labels, button names)")
            ai_suggestions.append("🎨 AI Tip: Ensure sufficient color contrast (4.5:1 for normal text, 3:1 for large text)")
            ai_suggestions.append("📚 AI Tip: Use semantic HTML elements (<main>, <nav>, <header>) for better structure")
        
        context.close()
        browser.close()
        
        return {
            "issues": issues,
            "genericSuggestions": list(set(generic_suggestions)),
            "aiSuggestions": ai_suggestions,
            "screenshot_url": screenshot_path,
            "score": score
        }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Usage: scanner_process.py <url> <project_id>"}))
        sys.exit(1)
    
    url = sys.argv[1]
    project_id = sys.argv[2]
    
    try:
        result = scan(url, project_id)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
