"""
ORBIT - 한 줄 아이디어로 '함께할 팀원을 찾는 비전'을 만들어 주는 프로그램

⭐ ORBIT의 핵심:
   ORBIT은 사업계획서를 만드는 서비스가 '아니라',
   "이 아이디어를 함께 만들 팀원을 찾아주는" 서비스입니다.
   그래서 결과에는 반드시 아래 두 가지가 들어갑니다:
     1. neededTeammates (필요한 팀원)   — 이 아이디어를 실현하려면 어떤 사람이 필요한가
     2. matchFactors    (매칭 중요 요소) — 실력 외에 어떤 성향·가치가 잘 맞아야 하는가

사용법:
    python src/main.py "페트병 뚜껑을 그립톡으로 재활용하는 사업"

아이디어가 너무 빈약하면(예: "그립톡 사업"), AI 가 비전을 억지로 만들지 않고
'무엇을 더 알려달라'(askFor)고 되물어 줍니다.
"""

import json
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

# 1) .env 파일에 적어둔 ANTHROPIC_API_KEY 를 불러옵니다.
#    (코드 안에 키를 직접 쓰지 않아도 됩니다 — 그게 안전한 방법입니다.)
load_dotenv()

# 2) 키가 제대로 들어있는지 친절하게 확인해 줍니다.
if not os.getenv("ANTHROPIC_API_KEY") or "여기에" in os.getenv("ANTHROPIC_API_KEY", ""):
    raise SystemExit(
        "❌ .env 파일에 진짜 API 키가 아직 없습니다.\n"
        "   ORBIT/.env 를 열어 ANTHROPIC_API_KEY= 뒤에 키를 붙여넣어 주세요."
    )

# 3) Anthropic 클라이언트를 만듭니다. (.env 의 키를 자동으로 사용합니다.)
client = Anthropic()

# 4) Claude 에게 줄 '역할(시스템 프롬프트)'.
#    여기서 ORBIT 의 핵심 규칙과, 받아야 할 JSON 모양을 정확히 알려줍니다.
SYSTEM_PROMPT = """당신은 ORBIT의 비전 생성 AI입니다.
사용자가 던진 한 줄 아이디어를, 함께 만들 팀원이 한눈에 이해하고 합류하고 싶게 만드는 '비전 페이지'로 구체화합니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 앞뒤에 다른 말, 설명, 코드펜스(```)를 절대 붙이지 마세요.
- 어조: 각 분야 전문가가 읽고 '나도 이 프로젝트에 합류하고 싶다'고 느낄 만큼 설득력 있고 진정성 있게 씁니다.
  단, 아직 '아이디어 단계(진척도 0%)'이므로 없는 성과를 있는 척하거나 과장하지는 마세요.
- story(왜 이 사업을 하는가)는 아이디어 제공자가 1인칭('저는…')으로 들려주는 짧은 이야기 3개 문단입니다. 계기 → 발견 → 신념/다짐 흐름으로, 사람 냄새 나게.
- whyNow(왜 지금·왜 함께)는 지금 시작해야 하는 이유 3가지. 각 {icon(이모지 1개), title(짧게), desc(한 줄)}.
- productNote: 어떤 제품/서비스를 만드는지 한 줄 설명.
- neededTeammates(필요한 팀원)는 3~5명. 각 {role, detail}.
    · role : 직무명(개발자)이 아니라 '무엇을 할 수 있는 사람'(폐플라스틱 가공 설비를 다룰 수 있는 사람)
    · detail : 합류하면 맡는 일과 왜 중요한지, 그 분야 사람이 끌릴 이유 한 줄
- matchFactors(매칭 중요 요소): 실력 외에 이 팀에 맞으려면 중요한 성향·가치 정확히 3개.
- aiQuestions: 합류 지원자가 답할 질문 2개. 이 아이디어 적합성을 가릴 단답형(1~2문장으로 답할 수 있는 것).
- founderQuestion: 아이디어 제공자가 팀원에게 묻고 싶을 법한 추천 질문 1개(나중에 제공자가 직접 수정합니다).
- 현실적이고 작게 시작할 수 있는 규모로, 모두 한국어로.

[정상 응답 JSON 형식]
{
  "serviceName": "서비스 이름(짧고 기억하기 쉽게)",
  "tagline": "한 줄 슬로건",
  "lead": "히어로에 들어갈 감성적인 소개 2~3문장",
  "story": ["1인칭 스토리 문단1", "문단2", "문단3"],
  "whyNow": [
    {"icon": "🌍", "title": "제목", "desc": "한 줄 설명"},
    {"icon": "🧩", "title": "제목", "desc": "한 줄 설명"},
    {"icon": "🚀", "title": "제목", "desc": "한 줄 설명"}
  ],
  "productNote": "어떤 제품/서비스를 만드는지 한 줄",
  "plan": {
    "problem": "어떤 문제를 푸는가",
    "solution": "어떻게 푸는가",
    "target": "누구를 위한 것인가",
    "revenue": "어떻게 돈을 버는가"
  },
  "neededTeammates": [
    {"role": "무엇을 할 수 있는 사람 1", "detail": "맡는 일과 끌리는 이유 한 줄"},
    {"role": "무엇을 할 수 있는 사람 2", "detail": "맡는 일과 끌리는 이유 한 줄"},
    {"role": "무엇을 할 수 있는 사람 3", "detail": "맡는 일과 끌리는 이유 한 줄"}
  ],
  "matchFactors": ["성향·가치 1", "성향·가치 2", "성향·가치 3"],
  "aiQuestions": ["팀원이 답할 질문 1", "팀원이 답할 질문 2"],
  "founderQuestion": "제공자가 팀원에게 물을 추천 질문 1개",
  "needMoreInfo": false
}

[입력이 너무 빈약해서 비전을 만들 수 없을 때 — 예: "그립톡 사업" 처럼 한두 단어]
{
  "needMoreInfo": true,
  "askFor": ["무엇을 재활용/활용하나요?", "누구에게 파나요?", "무엇이 강점인가요?"]
}"""


