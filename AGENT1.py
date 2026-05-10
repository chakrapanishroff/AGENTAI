"""
AGENT1 — Agentic AI Demo with Telugu Explanations
Built with LangChain ReAct + GROQ + Streamlit
"""

import streamlit as st
import math
import datetime
import re
import time

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AGENT1 — Agentic AI Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0d0d1a; }
[data-testid="stSidebar"]          { background: #111128; border-right: 1px solid #6c63ff30; }
[data-testid="stHeader"]           { background: transparent; }

/* ── App Title ── */
.app-title { text-align:center; font-size:2.8em; font-weight:900;
             background:linear-gradient(135deg,#6c63ff,#3ecfcf);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.app-sub   { text-align:center; color:#7070aa; font-size:13px; margin-top:-8px; margin-bottom:16px; }

/* ── Telugu Hover Tooltip ── */
.tc             { position:relative; display:inline-block; }
.tc .badge      { background:linear-gradient(135deg,#6c63ff,#3ecfcf); color:#fff;
                  border-radius:50%; width:20px; height:20px; display:inline-flex;
                  align-items:center; justify-content:center; font-size:10px;
                  font-weight:800; cursor:help; margin-left:5px; vertical-align:middle; }
.tc .tcard      { visibility:hidden; opacity:0; width:300px;
                  background:linear-gradient(135deg,#1a1a38,#26265a);
                  border:1px solid #6c63ff55; border-radius:12px;
                  padding:14px; position:absolute; z-index:9999;
                  top:26px; left:0; transition:opacity 0.25s;
                  box-shadow:0 8px 28px rgba(108,99,255,0.4); }
.tc:hover .tcard { visibility:visible; opacity:1; }
.tc .tcard h4   { color:#3ecfcf; margin:0 0 7px; font-size:13px; }
.tc .tcard p    { margin:0; font-size:12px; line-height:1.7; color:#b5b5ee; }

/* ── Trace Blocks ── */
.step        { border-radius:10px; padding:12px 16px; margin:6px 0;
               font-size:13px; line-height:1.6; }
.step-label  { font-size:10px; font-weight:800; text-transform:uppercase;
               letter-spacing:1.5px; margin-bottom:6px; opacity:0.75; }
.s-thought   { background:#0d1e38; border-left:4px solid #4fc3f7; color:#b3e5fc;
               font-family:'Courier New',monospace; }
.s-action    { background:#0d2515; border-left:4px solid #66bb6a; color:#c8e6c9;
               font-family:'Courier New',monospace; }
.s-obs       { background:#2a1800; border-left:4px solid #ffa726; color:#ffe0b2;
               font-family:'Courier New',monospace; }
.s-final     { background:#1a0e38; border-left:4px solid #ce93d8;
               color:#f3e5f5; font-size:14px; }

/* ── Concept Card ── */
.concept-card { background:linear-gradient(135deg,#111128,#181840);
                border:1px solid #6c63ff30; border-radius:14px;
                padding:20px; margin:10px 0; }
.concept-card h3 { color:#6c63ff; margin-top:0; }
.telugu      { color:#3ecfcf; font-size:14.5px; line-height:1.9; }

/* ── Tool Card ── */
.tool-card   { background:#111128; border:1px solid #3ecfcf30; border-radius:12px;
               padding:16px; margin:8px 0; }
.tool-name   { color:#3ecfcf; font-weight:700; font-size:15px; margin-bottom:4px; }
.tool-desc   { color:#8888bb; font-size:12px; }
.tool-te     { color:#aa99ff; font-size:12px; font-style:italic; margin-top:8px;
               border-top:1px solid #ffffff10; padding-top:8px; }

/* ── Compare Row ── */
.cmp-yes  { color:#66bb6a; }
.cmp-no   { color:#ef5350; }
.cmp-part { color:#ffa726; }

/* ── Architecture box ── */
.arch-box { background:#0d0d1a; border:1px solid #6c63ff40; border-radius:12px;
            padding:20px; text-align:center; font-family:'Courier New',monospace;
            font-size:13px; color:#b0b0ee; line-height:2; }
.arch-box .node { background:linear-gradient(135deg,#1a1a40,#252560);
                  border:1px solid #6c63ff; border-radius:8px;
                  display:inline-block; padding:6px 16px; margin:4px;
                  color:#c8c8ff; }
.arch-box .arrow { color:#3ecfcf; margin:0 8px; }
</style>
""", unsafe_allow_html=True)

# ─── TELUGU CONCEPTS ──────────────────────────────────────────────────────────
TE = {
    "agent":    ("AI Agent అంటే?",
                 "AI Agent స్వయంగా నిర్ణయాలు తీసుకుని Tools వాడి లక్ష్యాన్ని చేరే system. "
                 "Chatbot కేవలం Q&A చేస్తుంది — Agent plan, act, observe చేస్తుంది!"),
    "react":    ("ReAct అంటే?",
                 "ReAct = Reasoning + Acting. Agent: Thought → Action → Observation loop లో "
                 "పని చేస్తుంది. సమాధానం వచ్చే వరకు ఈ cycle repeat అవుతుంది."),
    "tools":    ("Tools అంటే?",
                 "Tools = Agent వాడే special capabilities. Calculator, Converter, Analyzer — "
                 "Agent సమస్యను బట్టి సరైన tool automatically select చేస్తుంది."),
    "planning": ("Planning అంటే?",
                 "Agent పెద్ద task ను చిన్న steps గా break చేస్తుంది. ఏ tool ఎప్పుడు "
                 "వాడాలో decide చేస్తుంది — Human problem-solving లాగే!"),
    "obs":      ("Observation అంటే?",
                 "Tool result ని Agent observe చేస్తుంది. Correct అయితే Final Answer. "
                 "లేకపోతే మళ్ళీ different approach try చేస్తుంది — Self-correction!"),
    "agentic":  ("Agentic AI అంటే?",
                 "2026 లో అతి పెద్ద trend! Complex multi-step tasks autonomously complete "
                 "చేసే AI systems. Chatbots కంటే చాలా powerful!"),
    "llm":      ("LLM అంటే?",
                 "Large Language Model — Agent యొక్క brain. Tool ఎప్పుడు వాడాలో, "
                 "ఏ input ఇవ్వాలో, final answer ఏమిటో ఇది decide చేస్తుంది."),
    "memory":   ("Agent Memory అంటే?",
                 "Agent conversation history remember చేస్తుంది. Previous steps, tools "
                 "used, observations — అన్నీ memory లో ఉంటాయి. Multi-turn possible!"),
}

def tip(key):
    """Return Telugu hover tooltip HTML"""
    t, b = TE[key]
    return (f'<span class="tc"><span class="badge">తె</span>'
            f'<div class="tcard"><h4>📖 {t}</h4><p>{b}</p></div></span>')

# ─── TOOL FUNCTIONS ───────────────────────────────────────────────────────────
def tool_calculator(expr: str) -> str:
    try:
        safe = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
        safe.update({'abs': abs, 'round': round, 'pow': pow, 'int': int, 'float': float})
        result = eval(expr.strip(), {"__builtins__": {}}, safe)
        return f"✅ {expr} = {result}"
    except Exception as e:
        return f"❌ Cannot evaluate '{expr}': {e}"

def tool_datetime(q: str) -> str:
    now = datetime.datetime.now()
    return (f"📅 {now.strftime('%A, %B %d, %Y')} | "
            f"⏰ {now.strftime('%I:%M %p')} | "
            f"Day #{now.timetuple().tm_yday} of {now.year} | "
            f"Week #{now.isocalendar()[1]}")

def tool_text_analyzer(text: str) -> str:
    words = text.split()
    sents = sum(1 for c in text if c in '.!?')
    paras = len([p for p in text.split('\n\n') if p.strip()])
    return (f"📝 Words: {len(words)} | Chars: {len(text)} | "
            f"Sentences: {max(sents,1)} | Unique words: {len(set(w.lower() for w in words))} | "
            f"Paragraphs: {paras} | Avg word length: {sum(len(w) for w in words)/max(len(words),1):.1f}")

def tool_data_stats(nums_str: str) -> str:
    try:
        nums = [float(x.strip()) for x in re.split(r'[,;]', nums_str) if x.strip()]
        if not nums:
            return "❌ No valid numbers found. Example input: 10, 20, 30, 40"
        n = len(nums)
        mean = sum(nums) / n
        s = sorted(nums)
        med = s[n//2] if n % 2 else (s[n//2-1] + s[n//2]) / 2
        var = sum((x - mean)**2 for x in nums) / n
        rng = max(nums) - min(nums)
        return (f"📊 Count: {n} | Sum: {sum(nums):.2f} | Mean: {mean:.2f} | "
                f"Median: {med:.2f} | Min: {min(nums):.2f} | Max: {max(nums):.2f} | "
                f"Std Dev: {var**0.5:.2f} | Range: {rng:.2f}")
    except Exception as e:
        return f"❌ Error: {e}"

def tool_unit_converter(q: str) -> str:
    ql = q.lower()
    nums = re.findall(r'[\d.]+', ql)
    if not nums:
        return "❌ No number found. Example: '100 km to miles' or '37 celsius to fahrenheit'"
    v = float(nums[0])
    conversions = [
        (['km', 'mile'],       lambda x: f"🔄 {x} km = {x*0.621371:.4f} miles"),
        (['mile', 'km'],       lambda x: f"🔄 {x} miles = {x*1.60934:.4f} km"),
        (['celsius', 'fahr'],  lambda x: f"🌡️ {x}°C = {x*9/5+32:.2f}°F = {x+273.15:.2f}K"),
        (['fahr', 'celsius'],  lambda x: f"🌡️ {x}°F = {(x-32)*5/9:.2f}°C"),
        (['kg', 'pound'],      lambda x: f"⚖️ {x} kg = {x*2.20462:.4f} lbs"),
        (['pound', 'kg'],      lambda x: f"⚖️ {x} lbs = {x*0.453592:.4f} kg"),
        (['meter', 'feet'],    lambda x: f"📏 {x} m = {x*3.28084:.4f} feet"),
        (['feet', 'meter'],    lambda x: f"📏 {x} ft = {x*0.3048:.4f} m"),
        (['inch', 'cm'],       lambda x: f"📏 {x} in = {x*2.54:.4f} cm"),
        (['cm', 'inch'],       lambda x: f"📏 {x} cm = {x/2.54:.4f} inches"),
        (['liter', 'gallon'],  lambda x: f"🧪 {x} L = {x*0.264172:.4f} gallons"),
        (['gallon', 'liter'],  lambda x: f"🧪 {x} gal = {x*3.78541:.4f} L"),
        (['gram', 'ounce'],    lambda x: f"⚖️ {x} g = {x*0.035274:.4f} oz"),
    ]
    for keys, fn in conversions:
        if all(k in ql for k in keys):
            return fn(v)
    return (f"❓ Conversion not recognized for '{q}'. "
            f"Supported: km↔miles, °C↔°F, kg↔lbs, m↔feet, in↔cm, L↔gallons, g↔oz")

def tool_word_counter(text: str) -> str:
    """Count specific word frequencies"""
    words = re.findall(r'\b\w+\b', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    top = sorted(freq.items(), key=lambda x: -x[1])[:10]
    top_str = ', '.join(f"'{w}':{c}" for w, c in top)
    return f"🔤 Total tokens: {len(words)} | Unique: {len(freq)} | Top words: {top_str}"

# ─── TOOL METADATA ────────────────────────────────────────────────────────────
# (icon, name, function, description_en, description_te)
TOOLS_META = [
    ("🧮", "Calculator",
     tool_calculator,
     "Evaluate math: sqrt, log, sin, cos, pi, e, abs, factorial, **, +, -, *, /",
     "గణిత calculations కి. sqrt(144), 2**10, sin(pi/2) అన్నీ చేయగలదు."),
    ("📅", "DateTime",
     tool_datetime,
     "Get current date, time, day of week, week number.",
     "ప్రస్తుత తేదీ, సమయం చెప్పడానికి."),
    ("📝", "TextAnalyzer",
     tool_text_analyzer,
     "Analyze text: word count, char count, sentence count, unique words.",
     "Text statistics కి. Words, sentences, unique words analyze చేయగలదు."),
    ("📊", "DataStats",
     tool_data_stats,
     "Stats on comma-separated numbers: mean, median, min, max, std dev.",
     "Numbers కి statistics. Mean, Median, Std Dev calculate చేయగలదు."),
    ("🔄", "UnitConverter",
     tool_unit_converter,
     "Convert: km-miles, C-F, kg-lbs, meters-feet, inches-cm.",
     "Units convert చేయడానికి. Distance, Temperature, Weight support!"),
    ("🔤", "WordFrequency",
     tool_word_counter,
     "Count word frequencies in text. Returns top 10 frequent words.",
     "Text లో words frequency count చేయడానికి."),
]

SAMPLE_QUERIES = [
    "What is sqrt(1764) + 2 raised to the power of 10?",
    "Analyze: Artificial Intelligence is transforming every industry in 2026. The future of AI looks bright!",
    "Statistics for these numbers: 45, 78, 23, 56, 89, 34, 67, 12, 90, 55, 71, 38",
    "Convert 37 Celsius to Fahrenheit, and also convert 150 km to miles.",
    "What day and time is it right now? Also what week number are we in?",
    "Calculate log(10000) + factorial(5) + sqrt(256), then tell me the result",
    "Count word frequency in: Machine learning is amazing. Learning makes machines smarter every day.",
]

# ─── AGENT BUILDER ────────────────────────────────────────────────────────────
REACT_TEMPLATE = """Assistant with tools. Answer using tools only.

Tools:
{tools}

Format:
Thought: reasoning
Action: one of [{tool_names}]
Action Input: tool input
Observation: result
(repeat as needed)
Thought: I know the answer
Final Answer: answer

Question: {input}
Thought:{agent_scratchpad}"""

def build_agent(api_key: str, model: str, selected_tool_names: list):
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_groq import ChatGroq
    from langchain.tools import Tool
    from langchain.prompts import PromptTemplate

    lc_tools = []
    for icon, name, fn, desc, _ in TOOLS_META:
        if name in selected_tool_names:
            lc_tools.append(Tool(name=name, func=fn, description=desc))

    if not lc_tools:
        return None

    llm = ChatGroq(api_key=api_key, model=model, temperature=0)
    prompt = PromptTemplate(
        template=REACT_TEMPLATE,
        input_variables=["tools", "tool_names", "input", "agent_scratchpad"]
    )
    agent = create_react_agent(llm=llm, tools=lc_tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=lc_tools,
        verbose=False,
        return_intermediate_steps=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )
    return executor

# ─── TRACE RENDERER ───────────────────────────────────────────────────────────
def render_trace(intermediate_steps, final_answer):
    st.markdown("### 🔍 Agent Execution Trace")

    if not intermediate_steps:
        st.info("Agent answered directly without using any tools.")
    else:
        for i, (action, observation) in enumerate(intermediate_steps, 1):
            log = getattr(action, 'log', '')
            # Extract thought from log
            m = re.search(r'(?:^|\n)\s*(.*?)(?=\nAction:)', log, re.DOTALL)
            thought = m.group(1).strip() if m else log.strip()
            thought = re.sub(r'^Thought:\s*', '', thought).strip()

            with st.container():
                st.markdown(f"**Step {i}**")

                if thought:
                    st.markdown(
                        f'<div class="step s-thought">'
                        f'<div class="step-label">💭 Thought</div>{thought}</div>',
                        unsafe_allow_html=True)

                st.markdown(
                    f'<div class="step s-action">'
                    f'<div class="step-label">⚡ Action → {action.tool}</div>'
                    f'<b>Tool:</b> {action.tool}<br>'
                    f'<b>Input:</b> {action.tool_input}</div>',
                    unsafe_allow_html=True)

                st.markdown(
                    f'<div class="step s-obs">'
                    f'<div class="step-label">👁️ Observation</div>{observation}</div>',
                    unsafe_allow_html=True)

                st.markdown("")

    st.markdown(
        f'<div class="step s-final">'
        f'<div class="step-label">✅ Final Answer</div>{final_answer}</div>',
        unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    api_key = st.text_input("🔑 GROQ API Key", type="password",
                             placeholder="gsk_...",
                             help="Free key at console.groq.com")

    model = st.selectbox("🧠 LLM Model", [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama-3.3-70b-specdec",
        "qwen/qwen3-32b",
    ], help="llama-3.1-8b-instant = fastest | llama-3.3-70b-versatile = most capable")

    st.markdown("#### 🛠️ Enable Tools")
    selected_tools = []
    for icon, name, *_ in TOOLS_META:
        if st.checkbox(f"{icon} {name}", value=True, key=f"tool_{name}"):
            selected_tools.append(name)

    st.markdown("---")
    st.markdown("#### 💡 Sample Queries")
    for i, q in enumerate(SAMPLE_QUERIES):
        if st.button(f"▶ Q{i+1}", key=f"sq_{i}", help=q, use_container_width=True):
            st.session_state['main_query'] = q

    st.markdown("---")
    st.markdown(
        "<span style='color:#555;font-size:11px'>"
        "🤖 AGENT1 | LangChain ReAct<br>"
        "GROQ LLM | Streamlit UI<br>"
        "Telugu Explanations తో</span>",
        unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">🤖 AGENT1</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-sub">Agentic AI Demo — Telugu Explanations తో | '
    'LangChain ReAct + GROQ + Streamlit</div>',
    unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 Agent Demo",
    "🧠 Concepts (Telugu)",
    "🛠️ Tools Explorer",
    "📊 Chatbot vs Agent"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: AGENT DEMO
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Concept badges row
    st.markdown(
        "Key Concepts: "
        f"**Agent**{tip('agent')}&nbsp;&nbsp;"
        f"**ReAct**{tip('react')}&nbsp;&nbsp;"
        f"**Tools**{tip('tools')}&nbsp;&nbsp;"
        f"**Planning**{tip('planning')}&nbsp;&nbsp;"
        f"**Observation**{tip('obs')}",
        unsafe_allow_html=True)
    st.markdown("")

    # Architecture diagram (ASCII)
    st.markdown("""
    <div class="arch-box">
        <span class="node">👤 User Query</span>
        <span class="arrow">→</span>
        <span class="node">🧠 LLM (GROQ)</span>
        <span class="arrow">→</span>
        <span class="node">💭 Thought</span>
        <span class="arrow">→</span>
        <span class="node">⚡ Action</span>
        <span class="arrow">→</span>
        <span class="node">🛠️ Tool</span><br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <span style="color:#6c63ff">↑ loop until done ↑</span>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <span class="arrow">←</span>
        <span class="node">👁️ Observation</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    # Query input
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        query = st.text_input(
            "🎯 Ask the Agent:",
            placeholder="e.g. What is sqrt(1764) + 2^10? Also convert 37°C to °F.",
            key="main_query"
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("▶ Run", use_container_width=True, type="primary")

    if run_btn:
        if not api_key:
            st.error("⚠️ Please enter your GROQ API Key in the sidebar. (Free at console.groq.com)")
        elif not query.strip():
            st.warning("⚠️ Please enter a question first.")
        elif not selected_tools:
            st.warning("⚠️ Please enable at least one tool in the sidebar.")
        else:
            try:
                executor = build_agent(api_key, model, selected_tools)
                with st.spinner("🤖 Agent is thinking, planning, and acting..."):
                    t0 = time.time()
                    result = executor.invoke({"input": query})
                    elapsed = time.time() - t0

                steps = result.get('intermediate_steps', [])
                tools_called = [a.tool for a, _ in steps]

                # Metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("⏱️ Time", f"{elapsed:.1f}s")
                c2.metric("🔄 Steps", len(steps))
                c3.metric("🛠️ Tools Called", len(tools_called))
                c4.metric("🔁 Unique Tools", len(set(tools_called)))

                if tools_called:
                    st.markdown(
                        "**Tool sequence:** " +
                        " → ".join(f"`{t}`" for t in tools_called))

                st.markdown("---")
                render_trace(steps, result.get('output', ''))

            except Exception as e:
                err = str(e)
                st.error(f"❌ Agent Error: {err}")
                if '413' in err or 'tokens per minute' in err.lower() or 'request too large' in err.lower():
                    st.warning(
                        "⚠️ **Token Limit Exceeded (Free Tier)**\n\n"
                        "Your query + tool descriptions exceeded GROQ's free limit.\n\n"
                        "**Fix options:**\n"
                        "1. 🔄 Switch to **`llama-3.3-70b-versatile`** in the sidebar (higher TPM limit)\n"
                        "2. ✂️ Keep your query **shorter and simpler**\n"
                        "3. 🛠️ **Uncheck unused tools** in the sidebar to reduce prompt size\n"
                        "4. ⏳ Wait 1 minute and try again (TPM = tokens per minute, resets each minute)"
                    )
                elif '401' in err or 'auth' in err.lower() or 'api' in err.lower():
                    st.info("💡 Check your GROQ API key — authentication issue.")
                elif 'rate' in err.lower() or '429' in err:
                    st.info("💡 Rate limit hit. Wait 30 seconds and try again.")
                elif 'decommissioned' in err.lower() or 'model' in err.lower():
                    st.info("💡 Model not available. Switch to `llama-3.3-70b-versatile` in the sidebar.")
                else:
                    st.info("💡 Try a simpler query or switch to a different model.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: CONCEPTS (TELUGU)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🧠 Agentic AI Concepts — Telugu లో నేర్చుకుందాం!")

    concepts = [
        ("🤖", "Agentic AI అంటే ఏమిటి?",
         "The biggest AI shift of 2026",
         """Agentic AI అనేది 2026 లో అతి పెద్ద technological shift.

Traditional Chatbot:
  User → "What's 25 × 4?" → Bot → "100" ✅ (simple, one-step)

Agentic AI:
  User → "Plan my trip to Hyderabad next week" →
  Agent: Checks date → Searches hotels → Calculates budget →
         Books tickets → Sets reminders → All automatically! ✅

Gartner prediction: 2026 చివరికి 40% enterprise apps లో
AI Agents embedded అవుతాయి (2025 లో కేవలం 5% మాత్రమే!)"""),

        ("💭", "ReAct Framework అంటే ఏమిటి?",
         "How agents think step by step",
         """ReAct = Reasoning + Acting — ఇది Agent యొక్క thought process.

ప్రతి step లో Agent ఇలా చేస్తుంది:

1. 💭 THOUGHT: "User 37°C to °F convert చేయమని అడిగాడు.
                  UnitConverter tool వాడాలి."

2. ⚡ ACTION: UnitConverter tool call చేస్తుంది
   Input: "37 celsius to fahrenheit"

3. 👁️ OBSERVATION: "🌡️ 37°C = 98.6°F" — result వస్తుంది

4. 💭 THOUGHT: "సమాధానం దొరికింది. Final Answer ఇవ్వగలను."

5. ✅ FINAL ANSWER: "37°C is equal to 98.6°F"

ఇది human problem-solving ని exactly copy చేస్తుంది!"""),

        ("🛠️", "Tools అంటే ఏమిటి?",
         "The hands of an AI agent",
         """Tools అనేవి Agent యొక్క capabilities — మనుషులు instruments వాడినట్లు!

AGENT1 లో tools:
  🧮 Calculator  — math expressions solve చేయడానికి
  📅 DateTime    — current date & time కి
  📝 TextAnalyzer — text statistics కి
  📊 DataStats   — numbers analysis కి
  🔄 UnitConverter — units convert చేయడానికి
  🔤 WordFrequency — word count కి

Agent automatically:
  ✅ సరైన tool select చేస్తుంది
  ✅ Correct input ఇస్తుంది
  ✅ Result process చేస్తుంది
  ✅ ఒక్క query లో multiple tools వాడగలదు!"""),

        ("🧠", "LLM — Agent యొక్క Brain",
         "The intelligence behind every agent",
         """LLM (Large Language Model) అనేది Agent యొక్క reasoning engine.

LLM చేసే పనులు:
  📖 User question అర్థం చేసుకోవడం
  🎯 Goal identify చేయడం
  📋 Multi-step plan తయారు చేయడం
  🛠️ Correct tool select చేయడం
  📝 Tool input formulate చేయడం
  🔍 Observation analyze చేయడం
  ✅ Final answer synthesize చేయడం

AGENT1 లో మనం GROQ platform వాడుతున్నాం.
GROQ = ultra-fast LLM inference (tokens per second బాగా ఎక్కువ!)
Models: LLaMA 3, Mixtral, Gemma2"""),

        ("🔁", "Self-Correction & Iteration",
         "Agents learn from mistakes within a session",
         """Agent ఒక్కసారి fail అయినా give up చేయదు!

Example:
  Step 1: Calculator తో 'sqrt 144' try చేసింది → Error
  Step 2: 💭 Thought: "Input format తప్పు. 'sqrt(144)' గా try చేస్తా"
  Step 3: Calculator 'sqrt(144)' → "✅ 12.0" → Success!

Self-correction process:
  ❌ Error observation → 🔄 Strategy change → ✅ Retry → Success

Max iterations reach అయినప్పుడు మాత్రమే stop అవుతుంది.
ఇది human persistence ని exactly mirror చేస్తుంది!"""),

        ("🌐", "Real-World Applications",
         "Agents are changing every industry",
         """Real world లో Agentic AI ఇప్పుడు వాడుతున్న use cases:

🏥 Healthcare:
   Patient data analyze → Appointment book → Follow-up schedule

🏦 Finance:
   Transaction monitor → Fraud detect → Alert send → Block card

🛒 E-Commerce:
   Order track → Delay detect → Customer notify → Refund process

🎓 Education:
   Student performance analyze → Weak areas identify →
   Personalized content suggest → Progress track

📞 Customer Support:
   Ticket receive → Category classify → Solution find →
   Auto-reply → Escalate if needed

అన్నీ autonomously, 24/7, human intervention లేకుండా!"""),
    ]

    for icon, title, subtitle, body in concepts:
        with st.expander(f"{icon} {title}", expanded=False):
            st.markdown(f"*{subtitle}*")
            st.markdown(
                f'<div class="concept-card">'
                f'<p class="telugu">{body.replace(chr(10), "<br>")}</p>'
                f'</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: TOOLS EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 🛠️ Tools Explorer")
    st.markdown("AGENT1 లో available tools మరియు వాటి capabilities:")
    st.markdown("")

    for icon, name, fn, desc_en, desc_te in TOOLS_META:
        c1, c2 = st.columns([1, 4])
        with c1:
            st.markdown(
                f'<div style="font-size:52px;text-align:center;padding-top:10px">{icon}</div>',
                unsafe_allow_html=True)
        with c2:
            st.markdown(
                f'<div class="tool-card">'
                f'<div class="tool-name">{name}</div>'
                f'<div class="tool-desc">📌 {desc_en}</div>'
                f'<div class="tool-te">తె: {desc_te}</div>'
                f'</div>',
                unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")
    st.markdown("### 🧪 Test a Tool Directly")
    st.markdown("Agent లేకుండా ఒక tool directly test చేయండి:")

    col_sel, col_inp = st.columns([1, 2])
    with col_sel:
        tool_names_display = [f"{icon} {name}" for icon, name, *_ in TOOLS_META]
        chosen = st.selectbox("Select Tool", tool_names_display)
    with col_inp:
        tool_in = st.text_input("Tool Input",
            placeholder="e.g. sqrt(144) + 2**10  |  37 celsius to fahrenheit  |  10, 20, 30, 40")

    if st.button("⚡ Test Tool", type="primary") and tool_in:
        idx = tool_names_display.index(chosen)
        _, _, fn, *_ = TOOLS_META[idx]
        with st.spinner("Running tool..."):
            out = fn(tool_in)
        st.success(out)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: CHATBOT vs AGENT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📊 Chatbot vs AI Agent — తేడా ఏమిటి?")
    st.markdown("")

    comparisons = [
        ("Single Q&A",              "✅ Yes",      "✅ Yes"),
        ("Multi-step reasoning",    "❌ No",       "✅ Yes"),
        ("Tool usage",              "❌ No",       "✅ Yes"),
        ("Real-time calculations",  "❌ No",       "✅ Yes"),
        ("Self-correction",         "❌ No",       "✅ Yes"),
        ("Autonomous planning",     "❌ No",       "✅ Yes"),
        ("Complex task execution",  "❌ No",       "✅ Yes"),
        ("Multiple tools per query","❌ No",       "✅ Yes"),
        ("Handles ambiguity",       "⚡ Limited",  "✅ Yes"),
        ("Memory across steps",     "⚡ Limited",  "✅ Yes"),
        ("Industry adoption 2026",  "✅ Mature",   "🚀 Exploding"),
    ]

    hcol1, hcol2, hcol3 = st.columns([3, 2, 2])
    with hcol1: st.markdown("**Feature**")
    with hcol2: st.markdown("**💬 Chatbot**")
    with hcol3: st.markdown("**🤖 AI Agent**")
    st.markdown("---")

    for feat, bot_val, agent_val in comparisons:
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1: st.markdown(f"*{feat}*")
        with c2:
            cls = "cmp-yes" if "✅" in bot_val else "cmp-no" if "❌" in bot_val else "cmp-part"
            st.markdown(f'<span class="{cls}">{bot_val}</span>', unsafe_allow_html=True)
        with c3:
            cls = "cmp-yes" if "✅" in agent_val else "cmp-no" if "❌" in agent_val else "cmp-part"
            st.markdown(f'<span class="{cls}">{agent_val}</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="concept-card">
        <h3>🔑 Key Insight — Telugu లో Summary</h3>
        <p class="telugu">
        💬 <b>Chatbot</b> = Question → Answer (simple, one-step, no tools)<br><br>
        🤖 <b>AI Agent</b> = Goal → Plan → Tools → Actions → Verify → Answer (complex, autonomous)<br><br>
        📈 <b>2026 Industry Trend:</b> Chatbots నుండి Agents కి rapid shift జరుగుతోంది.<br>
        Gartner: 2026 లో 40% enterprise apps లో Agents embedded అవుతాయి (2025 లో 5% మాత్రమే!)<br><br>
        💰 <b>Business Impact:</b><br>
        • AI inference cost 85% తగ్గింది (2023 → 2026)<br>
        • Average ROI: 340% first year లోనే<br>
        • Cost per interaction: $6 (human) → $0.50 (Agent)<br><br>
        🚀 <b>Bottom Line:</b> Chatbots are the past. <b>Agents are the future.</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Evolution timeline
    st.markdown("### 📅 Evolution Timeline")
    timeline = [
        ("2020-21", "🤖", "Rule-Based Chatbots",    "Fixed scripts, decision trees, no AI"),
        ("2022",    "💬", "LLM Chatbots",           "GPT-3 era — natural conversation, Q&A"),
        ("2023",    "🔌", "Plugin Chatbots",        "ChatGPT plugins — web search, code"),
        ("2024",    "🔗", "RAG Applications",       "Documents + LLM — knowledge retrieval"),
        ("2025",    "🛠️", "Tool-Augmented Agents",  "LangChain Agents — tool orchestration"),
        ("2026 🔥", "🚀", "Agentic AI Systems",     "Autonomous, multi-step, self-correcting — YOU ARE HERE!"),
    ]
    for year, icon, title, desc in timeline:
        highlight = "border:1px solid #6c63ff;" if "🔥" in year else "border:1px solid #ffffff10;"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:16px;padding:10px;'
            f'border-radius:10px;margin:6px 0;background:#111128;{highlight}">'
            f'<span style="color:#3ecfcf;font-weight:700;min-width:70px;font-size:13px">{year}</span>'
            f'<span style="font-size:24px">{icon}</span>'
            f'<div><div style="color:#c8c8ff;font-weight:600;font-size:14px">{title}</div>'
            f'<div style="color:#7070aa;font-size:12px">{desc}</div></div></div>',
            unsafe_allow_html=True)
