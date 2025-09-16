# keyword_generator.py
import os
import json
import requests
from datetime import datetime

# --- ⚙️ 1. 기본 설정 (사용자가 직접 수정) ---
CONFIG = {
    # OpenAI 또는 Gemini API 키를 GitHub Secrets에서 가져올 때 사용할 이름입니다. (이름을 바꾸지 마세요)
    "OPENAI_API_KEY_SECRET": "OPENAI_API_KEY",
    "GEMINI_API_KEY_SECRET": "GEMINI_API_KEY",

    # 키워드를 생성할 때 참고할 '씨앗' 키워드 목록입니다. 자유롭게 수정하세요.
    "SEED_KEYWORDS": ["IT 트렌드", "AI 신기술", "헬스케어", "MZ세대 유행", "국내여행 추천", "재테크 방법", "최신 영화 리뷰"],
    
    # 생성할 키워드 개수
    "KEYWORD_COUNT": 30,

    # 결과물을 저장할 파일 이름
    "OUTPUT_FILENAME": "keywords.json"
}

def call_ai(prompt: str) -> str:
    """
    사용 가능한 API 키를 사용하여 AI를 호출하고, 응답 텍스트를 반환합니다.
    """
    openai_key = os.getenv(CONFIG["OPENAI_API_KEY_SECRET"])
    gemini_key = os.getenv(CONFIG["GEMINI_API_KEY_SECRET"])

    if gemini_key:
        print("Gemini API를 사용하여 키워드를 생성합니다.")
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_key}"
        payload = {
            "contents": [{"parts":[{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        json_response = response.json()
        return json_response["candidates"][0]["content"]["parts"][0]["text"]
        
    elif openai_key:
        print("OpenAI API를 사용하여 키워드를 생성합니다.")
        api_url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {openai_key}'}
        payload = {
            'model': 'gpt-4o-mini',
            'messages': [{'role': 'user', 'content': prompt}],
            'response_format': {"type": "json_object"}
        }
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        json_response = response.json()
        return json_response["choices"][0]["message"]["content"]
        
    else:
        raise ValueError("API 키가 설정되지 않았습니다. GitHub Secrets를 확인하세요.")

def main():
    """
    메인 실행 함수. AI를 호출하여 키워드를 생성하고 파일로 저장합니다.
    """
    today = datetime.now().strftime('%Y년 %m월 %d일')
    prompt = f"""
        {today} 기준, 대한민국 최신 트렌드를 종합적으로 반영하여 블로그 글감으로 활용할 '롱테일 키워드'를 {CONFIG['KEYWORD_COUNT']}개 생성해줘.

        다음 씨앗 키워드들을 참고하되, 여기에 없는 완전히 새로운 분야의 키워드도 적극적으로 포함시켜줘.
        씨앗 키워드: {', '.join(CONFIG['SEED_KEYWORDS'])}

        [규칙]
        - IT, 건강, 경제, 여행, 문화, 라이프스타일 등 다양한 주제를 포함해야 해.
        - 각 키워드는 '2025년 다이어리 추천', '겨울철 실내 데이트 코스' 처럼 구체적인 검색어 형태여야 해.
        - 결과는 반드시 {"{ 'keywords': ['키워드1', '키워드2', ...] }"} 형식의 JSON 객체로만 응답해야 해. 다른 설명은 절대 추가하지 마.
    """

    try:
        print(f"AI에게 {CONFIG['KEYWORD_COUNT']}개의 트렌드 키워드 생성을 요청합니다...")
        ai_response_text = call_ai(prompt)
        
        if ai_response_text.strip().startswith("```json"):
            ai_response_text = ai_response_text.strip()[7:-3].strip()
            
        result = json.loads(ai_response_text)
        keywords = result.get("keywords", [])

        if not keywords:
            raise ValueError("AI가 유효한 키워드를 생성하지 못했습니다.")
        
        with open(CONFIG["OUTPUT_FILENAME"], "w", encoding="utf-8") as f:
            json.dump({"keywords": keywords}, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 성공: {len(keywords)}개의 키워드를 '{CONFIG['OUTPUT_FILENAME']}' 파일에 저장했습니다.")

    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        with open(CONFIG["OUTPUT_FILENAME"], "w", encoding="utf-8") as f:
            json.dump({"keywords": [f"키워드 생성 중 오류 발생: {e}"]}, f, ensure_ascii=False, indent=2)
        raise e

if __name__ == "__main__":
    from dotenv import load_dotenv
    print("로컬 테스트 모드로 실행합니다. .env 파일에서 API 키를 로드합니다.")
    load_dotenv()
    main()