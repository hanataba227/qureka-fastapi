import prompts.prompt as prompts
import summary.summarizer as summarizer

def run_generation(summary_text, generation_type):
    print(f">>> [{generation_type}] 문제 생성 시작...")

    # 프롬프트 구성
    prompt = prompts.get_summary_prompt(generation_type, summary_text)
    if not prompt or not prompt["system"] or not prompt["user"]:
        print("프롬프트 구성이 잘못되었습니다.")
        return

    # 문제 생성 요청
    result, usage = summarizer.summarize_with_chatgpt(prompt["system"], prompt["user"])

    print("\n🧠 생성된 문제:\n")
    print(result)
    print("\n📊 사용한 토큰 수:")
    print(f"- prompt_tokens: {usage.prompt_tokens}")
    print(f"- completion_tokens: {usage.completion_tokens}")
    print(f"- total_tokens: {usage.total_tokens}")

    return result  