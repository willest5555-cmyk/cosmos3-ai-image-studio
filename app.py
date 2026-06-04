import streamlit as st
import requests
import base64
import time
import random
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="AI 圖像生成器",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* Light Theme CSS */
body {
    background-color: #f9fafb !important;
    color: #1f2937 !important;
    font-family: 'Inter', sans-serif !important;
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
    font-size: 1.875rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.5rem;
}
.main-header p {
    color: #6b7280;
}
div.stButton > button:first-child {
    border-radius: 1rem;
    font-weight: 600;
    padding: 0.75rem 1rem;
}
.primary-btn > div > div > button:first-child {
    background-color: #2563eb !important;
    color: white !important;
    border: none;
}
.primary-btn > div > div > button:first-child:hover {
    background-color: #1d4ed8 !important;
}
.primary-btn-purple > div > div > button:first-child {
    background-color: #9333ea !important;
    color: white !important;
    border: none;
}
.primary-btn-purple > div > div > button:first-child:hover {
    background-color: #7e22ce !important;
}
/* Hide streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Helper Functions
def fetch_with_retry(url, method="POST", headers=None, json_data=None, max_retries=5):
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

def generate_cosmos3(prompt: str, hf_tok: str):
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, low quality, distorted, bad physics, text, watermark",
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
        headers=headers,
        json_data=payload,
    )
    
    if not resp or not resp.ok:
        err = {}
        try:
            err = resp.json()
        except Exception:
            pass
        if "is currently loading" in err.get("error", ""):
            time_est = err.get("estimated_time", "?")
            raise Exception(f"模型正在載入中，預計需要 {time_est} 秒。請稍後再試或切換至備用模型。")
        raise Exception(err.get("error", f"HF API error ({resp.status_code if resp else 'N/A'})."))
    
    img = Image.open(BytesIO(resp.content))
    return img

def generate_imagen(prompt: str, api_key: str):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
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

# Initialize session state
if "model" not in st.session_state:
    st.session_state.model = "huggingface"
if "hf_token" not in st.session_state:
    st.session_state.hf_token = ""
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "generated_img" not in st.session_state:
    st.session_state.generated_img = None
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# Layout
st.markdown("""
<div class="main-header">
    <div style="display:inline-block; padding: 0.75rem; background-color: #2563eb; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 1rem;">
        <span style="font-size:2rem; color: white;">🖼️</span>
    </div>
    <h1>AI 圖像生成器</h1>
    <p>輸入您的想像，讓 AI 為您繪製成真</p>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("**選擇 AI 模型**")
    
    col1, col2, col3, col_empty = st.columns([1.5, 1.5, 0.5, 2])
    with col1:
        if st.button("Cosmos3 (Hugging Face)", use_container_width=True, type="primary" if st.session_state.model == "huggingface" else "secondary"):
            st.session_state.model = "huggingface"
            st.rerun()
    with col2:
        if st.button("✨ Imagen (備用模型)", use_container_width=True, type="primary" if st.session_state.model == "gemini" else "secondary"):
            st.session_state.model = "gemini"
            st.rerun()
    with col3:
        if st.button("⚙️", help="設定 API Key"):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()

    if st.session_state.show_settings:
        with st.container(border=True):
            if st.session_state.model == "huggingface":
                st.markdown("**Hugging Face Access Token (選填)**")
                st.session_state.hf_token = st.text_input("hf_...", value=st.session_state.hf_token, type="password", label_visibility="collapsed", placeholder="hf_...")
                st.caption("某些大型模型或高頻率請求需要提供 Token。您可以在 Hugging Face 帳號設定中產生。")
            else:
                st.markdown("**Gemini API Key (必填)**")
                st.session_state.gemini_key = st.text_input("AIzaSy...", value=st.session_state.gemini_key, type="password", label_visibility="collapsed", placeholder="AIzaSy...")
                st.caption("使用 Imagen 備用模型需要提供您的 Gemini API Key。")

    st.markdown("<br/>**圖片描述 (Prompt)**", unsafe_allow_html=True)
    prompt_input = st.text_area(
        "圖片描述 (Prompt)", 
        value=st.session_state.prompt, 
        placeholder="例如: 一隻穿著太空衣的可愛貓咪，正在火星上漫步，高畫質，電影光影...",
        label_visibility="collapsed",
        height=120
    )
    st.session_state.prompt = prompt_input

    # Generate button wrapper
    wrapper_class = "primary-btn-purple" if st.session_state.model == "gemini" else "primary-btn"
    st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)

    if st.button("✨ 開始生成", use_container_width=True):
        if not prompt_input.strip():
            st.error("請先輸入圖片描述 (Prompt)！")
        else:
            # Fallback secrets retrieval
            hf_tok = st.session_state.hf_token if st.session_state.hf_token else ""
            gemini_key = st.session_state.gemini_key if st.session_state.gemini_key else ""
            try:
                if not hf_tok: hf_tok = st.secrets.get("HF_TOKEN", "")
                if not gemini_key: gemini_key = st.secrets.get("GEMINI_API_KEY", "")
            except:
                pass

            if st.session_state.model == "gemini" and not gemini_key:
                st.error("系統未配置 Gemini API Key，請檢查環境變數 (secrets)。")
            else:
                with st.spinner("正在生成圖片..."):
                    try:
                        if st.session_state.model == "huggingface":
                            img = generate_cosmos3(prompt_input, hf_tok)
                        else:
                            img = generate_imagen(prompt_input, gemini_key)
                        
                        st.session_state.generated_img = img
                    except Exception as e:
                        st.error(f"發生錯誤: {e}")
                        if st.session_state.model == "huggingface":
                            st.info("💡 建議：如果 Hugging Face 模型沒有回應或發生權限錯誤，您可以點擊上方的「Imagen (備用模型)」來切換至 Google 的圖像生成服務。")

    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.generated_img:
    with st.container(border=True):
        st.image(st.session_state.generated_img, use_container_width=True)
        
        buf = BytesIO()
        st.session_state.generated_img.save(buf, format="PNG")
        
        st.download_button(
            label="⬇️ 下載圖片",
            data=buf.getvalue(),
            file_name=f"generated-image-{int(time.time()*1000)}.png",
            mime="image/png",
            use_container_width=True
        )
