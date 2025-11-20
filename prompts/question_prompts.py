import os
from .education_config import user_question_level, field_features

def get_question_prompts(field, question_level, question_count, choice_count, choice_format, array_choice_count, blank_count, content):
    """문제 생성 프롬프트들을 반환하는 함수"""
    prompts = {
        "문제 생성_n지 선다형": {
            "system": f"""너는 {field}에서 20년 경력을 지닌 평가 설계 전문가로, {question_level} 수준의 학습자를 위한 객관식 문제를 설계하는 데 특화되어 있다.
                          반드시 JSON 형태로 출력하라.
                          출력 JSON 형식:
                          {{
                              "questions": [
                                  {{
                                      "question_text": "문제 내용",
                                      "options": [
                                          {{"id": "1", "text": "선택지1"}},
                                          {{"id": "2", "text": "선택지2"}},
                                          {{"id": "3", "text": "선택지3"}},
                                          {{"id": "4", "text": "선택지4"}}
                                      ],
                                      "correct_answer": "3",
                                      "explanation": "해설 내용"
                                  }}
                              ]
                          }}""",
            "user": f'''위 JSON 형식에 맞춰 {choice_count}지선다형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        - 선택지 수: {choice_count}개  
                        - 선택지 형태: {choice_format}
                        
                        출력 규칙:
                        - 반드시 JSON 형식만 출력
                        - 선택지는 {choice_format} 형태로 구성
                        - 해설에는 정답 근거, 오답 분석, 혼동 지점 포함
                        - 결론은 "따라서 정답은 X번이다" 형태로 작성
                        
                        \n\n\n{content}'''
        },
        "문제 생성_순서 배열형": {
            "system": f"""너는 {field}에서 20년 경력을 지닌 평가 설계 전문가로, {question_level} 수준의 학습자를 위한 논리적 흐름, 절차적 지식의 이해를 평가하는 배열형 문항을 설계하는 데 특화되어 있다.
                          반드시 JSON 형태로 출력하라.
                          
                          **중요: 다양한 순서 패턴을 생성하라. 항상 동일한 패턴(예: 1-3-2)만 반복하지 마라.**
                          
                          출력 JSON 형식:
                          {{
                              "questions": [
                                  {{
                                      "question_text": "문제 내용",
                                      "items": [
                                          {{"id": 1, "text": "항목1"}},
                                          {{"id": 2, "text": "항목2"}},
                                          {{"id": 3, "text": "항목3"}}
                                      ],
                                      "correct_sequence": [1, 2, 3],
                                      "explanation": "해설 내용"
                                  }}
                              ]
                          }}
                          
                          **필수 규칙:**
                          - items는 무작위로 섞인 순서로 제공
                          - correct_sequence는 논리적으로 올바른 순서의 id 배열
                          - 다양한 순서 조합 생성 (예: [1,2,3], [2,1,3], [3,1,2], [1,3,2], [2,3,1], [3,2,1] 등)""",
            "user": f'''위 JSON 형식에 맞춰 순서 배열형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        **중요: 다양한 순서 패턴을 생성하라. 특정 패턴(예: 1-3-2)에 편향되지 마라.**
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        - 배열 항목 수: {array_choice_count}개
                        
                        출력 규칙:
                        - 반드시 JSON 형식만 출력
                        - 각 항목은 id와 text로 구성
                        - items 배열: 순서가 섞여서 제공 (무작위 순서)
                        - correct_sequence: 논리적으로 올바른 순서의 id 배열
                        - 가능한 모든 순열을 고려하여 다양한 패턴 생성
                        - 각 문제마다 서로 다른 순서 패턴을 사용하도록 노력
                        - 해설에는 각 단계의 의미와 순서 논리를 명확히 설명
                        - 결론은 "따라서 정답은 X-Y-Z이다" 형태로 작성
                        
                        예시 순서 패턴 (참고용, 다양하게 생성):
                        - 3개 항목: [1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]
                        - 4개 항목: [1,2,3,4], [2,1,4,3], [3,4,1,2], [4,2,1,3] 등
                        - 5개 항목: [1,3,5,2,4], [2,4,1,3,5], [5,1,3,2,4] 등
                        
                        \n\n\n{content}'''
        },
        "문제 생성_참거짓형": {
            "system": f"""너는 {field}에서 20년 경력을 지닌 평가 설계 전문가로, {question_level} 수준의 학습자를 위한 논리적 흐름, 절차적 지식의 이해를 평가하는 참거짓형 문항을 설계하는 데 특화되어 있다.
                          반드시 JSON 형태로 출력하라.
                          
                          출력 JSON 형식:
                          {{
                              "questions": [
                                  {{
                                      "question_text": "문제 내용",
                                      "correct_answer": true,
                                      "explanation": "해설 내용"
                                  }}
                              ]
                          }}""",
            "user": f'''위 JSON 형식에 맞춰 참거짓형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        
                        출력 규칙:
                        - 반드시 JSON 형식만 출력
                        - correct_answer는 true 또는 false
                        - 해설에는 진위 판별 근거와 핵심 개념 포함
                        - 결론은 "따라서 정답은 O(또는 X)이다" 형태로 작성
                        
                        \n\n\n{content}'''
        },
        "문제 생성_빈칸 채우기형": {
            "system": f"""너는 {field}에서 20년 경력을 지닌 평가 설계 전문가로, {question_level} 수준의 학습자를 위한 빈칸 채우기형 문항을 설계하는 데 특화되어 있다.
                          반드시 JSON 형태로 출력하라.
                          
                          **중요: 각 문제는 정확히 {blank_count}개의 빈칸을 포함하며, 4개의 선택지 중에서 {blank_count}개를 선택하는 방식이다.**
                          
                          출력 JSON 형식:
                          {{
                              "questions": [
                                  {{
                                      "question_text": "첫 번째 빈칸 ____ 과 두 번째 빈칸 ____ 을 포함한 문제 내용",
                                      "options": [
                                          {{"id": "1", "text": "선택지1"}},
                                          {{"id": "2", "text": "선택지2"}},
                                          {{"id": "3", "text": "선택지3"}},
                                          {{"id": "4", "text": "선택지4"}}
                                      ],
                                      "correct_answers": ["1", "3"],
                                      "explanation": "해설 내용"
                                  }}
                              ]
                          }}
                          
                          **필수 규칙:**
                          - question_text: 반드시 {blank_count}개의 ____ 포함
                          - options: 정확히 4개 (1, 2, 3, 4)
                          - correct_answers: {blank_count}개의 정답 id 배열 (예: ["1", "3"])
                          - 각 빈칸에 해당하는 정답은 순서대로 correct_answers 배열에 포함""",
            "user": f'''위 JSON 형식에 맞춰 빈칸 채우기형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        **중요: 각 문제는 정확히 {blank_count}개의 빈칸을 포함하며, 4개 선택지 중 {blank_count}개를 선택한다.**
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        - 빈칸 수: {blank_count}개 (반드시 준수)
                        
                        출력 규칙:
                        - 반드시 JSON 형식만 출력
                        - question_text에 정확히 {blank_count}개 ____ 포함
                        - options는 정확히 4개 (1, 2, 3, 4)
                        - correct_answers는 {blank_count}개의 id 배열 (빈칸 순서대로)
                        - 4개 선택지 중 {blank_count}개가 정답
                        - 해설에는 각 빈칸에 어떤 선택지가 들어가는지 순서대로 설명
                        - 결론은 "따라서 정답은 (첫 번째 빈칸: 1, 두 번째 빈칸: 3)" 형태로 작성
                        
                        \n\n\n{content}'''
        },
        "문제 생성_단답형": {
            "system": f"""너는 {field}에서 20년 경력을 지닌 평가 설계 전문가로, {question_level} 수준의 학습자를 위한 단답형 문항을 설계하는 데 특화되어 있다.
                          반드시 JSON 형태로 출력하라.
                          
                          출력 JSON 형식:
                          {{
                              "questions": [
                                  {{
                                      "question_text": "문제 내용",
                                      "correct_answer": "주요 정답",
                                      "alternative_answers": ["대체답안1", "대체답안2"],
                                      "case_sensitive": false,
                                      "explanation": "해설 내용"
                                  }}
                              ]
                          }}""",
            "user": f'''위 JSON 형식에 맞춰 단답형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        
                        출력 규칙:
                        - question_text: 문제 내용을 명확히 제시
                        - correct_answer: 주요 정답 (단어나 구로 구성, 마침표 없이)
                        - alternative_answers: 동의어나 대체 가능한 정답들 (2-3개)
                        - case_sensitive: false (대소문자 구분 안함)
                        - explanation: 정답 근거, 개념 정의, 오개념 구분 포함
                        
                        \n\n\n{content}'''
        },
        "문제 생성_서술형": {
            "system": f"""너는 {field}에서 20년 경력을 지닌 평가 설계 전문가로, {question_level} 수준의 학습자를 위한 서술형 문항을 설계하는 데 특화되어 있다.
                          반드시 JSON 형태로 출력하라.
                          
                          출력 JSON 형식:
                          {{
                              "questions": [
                                  {{
                                      "question_text": "문제 내용",
                                      "answer_keywords": ["키워드1", "키워드2", "키워드3"],
                                      "model_answer": "모범 답안",
                                      "explanation": "해설 내용"
                                  }}
                              ]
                          }}""",
            "user": f'''위 JSON 형식에 맞춰 서술형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        
                        출력 규칙:
                        - question_text: 문제 내용을 명확히 제시
                        - answer_keywords: 채점에 사용될 핵심 키워드 목록 (3-5개)
                        - model_answer: 모범 답안 (채점 기준이 되는 완전한 답안)
                        - explanation: 문제의 평가 목적, 핵심 개념, 답안 작성 가이드 포함
                        
                        \n\n\n{content}'''
        }
    }
    
    return prompts
