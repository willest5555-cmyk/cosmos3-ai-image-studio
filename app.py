import streamlit as st
import requests
import base64
import time
import json
import random
from PIL import Image
from io import BytesIO
from datetime import datetime

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Cosmos 3 AI Image Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://huggingface.co/nvidia/Cosmos3-Super-Text2Image",
        "Report a bug": None,
        "About": "Cosmos 3 AI Image Studio — Powered by NVIDIA & Google Gemini",
    },
)

# ─────────────────────────────────────────────
# Custom CSS  (NVIDIA green dark theme)
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ─────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #090d16;
    color: #e2e8f0;
}

/* ── Sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0c1220 !important;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #76b900;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 1.2rem;
}

/* ── Tabs ────────────────────────────────────── */
[data-testid="stTabs"] button {
    color: #94a3b8 !important;
    font-weight: 500;
    border-radius: 8px 8px 0 0;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #76b900 !important;
    border-bottom: 2px solid #76b900 !important;
    background: #131c2e !important;
}
[data-testid="stTabsContent"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 0 12px 12px 12px;
    padding: 1.5rem;
}

/* ── Buttons ─────────────────────────────────── */
.stButton > button {
    background: #76b900 !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(118,185,0,0.2);
}
.stButton > button:hover {
    background: #87cf03 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(118,185,0,0.35) !important;
}
.stButton > button:disabled {
    background: #1e293b !important;
    color: #64748b !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Inputs ─────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #0a0f1a !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #76b900 !important;
    box-shadow: 0 0 0 2px rgba(118,185,0,0.15) !important;
}
.stSlider [data-testid="stSlider"] {
    accent-color: #76b900;
}

/* ── Metric cards ──────────────────────────── */
[data-testid="stMetric"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 0.75rem 1rem;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: #76b900 !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
}

