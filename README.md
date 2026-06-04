# ⚡ Cosmos 3 AI Image Studio

> 學生創新專題：高真物理影像生成學堂  
> Powered by **NVIDIA Cosmos 3** × **Google Gemini Imagen 4.0**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

---

## 🚀 Features

- 🖥️ **NVIDIA Cosmos 3 Super (64B)** image generation via Hugging Face Serverless API
- ✨ **Google Imagen 4.0** image generation via Gemini API
- 🤖 **AI Prompt Optimizer** — Gemini 2.5 Flash rewrites your simple idea into a detailed physical prompt
- 🎨 **Advanced controls** — CFG scale, inference steps, aspect ratio, seed
- 🕒 **Generation history gallery** with one-click download
- 🔗 **Architecture diagram** explaining the Model Chaining pipeline
- 💻 **Code integration** tab with ready-to-use Python & cURL snippets

---

## 🛠️ Local Development

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up API keys
```bash
# Create the secrets file (gitignored)
mkdir .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Then edit .streamlit/secrets.toml with your real keys
```

Or enter keys directly in the app sidebar at runtime.

### 3. Run the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🔑 Getting API Keys

| Key | Where to get |
|-----|-------------|
| **HF_TOKEN** | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (Read permission) |
| **GEMINI_API_KEY** | [aistudio.google.com](https://aistudio.google.com) → Get API Key |

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (public or private)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your GitHub repo, branch `main`, file `app.py`
4. Click **Advanced settings → Secrets** and add:
   ```toml
   HF_TOKEN = "hf_your_token_here"
   GEMINI_API_KEY = "AIzaSy_your_key_here"
   ```
5. Click **Deploy** — your app will be live in ~1 minute! 🎉

---

## 📁 Project Structure

```
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── .gitignore                    # Excludes secrets & cache
├── README.md                     # This file
├── .streamlit/
│   └── secrets.toml.example      # Secrets template (safe to commit)
└── cosmos_3_ai_image_studio.tsx  # Original React/TSX reference design
```

---

## 🎓 About

This project is an educational showcase demonstrating:
- **Model Chaining**: Connecting LLM (Gemini) → Diffusion Model (Cosmos 3) in a pipeline
- **Cloud Inference**: Using Hugging Face Serverless API to run 64B models without local GPU
- **Prompt Engineering**: AI-assisted prompt optimization for physics-accurate image generation

---

© 2026 Cosmos 3 AI 繪圖工坊 · Open-source AI Education Project
