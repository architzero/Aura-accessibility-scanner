# Aura: AI-Powered Web Accessibility Auditor 🚀

Aura is a full-stack web accessibility platform designed to simplify WCAG compliance. It leverages the industry-standard Axe-core engine for deep, accurate issue detection and integrates a multi-modal AI layer to provide actionable solutions, such as generated alt-text, color contrast corrections, and readability analysis.
---

## Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Roadmap](#roadmap)

---

## About The Project

In an increasingly digital world, web accessibility is a fundamental requirement, not a feature. However, auditing and fixing accessibility issues can be a complex and time-consuming process. Many tools can find problems, but few offer intelligent, actionable solutions.

Aura was built to bridge this gap. It combines a powerful, industry-standard scanning engine (**Axe-core**) with a multi-modal AI layer to provide developers with a comprehensive and helpful auditing experience. It finds the "what" and provides the "how," simplifying the path to a more inclusive web.

---

## Key Features

* **Comprehensive Live Audits:** Uses Playwright to control a headless browser and the Axe-core engine to perform deep, accurate analysis of dynamic web pages against WCAG standards.
* **AI-Powered Alt Text Generation:** Utilizes a Hugging Face Transformer model (BLIP) to automatically generate descriptive alt-text for images.
* **AI-Powered Color Contrast Suggestions:** Algorithmically calculates and suggests new color codes that meet WCAG contrast requirements for failing elements.
* **AI-Powered Readability Analysis:** Analyzes page content and flags paragraphs with a high reading grade level, suggesting simplification.
* **Project Management & Scan History:** Users can create projects, run multiple scans, and view a history of their results to track their progress over time.
* **Secure User Authentication:** Features a secure, JWT-based authentication system for user registration and login.

---

## Tech Stack

The project is built with a modern, robust tech stack:

* **Backend:** Python, FastAPI
* **Database:** MongoDB
* **Scanning Engine:** Playwright, Axe-core
* **AI & ML:** Hugging Face Transformers, PyTorch, TextStat
* **Authentication:** JWT (JSON Web Tokens)
* **Frontend:** HTML, CSS, JavaScript (Vanilla)

---

## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

Make sure you have the following installed on your system:
* Python 3.9+
* Node.js (for `npm`, if you choose to expand the frontend)
* Git

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/architzero/Aura-accessibility-scanner.git](https://github.com/architzero/Aura-accessibility-scanner.git)
    cd Aura-accessibility-scanner
    ```

2.  **Set up the Backend:**
    ```sh
    cd backend

    # Create and activate a virtual environment
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt

    # Install Playwright's browser engines
    playwright install

    # Create a .env file and add your secret keys
    # (Copy .env.example if you have one, or create it)
    touch .env
    ```
    Add the following to your `.env` file:
    ```env
    MONGO_DB_URI="your-mongodb-atlas-connection-string"
    JWT_SECRET_KEY="your-super-strong-random-secret-key"
    JWT_ALGORITHM="HS256"
    ```

3.  **Run the Backend Server:**
    ```sh
    uvicorn main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

4.  **Run the Frontend Server:**
    Open a **new, separate terminal**.
    ```sh
    cd frontend
    python -m http.server 8001
    ```
    The frontend will be running at `http://127.0.0.1:8001`.

---

## Usage

1.  Navigate to `http://127.0.0.1:8001` in your browser.
2.  Register for a new account and then log in.
3.  On the dashboard, create a new project by providing a name and a URL.
4.  Click "Scan Now" to initiate an accessibility scan.
5.  You will be redirected to the results page to see the score, screenshot, issues, and suggestions.
6.  Navigate back to the dashboard and click "View History" to see a list of all past scans for that project.

---

## Roadmap

Future enhancements planned for Aura include:

- [ ] **Deployment:** Deploy the application to a live web environment (Vercel/Render).
- [ ] **Screenshot Scanning:** Implement the ability to scan user-uploaded screenshots.
- [ ] **Authentication Enhancements:** Add Google OAuth login and email verification.

See the [open issues](https://github.com/architzero/Aura-accessibility-scanner/issues) for a full list of proposed features (and known issues).
