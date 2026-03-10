# IOT2026 ESP32 HW1
> 114-2 智慧物聯網 Arduino 系列課程 HW1

聊天記錄請見[聊天記錄](./聊天記錄.md)

# 硬體配置
- ESP32 (ESP-WROOM-32)
- DHT11
- LED
- 按鈕

# 專案架構
- edge：ESP32 的專案程式碼，使用 PlatformIO 作為開發環境
- backend：Python FastAPI 後端伺服器，負責接收並儲存感測器資料至 SQLite。

## 執行後端伺服器 (Backend)

首先請確保您已安裝了 [uv](https://github.com/astral-sh/uv) 作為 Python 專案管理工具。

1. 切換至 `backend` 資料夾：
   ```bash
   cd backend
   ```
2. 執行伺服器主程式：
   ```bash
   uv run main.py
   ```
3. 成功啟動後，伺服器會運作在 `http://127.0.0.1:8000` (或 `0.0.0.0:8000`)。
4. 打開瀏覽器前往 [http://localhost:8000/docs](http://localhost:8000/docs) 即可查看自動生成的 FastAPI 互動式 API 文件 (Swagger UI)，了解如何存取。