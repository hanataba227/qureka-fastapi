import os
from .summary_prompts import get_summary_prompts
from .question_prompts import get_question_prompts

# 요약 프롬프트 구성
def get_summary_prompt(type_name, content):
    # 환경 변수에서 설정값 가져오기
    field = os.getenv("field", "공학")
    summary_level = os.getenv("summary_level", "전공자")
    question_level = os.getenv("question_level", "전공자")
    sentence_count = os.getenv("sentence_count", "500")
    topic_count = os.getenv("topic_count", "2")
    keywords = os.getenv("keywords", "기타,등등")
    question_count = os.getenv("question_count", "3")
    choice_count = os.getenv("choice_count", "4")
    choice_format = os.getenv("choice_format", "문장형")
    array_choice_count = os.getenv("array_choice_count", "3")
    blank_count = os.getenv("blank_count", "1")

    if isinstance(keywords, str) and "," in keywords:
        keywords = keywords.split(",")

    # 요약 프롬프트들 가져오기
    if type_name in ["내용 요약_기본 요약", "내용 요약_핵심 요약", "내용 요약_주제 요약", "내용 요약_목차 요약", "내용 요약_키워드 요약"]:
        summary_prompts = get_summary_prompts(field, summary_level, sentence_count, topic_count, keywords, content)
        return summary_prompts.get(type_name, {"system": "", "user": ""})
    
    # 문제 생성 프롬프트들 가져오기
    elif type_name in ["문제 생성_n지 선다형", "문제 생성_순서 배열형", "문제 생성_참거짓형", "문제 생성_빈칸 채우기형", "문제 생성_단답형", "문제 생성_서술형"]:
        question_prompts = get_question_prompts(field, question_level, question_count, choice_count, choice_format, array_choice_count, blank_count, content)
        return question_prompts.get(type_name, {"system": "", "user": ""})
    
    return {"system": "", "user": ""}