# 4-2) 발표 데모용 '등록된 팀원 풀' — 실제로는 가입한 사람들의 프로필이 들어올 자리입니다.
#      지금은 임의의 8명을 다양한 분야로 만들어 두고, 이 안에서 매칭해 보여줍니다.
TEAMMATE_POOL = [
    {"name": "김도현", "headline": "플라스틱 사출·금형을 직접 다루는 제조 엔지니어",
     "skills": "PP/HDPE 분쇄·사출·금형 설계, 소형 생산설비 운용, 시제품 제작",
     "traits": "직접 손으로 만들며 빠르게 검증하는 걸 즐김, 환경 문제에 진심"},
    {"name": "이서연", "headline": "브랜드·제품 디자이너",
     "skills": "제품 외관/패키지 디자인, 브랜드 비주얼, 로고·굿즈 디자인",
     "traits": "미적 감각이 뛰어나고 트렌드에 민감, 작게 시작해 다듬는 걸 선호"},
    {"name": "박지훈", "headline": "SNS·콘텐츠 마케터",
     "skills": "인스타·틱톡 콘텐츠 기획, 브랜드 스토리텔링, 0에서 팬덤 만들기",
     "traits": "Gen Z 트렌드 이해도 높음, 가치소비·친환경 메시지에 공감"},
    {"name": "최민지", "headline": "B2B 제휴·영업 담당",
     "skills": "카페·학교·기업 대상 제안 영업, 파트너십 발굴, 단체 주문 수주",
     "traits": "사람 만나 발로 뛰는 걸 좋아함, 첫 매출을 만드는 데 집중"},
    {"name": "정우성", "headline": "웹·앱 풀스택 개발자",
     "skills": "웹/모바일 앱 개발, 결제·예약 시스템, 매칭 플랫폼 구축",
     "traits": "MVP를 빠르게 만들어 출시, 사용자 피드백으로 개선"},
    {"name": "한가람", "headline": "서비스 기획·운영 매니저",
     "skills": "서비스 기획, 업무 프로세스 설계, 고객 응대·운영 체계 구축",
     "traits": "꼼꼼하게 빈틈을 메우는 성향, 팀의 중심을 잡는 역할"},
    {"name": "오은별", "headline": "식품 조리·위생 표준화 전문가",
     "skills": "레시피 표준화, 식품 위생·HACCP, 소량 생산·포장",
     "traits": "맛과 안전을 둘 다 챙김, 정성스러운 손맛을 중시"},
    {"name": "강태현", "headline": "시니어 대상 교육·오프라인 운영 경험자",
     "skills": "어르신 눈높이 교육, 방문 강의 운영, 친절한 1:1 커뮤니케이션",
     "traits": "참을성 있고 사람을 편안하게 해줌, 사회적 가치를 중시"},
]

