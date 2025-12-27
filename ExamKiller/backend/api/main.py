import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import aiofiles
import httpx
from dotenv import load_dotenv

load_dotenv()

QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "sk-12835c34b4c744c59f1f24f3acef2b4d")
QWEN_MODEL = os.getenv("QWEN_MODEL_NAME", "qwen-plus")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

papers_db = {}
questions_db = {}
knowledge_db = {}
users_db = {"demo": {"id": "demo", "name": "演示用户", "email": "demo@example.com"}}

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    yield

app = FastAPI(title="ExamKiller - 大学考试复习辅助平台", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

class PaperUpload(BaseModel):
    title: str
    subject: str
    course: str
    chapter: Optional[str] = None
    difficulty: float = 3.0
    exam_date: Optional[str] = None

class ReviewInput(BaseModel):
    text: str
    source_type: str = "text"

class GenerationSettings(BaseModel):
    question_count: int = 10
    easy_ratio: int = 30
    medium_ratio: int = 50
    hard_ratio: int = 20
    question_types: List[str] = ["choice", "fill"]

class QuestionGenerate(BaseModel):
    review_input: ReviewInput
    settings: GenerationSettings

class KnowledgeExtract(BaseModel):
    text: str

class ExportSettings(BaseModel):
    title: str
    template: str = "academic"
    content: str

class SummaryGenerate(BaseModel):
    text: str
    source_type: str = "text"

async def call_qwen_api(messages: List[dict], max_tokens: int = 2000) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{QWEN_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": QWEN_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

@app.get("/")
async def serve_frontend():
    return FileResponse("../index.html")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "服务正常运行", "timestamp": datetime.now().isoformat()}

@app.post("/api/papers/upload")
async def upload_paper(paper: PaperUpload, background_tasks: BackgroundTasks):
    paper_id = str(uuid.uuid4())
    paper_data = {
        "id": paper_id,
        "title": paper.title,
        "subject": paper.subject,
        "course": paper.course,
        "chapter": paper.chapter,
        "difficulty": paper.difficulty,
        "exam_date": paper.exam_date,
        "status": "uploaded",
        "created_at": datetime.now().isoformat(),
        "questions": [],
        "analysis": None
    }
    papers_db[paper_id] = paper_data
    background_tasks.add_task(analyze_paper_background, paper_id, paper.title)
    return {"success": True, "paper_id": paper_id, "message": "试卷上传成功"}

async def analyze_paper_background(paper_id: str, title: str):
    try:
        await asyncio.sleep(2)
        analysis_result = {
            "question_count": 25,
            "knowledge_points": ["函数极限", "导数计算", "积分应用"],
            "difficulty_distribution": {"easy": 10, "medium": 10, "hard": 5},
            "subject": "高等数学",
            "course": "微积分"
        }
        if paper_id in papers_db:
            papers_db[paper_id]["analysis"] = analysis_result
            papers_db[paper_id]["status"] = "analyzed"
    except Exception as e:
        print(f"分析失败: {e}")

import asyncio

@app.get("/api/papers")
async def list_papers():
    return {"papers": list(papers_db.values())}

@app.get("/api/papers/{paper_id}")
async def get_paper(paper_id: str):
    if paper_id not in papers_db:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return papers_db[paper_id]

@app.delete("/api/papers/{paper_id}")
async def delete_paper(paper_id: str):
    if paper_id not in papers_db:
        raise HTTPException(status_code=404, detail="试卷不存在")
    del papers_db[paper_id]
    return {"success": True, "message": "删除成功"}

@app.post("/api/knowledge/extract")
async def extract_knowledge(input_data: KnowledgeExtract):
    try:
        prompt = f"""请从以下复习内容中提取知识点，并按重要性分级（核心/重要/一般）。返回JSON格式：

复习内容：
{input_data.text}

请提取所有专业术语、概念、定理、公式等知识点。

JSON格式：
{{
    "knowledge_points": [
        {{
            "name": "知识点名称",
            "importance": "core/important/normal",
            "description": "简短描述"
        }}
    ],
    "cross_domain": ["跨学科关联1", "跨学科关联2"]
}}

只返回JSON，不要其他内容。"""

        result = await call_qwen_api([
            {"role": "system", "content": "你是一个专业的学科知识提取助手，擅长从文本中提取结构化的知识点。"},
            {"role": "user", "content": prompt}
        ], max_tokens=2000)

        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            json_str = result[json_start:json_end]
            data = json.loads(json_str)
        except:
            data = {"knowledge_points": [], "cross_domain": []}

        extracted = []
        for i, kp in enumerate(data.get("knowledge_points", [])):
            kp_id = str(uuid.uuid4())
            kp_data = {
                "id": kp_id,
                "name": kp.get("name", f"知识点{i+1}"),
                "importance": kp.get("importance", "normal"),
                "description": kp.get("description", ""),
                "cross_domain": data.get("cross_domain", [])
            }
            knowledge_db[kp_id] = kp_data
            extracted.append(kp_data)

        return {"success": True, "knowledge_points": extracted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识点提取失败: {str(e)}")

@app.post("/api/questions/generate")
async def generate_questions(request: QuestionGenerate):
    try:
        settings = request.settings
        review_text = request.review_input.text
        
        difficulty_map = []
        difficulty_map.extend(["easy"] * settings.easy_ratio)
        difficulty_map.extend(["medium"] * settings.medium_ratio)
        difficulty_map.extend(["hard"] * settings.hard_ratio)
        
        prompt = f"""根据以下复习内容生成{settings.question_count}道练习题：

复习内容：
{review_text}

要求：
1. 题目类型包括：{', '.join(settings.question_types)}
2. 难度分布：简单{settings.easy_ratio}%，中等{settings.medium_ratio}%，困难{settings.hard_ratio}%
3. 每道题包含：题目内容、正确答案、简要解析

请生成题目并以JSON格式返回：

{{
    "questions": [
        {{
            "id": 1,
            "content": "题目内容",
            "type": "choice/fill/judge/essay",
            "difficulty": "easy/medium/hard",
            "score": 2,
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "answer": "正确答案",
            "explanation": "解析说明"
        }}
    ],
    "summary": {{
        "total_count": {settings.question_count},
        "estimated_time": 30,
        "difficulty_distribution": {{"easy": {int(settings.question_count * settings.easy_ratio / 100)}, "medium": {int(settings.question_count * settings.medium_ratio / 100)}, "hard": {int(settings.question_count * settings.hard_ratio / 100)}}}
    }}
}}

只返回JSON，不要其他内容。"""

        result = await call_qwen_api([
            {"role": "system", "content": "你是一个专业的出题老师，擅长根据复习内容生成高质量的练习题。"},
            {"role": "user", "content": prompt}
        ], max_tokens=4000)

        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            json_str = result[json_start:json_end]
            data = json.loads(json_str)
        except:
            data = {"questions": [], "summary": {"total_count": settings.question_count, "estimated_time": 30}}

        generated_questions = []
        for q in data.get("questions", []):
            q_id = str(uuid.uuid4())
            q_data = {
                "id": q_id,
                "content": q.get("content", ""),
                "type": q.get("type", "choice"),
                "difficulty": q.get("difficulty", "medium"),
                "score": q.get("score", 2),
                "options": q.get("options", []),
                "answer": q.get("answer", ""),
                "explanation": q.get("explanation", ""),
                "created_at": datetime.now().isoformat()
            }
            questions_db[q_id] = q_data
            generated_questions.append(q_data)

        summary = data.get("summary", {"total_count": len(generated_questions), "estimated_time": len(generated_questions) * 2})
        
        return {
            "success": True,
            "questions": generated_questions,
            "total_count": len(generated_questions),
            "estimated_time": summary.get("estimated_time", len(generated_questions) * 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"题目生成失败: {str(e)}")

@app.get("/api/knowledge/graph")
async def get_knowledge_graph():
    nodes = [
        {"id": "1", "name": "函数极限", "importance": "core", "x": 400, "y": 100},
        {"id": "2", "name": "极限定义", "importance": "important", "x": 250, "y": 200},
        {"id": "3", "name": "运算法则", "importance": "important", "x": 550, "y": 200},
        {"id": "4", "name": "邻域概念", "importance": "normal", "x": 150, "y": 320},
        {"id": "5", "name": "去心邻域", "importance": "normal", "x": 350, "y": 320},
        {"id": "6", "name": "四则运算", "importance": "normal", "x": 450, "y": 320},
        {"id": "7", "name": "复合函数", "importance": "normal", "x": 650, "y": 320}
    ]
    links = [
        {"source": "1", "target": "2"},
        {"source": "1", "target": "3"},
        {"source": "2", "target": "4"},
        {"source": "2", "target": "5"},
        {"source": "3", "target": "6"},
        {"source": "3", "target": "7"}
    ]
    return {"nodes": nodes, "links": links}

@app.get("/api/knowledge")
async def list_knowledge():
    return {"knowledge_points": list(knowledge_db.values())}

@app.post("/api/exports/generate")
async def generate_document(settings: ExportSettings):
    try:
        content = settings.content
        
        prompt = f"""根据以下内容生成一份结构化的复习资料：

标题：{settings.title}
模板风格：{settings.template}

内容：
{content}

请生成一份完整的复习文档，包含：
1. 知识点概述
2. 重点难点分析
3. 典型例题
4. 解题思路
5. 练习建议

以Markdown格式返回，只返回内容本身。"""

        result = await call_qwen_api([
            {"role": "system", "content": "你是一个专业的学习资料整理专家，擅长将知识点整理成结构清晰、易于理解的复习文档。"},
            {"role": "user", "content": prompt}
        ], max_tokens=3000)

        return {
            "success": True,
            "document": result,
            "format": "markdown"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档生成失败: {str(e)}")

@app.post("/api/exports/download")
async def download_document(settings: ExportSettings):
    try:
        from fastapi.responses import Response
        import datetime
        
        content = settings.content
        
        prompt = f"""根据以下内容生成一份结构化的复习资料：

标题：{settings.title}
模板风格：{settings.template}

内容：
{content}

请生成一份完整的复习文档，包含：
1. 知识点概述
2. 重点难点分析
3. 典型例题
4. 解题思路
5. 练习建议

以Markdown格式返回，只返回内容本身。"""

        result = await call_qwen_api([
            {"role": "system", "content": "你是一个专业的学习资料整理专家，擅长将知识点整理成结构清晰、易于理解的复习文档。"},
            {"role": "user", "content": prompt}
        ], max_tokens=3000)

        return Response(
            content=result,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={settings.title}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档下载失败: {str(e)}")

@app.post("/api/summary/generate")
async def generate_summary(request: SummaryGenerate):
    try:
        text = request.text
        
        prompt = f"""请根据以下内容生成一份知识摘要，包含知识图谱和表格形式的知识点整理：

内容：
{text}

要求：
1. 提取核心知识点
2. 生成知识图谱的节点和边关系
3. 以表格形式整理知识点，包含名称、重要程度（核心/重要/一般）、简短描述
4. 识别知识点之间的关联关系

返回格式：
{{
  "knowledge_points": [
    {{
      "id": "kp_1",
      "name": "知识点名称",
      "importance": "core/important/normal",
      "description": "知识点描述",
      "related_points": ["相关知识点1", "相关知识点2"]
    }}
  ],
  "knowledge_graph": {{
    "nodes": [
      {{ "id": "node_1", "name": "知识点1", "importance": "core", "x": 100, "y": 100 }}
    ],
    "links": [
      {{ "source": "node_1", "target": "node_2" }}
    ]
  }}
}}

只返回JSON格式，不要其他内容。"""

        result = await call_qwen_api([
            {"role": "system", "content": "你是一个专业的知识图谱构建专家，擅长从文本中提取结构化的知识点并构建知识网络。"},
            {"role": "user", "content": prompt}
        ], max_tokens=3000)

        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            json_str = result[json_start:json_end]
            data = json.loads(json_str)
        except:
            data = {
                "knowledge_points": [],
                "knowledge_graph": {"nodes": [], "links": []}
            }

        return {
            "success": True,
            "knowledge_points": data.get("knowledge_points", []),
            "knowledge_graph": data.get("knowledge_graph", {"nodes": [], "links": []})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识摘要生成失败: {str(e)}")

@app.post("/api/questions/download")
async def download_questions(questions: dict):
    try:
        from fastapi.responses import Response
        import datetime
        
        generated_questions = questions.get("questions", [])
        
        if not generated_questions:
            raise HTTPException(status_code=400, detail="没有可下载的题目")
        
        # 生成题目文档
        doc_content = "# 复习试卷\n\n"
        doc_content += f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        doc_content += f"题目数量: {len(generated_questions)}\n\n"
        
        for i, q in enumerate(generated_questions, 1):
            type_name = {"choice": "选择题", "fill": "填空题", "judge": "判断题", "essay": "简答题", "calculation": "计算题"}[q.get("type", "choice")]
            diff_name = {"easy": "简单", "medium": "中等", "hard": "困难"}[q.get("difficulty", "medium")]
            
            doc_content += f"## 第 {i} 题 ({type_name} · {diff_name})\n"
            doc_content += f"**题目**: {q.get('content', '')}\n\n"
            
            if q.get("type") == "choice" and q.get("options"):
                for opt in q.get("options"):
                    doc_content += f"{opt}\n"
                doc_content += "\n"
            
            doc_content += f"**答案**: {q.get('answer', '')}\n\n"
            doc_content += f"**解析**: {q.get('explanation', '')}\n\n"
        
        filename = f"review_questions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        return Response(
            content=doc_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"题目下载失败: {str(e)}")

@app.post("/api/voice/transcribe")
async def voice_transcribe():
    return {"text": "函数极限的定义：当x无限接近于x0时，f(x)无限接近于某个常数A，则称A为f(x)当x→x0时的极限。", "success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