/* ── Cards / containers ─────────────────────── */
.card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.card-title {
    color: #76b900;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

/* ── Status badges ───────────────────────────── */
.badge-green {
    background: rgba(118,185,0,0.12);
    color: #76b900;
    border: 1px solid rgba(118,185,0,0.25);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.65rem;
    font-weight: 600;
    display: inline-block;
}
.badge-amber {
    background: rgba(245,158,11,0.12);
    color: #f59e0b;
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.65rem;
    font-weight: 600;
    display: inline-block;
}

/* ── Header banner ──────────────────────────── */
.header-banner {
    background: linear-gradient(135deg, #0c1220 0%, #111827 50%, #0c1220 100%);
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
}
.header-icon {
    background: #76b900;
    border-radius: 12px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 0 20px rgba(118,185,0,0.4);
    flex-shrink: 0;
}
.header-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #fff;
    margin: 0;
}
.header-sub {
    color: #64748b;
    font-size: 0.75rem;
    margin: 2px 0 0;
}

/* ── Example prompt cards ───────────────────── */
.example-card {
    background: #0a0f1a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    cursor: pointer;
    transition: border-color 0.2s;
}
.example-card:hover {
    border-color: rgba(118,185,0,0.5);
}
.example-title {
    color: #e2e8f0;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 3px;
}
.example-desc {
    color: #64748b;
    font-size: 0.65rem;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── Architecture flow ───────────────────────── */
.arch-node {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.arch-icon {
    font-size: 1.75rem;
    margin-bottom: 0.4rem;
}
.arch-title {
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.arch-desc {
    color: #64748b;
    font-size: 0.65rem;
    line-height: 1.5;
}

/* ── Code blocks ─────────────────────────────── */
.code-block {
    background: #070c14;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem;
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 0.7rem;
    color: #a3e635;
    line-height: 1.7;
    overflow-x: auto;
    white-space: pre;
}

/* ── Success/Error alerts ─────────────────────── */
.alert-success {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    color: #6ee7b7;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
}
.alert-error {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    color: #fca5a5;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
}

/* ── Divider ─────────────────────────────────── */
hr {
    border-color: #1e293b !important;
    margin: 1.25rem 0 !important;
}

/* ── Hide streamlit branding ─────────────────── */
#MainMenu, footer, header {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = None
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "expanded_prompt" not in st.session_state:
    st.session_state.expanded_prompt = ""

# ─────────────────────────────────────────────
# Sidebar — API Keys & Engine Selection
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;">
            <div style="background:#76b900;border-radius:10px;width:36px;height:36px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.1rem;box-shadow:0 0 12px rgba(118,185,0,0.4);">⚡</div>
            <div>
                <div style="color:#fff;font-weight:700;font-size:0.9rem;">Cosmos 3 Studio</div>
                <div style="color:#64748b;font-size:0.65rem;">NVIDIA Model Base</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 🔧 Engine")
    engine = st.radio(
        "Generation Engine",
        ["🖥️ Cosmos 3 Super (64B) — HF", "✨ Imagen 4.0 — Gemini"],
        label_visibility="collapsed",
    )
    use_cosmos = engine.startswith("🖥️")

    st.markdown("## 🔑 API Keys")

    if use_cosmos:
        hf_token = st.text_input(
            "Hugging Face Token",
            type="password",
            placeholder="hf_xxxxxxxxxxxxxxxxxx",
            help="Get your token at huggingface.co/settings/tokens (Read permission)",
        )
        if hf_token:
            st.markdown('<span class="badge-green">✓ HF Token set</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-amber">⚠ HF Token missing</span>', unsafe_allow_html=True)
        gemini_key = st.text_input(
            "Gemini API Key (for prompt AI expand)",
            type="password",
            placeholder="AIzaSy...",
            help="Optional — needed only for the AI prompt optimizer",
        )
    else:
        hf_token = ""
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            help="Get your key at aistudio.google.com",
        )
        if gemini_key:
            st.markdown('<span class="badge-green">✓ Gemini Key set</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-amber">⚠ Gemini Key missing</span>', unsafe_allow_html=True)

    # Try loading from Streamlit secrets as fallback
    try:
        if not hf_token:
            hf_token = st.secrets.get("HF_TOKEN", "")
        if not gemini_key:
            gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass

    st.markdown("## ⚙️ Generation Params")
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["1:1 Square", "16:9 Widescreen", "9:16 Portrait"],
        disabled=not use_cosmos,
    )
    cfg_scale = st.slider("CFG Guidance Scale", 1.0, 20.0, 7.0, 0.5, disabled=not use_cosmos)
    steps = st.slider("Inference Steps", 10, 50, 25, 1, disabled=not use_cosmos)
    seed_val = st.number_input("Seed (-1 = random)", value=-1, step=1, disabled=not use_cosmos)
    negative_prompt = st.text_input(
        "Negative Prompt",
        value="blurry, low quality, distorted, bad physics, text, watermark",
        disabled=not use_cosmos,
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="color:#334155;font-size:0.65rem;line-height:1.6;">
        API keys are stored only in your browser session and never sent to third parties.<br><br>
        <a href="https://huggingface.co/settings/tokens" target="_blank" style="color:#76b900;">→ Get HF Token</a><br>
        <a href="https://aistudio.google.com" target="_blank" style="color:#76b900;">→ Get Gemini Key</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Header Banner
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="header-banner">
        <div class="header-icon">⚡</div>
        <div>
            <div class="header-title">Cosmos 3 AI Image Studio</div>
            <div class="header-sub">學生創新專題 · NVIDIA Cosmos 3 × Google Gemini · 高真物理影像生成學堂</div>
        </div>
        <div style="margin-left:auto;display:flex;gap:8px;align-items:center;">
            <span class="badge-green">NVIDIA Model Base</span>
            <span class="badge-green">Streamlit Cloud</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def fetch_with_retry(url, method="POST", headers=None, json_data=None, max_retries=5):
    """Exponential backoff retry for HTTP requests."""
    delay = 1.0
    for i in range(max_retries):
        try:
            resp = requests.request(method, url, headers=headers, json=json_data, timeout=120)
            if resp.status_code in (429,) or resp.status_code >= 500:
                if i == max_retries - 1:
                    raise Exception(f"Server busy (HTTP {resp.status_code})")
                time.sleep(delay)
                delay *= 2
                continue
            return resp
        except requests.exceptions.RequestException as e:
            if i == max_retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
    return None


def optimize_prompt(user_prompt: str, api_key: str) -> str:
    """Call Gemini 2.5 Flash to expand and optimize the prompt."""
    system_instruction = (
        "你是一個專業的 AI 繪圖 Prompt 提示詞優化專家。\n"
        "請將用戶輸入的簡單想法或提示詞，擴寫為適合 NVIDIA Cosmos 3 超高畫質物理圖像生成模型使用的詳細英文 Prompt。\n"
        "Cosmos 3 是一個物理真實性極高、世界模擬能力極強的模型，特別擅長細節、材質、物理光學、空間感。\n"
        "請輸出一個高水準的結構化英文 Prompt，包含：主體(Subject)、物理細節(Physical details)、光影(Lighting)、"
        "材質與質地(Textures & Materials)、相機透視(Camera perspective)。\n"
        "注意：請直接輸出最終的英文 Prompt 內容即可，千萬不要包含任何額外的解釋、引言、Markdown 標籤或符號。"
    )
    user_query = f"請優化以下提示詞：\n\"{user_prompt}\""

    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
    }
    resp = fetch_with_retry(endpoint, headers={"Content-Type": "application/json"}, json_data=payload)
    if not resp or not resp.ok:
        raise Exception(f"Gemini API error: {resp.status_code if resp else 'no response'}")
    data = resp.json()
    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    if not text:
        raise Exception("Empty response from Gemini")
    return text.strip()


def generate_cosmos3(prompt: str, hf_tok: str, aspect: str, cfg: float, n_steps: int, seed: int):
    """Call HuggingFace Serverless API for NVIDIA Cosmos 3."""
    width, height = 1024, 1024
    if "16:9" in aspect:
        width, height = 1024, 576
    elif "9:16" in aspect:
        width, height = 576, 1024

    actual_seed = random.randint(0, 99999) if seed == -1 else int(seed)

    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "guidance_scale": float(cfg),
            "num_inference_steps": int(n_steps),
            "width": width,
            "height": height,
            "seed": actual_seed,
        },
    }
    resp = fetch_with_retry(
        "https://api-inference.huggingface.co/models/nvidia/Cosmos3-Super-Text2Image",
        headers={
            "Authorization": f"Bearer {hf_tok.strip()}",
            "Content-Type": "application/json",
        },
        json_data=payload,
    )
    if not resp or not resp.ok:
        err = {}
        try:
            err = resp.json()
        except Exception:
            pass
        raise Exception(
            err.get("error", f"HF API error ({resp.status_code if resp else 'N/A'}). "
                             "Check your token and make sure the model is loaded.")
        )
    img = Image.open(BytesIO(resp.content))
    return img, actual_seed