# 4-3) 매칭 AI 의 역할(시스템 프롬프트).
MATCH_SYSTEM_PROMPT = """당신은 ORBIT의 팀원 매칭 AI입니다.
주어진 '사업 비전'과 '등록된 팀원 풀'을 보고, 이 아이디어를 함께 만들기에 가장 잘 맞는 팀원을 골라줍니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- 반드시 '등록된 팀원 풀' 안에 실제로 있는 사람(name)만 추천하세요. 없는 사람을 지어내지 마세요.
- 정말 잘 맞는 사람만 2~4명 고르세요. 억지로 채우지 마세요.
- 각 추천에는 그 사람이 비전의 어떤 '필요한 팀원' 역할을 채우는지(fitsRole)와,
  왜 이 아이디어/팀 분위기에 잘 맞는지(reason)를 구체적으로 적으세요.
- fitLevel 은 "높음" 또는 "보통" 중 하나로 적으세요.
- 모든 내용은 한국어로.

[응답 JSON 형식]
{
  "matches": [
    {"name": "팀원 이름", "fitsRole": "채우는 역할", "fitLevel": "높음", "reason": "왜 잘 맞는지 구체적으로"}
  ]
}"""


# 4-4) 합류 질문 추천 AI 의 역할 — 아이디어 제공자가 기획서를 만들 때 보여줄 질문 후보를 만듭니다.
QUESTION_SYSTEM_PROMPT = """당신은 ORBIT의 '합류 질문 추천 AI'입니다.
아이디어 제공자가 합류 지원자를 가릴 수 있도록, 이 프로젝트에 꼭 맞는 사람인지 판별하는 좋은 질문을 추천합니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- aiQuestionCandidates: 지원자의 역량·상황·의지를 가릴 수 있는, 1~2문장으로 답할 수 있는 단답형 질문 4개.
- founderQuestionSuggestions: 아이디어 제공자가 직접 묻고 싶어할 만한 질문 추천 3개 (시간 약속, 합류 동기, 가치관 등).
- 모두 한국어로, 짧고 명확하게.

[응답 JSON 형식]
{
  "aiQuestionCandidates": ["질문1", "질문2", "질문3", "질문4"],
  "founderQuestionSuggestions": ["질문1", "질문2", "질문3"]
}"""

# 4-5) 합류 적합도(매칭률) 평가 AI 의 역할.
JOIN_SYSTEM_PROMPT = """당신은 ORBIT의 '합류 적합도 평가 AI'입니다.
합류 지원자의 프로필과, 이 프로젝트의 비전·매칭 요소·필수 질문을 보고,
지원자가 각 질문에 어떻게 답할지 추정한 뒤, 프로젝트와 얼마나 잘 맞는지 매칭률(0~100%)을 매깁니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- answers: 주어진 필수 질문 각각에 대해, 이 지원자라면 줄 법한 1~2문장 답변(answer)과 그 답이 적합한지 한 줄 코멘트(comment).
- bestRole: 비전의 neededTeammates(필요 팀원) 중, 이 지원자의 이력서(skills·traits)에 가장 잘 맞는 자리 하나를 골라 그 role 문구를 그대로 적으세요. 지원자 역량과 동떨어진 자리를 고르지 마세요.
- fitItems: 이 팀과의 궁합을 보여주는 항목 3개. 각 {title, desc, level}. level 은 "잘 맞음" / "정확" / "보통" 중 하나이며, 솔직하게 약점("보통")도 하나 포함하세요.
- matchRate: 0~100 사이 정수. 비전의 matchFactors(성향·가치)와 neededTeammates(필요 역량)를 지원자 이력서가 얼마나 충족하는지 근거 있게 판단하세요. 과장하지 마세요.
- verdict: "강력 추천" / "추천" / "보류" 중 하나.
- summary: 매칭 결과를 한 줄로 요약.
- 모두 한국어로.

[응답 JSON 형식]
{
  "answers": [
    {"question": "질문", "answer": "지원자의 예상 답변", "comment": "적합성 코멘트"}
  ],
  "bestRole": "이 지원자에게 가장 잘 맞는 자리(neededTeammates 중 하나)",
  "fitItems": [
    {"title": "환경 마인드", "desc": "제공자 핵심 가치와 정확히 일치", "level": "잘 맞음"},
    {"title": "필요 역량", "desc": "1순위 역할과 맞물림", "level": "정확"},
    {"title": "다른 감각", "desc": "다른 팀원과 보완하면 충분", "level": "보통"}
  ],
  "matchRate": 87,
  "verdict": "추천",
  "summary": "한 줄 요약"
}"""


