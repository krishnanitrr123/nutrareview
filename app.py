import streamlit as st
import anthropic
import json

st.set_page_config(
    page_title="NutraReview AI",
    page_icon="🧪",
    layout="wide"
)

# i kept all the CSS in one place so it's easier to find and edit later
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* hide the default streamlit stuff at the top and bottom */
#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2.5rem;
}

/* dark sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0f172a, #1e293b);
    border-right: 1px solid #2d3f55;
}

[data-testid="stSidebar"] * {
    color: #dde4f0 !important;
}

[data-testid="stSidebar"] input {
    background: #192336 !important;
    border: 1px solid #3d5068 !important;
    color: #f0f4fa !important;
    border-radius: 7px !important;
}

[data-testid="stSidebar"] hr {
    border-color: #2d3f55 !important;
}

/* the dark banner at the top of each page */
.page-header {
    background: linear-gradient(130deg, #0f172a 0%, #1a3559 55%, #0f172a 100%);
    border-radius: 14px;
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(59, 130, 246, 0.18);
    overflow: hidden;
    position: relative;
}

.page-header h1 {
    color: #f0f4fa;
    font-size: 1.85rem;
    font-weight: 700;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.4px;
}

.page-header p {
    color: #8fa3bc;
    font-size: 0.92rem;
    margin: 0;
}

.page-header .pill {
    display: inline-block;
    background: #1e3fa8;
    color: #bdd5fc;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 999px;
    margin-bottom: 0.65rem;
}

/* inputs */
.stTextInput input,
.stTextArea textarea {
    border-radius: 9px !important;
    border: 1.5px solid #dde3ec !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.15s !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

/* primary button - blue gradient */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 0.55rem 1.6rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.3) !important;
}

