# AI-Grade HR Resume Engine — Setup Guide for HR

This guide is for HR staff who need to run the Resume Intelligence Engine on their computer. Follow the steps below once; after that, you only need to **run the app** (Step 6).

---

## What you need

- **Python 3.9 or newer** installed on your computer.  
  - Check: open Terminal (Mac/Linux) or Command Prompt (Windows) and type `python3 --version`. If you see a version number, you’re set. If not, install Python from [python.org](https://www.python.org/downloads/).
- **This project folder** (the whole `ai_grade_hr_resume_engine` folder with all files inside it).
- **A GROQ API key** (your IT or the person who gave you this app should provide it).

---

## Step 1: Open Terminal in the project folder

- **Mac:** Open Terminal, then run `cd` and drag the `ai_grade_hr_resume_engine` folder into the window, then press Enter.  
  Or: `cd` followed by the path to the folder, e.g.  
  `cd /Users/YourName/Downloads/ai_grade_hr_resume_engine`
- **Windows:** Open Command Prompt, then `cd` to the folder, e.g.  
  `cd C:\Users\YourName\Downloads\ai_grade_hr_resume_engine`
- **Linux:** Same as Mac: `cd /path/to/ai_grade_hr_resume_engine`

You must be *inside* the project folder (you should see files like `dashboard.py` and `requirements.txt` when you list files).

---

## Step 2: Create a virtual environment

Run exactly:

```bash
python3 -m venv ai_grade_hr_resume_engine_venv
```

*(On some Windows setups you may need `python` instead of `python3`.)*

This creates a separate environment so the app’s dependencies don’t conflict with other software.

---

## Step 3: Activate the virtual environment

- **Mac / Linux:**

  ```bash
  source ai_grade_hr_resume_engine_venv/bin/activate
  ```

- **Windows (Command Prompt):**

  ```bash
  ai_grade_hr_resume_engine_venv\Scripts\activate.bat
  ```

- **Windows (PowerShell):**

  ```bash
  ai_grade_hr_resume_engine_venv\Scripts\Activate.ps1
  ```

When it’s active, you’ll see `(ai_grade_hr_resume_engine_venv)` at the start of the line. You need to do this every time you open a new terminal to run the app.

---

## Step 4: Install dependencies

With the virtual environment **activated**, run:

```bash
pip install -r requirements.txt
```

Wait until it finishes without errors.

---

## Step 5: Set up your API key (.env file)

The app needs a GROQ API key to analyze resumes.

1. In the project folder, find the file **`.env.example`**.
2. Copy it and rename the copy to **`.env`** (same folder).
3. Open **`.env`** in a text editor.
4. Replace the placeholder with your real GROQ API key, for example:
   - `GROQ_API_KEY=your_actual_key_here`
   - Optionally set `GROQ_MODEL=llama-3.3-70b-versatile` (or the model you were given).
5. Save the file.

**Important:** Keep `.env` private. Don’t share it or upload it.

---

## Step 6: Run the app

With the virtual environment **activated** and from the **project folder**, run:

```bash
streamlit run dashboard.py
```

You’ll see a few lines of text; one of them will look like:

- **Local URL:** http://localhost:8501

Open that link in your web browser. You should see the **AI-Grade Internal HR Resume Intelligence Engine** page where you can upload PDF or DOCX resumes.

---

## Using the app

- Upload one or more resume files (PDF or DOCX).
- The app will score them and show a table with scores and categories.
- Use **Download Shortlist CSV** to save the results.

---

## Troubleshooting

| Problem | What to try |
|--------|--------------|
| `python3` not found | Install Python from [python.org](https://www.python.org/downloads/) or try `python` instead of `python3`. |
| `pip install` fails | Make sure the virtual environment is activated (you see `(ai_grade_hr_resume_engine_venv)`). |
| “Permission denied” when activating | Use `source ai_grade_hr_resume_engine_venv/bin/activate` (with **source**), not just the path to `activate`. |
| App opens but analysis fails | Check that `.env` exists in the project folder and contains a valid `GROQ_API_KEY`. |
| Port already in use | Another app may be using port 8501. Close it or run: `streamlit run dashboard.py --server.port 8502` and open http://localhost:8502. |

---

## Quick reference (after first-time setup)

1. Open Terminal / Command Prompt.
2. `cd` to the project folder.
3. Activate: `source ai_grade_hr_resume_engine_venv/bin/activate` (Mac/Linux) or `ai_grade_hr_resume_engine_venv\Scripts\activate` (Windows).
4. Run: `streamlit run dashboard.py`.
5. Open the URL shown (e.g. http://localhost:8501) in your browser.