# 4-6) 보충 질문 AI 의 역할 — 한 줄 아이디어를 또렷하게 만들 객관식 질문 2개.
BOOST_SYSTEM_PROMPT = """당신은 ORBIT의 '보충 질문 AI'입니다.
한 줄 아이디어를 더 또렷한 비전으로 만들기 위해, 제공자에게 물을 객관식 질문 2개를 만듭니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. JSON 외 다른 말이나 코드펜스(```)를 절대 붙이지 마세요.
- 1번 질문은 '누가 가장 사고 싶어 할까/이용할까'(타겟), 2번은 '가장 중요한 강점은'을 묻습니다.
- 각 질문에 이 아이디어에 맞는 선택지 2개씩 제시합니다.
- 한국어로 짧고 명확하게.

[응답 JSON 형식]
{
  "questions": [
    {"q": "누가 가장 사고 싶어 할까요?", "options": ["선택지 A", "선택지 B"]},
    {"q": "가장 중요한 강점은요?", "options": ["선택지 A", "선택지 B"]}
  ]
}"""


# 4-7) 응답 스키마 — 구조화 출력(structured output)으로 AI가 항상 유효한 JSON만 내게 강제합니다.
#      (story 같은 긴 글에 따옴표가 들어가도 JSON이 깨지지 않습니다.)
def _obj(props, required):
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}

VISION_SCHEMA = _obj({
    "serviceName": {"type": "string"},
    "tagline": {"type": "string"},
    "lead": {"type": "string"},
    "story": {"type": "array", "items": {"type": "string"}},
    "whyNow": {"type": "array", "items": _obj(
        {"icon": {"type": "string"}, "title": {"type": "string"}, "desc": {"type": "string"}},
        ["icon", "title", "desc"])},
    "productNote": {"type": "string"},
    "plan": _obj(
        {"problem": {"type": "string"}, "solution": {"type": "string"},
         "target": {"type": "string"}, "revenue": {"type": "string"}},
        ["problem", "solution", "target", "revenue"]),
    "neededTeammates": {"type": "array", "items": _obj(
        {"role": {"type": "string"}, "detail": {"type": "string"}}, ["role", "detail"])},
    "matchFactors": {"type": "array", "items": {"type": "string"}},
    "aiQuestions": {"type": "array", "items": {"type": "string"}},
    "founderQuestion": {"type": "string"},
}, ["serviceName", "tagline", "lead", "story", "whyNow", "productNote",
    "plan", "neededTeammates", "matchFactors", "aiQuestions", "founderQuestion"])

BOOST_SCHEMA = _obj({
    "questions": {"type": "array", "items": _obj(
        {"q": {"type": "string"}, "options": {"type": "array", "items": {"type": "string"}}},
        ["q", "options"])},
}, ["questions"])

MATCH_SCHEMA = _obj({
    "matches": {"type": "array", "items": _obj(
        {"name": {"type": "string"}, "fitsRole": {"type": "string"},
         "fitLevel": {"type": "string"}, "reason": {"type": "string"}},
        ["name", "fitsRole", "fitLevel", "reason"])},
}, ["matches"])

JOIN_SCHEMA = _obj({
    "answers": {"type": "array", "items": _obj(
        {"question": {"type": "string"}, "answer": {"type": "string"}, "comment": {"type": "string"}},
        ["question", "answer", "comment"])},
    "bestRole": {"type": "string"},
    "fitItems": {"type": "array", "items": _obj(
        {"title": {"type": "string"}, "desc": {"type": "string"}, "level": {"type": "string"}},
        ["title", "desc", "level"])},
    "matchRate": {"type": "integer"},
    "verdict": {"type": "string"},
    "summary": {"type": "string"},
}, ["answers", "bestRole", "fitItems", "matchRate", "verdict", "summary"])


