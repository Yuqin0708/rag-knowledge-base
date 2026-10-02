"""不需要 OPENAI_API_KEY 的展示用後端。

端點與 main.py 相同，但不呼叫 OpenAI：以關鍵字重疊度取代向量檢索，
回答直接引用最相關的知識。僅供本機預覽前端畫面，不代表實際的 RAG 品質。

啟動：poetry run fastapi dev mock_server.py
"""

import uuid

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# id -> content（記憶體，重啟後清空）；放兩筆範例讓畫面不是空的
knowledge: dict[str, str] = {
    str(uuid.uuid4()): "這是一個 RAG 範例系統：先把知識存進知識庫，AI 只依據知識庫內容回答。",
    str(uuid.uuid4()): "知識庫管理頁可以新增、搜尋、編輯與刪除知識。",
}


def score(query: str, text: str) -> int:
    """以共同字元數粗略估計相關度（中英文皆可）。"""
    return len(set(query.lower()) & set(text.lower()) - set(" ，。？！,.?!"))


@app.get("/")
async def root():
    return {"message": "Mock server"}


@app.post("/chat")
async def chat(msg: str = Body(..., embed=True)):
    ranked = sorted(knowledge.values(), key=lambda t: score(msg, t), reverse=True)
    top = [t for t in ranked[:3] if score(msg, t) >= 2]
    if not top:
        return {"message": "我找不到相關資料。"}
    return {"message": "（模擬回答，未呼叫 OpenAI）根據知識庫：\n- " + "\n- ".join(top)}


@app.post("/knowledge")
async def add_knowledge(msg: str = Body(..., embed=True)):
    knowledge[str(uuid.uuid4())] = msg
    return {"message": "Knowledge added successfully"}


@app.get("/knowledge")
async def get_knowledge():
    return {"items": [{"id": k, "content": v} for k, v in knowledge.items()]}


@app.delete("/knowledge/{id}")
async def delete_knowledge(id: str):
    knowledge.pop(id, None)
    return {"message": "Knowledge deleted successfully"}


class UpdateKnowledgeRequest(BaseModel):
    content: str


@app.put("/knowledge/{id}")
async def update_knowledge(id: str, req: UpdateKnowledgeRequest):
    knowledge[id] = req.content
    return {"message": "Knowledge updated successfully"}
