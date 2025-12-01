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
    summarize_with_chatgpt,
    get_summary_prompt,
    get_base_url
)
from settings import ALLOWED_ORIGINS, ALLOW_ALL_ORIGINS

# FastAPI 앱 생성
app = FastAPI(
    title="Qureka API",
    description="문서 요약 및 문제 생성 API",
    version="1.0.0"
)

# CORS 설정 - 통합된 버전
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOW_ALL_ORIGINS else ALLOWED_ORIGINS,  # 설정에 따라 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400  # 프리플라이트 요청 캐싱 (24시간)
)

# 요청 모델 정의
class SummaryRequest(BaseModel):
    summary_type: str
    field: str = "공학"
    level: str = "대학생"
    sentence_count: int = 500
    topic_count: Optional[int] = 2
    keyword_count: Optional[int] = 3
    keywords: Optional[List[str]] = None
    
class GenerationRequest(BaseModel):
    generation_type: str
    summary_text: str
    field: str = "공학"
    level: str = "대학생"
    question_count: int = 3
    choice_count: Optional[int] = 4
    choice_format: Optional[str] = "문장형"
    array_choice_count: Optional[int] = 3
    blank_count: Optional[int] = 1

@app.get("/")
async def root():
    return {"message": "Qureka API is running", "base_url": get_base_url()}

@app.post("/api/summarize")
async def summarize(
    file: UploadFile = File(...),
    summary_type: str = Form(...),
    field: str = Form("공학"),
    level: str = Form("전공자"),
    sentence_count: int = Form(500),
    topic_count: Optional[int] = Form(2),
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
        
        # 텍스트 길이 확인
        if len(content.strip()) < 200:
            raise HTTPException(status_code=400, detail="파일에서 추출된 텍스트가 너무 짧습니다. 최소 200자 이상이어야 합니다.")
        
        # 전역 변수 설정 (get_summary_prompt에서 필요)
        global_vars = {
            "field": field,
            "level": level,
            "sentence_count": sentence_count,
            "topic_count": topic_count,
            "keywords": keywords.split(",") if keywords else ["키워드1", "키워드2", "키워드3"]
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

# 파일 업로드 기반 문제 생성 엔드포인트
@app.post("/api/generate-from-file")
async def generate_from_file(
    file: UploadFile = File(...),
    generation_type: str = Form(...),
    field: str = Form("공학"),
    level: str = Form("대학생"),
    question_count: int = Form(3),
    choice_count: Optional[int] = Form(4),
    choice_format: Optional[str] = Form("문장형"),
    array_choice_count: Optional[int] = Form(3),
    blank_count: Optional[int] = Form(1),
):
    # 파일 확장자 확인 및 임시 저장
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in [".pdf", ".pptx"]:
        raise HTTPException(status_code=400, detail="지원되지 않는 파일 형식입니다. PDF 또는 PPTX만 가능합니다.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 파일에서 원문 텍스트 추출
        if file_extension == ".pdf":
            original_text = extract_text_from_pdf(tmp_path)
        else:  # .pptx
            original_text = extract_text_from_pptx(tmp_path)

        if not original_text or not original_text.strip():
            raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다.")

        # 텍스트 길이 확인
        if len(original_text.strip()) < 200:
            raise HTTPException(status_code=400, detail="파일에서 추출된 텍스트가 너무 짧습니다. 최소 200자 이상이어야 합니다.")

        # /api/generate와 동일하게 환경 변수 설정
        global_vars = {
            "field": field,
            "level": level,
            "question_count": question_count,
            "choice_count": choice_count,
            "choice_format": choice_format,
            "array_choice_count": array_choice_count,
            "blank_count": blank_count,
        }
        for key, value in global_vars.items():
            if value is not None:
                os.environ[key] = str(value)

        # 프롬프트 구성 및 문제 생성 실행
        prompt = get_summary_prompt(generation_type, original_text)
        if not prompt or not prompt.get("system") or not prompt.get("user"):
            raise HTTPException(status_code=500, detail="프롬프트 구성이 잘못되었습니다.")

        result, usage = summarize_with_chatgpt(prompt["system"], prompt["user"])

        return JSONResponse(content={
            "result": result,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            },
        })
    finally:
        # 임시 파일 삭제
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port)