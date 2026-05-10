# NutraReview AI
**Here i have discussed all the steps used in this project**

A prototype system I built to help review supplement and nutraceutical formulations using AI. You paste in a product name, category, and ingredient list, and it gives you a full breakdown of dosage safety, formulation quality, marketing claim compliance, and an overall grade.

Also has a semantic ingredient search where you can type something like "ingredients for sleep support" and it actually understands what you mean instead of just matching keywords.

Built with Python, Streamlit, and the Anthropic Claude API.

---

## What it does

- Pulls out structured ingredient data from a plain text ingredient list
- Flags ingredients with unusual or risky dosages (rated low / medium / high)
- Writes up formulation observations — what's working, what's not
- Checks marketing claims against FDA/FTC guidelines
- Gives the product an overall score and letter grade (A to F)
- Semantic ingredient search by benefit or intent

---

## Setup

You'll need Python 3.9+ and an Anthropic API key. Get one at [console.anthropic.com](https://console.anthropic.com).

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the app:**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Paste your API key in the sidebar and you're good to go.

**I used the jupyter notebook**:
```python
import subprocess, time, webbrowser
subprocess.Popen(["streamlit", "run", "app.py"])
time.sleep(3)
webbrowser.open("http://localhost:8501")
```

---

## How to use it

**Reviewing a formulation:**
1. Type in the product name, pick a category, paste the ingredient list with dosages
2. Optionally add any marketing claims you want checked
3. Hit Analyze — takes about 10-15 seconds
4. Results show up in tabs: Ingredients, Risk Flags, Observations, Claims

There are 3 sample products preloaded in the sidebar if you want to try it out quickly — one well-formulated, one with some risky dosages, and one with banned ingredients.

**Ingredient search:**
Switch to the Ingredient Search page from the sidebar. Type any benefit or intent and it returns relevant ingredients with dosage ranges, mechanism of action, and evidence level.

---

## Main Files

```
- app.py              main app
- requirements.txt    dependencies
- README.md
```

---

## Deploying to Streamlit Cloud

1. Push the files to a public GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Under Advanced Settings → Secrets, add:
```toml
ANTHROPIC_API_KEY = "your-key-here"
**I don't have any API key so i did not pasted it. You need to purchase it from claude**
```
4. Deploy, you'll get a public URL in about 2 minutes.

Make sure `app.py` has this in the `get_client()` function so it picks up the secret:
```python
api_key = st.session_state.get("api_key", "") or st.secrets.get("ANTHROPIC_API_KEY", "")
```

 I already provided app link.


