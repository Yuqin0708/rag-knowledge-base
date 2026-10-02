# RAG

以自訂知識庫為基礎的問答系統：先把知識存進去，AI 只依據這些知識回答；知識庫裡找不到答案時，會回覆找不到資料（規則見 `backend/system_prompt.md`）。

## 功能

- **對話頁（`/chat`）**：輸入問題，取得依知識庫產生的回答。
- **知識庫管理（`/knowledge`）**：新增、關鍵字搜尋、編輯、刪除知識。

## 運作流程

1. 新增知識時，後端以 `text-embedding-3-small` 產生向量，連同原文存入 ChromaDB。
2. 提問時，後端把問題轉成向量，取出最相近的 3 筆知識。
3. 將這 3 筆知識填入系統提示詞，呼叫 `gpt-4.1-nano` 產生回答。

## 技術棧

| | |
|---|---|
| 後端 | Python 3.12、FastAPI、OpenAI SDK、ChromaDB、python-dotenv、Poetry |
| 前端 | Vue 3、Vuetify 3、Vite、TypeScript、axios、vue-router、Pinia、yarn |

## API

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/` | 健康檢查 |
| POST | `/chat` | body `{ "msg": "..." }`，回傳 `{ "message": "..." }` |
| GET | `/knowledge` | 列出全部知識 |
| POST | `/knowledge` | body `{ "msg": "..." }`，新增知識 |
| PUT | `/knowledge/{id}` | body `{ "content": "..." }`，更新知識 |
| DELETE | `/knowledge/{id}` | 刪除知識 |

## 專案結構

```
backend/    FastAPI 服務（main.py、system_prompt.md）
frontend/   Vue + Vuetify 前端
```

## 執行

### 後端（預設埠 8000）

```bash
cd backend
poetry install
cp .env.example .env   # 填入 OPENAI_API_KEY
poetry run fastapi dev main.py
```

### 前端（預設埠 3000）

```bash
cd frontend
yarn
yarn dev
```

後端網址預設為 `http://localhost:8000`，可用 `VITE_API_BASE` 覆寫；後端允許的前端來源預設為 `http://localhost:3000`，可用 `CORS_ORIGINS` 覆寫（見各目錄的 `.env.example`）。

### 沒有 OpenAI 金鑰時預覽畫面

`backend/mock_server.py` 是不呼叫 OpenAI 的展示用後端，端點與 `main.py` 相同，以關鍵字重疊取代向量檢索，回答直接引用知識原文，僅供預覽前端畫面：

```bash
cd backend
poetry run fastapi dev mock_server.py
```

## 已知限制

- ChromaDB 使用記憶體模式，後端重啟後知識會清空。
- 每次提問獨立處理，不保留對話歷史。
- 沒有登入或權限控管。