def _extract_json(raw: str) -> dict:
    """AI 답변 문자열에서 JSON 부분만 안전하게 뽑아 dict 로 만듭니다.
    혹시 ```json 펜스나 앞뒤 잡설이 붙어 와도 견디도록 처리합니다."""
    text = raw.strip()
    # 코드펜스(```json ... ```)가 붙어 오면 제거
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    # 그래도 앞뒤에 글자가 있으면, 첫 '{' 부터 마지막 '}' 까지만 잘라서 파싱
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    # strict=False: 문자열 값 안에 줄바꿈 같은 제어문자가 있어도 견디게 파싱
    return json.loads(text, strict=False)


def generate_vision(idea: str, target_answer: str = "", strength_answer: str = "") -> dict:
    """한 줄 아이디어(+선택 보충답변)를 받아 비전(dict)을 만들어 돌려줍니다."""
    user_prompt = (
        "다음 아이디어로 비전을 만들어주세요.\n\n"
        f"[아이디어]\n{idea}\n\n"
        "[보충 답변]\n"
        f"- 가장 사고 싶어 할/이용할 사람: {target_answer or '(아직 없음)'}\n"
        f"- 가장 중요한 강점: {strength_answer or '(아직 없음)'}\n\n"
        "위에서 정한 JSON 형식으로만 답하세요."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",  # 속도·비용·품질 균형이 좋은 모델 (Opus보다 약 1.6배 저렴)
        max_tokens=3000,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": VISION_SCHEMA}},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = "".join(block.text for block in response.content if block.type == "text")
    return _extract_json(raw)


def generate_boost_questions(idea: str) -> dict:
    """한 줄 아이디어를 또렷하게 만들 보충 질문 2개(객관식)를 생성합니다."""
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=600,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": BOOST_SCHEMA}},
        system=BOOST_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"아이디어: {idea}\n\n보충 질문 2개를 JSON으로 만들어 주세요."}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")
    return _extract_json(raw)


