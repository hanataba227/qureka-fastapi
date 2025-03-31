import os
import summary.extractor as extractor
import summary.summarizer as summarizer
import prompts.prompt as prompts
import generate.generator as generate

def run_summary(file_path, summary_type):
    print(f">>> [{summary_type}] 요약 시작...")

    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        content = extractor.extract_text_from_pdf(file_path)
    elif ext == ".pptx":
        content = extractor.extract_text_from_pptx(file_path)
    else:
        print("지원되지 않는 파일 형식입니다. PDF 또는 PPTX만 가능합니다.")
        return

    prompt = prompts.get_summary_prompt(summary_type, content)
    if not prompt or not prompt["system"] or not prompt["user"]:
        print("프롬프트 구성이 잘못되었습니다.")
        return

    summary, usage = summarizer.summarize_with_chatgpt(prompt["system"], prompt["user"])

    print("\n📘 요약 결과:\n")
    print(summary)
    print("\n📊 사용한 토큰 수:")
    print(f"- prompt_tokens: {usage.prompt_tokens}")
    print(f"- completion_tokens: {usage.completion_tokens}")
    print(f"- total_tokens: {usage.total_tokens}")
    
    generate.run_generation(summary, "문제 생성_단답형")

if __name__ == "__main__":
    file_path = "data/영상처리.pdf"
    summary_type = "내용 요약_기본 요약"
    run_summary(file_path, summary_type)