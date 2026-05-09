import streamlit as st
import anthropic
import json

st.set_page_config(
    page_title="NutraReview AI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .risk-high { background: #FCEBEB; border-left: 4px solid #E24B4A; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .risk-medium { background: #FAEEDA; border-left: 4px solid #EF9F27; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .risk-low { background: #EAF3DE; border-left: 4px solid #639922; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .obs-positive { background: #E6F1FB; border-left: 4px solid #378ADD; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .obs-concern { background: #FAECE7; border-left: 4px solid #D85A30; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .obs-neutral { background: #F1EFE8; border-left: 4px solid #888780; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .claim-compliant { background: #EAF3DE; padding: 8px 12px; border-radius: 6px; margin: 4px 0; }
    .claim-caution { background: #FAEEDA; padding: 8px 12px; border-radius: 6px; margin: 4px 0; }
    .claim-noncompliant { background: #FCEBEB; padding: 8px 12px; border-radius: 6px; margin: 4px 0; }
    .grade-box { text-align: center; padding: 20px; border-radius: 12px; }
    .search-card { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; padding: 16px; margin: 8px 0; }
    .evidence-strong { color: #185FA5; font-weight: 600; }
    .evidence-moderate { color: #854F0B; font-weight: 600; }
    .evidence-limited { color: #5F5E5A; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

CATEGORIES = [
    "Sleep & Recovery", "Energy & Focus", "Immunity", "Weight Management",
    "Joint & Bone Health", "Digestive Health", "Heart Health", "Muscle & Performance",
    "Stress & Mood", "Women's Health", "Men's Health", "General Wellness"
]

SAMPLE_PRODUCTS = {
    "DeepRest Pro (High-risk)": {
        "name": "DeepRest Pro",
        "category": "Sleep & Recovery",
        "ingredients": "Melatonin 20mg, Valerian Root Extract 600mg, L-Theanine 400mg, Magnesium Glycinate 200mg, 5-HTP 150mg, GABA 750mg, Ashwagandha KSM-66 300mg",
        "claims": "Clinically proven to cure insomnia. Guaranteed 8 hours of deep sleep. FDA approved formula."
    },
    "NeuroBlast Energy (Dangerous)": {
        "name": "NeuroBlast Energy",
        "category": "Energy & Focus",
        "ingredients": "Caffeine Anhydrous 400mg, L-Tyrosine 2000mg, Alpha-GPC 600mg, Huperzine A 400mcg, Synephrine 100mg, DMAA 75mg, Yohimbine 20mg",
        "claims": "Unleash superhuman focus. 100% safe for daily use. No side effects guaranteed."
    },
    "ImmunoShield Complete (Well-formulated)": {
        "name": "ImmunoShield Complete",
        "category": "Immunity",
        "ingredients": "Vitamin C 500mg, Vitamin D3 2000 IU, Zinc 15mg, Elderberry Extract 200mg, Echinacea 100mg, Quercetin 500mg, Selenium 55mcg",
        "claims": "Supports immune defense. Contains key vitamins and minerals for wellness."
    }
}

GRADE_COLORS = {"A": "#185FA5", "B": "#3B6D11", "C": "#854F0B", "D": "#993C1D", "F": "#A32D2D"}
GRADE_BG = {"A": "#E6F1FB", "B": "#EAF3DE", "C": "#FAEEDA", "D": "#FAECE7", "F": "#FCEBEB"}

def get_client():
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)

def analyze_formulation(client, product_name, category, ingredients, claims):
    prompt = f"""You are an expert nutraceutical formulation scientist and regulatory specialist. Analyze the following supplement product and return ONLY valid JSON (no markdown, no explanation outside JSON).

Product Name: {product_name}
Category: {category}
Ingredients & Dosages: {ingredients}
Marketing Claims: {claims or "None provided"}

Return this exact JSON structure:
{{
  "extractedIngredients": [
    {{"name": "string", "dosage": "string", "unit": "string", "function": "string"}}
  ],
  "riskFlags": [
    {{"ingredient": "string", "severity": "low|medium|high", "issue": "string", "recommendation": "string"}}
  ],
  "formObservations": [
    {{"type": "positive|neutral|concern", "observation": "string"}}
  ],
  "claimsAnalysis": [
    {{"claim": "string", "status": "compliant|caution|non-compliant", "reason": "string"}}
  ],
  "overallScore": 0,
  "overallGrade": "A|B|C|D|F",
  "summary": "string (3-4 sentences)",
  "keyStrengths": ["string"],
  "keyWeaknesses": ["string"]
}}"""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        full_text = ""
        placeholder = st.empty()
        for text in stream.text_stream:
            full_text += text
            placeholder.caption(f"⏳ Analyzing... {len(full_text)} tokens received")
        placeholder.empty()

    clean = full_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

def semantic_search(client, query):
    prompt = f"""You are a nutraceutical ingredient expert. A user is searching for: "{query}"

Return ONLY valid JSON with this structure:
{{
  "relatedIngredients": [
    {{
      "name": "string",
      "category": "string",
      "mechanism": "string",
      "typicalDosage": "string",
      "evidence": "strong|moderate|limited",
      "notes": "string"
    }}
  ],
  "searchSummary": "string"
}}

List 5-7 ingredients most relevant to the search query."""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        full_text = ""
        placeholder = st.empty()
        for text in stream.text_stream:
            full_text += text
            placeholder.caption(f"⏳ Searching... {len(full_text)} tokens received")
        placeholder.empty()

    clean = full_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧪 NutraReview AI")
    st.markdown("*Supplement Formulation Intelligence*")
    st.divider()

    api_key = st.text_input("Anthropic API Key", type="password", key="api_key",
                             placeholder="sk-ant-...")
    if not api_key:
        st.warning("Enter your API key to get started.")

    st.divider()
    st.markdown("### 📦 Load Sample")
    sample_choice = st.selectbox("Choose a sample product", ["— select —"] + list(SAMPLE_PRODUCTS.keys()))
    if sample_choice != "— select —":
        s = SAMPLE_PRODUCTS[sample_choice]
        st.session_state["sample"] = s
        st.success(f"Loaded: {s['name']}")

    st.divider()
    st.markdown("### 🧭 Navigation")
    page = st.radio("", ["Review Formulation", "Ingredient Search"], label_visibility="collapsed")

    st.divider()
    st.caption("⚠️ For research & educational use only. Not medical advice.")

# ── Main ─────────────────────────────────────────────────────────────────────
st.title("NutraReview AI")
st.markdown("*AI-powered supplement formulation analysis — safety, dosing, compliance & ingredient science*")
st.divider()

client = get_client()

# ══════════════════════════════════════════════════════
# PAGE 1: REVIEW FORMULATION
# ══════════════════════════════════════════════════════
if page == "Review Formulation":

    # Pre-fill from sidebar sample
    sample = st.session_state.get("sample", {})

    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("Product Name", value=sample.get("name", ""), placeholder="e.g. SleepWell Pro")
    with col2:
        cat_index = CATEGORIES.index(sample["category"]) if sample.get("category") in CATEGORIES else 0
        category = st.selectbox("Category", CATEGORIES, index=cat_index)

    ingredients = st.text_area(
        "Ingredient List with Dosages",
        value=sample.get("ingredients", ""),
        height=100,
        placeholder="e.g. Melatonin 3mg, L-Theanine 200mg, Magnesium Glycinate 150mg…"
    )
    claims = st.text_area(
        "Marketing Claims (optional)",
        value=sample.get("claims", ""),
        height=70,
        placeholder="e.g. Clinically proven to improve sleep quality by 40%…"
    )

    analyze_btn = st.button("🔬 Analyze Formulation", type="primary", disabled=not (client and product_name and ingredients))
    if not client:
        st.caption("⬅️ Add your API key in the sidebar to enable analysis.")

    if analyze_btn:
        with st.spinner("Running AI formulation review…"):
            try:
                result = analyze_formulation(client, product_name, category, ingredients, claims)
                st.session_state["review"] = result
                st.session_state["reviewed_product"] = product_name
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    # ── Display Results ────────────────────────────────
    if "review" in st.session_state:
        r = st.session_state["review"]
        st.divider()
        st.subheader(f"Review: {st.session_state.get('reviewed_product', '')}")

        # Grade + Summary
        g = r.get("overallGrade", "?")
        score = r.get("overallScore", 0)
        col_grade, col_summary = st.columns([1, 4])
        with col_grade:
            st.markdown(f"""
            <div class="grade-box" style="background:{GRADE_BG.get(g,'#F1EFE8')};">
                <div style="font-size:56px; font-weight:700; color:{GRADE_COLORS.get(g,'#333')};">{g}</div>
                <div style="font-size:14px; color:{GRADE_COLORS.get(g,'#333')}; font-weight:600;">{score}/100</div>
            </div>
            """, unsafe_allow_html=True)
        with col_summary:
            st.info(r.get("summary", ""))

        # Strengths & Weaknesses
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("**✅ Key Strengths**")
            for s in r.get("keyStrengths", []):
                st.markdown(f"• {s}")
        with col_w:
            st.markdown("**⚠️ Key Concerns**")
            for w in r.get("keyWeaknesses", []):
                st.markdown(f"• {w}")

        st.divider()

        # Tabs for detail sections
        t1, t2, t3, t4 = st.tabs(["📋 Ingredients", "🚨 Risk Flags", "🔭 Observations", "📢 Claims"])

        with t1:
            ings = r.get("extractedIngredients", [])
            if ings:
                st.dataframe(
                    [{"Ingredient": i["name"], "Dosage": f"{i['dosage']} {i['unit']}", "Function": i["function"]} for i in ings],
                    use_container_width=True, hide_index=True
                )

        with t2:
            flags = r.get("riskFlags", [])
            if not flags:
                st.success("No significant risk flags identified.")
            for f in flags:
                sev = f["severity"]
                css = f"risk-{sev}"
                icon = "🔴" if sev == "high" else "🟠" if sev == "medium" else "🟢"
                st.markdown(f"""
                <div class="{css}">
                    <strong>{icon} {sev.upper()} — {f['ingredient']}</strong><br>
                    {f['issue']}<br>
                    <em>Recommendation: {f['recommendation']}</em>
                </div>
                """, unsafe_allow_html=True)

        with t3:
            for o in r.get("formObservations", []):
                t = o["type"]
                css = f"obs-{t}"
                icon = "✅" if t == "positive" else "⚠️" if t == "concern" else "ℹ️"
                st.markdown(f'<div class="{css}">{icon} {o["observation"]}</div>', unsafe_allow_html=True)

        with t4:
            ca = r.get("claimsAnalysis", [])
            if not ca:
                st.info("No marketing claims were provided for analysis.")
            for c in ca:
                status = c["status"]
                css = "claim-compliant" if status == "compliant" else "claim-caution" if status == "caution" else "claim-noncompliant"
                badge = "✅ COMPLIANT" if status == "compliant" else "⚠️ CAUTION" if status == "caution" else "❌ NON-COMPLIANT"
                st.markdown(f"""
                <div class="{css}">
                    <strong>{badge}</strong> &nbsp;|&nbsp; <em>"{c['claim']}"</em><br>
                    <small>{c['reason']}</small>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# PAGE 2: INGREDIENT SEARCH
# ══════════════════════════════════════════════════════
elif page == "Ingredient Search":
    st.subheader("🔍 Semantic Ingredient Search")
    st.markdown("Search by intent or benefit — powered by LLM reasoning, not just keywords.")

    quick = ["sleep support", "cognitive enhancement", "anti-inflammatory", "gut health", "testosterone support", "energy without stimulants"]
    st.markdown("**Quick searches:**")
    qcols = st.columns(len(quick))
    for i, q in enumerate(quick):
        if qcols[i].button(q, key=f"q{i}"):
            st.session_state["search_query"] = q

    query = st.text_input(
        "Search query",
        value=st.session_state.get("search_query", ""),
        placeholder='e.g. "ingredients for stress and cortisol management"',
        key="search_query"
    )

    search_btn = st.button("🔎 Search Ingredients", type="primary", disabled=not (client and query.strip()))

    if search_btn and query.strip():
        with st.spinner("Running semantic ingredient search…"):
            try:
                results = semantic_search(client, query)
                st.session_state["search_results"] = results
            except Exception as e:
                st.error(f"Search failed: {e}")

    if "search_results" in st.session_state:
        sr = st.session_state["search_results"]
        st.divider()
        st.markdown(f"*{sr.get('searchSummary', '')}*")
        st.markdown("")

        for ing in sr.get("relatedIngredients", []):
            ev = ing.get("evidence", "limited")
            ev_color = "#185FA5" if ev == "strong" else "#854F0B" if ev == "moderate" else "#5F5E5A"
            with st.container():
                st.markdown(f"""
                <div class="search-card">
                    <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:6px;">
                        <strong style="font-size:16px;">{ing['name']}</strong>
                        <span style="background:#e9ecef; border-radius:20px; padding:2px 10px; font-size:12px;">{ing['category']}</span>
                        <span style="color:{ev_color}; font-size:12px; font-weight:600;">Evidence: {ev}</span>
                        <span style="margin-left:auto; font-size:12px; color:#666;">Typical dose: {ing['typicalDosage']}</span>
                    </div>
                    <p style="margin:4px 0; font-size:14px;">{ing['mechanism']}</p>
                    <p style="margin:0; font-size:13px; color:#666; font-style:italic;">{ing['notes']}</p>
                </div>
                """, unsafe_allow_html=True)
