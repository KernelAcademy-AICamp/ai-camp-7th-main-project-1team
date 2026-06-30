[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ERWdZ46N)

# ORBIT 🛰️

빛나는 아이디어를 함께 실현할 팀원을 찾는 AI 팀빌딩 플랫폼.
한 줄 아이디어 → AI 기획안 → 필요 팀원 매칭 → 합류까지.

## 📁 폴더 구조

```
ORBIT/
├── .env                ← 🔑 진짜 API 키 (깃허브에 안 올라감, 각자 만들어야 함)
├── .env.example        ← 키 형식 견본
├── requirements.txt    ← 필요한 라이브러리 목록
├── src/
│   ├── main.py         ← AI 엔진 (비전 생성·매칭·평가 로직)
│   ├── app.py          ← 웹 서버 (Flask)
│   └── templates/
│       └── index.html  ← 화면 (랜딩·로그인·마이페이지 등 전체 UI)
└── 오르빗_데이터/        ← 기획 자료 (PRD·IA·로고 등)
```

## 🚀 처음 셋업 (팀원도 동일하게!)

```bash
# 1) 필요한 라이브러리 설치 (처음 한 번만)
pip install -r requirements.txt

# 2) 웹 서버 실행
python src/app.py

# 3) 브라우저에서 접속
#    http://localhost:5001
```

> 끄려면 터미널에서 **Ctrl + C**

## 🔑 API 키 넣는 법 (각자 본인 키로)

`.env` 는 깃허브에 올라가지 않으므로, **clone 받은 사람은 각자 키를 넣어야** 합니다.

1. https://console.anthropic.com → **API Keys** → **Create Key** 로 발급 (`sk-ant-...`)
2. `.env.example` 을 복사해 `.env` 로 이름을 바꾸고, 키를 붙여넣기:
   ```
   ANTHROPIC_API_KEY=sk-ant-여기에본인키
   ```
3. 저장하면 끝!

> ⚠️ 진짜 키는 **오직 `.env` 에만**. 코드·채팅·깃허브엔 절대 붙여넣지 마세요.

## 👥 팀원 합류 방법

1. (오너가 보낸) GitHub 저장소 초대 수락
2. GitHub Desktop 또는 `git clone <저장소 주소>` 로 받기
3. 위 **처음 셋업** 따라하기 + **본인 API 키** 넣기
4. 작업할 땐 **각자 브랜치**를 만들어 작업 → Pull Request 로 합치기
