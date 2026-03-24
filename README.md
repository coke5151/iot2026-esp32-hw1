# IOT2026 ESP32 HW1
> 114-2 智慧物聯網 Arduino 系列課程 HW1

聊天記錄請見[聊天記錄](./聊天記錄.md)

# 硬體配置
- ESP32 (ESP-WROOM-32)
- DHT11
- LED
- 按鈕

# 專案架構
- **edge**：ESP32 的專案程式碼，使用 PlatformIO 作為開發環境。
- **backend**：Python FastAPI 後端伺服器，負責接收感測器資料並儲存至 SQLite 資料庫。
- **frontend**：由 Streamlit 打造的即時互動式資料儀表板 (Dashboard)，主程式位於根目錄的 `app.py`。

# 如何執行專案

首先，請確保您已安裝了 [uv](https://github.com/astral-sh/uv) 作為 Python 專案管理工具。

## 1. 執行後端伺服器 (FastAPI Backend)

負責提供 ESP32 發佈感測器資料的 API 端點，並連接 SQLite 資料庫。

1. 切換至 `backend` 資料夾：
   ```bash
   cd backend
   ```
2. 執行伺服器主程式：
   ```bash
   uv run main.py
   ```
3. 成功啟動後，伺服器會運作在 `http://127.0.0.1:8000`。您可以打開網頁前往 [http://localhost:8000/docs](http://localhost:8000/docs) 來測試與查看自動生成的 API 文件。

## 2. 執行前端資料儀表板 (Streamlit Dashboard)

負責讀取 SQLite 中的歷史資料，並透過視覺化圖表展示即時的溫濕度趨勢。

1. 請確保終端機目前位於**專案根目錄** (就是有 `app.py` 與 `pyproject.toml` 的那一層)。
2. 使用 `uv` 執行 Streamlit 應用程式：
   ```bash
   uv run streamlit run app.py
   ```
3. 啟動後，系統通常會自動開啟您的瀏覽器並進入 Dashboard 頁面。如有需要，請手動前往 `http://localhost:8501`。