/* secondary button - for quick search chips */
.stButton > button[kind="secondary"] {
    border-radius: 7px !important;
    border: 1.5px solid #dde3ec !important;
    color: #4a5568 !important;
    background: #fff !important;
    font-size: 0.78rem !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button[kind="secondary"]:hover {
    border-color: #3b82f6 !important;
    color: #1d4ed8 !important;
    background: #eff6ff !important;
}

/* the big letter grade card */
.grade-box {
    text-align: center;
    padding: 1.4rem 0.8rem;
    border-radius: 14px;
    box-shadow: 0 3px 16px rgba(0, 0, 0, 0.07);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.grade-letter {
    font-size: 3.8rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -2px;
}

.grade-score {
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 5px;
    opacity: 0.75;
}

/* summary / strength / weakness boxes */
.summary-card {
    background: linear-gradient(130deg, #eef9ff, #ddf0fc);
    border: 1px solid #b5dff8;
    border-radius: 13px;
    padding: 1.15rem 1.4rem;
    font-size: 0.9rem;
    line-height: 1.75;
    color: #0b4068;
}

.strength-card {
    background: #f0fdf5;
    border: 1px solid #b8f0cc;
    border-radius: 11px;
    padding: 0.95rem 1.15rem;
}

.weakness-card {
    background: #fff8f0;
    border: 1px solid #fdd9a8;
    border-radius: 11px;
    padding: 0.95rem 1.15rem;
}

.card-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.55rem;
}

.card-item {
    font-size: 0.85rem;
    line-height: 1.6;
    margin-bottom: 0.25rem;
    padding-left: 0.9rem;
    position: relative;
}

.card-item::before {
    content: "›";
    position: absolute;
    left: 0;
    font-weight: 700;
}

/* risk flag cards */
.risk-high   { background: linear-gradient(135deg, #fff0f2, #ffdde1); border-left: 4px solid #f43f5e; border-radius: 0 9px 9px 0; padding: 11px 15px; margin: 7px 0; }
.risk-medium { background: linear-gradient(135deg, #fffae8, #fef1c0); border-left: 4px solid #f59e0b; border-radius: 0 9px 9px 0; padding: 11px 15px; margin: 7px 0; }
.risk-low    { background: linear-gradient(135deg, #f0fdf5, #d9fce6); border-left: 4px solid #22c55e; border-radius: 0 9px 9px 0; padding: 11px 15px; margin: 7px 0; }

.risk-pill              { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; padding: 2px 7px; border-radius: 999px; display: inline-block; margin-bottom: 3px; }
.risk-pill.pill-high    { background: #f43f5e; color: #fff; }
.risk-pill.pill-medium  { background: #f59e0b; color: #fff; }
.risk-pill.pill-low     { background: #22c55e; color: #fff; }

/* observation rows */
.obs-positive { background: #eef5ff; border-left: 4px solid #3b82f6; border-radius: 0 9px 9px 0; padding: 9px 13px; margin: 5px 0; font-size: 0.87rem; color: #1a3880; }
.obs-concern  { background: #fff6ee; border-left: 4px solid #f97316; border-radius: 0 9px 9px 0; padding: 9px 13px; margin: 5px 0; font-size: 0.87rem; color: #7a2c10; }
.obs-neutral  { background: #f7f9fc; border-left: 4px solid #94a3b8; border-radius: 0 9px 9px 0; padding: 9px 13px; margin: 5px 0; font-size: 0.87rem; color: #334155; }

/* marketing claims */
.claim-card             { border-radius: 9px; padding: 11px 15px; margin: 7px 0; border: 1px solid transparent; }
.claim-compliant        { background: #f0fdf5; border-color: #b8f0cc; }
.claim-caution          { background: #fffae8; border-color: #fde39a; }
.claim-noncompliant     { background: #fff0f2; border-color: #fecacf; }

.claim-pill                     { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; padding: 2px 9px; border-radius: 999px; display: inline-block; margin-bottom: 5px; }
.claim-pill.cpill-compliant     { background: #22c55e; color: #fff; }
.claim-pill.cpill-caution       { background: #f59e0b; color: #fff; }
.claim-pill.cpill-noncompliant  { background: #f43f5e; color: #fff; }

/* ingredient search result cards */
.search-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 13px;
    padding: 1.15rem 1.4rem;
    margin: 9px 0;
    box-shadow: 0 2px 7px rgba(0, 0, 0, 0.04);
    transition: box-shadow 0.18s, transform 0.18s;
}

.search-card:hover {
    box-shadow: 0 7px 22px rgba(0, 0, 0, 0.09);
    transform: translateY(-2px);
}

/* tags / pills inside search cards */
.ing-name    { font-size: 1rem; font-weight: 700; color: #0f172a; }
.tag         { background: #f1f5f9; color: #475569; font-size: 0.7rem; font-weight: 600; padding: 2px 9px; border-radius: 999px; display: inline-block; }
.ev-strong   { background: #dbeafe; color: #1d4ed8; font-size: 0.7rem; font-weight: 600; padding: 2px 9px; border-radius: 999px; display: inline-block; }
.ev-moderate { background: #fef3c7; color: #92400e; font-size: 0.7rem; font-weight: 600; padding: 2px 9px; border-radius: 999px; display: inline-block; }
.ev-limited  { background: #f1f5f9; color: #64748b; font-size: 0.7rem; font-weight: 600; padding: 2px 9px; border-radius: 999px; display: inline-block; }
.dose-tag    { background: #f0fdf5; color: #166534; font-size: 0.7rem; font-weight: 600; padding: 2px 9px; border-radius: 999px; display: inline-block; }

/* pill-style tab bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px;
    background: #f1f5f9;
    border-radius: 11px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    color: #64748b !important;
}

.stTabs [aria-selected="true"] {
    background: #fff !important;
    color: #1d4ed8 !important;
    box-shadow: 0 2px 7px rgba(0, 0, 0, 0.07) !important;
}

/* sidebar logo */
.logo-wrap      { text-align: center; padding: 0.9rem 0 0.4rem; }
.logo-wrap .icon { font-size: 2.3rem; display: block; margin-bottom: 0.35rem; }
.logo-wrap .name { font-size: 1.05rem; font-weight: 700; }
.logo-wrap .sub  { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.07em; color: #607080 !important; }
</style>
""", unsafe_allow_html=True)


# ── constants ─────────────────────────────────────────────────────────────────

CATEGORIES = [
    "Sleep & Recovery", "Energy & Focus", "Immunity", "Weight Management",
    "Joint & Bone Health", "Digestive Health", "Heart Health", "Muscle & Performance",
    "Stress & Mood", "Women's Health", "Men's Health", "General Wellness",
]

# three sample products so users can try the app without typing anything
SAMPLES = {
    "DeepRest Pro (High-risk)": {
        "name": "DeepRest Pro",
        "category": "Sleep & Recovery",
        "ingredients": "Melatonin 20mg, Valerian Root Extract 600mg, L-Theanine 400mg, Magnesium Glycinate 200mg, 5-HTP 150mg, GABA 750mg, Ashwagandha KSM-66 300mg",
        "claims": "Clinically proven to cure insomnia. Guaranteed 8 hours of deep sleep. FDA approved formula.",
    },
    "NeuroBlast Energy (Dangerous)": {
        "name": "NeuroBlast Energy",
        "category": "Energy & Focus",
        "ingredients": "Caffeine Anhydrous 400mg, L-Tyrosine 2000mg, Alpha-GPC 600mg, Huperzine A 400mcg, Synephrine 100mg, DMAA 75mg, Yohimbine 20mg",
        "claims": "Unleash superhuman focus. 100% safe for daily use. No side effects guaranteed.",
    },
    "ImmunoShield Complete (Well-formulated)": {
        "name": "ImmunoShield Complete",
        "category": "Immunity",
        "ingredients": "Vitamin C 500mg, Vitamin D3 2000 IU, Zinc 15mg, Elderberry Extract 200mg, Echinacea 100mg, Quercetin 500mg, Selenium 55mcg",
        "claims": "Supports immune defense. Contains key vitamins and minerals for wellness.",
    },
}

GRADE_COLOR = {"A": "#16a34a", "B": "#2563eb", "C": "#d97706", "D": "#ea580c", "F": "#dc2626"}
GRADE_BG    = {"A": "#f0fdf4", "B": "#eff6ff", "C": "#fffbeb", "D": "#fff7ed", "F": "#fff1f2"}


# ── helpers ───────────────────────────────────────────────────────────────────

def get_client():
    # sidebar input takes priority; falls back to st.secrets for cloud deployments
    key = st.session_state.get("api_key", "") or st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    return anthropic.Anthropic(api_key=key)


def run_analysis(client, name, category, ingredients, claims):
    prompt = f"""You are an expert nutraceutical formulation scientist and regulatory specialist.
Analyze the supplement below and return ONLY valid JSON — no markdown, no extra text outside the JSON.

Product: {name}
Category: {category}
Ingredients: {ingredients}
Marketing Claims: {claims or "none provided"}

Return exactly this structure:
{{
  "extractedIngredients": [
    {{"name": "", "dosage": "", "unit": "", "function": ""}}
  ],
  "riskFlags": [
    {{"ingredient": "", "severity": "low|medium|high", "issue": "", "recommendation": ""}}
  ],
  "formObservations": [
    {{"type": "positive|neutral|concern", "observation": ""}}
  ],
  "claimsAnalysis": [
    {{"claim": "", "status": "compliant|caution|non-compliant", "reason": ""}}
  ],
  "overallScore": 0,
  "overallGrade": "A|B|C|D|F",
  "summary": "",
  "keyStrengths": [""],
  "keyWeaknesses": [""]
}}"""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        collected = ""
        status = st.empty()
        for chunk in stream.text_stream:
            collected += chunk
            status.caption(f"⏳ Analyzing… received {len(collected)} chars")
        status.empty()

    clean = collected.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def run_search(client, query):
    prompt = f"""You are a nutraceutical ingredient expert.
The user wants: "{query}"

Return ONLY valid JSON — no markdown, nothing outside the JSON object.

{{
  "relatedIngredients": [
    {{
      "name": "",
      "category": "",
      "mechanism": "",
      "typicalDosage": "",
      "evidence": "strong|moderate|limited",
      "notes": ""
    }}
  ],
  "searchSummary": ""
}}

Include 5–7 of the most relevant ingredients for this query."""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        collected = ""
        status = st.empty()
        for chunk in stream.text_stream:
            collected += chunk
            status.caption(f"🔍 Searching… received {len(collected)} chars")
        status.empty()

    clean = collected.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="logo-wrap">
        <span class="icon">🧪</span>
        <div class="name">NutraReview AI</div>
        <div class="sub">Formulation Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**🔑 API Key**")
    api_key = st.text_input("", type="password", key="api_key", placeholder="sk-ant-...")

    if not api_key:
        st.caption("⚠️ Paste your Anthropic API key above to get started.")
    else:
        st.markdown("<span style='color:#22c55e; font-size:0.82rem;'>✓ Key saved</span>", unsafe_allow_html=True)

    st.divider()

    st.markdown("**📦 Sample Products**")
    pick = st.selectbox("", ["— pick one —"] + list(SAMPLES.keys()), label_visibility="collapsed")
    if pick != "— pick one —":
        st.session_state["sample"] = SAMPLES[pick]
        st.markdown(
            f"<span style='color:#22c55e; font-size:0.82rem;'>✓ Loaded {SAMPLES[pick]['name']}</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown("**🧭 Pages**")
    page = st.radio("", ["🔬 Review Formulation", "🔍 Ingredient Search"], label_visibility="collapsed")

    st.divider()
    st.caption("For research & educational use only — not medical advice.")


# ── page banners ──────────────────────────────────────────────────────────────

client = get_client()

if page == "🔬 Review Formulation":
    st.markdown("""
    <div class="page-header">
        <span class="pill">AI-Powered Analysis</span>
        <h1>Formulation Review</h1>
        <p>Paste any supplement's ingredient list for an instant safety, dosing, and compliance review.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="page-header">
        <span class="pill">Semantic Search</span>
        <h1>Ingredient Search</h1>
        <p>Search by benefit or intent — the AI understands what you mean, not just the keywords.</p>
    </div>
    """, unsafe_allow_html=True)


# ── page 1 — review formulation ───────────────────────────────────────────────

if page == "🔬 Review Formulation":

    sample = st.session_state.get("sample", {})

    c1, c2 = st.columns(2)
    with c1:
        product_name = st.text_input(
            "🏷️ Product Name",
            value=sample.get("name", ""),
            placeholder="e.g. SleepWell Pro",
        )
    with c2:
        cat_idx = CATEGORIES.index(sample["category"]) if sample.get("category") in CATEGORIES else 0
        category = st.selectbox("📂 Category", CATEGORIES, index=cat_idx)

    ingredients = st.text_area(
        "🧬 Ingredients with Dosages",
        value=sample.get("ingredients", ""),
        height=105,
        placeholder="e.g. Melatonin 3mg, L-Theanine 200mg, Magnesium Glycinate 150mg…",
    )
    claims = st.text_area(
        "📢 Marketing Claims (optional)",
        value=sample.get("claims", ""),
        height=70,
        placeholder="e.g. Clinically proven to improve sleep quality by 40%…",
    )

    btn_col, hint_col = st.columns([2, 5])
    with btn_col:
        go = st.button(
            "🔬 Analyze Formulation",
            type="primary",
            disabled=not (client and product_name and ingredients),
        )
    with hint_col:
        if not client:
            st.markdown(
                "<div style='color:#f59e0b; font-size:0.84rem; padding-top:0.55rem;'>⬅️ Add your API key in the sidebar first</div>",
                unsafe_allow_html=True,
            )
        elif not (product_name and ingredients):
            st.markdown(
                "<div style='color:#94a3b8; font-size:0.84rem; padding-top:0.55rem;'>Fill in product name and ingredients to continue</div>",
                unsafe_allow_html=True,
            )

    if go:
        with st.spinner(""):
            try:
                result = run_analysis(client, product_name, category, ingredients, claims)
                st.session_state["review"] = result
                st.session_state["reviewed"] = product_name
                st.success("✅ Analysis complete!")
            except Exception as err:
                st.error(f"Something went wrong: {err}")

    # show results
    if "review" in st.session_state:
        r = st.session_state["review"]
        g     = r.get("overallGrade", "?")
        score = r.get("overallScore", 0)
        gc    = GRADE_COLOR.get(g, "#64748b")
        gb    = GRADE_BG.get(g, "#f8fafc")

        st.divider()

        # grade card + summary side by side
        grade_col, summary_col = st.columns([1, 4])
        with grade_col:
            st.markdown(f"""
            <div class="grade-box" style="background:{gb};">
                <div class="grade-letter" style="color:{gc};">{g}</div>
                <div class="grade-score"  style="color:{gc};">{score} / 100</div>
            </div>
            """, unsafe_allow_html=True)
        with summary_col:
            st.markdown(f'<div class="summary-card">{r.get("summary", "")}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # strengths and concerns
        s_col, w_col = st.columns(2)
        with s_col:
            rows = "".join(f'<div class="card-item">{x}</div>' for x in r.get("keyStrengths", []))
            st.markdown(
                f'<div class="strength-card"><div class="card-title" style="color:#15803d;">✅ Strengths</div>{rows}</div>',
                unsafe_allow_html=True,
            )
        with w_col:
            rows = "".join(f'<div class="card-item">{x}</div>' for x in r.get("keyWeaknesses", []))
            st.markdown(
                f'<div class="weakness-card"><div class="card-title" style="color:#c2410c;">⚠️ Concerns</div>{rows}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["📋 Ingredients", "🚨 Risk Flags", "🔭 Observations", "📢 Claims"])

        with tab1:
            rows = r.get("extractedIngredients", [])
            if rows:
                st.dataframe(
                    [
                        {
                            "Ingredient": x["name"],
                            "Dosage": f"{x['dosage']} {x['unit']}",
                            "Function": x["function"],
                        }
                        for x in rows
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

        with tab2:
            flags = r.get("riskFlags", [])
            if not flags:
                st.success("✅ No significant risk flags found.")
            for f in flags:
                sev = f["severity"]
                st.markdown(f"""
                <div class="risk-{sev}">
                    <span class="risk-pill pill-{sev}">{sev.upper()}</span>
                    <strong style="font-size:0.93rem; margin-left:7px;">{f["ingredient"]}</strong><br>
                    <span style="font-size:0.87rem;">{f["issue"]}</span><br>
                    <span style="font-size:0.81rem; opacity:0.78;">💡 {f["recommendation"]}</span>
                </div>
                """, unsafe_allow_html=True)

        with tab3:
            for obs in r.get("formObservations", []):
                t    = obs["type"]
                icon = "✅" if t == "positive" else "⚠️" if t == "concern" else "ℹ️"
                st.markdown(f'<div class="obs-{t}">{icon} {obs["observation"]}</div>', unsafe_allow_html=True)

        with tab4:
            claims_list = r.get("claimsAnalysis", [])
            if not claims_list:
                st.info("No marketing claims were submitted for review.")
            for c in claims_list:
                s         = c["status"]
                card_cls  = "claim-compliant"    if s == "compliant"     else "claim-caution"      if s == "caution" else "claim-noncompliant"
                pill_cls  = "cpill-compliant"    if s == "compliant"     else "cpill-caution"      if s == "caution" else "cpill-noncompliant"
                pill_text = "✅ Compliant"        if s == "compliant"     else "⚠️ Caution"          if s == "caution" else "❌ Non-compliant"
                st.markdown(f"""
                <div class="claim-card {card_cls}">
                    <span class="claim-pill {pill_cls}">{pill_text}</span>
                    <div style="font-size:0.88rem; font-style:italic; margin-bottom:4px;">"{c["claim"]}"</div>
                    <div style="font-size:0.81rem; opacity:0.72;">{c["reason"]}</div>
                </div>
                """, unsafe_allow_html=True)


# ── page 2 — ingredient search ────────────────────────────────────────────────

elif page == "🔍 Ingredient Search":

    quick_options = [
        "sleep support",
        "cognitive enhancement",
        "anti-inflammatory",
        "gut health",
        "testosterone support",
        "energy without stimulants",
    ]

    st.markdown(
        "<div style='font-size:0.82rem; font-weight:600; color:#64748b; margin-bottom:7px; text-transform:uppercase; letter-spacing:0.06em;'>Quick picks</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(len(quick_options))
    for i, q in enumerate(quick_options):
        if cols[i].button(q, key=f"q{i}", type="secondary"):
            st.session_state["search_query"] = q

    st.markdown("<br>", unsafe_allow_html=True)

    query = st.text_input(
        "🔍 What are you looking for?",
        value=st.session_state.get("search_query", ""),
        placeholder='e.g. "ingredients for sleep and cortisol management"',
        key="search_query",
    )

    sbtn_col, _ = st.columns([2, 5])
    with sbtn_col:
        do_search = st.button(
            "🔎 Search",
            type="primary",
            disabled=not (client and query.strip()),
        )

    if do_search and query.strip():
        with st.spinner(""):
            try:
                results = run_search(client, query)
                st.session_state["search_results"] = results
            except Exception as err:
                st.error(f"Search failed: {err}")

    if "search_results" in st.session_state:
        sr = st.session_state["search_results"]
        st.divider()
        st.markdown(
            f"<p style='color:#4a5568; font-size:0.88rem; line-height:1.65; font-style:italic;'>{sr.get('searchSummary', '')}</p>",
            unsafe_allow_html=True,
        )

        for ing in sr.get("relatedIngredients", []):
            ev = ing.get("evidence", "limited")
            st.markdown(f"""
            <div class="search-card">
                <div style="display:flex; align-items:center; gap:7px; flex-wrap:wrap; margin-bottom:9px;">
                    <span class="ing-name">{ing["name"]}</span>
                    <span class="tag">{ing["category"]}</span>
                    <span class="ev-{ev}">Evidence: {ev}</span>
                    <span class="dose-tag">💊 {ing["typicalDosage"]}</span>
                </div>
                <p style="margin:0 0 5px; font-size:0.87rem; color:#1e293b; line-height:1.6;">{ing["mechanism"]}</p>
                <p style="margin:0; font-size:0.81rem; color:#64748b; font-style:italic; line-height:1.5;">{ing["notes"]}</p>
            </div>
            """, unsafe_allow_html=True)
