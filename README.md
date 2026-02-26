# Aura: AI-Powered Web Accessibility Auditor 🚀

Aura is a full-stack web accessibility platform that combines **Axe-core** scanning with **AI-powered suggestions** to achieve WCAG compliance.

## 🤖 AI Features

1. **BLIP Image Captions** - Generates alt text using Hugging Face's BLIP model
2. **Color Contrast AI** - Calculates WCAG-compliant color fixes (4.5:1 ratio)
3. **Flesch-Kincaid Analysis** - Analyzes text readability grade level

## 🛠️ Tech Stack

**Backend:** Python, FastAPI, MongoDB, Playwright, Axe-core  
**AI/ML:** Hugging Face Transformers (BLIP), PyTorch, TextStat  
**Frontend:** HTML, CSS, JavaScript

## 📦 Installation

### Prerequisites
- Python 3.11+
- MongoDB Atlas account

### Setup

1. **Clone & Install**
```bash
git clone https://github.com/architzero/Aura-accessibility-scanner.git
cd Aura-accessibility-scanner/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium
```

2. **Configure Environment**

Create `backend/.env`:
```env
MONGO_DB_URI="your-mongodb-connection-string"
JWT_SECRET_KEY="your-secret-key"  # Generate: python -c "import secrets; print(secrets.token_hex(32))"
JWT_ALGORITHM="HS256"
CORS_ORIGINS=["http://127.0.0.1:8001","http://localhost:8001"]
ENVIRONMENT="development"
```

3. **Run Application**

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
python -m http.server 8001
```

4. **Access**: http://127.0.0.1:8001

## 🧪 Test AI Features

```bash
cd backend
python test_ai_features.py
```

Expected output:
- ✅ BLIP Model Working!
- ✅ Color Contrast AI Working!
- ✅ Flesch-Kincaid Working!

## 🌐 Test Sites

**Recommended:**
- https://example.com - Simple baseline
- https://www.berkshirehathaway.com - Contrast issues
- https://www.arngren.net - Multiple issues
- https://news.ycombinator.com - Fast scan

**Blocked (CSP):**
- Instagram, Facebook, Twitter, LinkedIn

## 📊 How It Works

1. User creates project with URL
2. Playwright + Axe-core scan website
3. AI analyzes violations:
   - **Image-alt** → BLIP generates descriptions
   - **Color-contrast** → Calculates WCAG fixes
   - **Text** → Flesch-Kincaid readability
4. Results stored with severity-based score
5. User views issues + AI suggestions

## 🎯 Key Features

- ✅ Live website audits
- ✅ WCAG 2.1 compliance checking
- ✅ AI-powered fix suggestions
- ✅ Severity-based scoring (Critical: 10pts, Serious: 7pts, Moderate: 4pts, Minor: 2pts)
- ✅ Full-page screenshots
- ✅ Scan history tracking
- ✅ JWT authentication
- ✅ Responsive UI

## 📁 Project Structure

```
backend/
  scanner_process.py    # Main AI scanner
  routers/              # API endpoints
  services/             # Business logic
  config.py             # Configuration
  
frontend/
  dashboard.html        # Projects & scanning
  results.html          # AI suggestions
  style.css             # Modern UI
```

## 🔒 Security

- JWT authentication
- Password hashing (bcrypt)
- URL validation (SSRF prevention)
- CORS protection
- Input sanitization

## 📝 License

MIT License

## 👨‍💻 Author

**Archit** - [@architzero](https://github.com/architzero)

---

**Built with ❤️ for a more accessible web**