def match_teammates(vision: dict) -> dict:
    """만들어진 비전과 등록된 팀원 풀을 비교해, 잘 맞는 팀원을 골라 돌려줍니다."""
    # 비전에서 매칭에 필요한 핵심만 추려서 전달합니다.
    needed = [t["role"] for t in vision.get("neededTeammates", [])]
    vision_brief = {
        "serviceName": vision.get("serviceName"),
        "oneLineDesc": vision.get("oneLineDesc"),
        "neededTeammates": needed,
        "matchFactors": vision.get("matchFactors", []),
    }
    user_prompt = (
        "[사업 비전]\n"
        f"{json.dumps(vision_brief, ensure_ascii=False, indent=2)}\n\n"
        "[등록된 팀원 풀]\n"
        f"{json.dumps(TEAMMATE_POOL, ensure_ascii=False, indent=2)}\n\n"
        "위 팀원 풀 안에서 이 아이디어에 가장 잘 맞는 사람을 골라 JSON 형식으로 답하세요."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": MATCH_SCHEMA}},
        system=MATCH_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(block.text for block in response.content if block.type == "text")
    return _extract_json(raw)


def print_matches(matches: dict) -> None:
    """매칭된 팀원을 보기 좋게 출력합니다."""
    found = matches.get("matches", [])
    print("\n🔗 ORBIT이 찾은 합류 추천 팀원 (등록된 8명 중에서)")
    print("=" * 60)
    if not found:
        print("   아직 딱 맞는 팀원이 없어요. (팀원 풀을 더 넓혀보세요)")
        print("=" * 60)
        return
    for person in found:
        star = "⭐⭐⭐" if person.get("fitLevel") == "높음" else "⭐⭐"
        print(f"   {star} {person['name']} — 매칭도: {person.get('fitLevel', '?')}")
        print(f"        맡을 역할: {person.get('fitsRole', '')}")
        print(f"        추천 이유: {person.get('reason', '')}")
        print()
    print("=" * 60)


def recommend_questions(vision: dict) -> dict:
    """아이디어 제공자에게 보여줄 '합류 질문 후보'를 AI 가 추천합니다."""
    brief = {
        "serviceName": vision.get("serviceName"),
        "oneLineDesc": vision.get("oneLineDesc"),
        "neededTeammates": [t["role"] for t in vision.get("neededTeammates", [])],
        "matchFactors": vision.get("matchFactors", []),
    }
    user_prompt = (
        "[사업 비전]\n"
        f"{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "이 프로젝트에 합류 지원자를 가릴 질문 후보를 JSON 형식으로 추천하세요."
    )
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1000,
        output_config={"effort": "low"},
        system=QUESTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")
    return _extract_json(raw)


def evaluate_applicant(vision: dict, question_texts: list, applicant: dict) -> dict:
    """지원자 프로필과 필수 질문 3개로, 프로젝트와의 매칭률(%)을 평가합니다."""
    brief = {
        "serviceName": vision.get("serviceName"),
        "oneLineDesc": vision.get("oneLineDesc"),
        "neededTeammates": [t["role"] for t in vision.get("neededTeammates", [])],
        "matchFactors": vision.get("matchFactors", []),
    }
    user_prompt = (
        "[사업 비전]\n"
        f"{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "[합류 필수 질문 3개]\n"
        f"{json.dumps(question_texts, ensure_ascii=False, indent=2)}\n\n"
        "[합류 지원자 프로필]\n"
        f"{json.dumps(applicant, ensure_ascii=False, indent=2)}\n\n"
        "이 지원자의 매칭률을 JSON 형식으로 평가하세요."
    )
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1200,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": JOIN_SCHEMA}},
        system=JOIN_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")
    return _extract_json(raw)


def print_join_questions(questions: list) -> None:
    """확정된 합류 필수 질문 3개를 출력합니다."""
    print("\n📋 합류 지원자가 답해야 할 필수 질문 3개 (제공자가 기획서에서 설정)")
    print("=" * 60)
    for i, q in enumerate(questions, 1):
        print(f"   {i}. [{q['by']}] {q['text']}")
    print("=" * 60)


def print_join_result(applicant_name: str, service_name: str, result: dict) -> None:
    """지원자의 답변과 매칭률을 출력합니다."""
    rate = int(result.get("matchRate", 0))
    filled = max(0, min(10, rate // 10))
    bar = "█" * filled + "░" * (10 - filled)
    print(f"\n🙋 {applicant_name} 님이 '{service_name}'에 합류 신청했어요")
    print("=" * 60)
    for i, a in enumerate(result.get("answers", []), 1):
        print(f"   Q{i}. {a.get('question', '')}")
        print(f"       💬 {a.get('answer', '')}")
        print(f"       ↳ {a.get('comment', '')}")
        print()
    print(f"   🎯 매칭률: {rate}%   [{bar}]")
    print(f"   📌 평가: {result.get('verdict', '')} — {result.get('summary', '')}")
    print("=" * 60)


def print_slack_invite(service_name: str, applicant_name: str) -> None:
    """양측이 수락하면 슬랙 채팅방으로 안내합니다."""
    print("\n🎉 서로 수락했어요! 이제 이 여정을 함께 시작합니다.")
    print("=" * 60)
    print(f"   '{service_name}' 프로젝트 슬랙 채널에 초대되었습니다.")
    print(f"   👥 참여자: 아이디어 제공자  +  {applicant_name}")
    # 서비스 이름에서 영문·숫자만 뽑아 깔끔한 채널 주소(slug)를 만듭니다.
    slug = "".join(ch for ch in service_name if ch.isascii() and ch.isalnum()).lower() or "project"
    print(f"   🔗 https://orbit-team.slack.com/{slug}  (데모용 링크)")
    print("=" * 60)


def print_vision(idea: str, vision: dict) -> None:
    """만들어진 비전(또는 되묻기 질문)을 보기 좋게 출력합니다."""
    print(f"\n💡 입력한 아이디어: {idea}\n")

    # (A) 입력이 빈약해서 AI 가 되물어 온 경우
    if vision.get("needMoreInfo"):
        print("🤔 아이디어가 조금 짧아서, 좋은 팀원을 찾으려면 아래가 더 필요해요:")
        for question in vision.get("askFor", []):
            print(f"   • {question}")
        return

    # (B) 정상적으로 비전이 만들어진 경우
    print("=" * 60)
    print(f"🚀 서비스 이름:  {vision['serviceName']}")
    print(f"🏷  슬로건:      {vision['tagline']}")
    print(f"📝 한 줄 소개:   {vision['oneLineDesc']}\n")

    print("🧩 핵심 기능")
    for feature in vision["features"]:
        print(f"   {feature['icon']} {feature['title']} — {feature['desc']}")
    print()

    plan = vision["plan"]
    print("📊 사업 개요")
    print(f"   • 문제:   {plan['problem']}")
    print(f"   • 해결:   {plan['solution']}")
    print(f"   • 타겟:   {plan['target']}")
    print(f"   • 수익:   {plan['revenue']}\n")

    # ⭐ ORBIT 의 핵심 — 필요한 팀원 (역할 + 합류 매력 한 줄)
    print("👥 필요한 팀원 (neededTeammates) ★ORBIT의 핵심")
    for teammate in vision["neededTeammates"]:
        print(f"   • {teammate['role']}")
        print(f"     └ 💬 {teammate['why']}")
    print()

    # ⭐ ORBIT 의 핵심 — 매칭 중요 요소
    print("🤝 매칭 중요 요소 (matchFactors) ★ORBIT의 핵심")
    for factor in vision["matchFactors"]:
        print(f"   • {factor}")
    print("=" * 60)


if __name__ == "__main__":
    # 명령줄에서 아이디어를 받습니다. 없으면 예시 아이디어를 사용합니다.
    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        idea = "페트병 뚜껑을 그립톡으로 재활용하는 사업"
        print("ℹ️  아이디어를 입력하지 않아 예시 아이디어로 실행합니다.")
        print('   (직접 넣으려면:  python src/main.py "나의 아이디어")')

    # ── 발표 데모 설정 (발표자가 이 값만 바꾸면 시나리오를 조정할 수 있어요) ──
    DEMO_PICKED_AI_QUESTIONS = [0, 1]   # 제공자가 고른 AI 추천 질문 번호 (0부터)
    DEMO_FOUNDER_QUESTION = ""          # 제공자가 직접 정한 질문 (비우면 추천 질문 사용)
    DEMO_JOIN_THRESHOLD = 70            # 이 % 이상이면 합류 성사 → 슬랙 안내

    # ── [1/4] 한 줄 아이디어 → 기획서 ──
    print("\n⏳ [1/4] 한 줄 아이디어로 기획서를 만드는 중...")
    vision = generate_vision(idea)
    print_vision(idea, vision)
    if vision.get("needMoreInfo"):
        sys.exit(0)  # 아이디어가 빈약하면 되묻기만 하고 종료

    # ── [2/4] 합류 질문 3개 설정 (아이디어 제공자가 기획서 만들 때) ──
    print("\n⏳ [2/4] 합류 지원자에게 물을 질문을 준비하는 중...")
    qcand = recommend_questions(vision)
    ai_cands = qcand.get("aiQuestionCandidates", [])
    founder_sugs = qcand.get("founderQuestionSuggestions", [])

    print("\n🤖 AI 추천 질문 후보 (이 중에서 제공자가 2개 선택)")
    for i, q in enumerate(ai_cands):
        mark = "✅" if i in DEMO_PICKED_AI_QUESTIONS else "  "
        print(f"   {mark} {q}")
    founder_q = DEMO_FOUNDER_QUESTION or (founder_sugs[0] if founder_sugs else "왜 이 프로젝트에 합류하고 싶나요?")
    print(f"\n👤 제공자가 직접 정한 질문: {founder_q}")

    questions = [{"by": "AI", "text": ai_cands[i]} for i in DEMO_PICKED_AI_QUESTIONS if i < len(ai_cands)]
    questions.append({"by": "제공자", "text": founder_q})
    print_join_questions(questions)

    # ── [3/4] 등록된 팀원 매칭 ──
    print("\n⏳ [3/4] 등록된 팀원 중에서 잘 맞는 사람을 찾는 중...")
    matches = match_teammates(vision)
    print_matches(matches)

    found = matches.get("matches", [])
    if not found:
        sys.exit(0)

    # ── [4/4] 합류 신청 → 3개 질문 답변 → 매칭률 ──
    applicant_name = found[0]["name"]  # 매칭 1위가 합류 신청한다고 가정
    applicant = next((p for p in TEAMMATE_POOL if p["name"] == applicant_name), {"name": applicant_name})
    print(f"\n⏳ [4/4] {applicant_name} 님의 합류 적합도(매칭률)를 평가하는 중...")
    result = evaluate_applicant(vision, [q["text"] for q in questions], applicant)
    print_join_result(applicant_name, vision["serviceName"], result)

    # ── 양측 수락 → 슬랙 채팅방 안내 ──
    if int(result.get("matchRate", 0)) >= DEMO_JOIN_THRESHOLD:
        print_slack_invite(vision["serviceName"], applicant_name)
    else:
        print(f"\n📭 매칭률이 {DEMO_JOIN_THRESHOLD}% 미만이라 아직 합류 안내를 보내지 않았어요.")
