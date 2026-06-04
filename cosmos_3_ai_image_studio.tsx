import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, Wand2, Settings2, AlertCircle, RefreshCw, Download } from 'lucide-react';

// 延遲函數，用於重試機制
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [model, setModel] = useState('huggingface'); // 'huggingface' 或 'gemini'
  const [hfToken, setHfToken] = useState('');
  const [showSettings, setShowSettings] = useState(false);

  // 處理 Hugging Face API 呼叫
  const generateWithHuggingFace = async (textPrompt) => {
    // 依照要求設定目標模型名稱
    const modelId = "nvidia/Cosmos3-Super-Text2Image";
    const url = `https://api-inference.huggingface.co/models/${modelId}`;

    const headers = {
      "Content-Type": "application/json",
    };

    if (hfToken) {
      headers["Authorization"] = `Bearer ${hfToken}`;
    }

    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ inputs: textPrompt }),
    });

    if (!response.ok) {
      const errText = await response.text();
      // 解析常見的 Hugging Face 錯誤 (例如模型正在載入)
      try {
        const errJson = JSON.parse(errText);
        if (errJson.error && errJson.error.includes("is currently loading")) {
          throw new Error(`模型正在載入中，預計需要 ${errJson.estimated_time?.toFixed(0) || '?'} 秒。請稍後再試或切換至備用模型。`);
        }
        throw new Error(errJson.error || `HTTP 錯誤: ${response.status}`);
      } catch (e) {
        throw new Error(`Hugging Face API 錯誤: ${e.message || response.statusText}`);
      }
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
  };

  // 處理 Gemini (Imagen) API 呼叫，包含指數退避重試機制
  const generateWithGemini = async (textPrompt) => {
    const apiKey = ""; // 執行環境會在執行時提供
    const url = `https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=${apiKey}`;
    const payload = {
      instances: { prompt: textPrompt },
      parameters: { sampleCount: 1 }
    };

    const maxRetries = 5;
    const delays = [1000, 2000, 4000, 8000, 16000];

    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error?.message || `API 錯誤 (${response.status})`);
        }

        const data = await response.json();
        if (data.predictions && data.predictions.length > 0) {
          return `data:image/png;base64,${data.predictions[0].bytesBase64Encoded}`;
        } else {
          throw new Error("API 未回傳有效的圖片資料");
        }
      } catch (err) {
        if (i === maxRetries - 1) {
          throw err; // 最後一次重試仍然失敗，拋出錯誤
        }
        await delay(delays[i]); // 等待後重試
      }
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("請先輸入圖片描述 (Prompt)！");
      return;
    }

    setLoading(true);
    setError('');
    setImageUrl(''); // 清除先前的圖片

    try {
      let generatedImage = '';
      if (model === 'huggingface') {
        generatedImage = await generateWithHuggingFace(prompt);
      } else {
        generatedImage = await generateWithGemini(prompt);
      }
      setImageUrl(generatedImage);
    } catch (err) {
      console.error(err);
      setError(err.message || "發生未知錯誤，請嘗試切換模型或稍後再試。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 p-4 md:p-8 font-sans">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-600 rounded-2xl shadow-lg">
              <ImageIcon className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">AI 圖像生成器</h1>
          <p className="text-gray-500">輸入您的想像，讓 AI 為您繪製成真</p>
        </div>

        {/* Main Card */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-200">

          {/* Model Selection */}
          <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gray-50 p-4 rounded-2xl">
            <div className="space-y-1">
              <span className="text-sm font-semibold text-gray-700 block">選擇 AI 模型</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setModel('huggingface')}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${model === 'huggingface'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                    }`}
                >
                  Cosmos3 (Hugging Face)
                </button>
                <button
                  onClick={() => setModel('gemini')}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors flex items-center gap-2 ${model === 'gemini'
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                    }`}
                >
                  <Wand2 className="w-4 h-4" />
                  Imagen (備用模型)
                </button>
              </div>
            </div>

            {/* Settings Toggle for HF Token */}
            {model === 'huggingface' && (
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="text-gray-500 hover:text-gray-800 transition p-2 rounded-full hover:bg-gray-200"
                title="設定 Hugging Face Token"
              >
                <Settings2 className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Optional HF Token Input */}
          {model === 'huggingface' && showSettings && (
            <div className="mb-6 p-4 bg-blue-50/50 border border-blue-100 rounded-2xl transition-all">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hugging Face Access Token (選填)
              </label>
              <input
                type="password"
                value={hfToken}
                onChange={(e) => setHfToken(e.target.value)}
                placeholder="hf_..."
                className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
              <p className="text-xs text-gray-500 mt-2">
                某些大型模型或高頻率請求需要提供 Token。您可以在 Hugging Face 帳號設定中產生。
              </p>
            </div>
          )}

          {/* Prompt Input */}
          <div className="space-y-3">
            <label className="block text-sm font-semibold text-gray-700">
              圖片描述 (Prompt)
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="例如: 一隻穿著太空衣的可愛貓咪，正在火星上漫步，高畫質，電影光影..."
              className="w-full h-32 px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white outline-none transition resize-none text-gray-800"
              disabled={loading}
            />

            <button
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
              className={`w-full py-3.5 rounded-2xl font-semibold text-white transition-all flex justify-center items-center gap-2 ${loading || !prompt.trim()
                ? 'bg-gray-400 cursor-not-allowed'
                : model === 'gemini' ? 'bg-purple-600 hover:bg-purple-700 hover:shadow-lg' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg'
                }`}
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  正在生成圖片...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  開始生成
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-start gap-3 text-red-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <strong className="block mb-1">發生錯誤</strong>
              {error}
              {model === 'huggingface' && (
                <p className="mt-2 text-red-600">
                  💡 建議：如果 Hugging Face 模型沒有回應或發生權限錯誤，您可以點擊上方的「Imagen (備用模型)」來切換至 Google 的圖像生成服務。
                </p>
              )}
            </div>
          </div>
        )}

        {/* Image Output */}
        {imageUrl && !loading && (
          <div className="bg-white p-4 rounded-3xl shadow-sm border border-gray-200 flex flex-col items-center">
            <div className="w-full rounded-2xl overflow-hidden bg-gray-100 mb-4 border border-gray-200">
              <img
                src={imageUrl}
                alt={prompt}
                className="w-full h-auto object-contain max-h-[600px]"
              />
            </div>
            <a
              href={imageUrl}
              download={`generated-image-${Date.now()}.png`}
              className="flex items-center gap-2 px-6 py-2.5 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition font-medium text-sm"
            >
              <Download className="w-4 h-4" />
              下載圖片
            </a>
          </div>
        )}

      </div>
    </div>
  );
}