def generate_imagen(prompt: str, api_key: str):
    """Call Gemini Imagen 4.0 for image generation."""
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"imagen-4.0-generate-001:predict?key={api_key}"
    )
    payload = {
        "instances": {"prompt": prompt},
        "parameters": {"sampleCount": 1},
    }
    resp = fetch_with_retry(endpoint, headers={"Content-Type": "application/json"}, json_data=payload)
    if not resp or not resp.ok:
        raise Exception(f"Imagen API error: {resp.status_code if resp else 'no response'}")
    data = resp.json()
    b64 = data.get("predictions", [{}])[0].get("bytesBase64Encoded", "")
    if not b64:
        raise Exception("No image data returned from Imagen 4.0")
    img = Image.open(BytesIO(base64.b64decode(b64)))
    return img

# ─────────────────────────────────────────────
# Main Tabs
# ─────────────────────────────────────────────
tab_gen, tab_arch, tab_code = st.tabs(
    ["🎨 創意繪圖板", "🔗 系統架構圖", "💻 程式碼整合"]
)

# ══════════════════════════════════════════════
# TAB 1 — Generator
# ══════════════════════════════════════════════
with tab_gen:
    col_left, col_right = st.columns([5, 7], gap="large")

    # ── Left Column ──────────────────────────
    with col_left:

        # Step 1 info card
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">⚙️ Step 01 · Active Engine</div>
                <div style="font-size:0.85rem;font-weight:700;color:#fff;">
                    {'🖥️ NVIDIA Cosmos 3 Super (64B)' if use_cosmos else '✨ Google Imagen 4.0'}
                </div>
                <div style="font-size:0.7rem;color:#64748b;margin-top:3px;">
                    {'Hugging Face Serverless Inference' if use_cosmos else 'Gemini API · No HF token needed'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 2 — Prompt Input
        st.markdown(
            '<div class="card-title" style="margin-bottom:4px;">✍️ Step 02 · 輸入提示詞</div>',
            unsafe_allow_html=True,
        )
        prompt_input = st.text_area(
            "Prompt",
            value=st.session_state.prompt,
            height=160,
            placeholder="e.g. An advanced industrial robotic arm assembling an EV battery in a futuristic Gigafactory...\n\n(建議英文輸入，或點擊 AI 擴寫按鈕讓 Gemini 幫你優化)",
            label_visibility="collapsed",
        )
        st.session_state.prompt = prompt_input

        # AI Expand button
        col_expand, col_reset = st.columns([3, 1])
        with col_expand:
            if st.button("✨ AI 擴寫 (Gemini 優化)", use_container_width=True, key="btn_expand"):
                if not prompt_input.strip():
                    st.warning("請先輸入基本的提示詞構想！")
                elif not gemini_key:
                    st.error("需要 Gemini API Key 才能使用 AI 擴寫功能（請在側欄輸入）")
                else:
                    with st.spinner("✨ Gemini 正在優化提示詞..."):
                        try:
                            optimized = optimize_prompt(prompt_input, gemini_key)
                            st.session_state.prompt = optimized
                            st.session_state.expanded_prompt = optimized
                            st.rerun()
                        except Exception as e:
                            st.error(f"擴寫失敗: {e}")

        with col_reset:
            if st.button("↺ 重設", use_container_width=True, key="btn_reset"):
                st.session_state.prompt = ""
                st.session_state.expanded_prompt = ""
                st.rerun()

        # Show expanded prompt preview
        if st.session_state.expanded_prompt and st.session_state.expanded_prompt == st.session_state.prompt:
            st.markdown(
                """
                <div style="background:rgba(118,185,0,0.06);border:1px solid rgba(118,185,0,0.2);
                            border-radius:10px;padding:0.6rem 0.85rem;margin-top:4px;">
                    <div style="color:#76b900;font-size:0.65rem;font-weight:700;margin-bottom:3px;">
                        ✅ AI 優化完成 · 已填入上方輸入框
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        # Generate Button
        btn_label = (
            "🖥️ 生成 Cosmos 3 Super 影像" if use_cosmos else "✨ 生成 Imagen 4.0 影像"
        )
        if st.button(btn_label, use_container_width=True, key="btn_generate", type="primary"):
            if not prompt_input.strip():
                st.error("請輸入提示詞！")
            elif use_cosmos and not hf_token:
                st.error("請在側欄填入 Hugging Face Token！")
            elif not use_cosmos and not gemini_key:
                st.error("請在側欄填入 Gemini API Key！")
            else:
                with st.spinner("🔄 正在調度 GPU 算力集群，請稍候 (10-30 秒)..."):
                    progress = st.progress(0, text="初始化生成引擎...")
                    try:
                        progress.progress(15, text="連結推理伺服器...")
                        if use_cosmos:
                            progress.progress(35, text="NVIDIA Cosmos 3 物理世界矩陣運算中...")
                            img, used_seed = generate_cosmos3(
                                prompt_input, hf_token, aspect_ratio,
                                cfg_scale, steps, seed_val
                            )
                            engine_label = "nvidia/Cosmos3-Super-Text2Image"
                            extra = {"steps": steps, "cfg": cfg_scale, "seed": used_seed, "ratio": aspect_ratio}
                        else:
                            progress.progress(35, text="Google Imagen 4.0 生成中...")
                            img = generate_imagen(prompt_input, gemini_key)
                            engine_label = "Google Imagen 4.0"
                            extra = {"steps": "Auto", "cfg": "Auto", "seed": "Auto", "ratio": "1:1"}

                        progress.progress(85, text="接收並解碼圖像數據...")

                        # Save to session history
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        record = {
                            "id": f"gen-{int(time.time()*1000)}",
                            "prompt": prompt_input,
                            "engine": engine_label,
                            "image": buf.getvalue(),
                            "img_obj": img,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            **extra,
                        }
                        st.session_state.history.insert(0, record)
                        st.session_state.selected_idx = 0
                        progress.progress(100, text="✅ 生成成功！")
                        time.sleep(0.5)
                        progress.empty()
                        st.success("🎨 影像生成成功！")

                    except Exception as e:
                        progress.empty()
                        st.error(f"❌ 生成失敗: {e}")

        # Example Prompts
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            '<div class="card-title">📚 範例提示詞庫 (點擊套用)</div>',
            unsafe_allow_html=True,
        )
        examples = [
            {
                "title": "🤖 未來物理工廠",
                "desc": "An advanced industrial robotic arm assembling an electric vehicle battery in a pristine futuristic Gigafactory. Intense physical realism, detailed pneumatic tubes, metallic reflections, glowing status LEDs, precise cinematic lighting.",
            },
            {
                "title": "🌧️ 台北賽博朋克夜色",
                "desc": "A cinematic hyper-realistic shot of Taipei City in the year 2099. Cyberpunk skyscrapers with giant holograms, wet streets reflecting multi-colored neon signs in Traditional Chinese.",
            },
            {
                "title": "🌊 紐西蘭魔戒峽灣",
                "desc": "A breathtaking wide-angle shot of Milford Sound, New Zealand. Mirror-like water reflecting massive fjords and waterfalls, golden hour sunlight piercing through storm clouds.",
            },
            {
                "title": "🔮 桌上懸浮星系",
                "desc": "A floating glass sphere holding a miniature solar system inside. Sitting on dark volcanic beach sand, reflecting ocean waves. Macro shot, highly detailed, photorealistic.",
            },
        ]
        for ex in examples:
            with st.container():
                st.markdown(
                    f"""
                    <div class="example-card">
                        <div class="example-title">{ex['title']}</div>
                        <div class="example-desc">{ex['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"套用「{ex['title']}」", key=f"ex_{ex['title']}", use_container_width=True):
                    st.session_state.prompt = ex["desc"]
                    st.rerun()

    # ── Right Column ──────────────────────────
    with col_right:

        # Canvas area
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span style="width:8px;height:8px;border-radius:50%;background:#76b900;
                             display:inline-block;animation:pulse 2s infinite;"></span>
                <span style="font-size:0.75rem;font-weight:600;color:#e2e8f0;">AI 核心畫布區</span>
            </div>
            <style>@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.4;}}</style>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.history and st.session_state.selected_idx is not None:
            sel = st.session_state.history[st.session_state.selected_idx]
            img_obj: Image.Image = sel["img_obj"]

            # Display image
            st.image(img_obj, use_container_width=True)

            # Image meta info
            st.markdown(
                f"""
                <div class="card" style="margin-top:10px;">
                    <div style="font-size:0.7rem;color:#76b900;font-weight:600;margin-bottom:6px;">
                        💡 生成 Prompt
                    </div>
                    <div style="font-size:0.72rem;color:#cbd5e1;line-height:1.6;">{sel['prompt']}</div>
                    <hr>
                    <div style="display:flex;flex-wrap:wrap;gap:16px;font-size:0.65rem;font-family:monospace;color:#64748b;">
                        <span>Engine: <span style="color:#e2e8f0;">{sel['engine']}</span></span>
                        <span>Steps: <span style="color:#e2e8f0;">{sel['steps']}</span></span>
                        <span>CFG: <span style="color:#e2e8f0;">{sel['cfg']}</span></span>
                        <span>Ratio: <span style="color:#e2e8f0;">{sel['ratio']}</span></span>
                        <span style="margin-left:auto;">{sel['timestamp']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Download button
            dl_buf = BytesIO()
            img_obj.save(dl_buf, format="PNG")
            st.download_button(
                label="⬇️ 下載高畫質大圖 (PNG)",
                data=dl_buf.getvalue(),
                file_name=f"cosmos3_{sel['id']}.png",
                mime="image/png",
                use_container_width=True,
            )

        else:
            st.markdown(
                """
                <div style="background:#070c14;border:1px dashed #1e293b;border-radius:16px;
                            min-height:360px;display:flex;flex-direction:column;
                            align-items:center;justify-content:center;text-align:center;padding:3rem;">
                    <div style="font-size:3rem;margin-bottom:1rem;opacity:0.3;">🖼️</div>
                    <div style="color:#475569;font-size:0.85rem;font-weight:600;">準備就緒，等候指令</div>
                    <div style="color:#334155;font-size:0.72rem;margin-top:6px;max-width:280px;line-height:1.6;">
                        在左側輸入提示詞並點擊「生成」，或套用範例提示詞快速體驗 Cosmos 3 的強大能力。
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # History Gallery
        if st.session_state.history:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                f'<div class="card-title">🕒 生成歷程紀錄 ({len(st.session_state.history)})</div>',
                unsafe_allow_html=True,
            )
            n_cols = min(6, len(st.session_state.history))
            gallery_cols = st.columns(n_cols)
            for i, rec in enumerate(st.session_state.history[:n_cols * 2]):
                col_idx = i % n_cols
                with gallery_cols[col_idx]:
                    thumb = rec["img_obj"].copy()
                    thumb.thumbnail((120, 120))
                    is_selected = i == st.session_state.selected_idx
                    border_color = "#76b900" if is_selected else "#1e293b"
                    st.markdown(
                        f'<div style="border:2px solid {border_color};border-radius:8px;overflow:hidden;cursor:pointer;">',
                        unsafe_allow_html=True,
                    )
                    st.image(thumb, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    if st.button("選", key=f"sel_{rec['id']}", use_container_width=True):
                        st.session_state.selected_idx = i
                        st.rerun()

            if st.button("🗑️ 清空歷史紀錄", key="btn_clear_history"):
                st.session_state.history = []
                st.session_state.selected_idx = None
                st.rerun()

# ══════════════════════════════════════════════
# TAB 2 — Architecture
# ══════════════════════════════════════════════
with tab_arch:
    st.markdown(
        """
        <h2 style="color:#fff;font-size:1.15rem;font-weight:700;margin-bottom:4px;">
            🔗 NVIDIA Cosmos 3 Web App 系統運作架構
        </h2>
        <p style="color:#64748b;font-size:0.75rem;margin-bottom:1.5rem;">
            幫助學生理解前後端、Hugging Face 雲端算力與 Gemini 智慧擴寫大語言模型之間的
            「模型鏈 (Model Chaining)」與傳輸機制。
        </p>
        """,
        unsafe_allow_html=True,
    )

    arch_cols = st.columns(5)
    arch_nodes = [
        ("🖥️", "1. Streamlit UI", "輸入創意提示詞，設定 CFG、去噪步數與長寬比。"),
        ("✨", "2. Gemini 提示大師", "大模型自動擴寫為包含光影、物理材質的 3D 物理提示詞。"),
        ("🌐", "3. HF Serverless API", "攜帶 Bearer Token 傳送 POST 請求至 nvidia/Cosmos3 推理端點。"),
        ("⚡", "4. Cosmos 3 (64B)", "Mixture-of-Transformers 在多張 H100 GPU 進行高效能物理去噪。"),
        ("🖼️", "5. 圖像還原", "接收 Blob 二進制數據，轉化成 PNG 圖像渲染，完成流程。"),
    ]
    arrows = ["→", "→", "→", "→"]
    for i, (col, node) in enumerate(zip(arch_cols, arch_nodes)):
        with col:
            st.markdown(
                f"""
                <div class="arch-node">
                    <div class="arch-icon">{node[0]}</div>
                    <div class="arch-title">{node[1]}</div>
                    <div class="arch-desc">{node[2]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    info_col1, info_col2 = st.columns(2, gap="large")
    with info_col1:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">⚡ NVIDIA Cosmos 3 Super 旗艦優勢</div>
                <ul style="color:#cbd5e1;font-size:0.72rem;line-height:1.8;padding-left:1.2rem;">
                    <li><strong>物理世界大模型：</strong> 不僅是靜態畫素，Cosmos 3 兼備物理世界模擬器與行動推理能力。</li>
                    <li><strong>640 億巨大參數量：</strong> 32B Autoregressive 推理塔 + 32B Diffusion 生成塔的「雙塔式混合架構」。</li>
                    <li><strong>3D 旋轉位置編碼：</strong> mRoPE 技術實現視覺、音訊、文字等多模態空間與時間軸的無縫貼合。</li>
                    <li><strong>高保真物理光學：</strong> 玻璃折射、金屬材質、流體重力等基準全面領先同級開源模型。</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with info_col2:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">🎓 學生實驗專題思考</div>
                <div style="background:#070c14;border:1px solid #1e293b;border-radius:10px;padding:0.75rem;margin-bottom:0.75rem;">
                    <div style="color:#f59e0b;font-size:0.72rem;font-weight:600;">思考一：為什麼 Cosmos 3 本地部署極為困難？</div>
                    <div style="color:#64748b;font-size:0.68rem;margin-top:4px;line-height:1.6;">
                        高達 64B 的參數量，完整本地推演需要超過 128GB VRAM，
                        凸顯了本專題使用 Hugging Face API 雲端推理的實用性。
                    </div>
                </div>
                <div style="background:#070c14;border:1px solid #1e293b;border-radius:10px;padding:0.75rem;">
                    <div style="color:#f59e0b;font-size:0.72rem;font-weight:600;">思考二：何謂 AI 提示詞擴寫 (Prompt Upsampling)？</div>
                    <div style="color:#64748b;font-size:0.68rem;margin-top:4px;line-height:1.6;">
                        LLM 能夠預測物理細節、燈光、焦距等輔助資訊，
                        從而產生具備 Physical Realism 的高水準畫作。
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════
# TAB 3 — Code Integration
# ══════════════════════════════════════════════
with tab_code:
    st.markdown(
        """
        <h2 style="color:#fff;font-size:1.15rem;font-weight:700;margin-bottom:4px;">
            💻 後端與命令列自動化整合代碼 (API Integration)
        </h2>
        <p style="color:#64748b;font-size:0.75rem;margin-bottom:1.5rem;">
            根據您在「創意繪圖板」中配置的 Prompt 及設定，即時生成 Python 腳本或 cURL 命令。
            可直接複製到 Jupyter Notebook 或 Terminal 進行後端批量生成。
        </p>
        """,
        unsafe_allow_html=True,
    )

    current_prompt = st.session_state.prompt or "A majestic medieval castle on a floating island..."
    safe_hf_tok = hf_token if hf_token else "YOUR_HF_TOKEN_HERE"

    w = 1024
    h = 1024
    if "16:9" in aspect_ratio:
        w, h = 1024, 576
    elif "9:16" in aspect_ratio:
        w, h = 576, 1024

    code_col1, code_col2 = st.columns(2, gap="large")
    with code_col1:
        st.markdown(
            '<div class="card-title">🐍 Python requests 腳本</div>',
            unsafe_allow_html=True,
        )
        python_code = f'''import requests

# 1. Configure API endpoint and token
API_URL = "https://api-inference.huggingface.co/models/nvidia/Cosmos3-Super-Text2Image"
headers = {{"Authorization": "Bearer {safe_hf_tok}"}}

def query_cosmos(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"API Error: {{response.text}}")
    return response.content

# 2. Define generation parameters
payload = {{
    "inputs": "{current_prompt[:80]}...",
    "parameters": {{
        "negative_prompt": "{negative_prompt}",
        "guidance_scale": {cfg_scale},
        "num_inference_steps": {steps},
        "width": {w},
        "height": {h}
    }}
}}

print("Requesting Cosmos 3 render from Hugging Face...")
try:
    image_bytes = query_cosmos(payload)
    with open("cosmos3_output.png", "wb") as f:
        f.write(image_bytes)
    print("✨ Success! Saved as cosmos3_output.png")
except Exception as e:
    print(f"❌ Failed: {{e}}")'''

        st.code(python_code, language="python")

    with code_col2:
        st.markdown(
            '<div class="card-title">📡 cURL 指令 (Terminal)</div>',
            unsafe_allow_html=True,
        )
        curl_prompt = current_prompt[:60].replace('"', '\\"')
        curl_code = f'''curl https://api-inference.huggingface.co/models/nvidia/Cosmos3-Super-Text2Image \\
  -X POST \\
  -H "Authorization: Bearer {safe_hf_tok}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "inputs": "{curl_prompt}...",
    "parameters": {{
      "negative_prompt": "blurry, low quality",
      "guidance_scale": {cfg_scale},
      "num_inference_steps": {steps},
      "width": {w},
      "height": {h}
    }}
  }}' \\
  --output cosmos3_image.png'''

        st.code(curl_code, language="bash")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">🎓 學科小筆記：如何本地微調與推演 (vLLM-Omni)？</div>
            <div style="color:#94a3b8;font-size:0.72rem;line-height:1.7;">
                NVIDIA 隨 Cosmos 3 推出了專門的輕量級推演容器 <code style="color:#76b900;background:#070c14;padding:1px 5px;border-radius:4px;">vllm-omni:cosmos3</code>。
                對於具備頂級硬體設備（如 8x H100 節點）的高級研究室，可以使用該容器啟動相容 OpenAI 的 API 伺服器，
                並以此前端網頁更換基本 API Endpoint 網址，即可輕鬆實現完全自主控制的校園 AI 圖像生成系統！
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown(
    """
    <hr>
    <div style="text-align:center;color:#334155;font-size:0.68rem;padding:1rem 0;">
        © 2026 Cosmos 3 AI 繪圖工坊 · 基於開源 AI 科普教學專題 ·
        <a href="https://huggingface.co/nvidia/Cosmos3-Super-Text2Image" target="_blank"
           style="color:#76b900;text-decoration:none;">Hugging Face 模型卡</a> ·
        <a href="https://github.com/nvidia/cosmos" target="_blank"
           style="color:#76b900;text-decoration:none;">NVIDIA Cosmos GitHub</a>
    </div>
    """,
    unsafe_allow_html=True,
)
