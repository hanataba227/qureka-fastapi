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
                                          {{"id": "A", "text": "선택지1"}},
                                          {{"id": "B", "text": "선택지2"}},
                                          {{"id": "C", "text": "선택지3"}},
                                          {{"id": "D", "text": "선택지4"}}
                                      ],
                                      "correct_answer": "C",
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
                          }}""",
            "user": f'''위 JSON 형식에 맞춰 순서 배열형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        - 배열 항목 수: {array_choice_count}개
                        
                        출력 규칙:
                        - 반드시 JSON 형식만 출력
                        - 각 항목은 id와 text로 구성
                        - correct_sequence는 올바른 순서의 id 배열
                        - 해설에는 각 단계의 의미와 순서 논리 포함
                        - 결론은 "따라서 정답은 X-Y-Z이다" 형태로 작성
                        
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
            "system": f"""너는 {field}에서 20년 경력을 지닌 평가 설계 전문가로, {question_level} 수준의 학습자를 위한 논리적 흐름, 절차적 지식의 이해를 평가하는 빈칸채우기형 문항을 설계하는 데 특화되어 있다.
                          반드시 JSON 형태로 출력하라.
                          
                          출력 JSON 형식:
                          {{
                              "questions": [
                                  {{
                                      "question_text": "빈칸이 포함된 문제 내용",
                                      "blanks": [
                                          {{
                                              "id": 1,
                                              "position": "____",
                                              "correct_answer": "정답",
                                              "options": [
                                                  {{"id": "A", "text": "선택지1"}},
                                                  {{"id": "B", "text": "선택지2"}},
                                                  {{"id": "C", "text": "선택지3"}},
                                                  {{"id": "D", "text": "선택지4"}}
                                              ]
                                          }}
                                      ],
                                      "explanation": "해설 내용"
                                  }}
                              ]
                          }}""",
            "user": f'''위 JSON 형식에 맞춰 빈칸 채우기형 문제 {question_count}개를 생성하라.
                        반드시 JSON 형식으로만 출력하고, 추가 설명이나 텍스트는 포함하지 마라.
                        
                        문제 요구사항:
                        - 분야: {field} ({field_features(field)})
                        - 학습자 수준: {question_level}
                        - 사고 구조: {user_question_level(question_level)}
                        - 문제 수: {question_count}개
                        - 빈칸 수: {blank_count}개
                        
                        출력 규칙:
                        - 반드시 JSON 형식만 출력
                        - 빈칸은 ____ 형태로 표시
                        - 각 빈칸은 id, position, correct_answer, options 포함
                        - 해설에는 문맥 분석과 정답 근거 포함
                        - 결론은 "따라서 정답은 X이다" 형태로 작성
                        
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
