# ORBIT — 비전 페이지 생성 프롬프트 설계

> 한 줄 아이디어 → Claude API → 비전 페이지(JSON).
> **이 파일을 Claude Code에 주고 "이 규칙대로 비전 생성을 바꿔줘"라고 하면 됩니다.**

---

## ⭐ 가장 중요 — 우리 서비스의 핵심

ORBIT은 *사업계획서를 만드는 서비스가 아니라*, **"이 아이디어를 함께 만들 팀원을 찾아주는"** 서비스다.
그래서 비전 결과에는 **반드시 아래 두 가지가 들어가야 한다:**

1. **neededTeammates (필요한 팀원)** — 이 아이디어를 실현하려면 어떤 사람이 필요한가
2. **matchFactors (매칭 중요 요소)** — 실력 외에, 이 팀에 맞으려면 어떤 성향·가치가 중요한가

→ "미션, 핵심가치, 첫해 목표" 같은 일반 사업계획서 항목이 아니라, **위 두 가지가 핵심이다.**

---

## 1) 시스템 프롬프트 (Claude에게 줄 역할)

```
당신은 ORBIT의 비전 생성 AI입니다.
사용자가 던진 한 줄 아이디어를, 함께 만들 팀원이 한눈에 이해하고 합류하고 싶게 만드는 '비전'으로 구체화합니다.

규칙:
- 반드시 아래 JSON 형식으로만 답하세요. 다른 말은 절대 붙이지 마세요.
- 과장하지 마세요. 아직 '아이디어 단계(진척도 0%)'임을 전제로, 가능성을 담되 완성된 척하지 않습니다.
- neededTeammates(필요한 팀원)는 '이 아이디어를 실제로 만들려면 어떤 역량이 필요한가'로 도출합니다.
  직무명(예: 개발자)이 아니라 '무엇을 할 수 있는 사람'(예: 폐플라스틱 가공 설비를 다룰 수 있는 사람)으로 적습니다. 3~5명.
- matchFactors(매칭 중요 요소)는 '실력 외에, 이 팀에 맞으려면 어떤 성향·가치가 중요한가'입니다. 3개.
- 모든 내용은 한국어로, 쉽고 구체적으로.
```

## 2) 사용자 프롬프트 (입력 끼우기)

```
다음 아이디어로 비전을 만들어주세요.

[아이디어]
{사용자가 입력한 한 줄}

[보충 답변]
- 가장 사고 싶어 할/이용할 사람: {질문1 답}
- 가장 중요한 강점: {질문2 답}

아래 JSON 형식으로만 답하세요.
```

## 3) 받을 JSON 구조 (★이대로 나와야 함)

```json
{
  "serviceName": "에코그립",
  "tagline": "버려진 뚜껑이 손안의 무드",
  "oneLineDesc": "페트병 뚜껑을 업사이클링한 친환경 그립톡, Gen Z를 위한 굿즈",

  "features": [
    {"icon": "♻", "title": "업사이클링", "desc": "뚜껑 수거·가공"},
    {"icon": "◎", "title": "디자인 굿즈", "desc": "감각적 그립톡"},
    {"icon": "⌗", "title": "온라인 판매", "desc": "스토어·SNS"}
  ],

  "plan": {
    "problem": "버려지는 페트병 뚜껑은 재활용이 어렵고, Gen Z는 가치소비를 원하지만 마땅한 친환경 굿즈가 적다.",
    "solution": "폐뚜껑을 압출·가공해 디자인 그립톡으로 업사이클링하고 SNS로 확산.",
    "target": "환경에 관심 많고 인증샷·가치소비에 적극적인 Gen Z.",
    "revenue": "그립톡 판매 · 기업 ESG 굿즈 B2B · 한정 콜라보."
  },

  "neededTeammates": [
    "압출 기계·생산 시설 지식 보유자",
    "카페·공방 형태 사업 경력자",
    "온라인 판매 사업 지식 보유자",
    "SNS 마케팅 전문가"
  ],

  "matchFactors": [
    "환경보호·자원 재활용에 대한 마인드 공유",
    "미적 감각 보유",
    "트렌드 및 Gen Z 세대에 대한 높은 이해도"
  ],

  "needMoreInfo": false
}
```

### 입력이 너무 빈약할 때 (예: "그립톡 사업" 한 단어)
```json
{
  "needMoreInfo": true,
  "askFor": ["무엇을 재활용/활용하나요?", "누구에게 파나요?", "무엇이 강점인가요?"]
}
```

---

## 4) 코드에서 호출 (참고용 골격)

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": process.env.ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01"
  },
  body: JSON.stringify({
    model: "claude-sonnet-4-6",
    max_tokens: 1500,
    system: "(위 1) 시스템 프롬프트)",
    messages: [{ role: "user", content: "(위 2) 사용자 프롬프트, 입력 끼워서)" }]
  })
});
const data = await response.json();
const text = data.content.map(i => i.text || "").join("");
const vision = JSON.parse(text.replace(/```json|```/g, "").trim());
// vision.serviceName, vision.neededTeammates, vision.matchFactors ... 화면에 꽂기
```

(파이썬이면 anthropic 라이브러리로 동일하게. 키는 .env의 ANTHROPIC_API_KEY 사용.)

---

## 5) 테스트 체크리스트 (★꼭 확인)

- [ ] 페트병 그립톡 → **neededTeammates(필요한 팀원)가 나오나** ← 제일 중요
- [ ] **matchFactors(매칭 요소)가 나오나** ← 제일 중요
- [ ] serviceName, tagline이 나오나
- [ ] 전혀 다른 아이디어(예: "동네 반찬 구독 서비스") → 그것에 맞는 팀원·매칭요소로 바뀌나
- [ ] "그립톡" 한 단어 → needMoreInfo: true 가 뜨나
- [ ] 항상 JSON만 오나 (잡설 안 붙나)

---

## 6) 다듬는 팁

- 결과가 밋밋하면 시스템 프롬프트에 위 그립톡 JSON 예시를 통째로 넣어주세요 → 품질 확 올라감.
- 필요 팀원이 직무명("개발자")으로 나오면 → "무엇을 할 수 있는 사람으로" 규칙을 강조.
- 너무 거창하면 → "현실적이고 작게 시작할 수 있는 규모로" 추가.
