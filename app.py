import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import shutil
from pathlib import Path
import uvicorn

from utils import (
    extract_text_from_pdf, 
    extract_text_from_pptx, 
    truncate_by_tokens, 
    summarize_with_chatgpt,
    get_summary_prompt
)

# FastAPI 앱 생성
app = FastAPI(
    title="Qureka API",
    description="문서 요약 및 문제 생성 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],  # 프론트엔드 주소 명시적 추가
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
)

# 요청 모델 정의
class SummaryRequest(BaseModel):
    summary_type: str
    field: str = "모든 분야"
    level: str = "비전공자"
    sentence_count: int = 3
    topic_count: Optional[int] = 1
    keyword_count: Optional[int] = 0
    keywords: Optional[List[str]] = None
    
class GenerationRequest(BaseModel):
    generation_type: str
    summary_text: str
    field: str = "모든 분야"
    level: str = "비전공자"
    question_count: int = 3
    choice_count: Optional[int] = 4
    choice_format: Optional[str] = "단답형"
    array_choice_count: Optional[int] = 3
    blank_count: Optional[int] = 1

@app.get("/")
async def root():
    return {"message": "Qureka API is running"}

@app.post("/api/summarize")
async def summarize(
    file: UploadFile = File(...),
    summary_type: str = Form(...),
    field: str = Form("모든 분야"),
    level: str = Form("비전공자"),
    sentence_count: int = Form(3),
    topic_count: Optional[int] = Form(1),
    keyword_count: Optional[int] = Form(0),
    keywords: Optional[str] = Form(None)
):
    # 파일 임시 저장
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in [".pdf", ".pptx"]:
        raise HTTPException(status_code=400, detail="지원되지 않는 파일 형식입니다. PDF 또는 PPTX만 가능합니다.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # 파일에서 텍스트 추출
        if file_extension == ".pdf":
            content = extract_text_from_pdf(tmp_path)
        elif file_extension == ".pptx":
            content = extract_text_from_pptx(tmp_path)
        
        # 전역 변수 설정 (get_summary_prompt에서 필요)
        global_vars = {
            "field": field,
            "level": level,
            "sentence_count": sentence_count,
            "topic_count": topic_count,
            "keyword_count": keyword_count,
            "keywords": keywords.split(",")
        }
        
        # 환경 변수로 전역 변수 설정
        for key, value in global_vars.items():
            os.environ[key] = str(value)
        
        # 프롬프트 구성
        prompt = get_summary_prompt(summary_type, content)
        
        if not prompt or not prompt["system"] or not prompt["user"]:
            raise HTTPException(status_code=500, detail="프롬프트 구성이 잘못되었습니다.")
            
        # 요약 실행
        summary, usage = summarize_with_chatgpt(prompt["system"], prompt["user"])
        
        # 결과 반환
        return JSONResponse(content={
            "summary": summary,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
        })
    finally:
        # 임시 파일 삭제
        os.unlink(tmp_path)

@app.post("/api/generate")
async def generate(request: GenerationRequest):
    try:
        # 전역 변수 설정
        global_vars = {
            "field": request.field,
            "level": request.level,
            "question_count": request.question_count,
            "choice_count": request.choice_count,
            "choice_format": request.choice_format,
            "array_choice_count": request.array_choice_count,
            "blank_count": request.blank_count
        }
        
        # 환경 변수로 전역 변수 설정
        for key, value in global_vars.items():
            if value is not None:
                os.environ[key] = str(value)
        
        # 프롬프트 구성
        prompt = get_summary_prompt(request.generation_type, request.summary_text)
        
        if not prompt or not prompt["system"] or not prompt["user"]:
            raise HTTPException(status_code=500, detail="프롬프트 구성이 잘못되었습니다.")
            
        # 문제 생성 실행
        result, usage = summarize_with_chatgpt(prompt["system"], prompt["user"])
        
        # 결과 반환
        return JSONResponse(content={
            "result": result,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
