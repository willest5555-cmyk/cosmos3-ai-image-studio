import streamlit as st
import requests
import base64
import time
import random
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="AI 圖像生成器",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
body {
    background-color: #f9fafb !important;
    color: #1f2937 !important;
}
.stApp {
    background-color: #f9fafb !important;
}
.main-header {
    text-align: center;
    margin-bottom: 2rem;
    margin-top: 1rem;
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.4rem;
}
.main-header p {
    color: #6b7280;
    font-size: 0.95rem;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.65rem;
    font-weight: 600;
    margin: 0 2px;
}
.badge-green { background: rgba(22,163,74,0.1); color: #16a34a; border: 1px solid rgba(22,163,74,0.2); }
.badge-blue  { background: rgba(37,99,235,0.1);  color: #2563eb; border: 1px solid rgba(37,99,235,0.2); }
.badge-amber { background: rgba(217,119,6,0.1);  color: #d97706; border: 1px solid rgba(217,119,6,0.2); }

/* Enhance Prompt Text Area */
.stTextArea textarea {
    background-color: #eff6ff !important;
    border: 2px solid #93c5fd !important;
    border-radius: 0.75rem !important;
    font-size: 1.05rem !important;
    color: #1e3a8a !important;
    padding: 1rem !important;
    transition: all 0.3s ease;
}
.stTextArea textarea:focus {
    background-color: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,0.2) !important;
}

/* Hide streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────

def fetch_with_retry(url, method="POST", headers=None, json_data=None, max_retries=4, timeout=120):
    delay = 1.5
    for i in range(max_retries):
        try:
            resp = requests.request(method, url, headers=headers, json=json_data, timeout=timeout)
            if resp.status_code in (429,) or resp.status_code >= 500:
                if i == max_retries - 1:
                    raise Exception(f"Server busy (HTTP {resp.status_code})")
                time.sleep(delay)
                delay *= 2
                continue
            return resp
        except requests.exceptions.Timeout:
            if i == max_retries - 1:
                raise Exception("連線逾時 (Timeout)，請稍後再試。")
            time.sleep(delay)
            delay *= 2
        except requests.exceptions.RequestException as e:
            if i == max_retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
    return None


def generate_flux_schnell(prompt: str, hf_tok: str):
    """使用 HF Inference API 呼叫 FLUX.1-schnell，速度最快的 FLUX 模型。"""
    url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Content-Type": "application/json"}
    if hf_tok:
        headers["Authorization"] = f"Bearer {hf_tok.strip()}"
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4,
            "guidance_scale": 0.0,
            "width": 1024,
            "height": 1024,
        }
    }
    resp = fetch_with_retry(url, headers=headers, json_data=payload)
    if resp is None or not resp.ok:
        err = {}
        status = resp.status_code if resp is not None else "N/A"
        if resp is not None:
            try: err = resp.json()
            except: err = {"error": resp.text}
        if isinstance(err, dict) and "is currently loading" in str(err.get("error", "")):
            t = err.get("estimated_time", "?")
            raise Exception(f"模型正在載入中 (~{t} 秒)，請稍後再試。")
        error_msg = err.get("error", err) if isinstance(err, dict) else err
        raise Exception(f"FLUX API error ({status}): {error_msg}")
    return Image.open(BytesIO(resp.content))


def generate_cosmos3(prompt: str, hf_tok: str):
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, low quality, distorted, text, watermark",
            "guidance_scale": 7.0,
            "num_inference_steps": 25,
            "width": 1024,
            "height": 1024,
            "seed": random.randint(0, 99999),
        },
    }
    headers = {"Content-Type": "application/json"}
    if hf_tok:
        headers["Authorization"] = f"Bearer {hf_tok.strip()}"
    resp = fetch_with_retry(
        "https://api-inference.huggingface.co/models/nvidia/Cosmos3-Super-Text2Image",
        headers=headers, json_data=payload,
    )
    if resp is None or not resp.ok:
        err = {}
        status = resp.status_code if resp is not None else "N/A"
        if resp is not None:
            try: err = resp.json()
            except: err = {"error": resp.text}
        if isinstance(err, dict) and "is currently loading" in str(err.get("error", "")):
            t = err.get("estimated_time", "?")
            raise Exception(f"模型正在載入中 (~{t} 秒)，請稍後再試。")
        error_msg = err.get("error", err) if isinstance(err, dict) else err
        raise Exception(f"HF API error ({status}): {error_msg}")
    return Image.open(BytesIO(resp.content))


def generate_imagen(prompt: str, api_key: str):
    endpoint = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"imagen-4.0-generate-001:predict?key={api_key}")
    payload = {"instances": {"prompt": prompt}, "parameters": {"sampleCount": 1}}
    resp = fetch_with_retry(endpoint, headers={"Content-Type": "application/json"}, json_data=payload)
    if resp is None or not resp.ok:
        status = resp.status_code if resp is not None else "N/A"
        err_msg = ""
        if resp is not None:
            try:
                err_json = resp.json()
                err_msg = err_json.get("error", {}).get("message", resp.text)
            except: err_msg = resp.text
        raise Exception(f"Imagen API error ({status}): {err_msg}")
    data = resp.json()
    b64 = data.get("predictions", [{}])[0].get("bytesBase64Encoded", "")
    if not b64:
        raise Exception("No image data returned from Imagen 4.0")
    return Image.open(BytesIO(base64.b64decode(b64)))


# ── Session State ─────────────────────────────────────────────────────────────

for k, v in {
    "model": "flux",
    "hf_token": "",
    "gemini_key": "",
    "prompt": "",
    "generated_img": None,
    "show_settings": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Layout ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <div style="display:inline-block;padding:0.85rem;background:linear-gradient(135deg,#2563eb,#7c3aed);
                border-radius:1.2rem;box-shadow:0 10px 30px rgba(37,99,235,0.25);margin-bottom:1rem;">
        <span style="font-size:2rem;">🎨</span>
    </div>
    <h1>AI 圖像生成器</h1>
    <p>輸入文字描述，讓 AI 為您即時繪製圖像</p>
</div>
""", unsafe_allow_html=True)

# ── Model Selection ───────────────────────────────────────────────────────────
with st.container(border=True):

    st.markdown("##### 🤖 選擇生成引擎")

    col_a, col_b, col_c, col_gear = st.columns([1.6, 1.6, 1.4, 0.45])
    with col_a:
        if st.button(
            "⚡ FLUX.1-schnell",
            use_container_width=True,
            type="primary" if st.session_state.model == "flux" else "secondary"
        ):
            st.session_state.model = "flux"
            st.session_state.show_settings = False
            st.rerun()
    with col_b:
        if st.button(
            "🖥️ Cosmos 3 (HF)",
            use_container_width=True,
            type="primary" if st.session_state.model == "huggingface" else "secondary"
        ):
            st.session_state.model = "huggingface"
            st.session_state.show_settings = False
            st.rerun()
    with col_c:
        if st.button(
            "✨ Imagen 4.0",
            use_container_width=True,
            type="primary" if st.session_state.model == "gemini" else "secondary"
        ):
            st.session_state.model = "gemini"
            st.session_state.show_settings = False
            st.rerun()
    with col_gear:
        if st.button("⚙️", help="設定 API Key", use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()

    # Model info badges
    if st.session_state.model == "flux":
        st.markdown(
            '<span class="badge badge-blue">FLUX.1-schnell</span>'
            '<span class="badge badge-green">最快 4 步生成</span>'
            '<span class="badge badge-amber">建議提供 HF Token</span>',
            unsafe_allow_html=True
        )
    elif st.session_state.model == "huggingface":
        st.markdown(
            '<span class="badge badge-amber">需要 HF Token</span>'
            '<span class="badge badge-blue">NVIDIA Cosmos 3 Super 64B</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="badge badge-amber">需要 Gemini API Key (付費帳號)</span>'
            '<span class="badge badge-blue">Google Imagen 4.0</span>',
            unsafe_allow_html=True
        )

    # API Key Settings Panel
    if st.session_state.show_settings:
        with st.container(border=True):
            if st.session_state.model in ("flux", "huggingface"):
                st.markdown("**Hugging Face Access Token**")
                st.session_state.hf_token = st.text_input(
                    "hf_token", value=st.session_state.hf_token, type="password",
                    label_visibility="collapsed", placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxx"
                )
                st.caption("從 huggingface.co/settings/tokens 取得 Read Token。FLUX 與 Cosmos 3 皆需此 Token。")
            elif st.session_state.model == "gemini":
                st.markdown("**Gemini API Key (必填，需付費帳號)**")
                st.session_state.gemini_key = st.text_input(
                    "gemini_key", value=st.session_state.gemini_key, type="password",
                    label_visibility="collapsed", placeholder="AIzaSy..."
                )
                st.caption("從 aistudio.google.com 取得。Imagen 4.0 需要升級至付費方案。")

    st.markdown("---")

    # ── Prompt Input ─────────────────────────────────────────────────────────
    st.markdown("##### ✍️ 圖片描述 (Prompt)")
    prompt_input = st.text_area(
        "prompt",
        value=st.session_state.prompt,
        placeholder="例如: a futuristic city at sunset with flying cars, cinematic lighting, photorealistic, 8K...\n\n(建議使用英文以獲得最佳效果)",
        label_visibility="collapsed",
        height=130
    )
    st.session_state.prompt = prompt_input

    # ── Generate Button ───────────────────────────────────────────────────────
    btn_label = {
        "flux":        "⚡ 生成圖片 (FLUX.1-schnell)",
        "huggingface": "🖥️ 生成 Cosmos 3 影像",
        "gemini":      "✨ 生成 Imagen 4.0 影像",
    }[st.session_state.model]

    if st.button(btn_label, use_container_width=True, type="primary"):
        if not prompt_input.strip():
            st.error("請先輸入圖片描述 (Prompt)！")
        else:
            # Resolve API keys (UI input → secrets fallback)
            hf_tok = st.session_state.hf_token
            gemini_key = st.session_state.gemini_key
            try:
                if not hf_tok:     hf_tok = st.secrets.get("HF_TOKEN", "")
                if not gemini_key: gemini_key = st.secrets.get("GEMINI_API_KEY", "")
            except: pass

            if st.session_state.model == "gemini" and not gemini_key:
                st.error("請先點擊 ⚙️ 設定您的 Gemini API Key。")
            elif st.session_state.model in ("flux", "huggingface") and not hf_tok:
                st.warning("⚠️ 未設定 HF Token，將以匿名方式呼叫 API（可能有速率限制）。如遇錯誤請點 ⚙️ 設定 Token。")

            spinner_msg = {
                "flux":        "⚡ FLUX.1-schnell 生成中 (約 10~20 秒)...",
                "huggingface": "🖥️ Cosmos 3 生成中 (約 30~60 秒)...",
                "gemini":      "✨ Imagen 4.0 生成中...",
            }[st.session_state.model]

            if st.session_state.model != "gemini" or gemini_key:
                with st.spinner(spinner_msg):
                    try:
                        if st.session_state.model == "flux":
                            img = generate_flux_schnell(prompt_input, hf_tok)
                        elif st.session_state.model == "huggingface":
                            img = generate_cosmos3(prompt_input, hf_tok)
                        else:
                            img = generate_imagen(prompt_input, gemini_key)
                        st.session_state.generated_img = img
                        st.success("✅ 圖片生成成功！")
                    except Exception as e:
                        st.error(f"❌ 發生錯誤: {e}")
                        st.info("💡 請點擊 ⚙️ 設定您的 Hugging Face Token 後重試。")

# ── Result ────────────────────────────────────────────────────────────────────
if st.session_state.generated_img:
    with st.container(border=True):
        st.image(st.session_state.generated_img, use_container_width=True)

        buf = BytesIO()
        st.session_state.generated_img.save(buf, format="PNG")

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="⬇️ 下載圖片 (PNG)",
                data=buf.getvalue(),
                file_name=f"ai-image-{int(time.time())}.png",
                mime="image/png",
                use_container_width=True
            )
        with c2:
            if st.button("🗑️ 清除圖片", use_container_width=True):
                st.session_state.generated_img = None
                st.rerun()
