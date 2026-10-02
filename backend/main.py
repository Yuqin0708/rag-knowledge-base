import os
import uuid  # 用於產生唯一的知識 ID
from fastapi import Body, FastAPI  # FastAPI 基本組件
from openai import AsyncOpenAI  # OpenAI 非同步 API 客戶端
import chromadb  # 向量資料庫
from dotenv import load_dotenv  # 自動載入 .env 變數
from fastapi.middleware.cors import CORSMiddleware  # CORS 中介軟體
from pydantic import BaseModel

load_dotenv()  # 讀取 OpenAI API Key 等環境變數

openai_client = AsyncOpenAI()
chroma_client = chromadb.Client()  # 預設記憶體模式，資料會隨程式結束而消失

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # 以逗號分隔多個來源；未設定時只允許本機前端
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

collection = chroma_client.get_or_create_collection(
    "my_collection"
)  # 建立（或取得）一個知識集合

# 載入系統提示詞（system prompt），用於指示 AI 的回答規則
with open("system_prompt.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()


# 非同步取得文本的 embedding
async def get_embeddings(text: str):
    response = await openai_client.embeddings.create(
        input=text, model="text-embedding-3-small"
    )
    return response.data[0].embedding


# 預設首頁
@app.get("/")
async def root():
    return {"message": "Hello World"}


# 主要的聊天端點
@app.post("/chat")
async def chat(
    msg: str = Body(..., embed=True),  # 用戶輸入
):
    embedding = await get_embeddings(msg)  # 把用戶輸入轉成 embedding
    results = collection.query(
        query_embeddings=[embedding],  # 查詢向量
        n_results=3,  # 取最相近的三筆知識
    )
    # 用查詢到的知識，替換到 system prompt 中
    instructions_prompt = system_prompt.format(
        knowledge="- " + "\n- ".join(results["documents"][0]),  # type: ignore # 轉成條列格式
    )

    # 呼叫 OpenAI GPT 模型，注入 prompt 與用戶輸入
    response = await openai_client.responses.create(
        model="gpt-4.1-nano",  # 指定要使用的 GPT 模型名稱（根據你的權限設置）
        instructions=instructions_prompt,  # 傳入整理好的 system prompt（含知識庫資料與回答規則）
        input=msg,  # 用戶的輸入訊息（問題或對話內容）
        temperature=0.7,  # 生成文本的隨機程度，0.7 表示回答較有創意又不失穩定
    )
    return {"message": response.output_text}


# 新增知識的端點
@app.post("/knowledge")
async def knowledge(
    msg: str = Body(..., embed=True),  # 新知識的內容
):
    embedding = await get_embeddings(msg)
    collection.add(
        ids=[str(uuid.uuid4())],  # 用 uuid 產生唯一識別碼
        embeddings=[embedding],  # 儲存向量
        documents=[msg],  # 儲存原文
    )
    return {"message": "Knowledge added successfully"}


# 新增：取得全部知識的端點
@app.get("/knowledge")
async def get_knowledge():
    # chromadb collection.get() 會回傳一個 dict，裡面有 'documents'
    data = collection.get()
    return {
        "items": [
            {"id": id, "content": doc}
            for id, doc in zip(data["ids"], data["documents"])  # type: ignore
        ]
    }


# DELETE /knowledge/{id}
@app.delete("/knowledge/{id}")
async def delete_knowledge(id: str):
    collection.delete(ids=[id])
    return {"message": "Knowledge deleted successfully"}


# PUT /knowledge/{id}


class UpdateKnowledgeRequest(BaseModel):
    content: str


@app.put("/knowledge/{id}")
async def update_knowledge(id: str, req: UpdateKnowledgeRequest):
    # 刪掉原本的，新增新的
    collection.delete(ids=[id])
    embedding = await get_embeddings(req.content)
    collection.add(
        ids=[id],
        embeddings=[embedding],
        documents=[req.content],
    )
    return {"message": "Knowledge updated successfully"}
