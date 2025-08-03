import os
from utils import (
    extract_text_from_pptx,
    get_summary_prompt,
    summarize_with_chatgpt
)

def test_basic_summary():
    # SW개발.pptx 파일 경로
    file_path = "data/SW개발.pptx"
    
    # 파일이 존재하는지 확인
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return
    
    try:
        # PPTX 파일에서 텍스트 추출
        print("PPTX 파일에서 텍스트 추출 중...")
        content = extract_text_from_pptx(file_path)
        print(f"추출된 텍스트 길이: {len(content)} 글자")
        print(f"추출된 텍스트 일부:\n{content[:500]}...\n")
        
        # 전역 변수 설정 (프롬프트에서 필요)
        global_vars = {
            "field": "공학",
            "summary_level": "전공자", 
            "sentence_count": "3",
            "topic_count": "3",
            "keywords": "소프트웨어,개발,프로그래밍"
        }
        
        # 환경 변수로 전역 변수 설정
        for key, value in global_vars.items():
            os.environ[key] = str(value)
        
        # 프롬프트 구성
        print("프롬프트 구성 중...")
        prompt = get_summary_prompt("내용 요약_기본 요약", content)
        
        if not prompt or not prompt["system"] or not prompt["user"]:
            print("프롬프트 구성이 잘못되었습니다.")
            return
        
        print("시스템 프롬프트:")
        print(prompt["system"][:500] + "...\n")
        
        # 요약 실행
        print("GPT를 이용한 요약 진행 중...")
        summary, usage = summarize_with_chatgpt(prompt["system"], prompt["user"])
        
        # 결과 출력
        print("\n" + "="*50)
        print("요약 결과:")
        print("="*50)
        print(summary)
        print("\n" + "="*50)
        print("토큰 사용량:")
        print(f"프롬프트 토큰: {usage.prompt_tokens}")
        print(f"완성 토큰: {usage.completion_tokens}")
        print(f"총 토큰: {usage.total_tokens}")
        print("="*50)
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

def test_multiple_choice_generation():
    # 샘플 요약 텍스트 (실제로는 위 함수에서 생성된 요약을 사용)
    sample_summary = """
    소프트웨어 개발은 체계적인 접근 방식을 통해 사용자의 요구사항을 분석하고 설계, 구현, 테스트, 유지보수의 단계를 거쳐 완성되는 과정이다.
    개발 생명주기에서는 폭포수 모델, 애자일 방법론 등 다양한 방법론이 사용되며, 각각의 특성에 따라 프로젝트에 적합한 방법을 선택해야 한다.
    품질 보증을 위해서는 단위 테스트, 통합 테스트, 시스템 테스트 등 다단계 테스트 과정이 필요하며, 지속적인 리팩토링을 통해 코드의 품질을 유지해야 한다.
    """
    
    try:
        # 전역 변수 설정 (문제 생성용)
        global_vars = {
            "field": "공학",
            "question_level": "전공자",
            "question_count": "2",
            "choice_count": "4",
            "choice_format": "문장형"
        }
        
        # 환경 변수로 전역 변수 설정
        for key, value in global_vars.items():
            os.environ[key] = str(value)
        
        # 프롬프트 구성
        print("\n" + "="*50)
        print("문제 생성 테스트 시작")
        print("="*50)
        print("문제 생성용 프롬프트 구성 중...")
        prompt = get_summary_prompt("문제 생성_n지 선다형", sample_summary)
        
        if not prompt or not prompt["system"] or not prompt["user"]:
            print("프롬프트 구성이 잘못되었습니다.")
            return
        
        print("시스템 프롬프트:")
        print(prompt["system"][:500] + "...\n")
        
        # 문제 생성 실행
        print("GPT를 이용한 문제 생성 진행 중...")
        questions, usage = summarize_with_chatgpt(prompt["system"], prompt["user"])
        
        # 결과 출력
        print("\n" + "="*50)
        print("생성된 문제:")
        print("="*50)
        print(questions)
        print("\n" + "="*50)
        print("토큰 사용량:")
        print(f"프롬프트 토큰: {usage.prompt_tokens}")
        print(f"완성 토큰: {usage.completion_tokens}")
        print(f"총 토큰: {usage.total_tokens}")
        print("="*50)
        
    except Exception as e:
        print(f"문제 생성 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_basic_summary()
    test_multiple_choice_generation()
