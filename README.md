# 여기저기 · GitHub / Vercel 배포용

**여기 붐비는 곳 말고, 저기 닮은 옆 동네.** 서울 상권의 소비·유동·버스 정류장 데이터로 한 데이터를 두 고객에게 씁니다. 시민에게는 버스 1~3정거장 안의 닮고 덜 붐비는 동네를, 광고주에게는 정류장 광고 위치를 제안합니다.

`ABA_1st_proj`에서 빌드한 화면만 복제했습니다. 원본 데이터·노트북·학습 환경·API 키는 포함하지 않습니다.

## 페이지

| 파일 | 메뉴 | 내용 |
| --- | --- | --- |
| `index.html` | 홈 | 기준 상권 → 버스 1~3정거장 안의 닮고 덜 붐비는 동네. 방문 조건별 추천, 지도 핀과 카드 연동, 주변 매장 검색 |
| `dashboard.html` | 대시보드 | 상권 지도, 유사 상권의 소비 특성 비교, 선택 상권의 버스 대안으로 이동 |
| `eda.html` | EDA | 가설1~5와 추가분석A~F, EDA 최종 보고서·모델링 분석 보고서 PDF 다운로드 |
| `insights.html` | 인사이트 | 디저트 팝업 지도 사례, 업종·시간대·지역별 광고 후보 탐색, 가까운 대안 동네 제안, 보고서 PDF 다운로드 |

네 페이지는 데이터·글꼴·그래프·PDF가 들어 있는 단일 HTML입니다. 화면을 수정할 때는 이 파일을 직접 고치지 말고 원본 프로젝트(`ABA_1st_proj/persona_dashboard`)에서 빌드한 뒤 `scripts/export_github.py`로 다시 복제합니다.

## 그 밖의 파일

| 파일/폴더 | 역할 |
| --- | --- |
| `api/map-config.py` | 브라우저에 지도용 공개 Client ID 전달 |
| `api/local-search.py` | NAVER 지역검색 중계, 상권 경계 약 500m 필터 |
| `server_lib/` | 검색·좌표·경계 로직과 상권 경계 데이터 |
| `vercel.json` | 정적 화면과 Python API 배포 설정, 예전 주소 리다이렉트 |
| `scripts/` | 정적 파일 빌드(`build_static.py`)와 로컬 미리보기(`dev_server.py`) |
| `assets/fonts/LICENSE.txt` | 페이지에 내장한 Noto Sans KR 라이선스 |
| `.env.example` | 실제 값이 없는 설정 항목 |

## GitHub 업로드

이 폴더 **안의 파일들**을 저장소 루트에 올립니다. `.env.example`, `.gitignore`, `.python-version`, `.vercelignore`도 포함합니다. 실제 `.env`, API 키, `public/`, `__pycache__/`, `.vercel/`은 올리지 않습니다(.gitignore에 포함).

## Vercel

1. 저장소를 Import, Framework Preset **Other**, Root Directory `./`
2. `vercel.json`의 Build Command `python3 scripts/build_static.py`, Output Directory `public`
3. Environment Variables: `NAVER_MAP_CLIENT_ID`(지도 공개 ID), `NAVER_SEARCH_CLIENT_ID`·`NAVER_SEARCH_CLIENT_SECRET`(서버 전용)
4. 네이버 Maps의 Web 서비스 URL에 실제 배포 도메인 등록 후 재배포

지도 키가 없으면 경계 지도로, 검색 키가 없으면 안내 메시지로 동작합니다. 검색 결과는 실제 영업·제휴 여부를 보장하지 않습니다.

## 로컬 미리보기

`start.command` 또는 `python3 scripts/dev_server.py --port 8767` → `http://localhost:8767/`. 키가 필요하면 `.env.example`을 `.env`로 복사해 값을 채웁니다.

## 해석 범위

추천·광고 효과는 검증 전이고 매체 단가는 가상값입니다. 기간: 소비 2025년, 유동인구 2025Q2~2026Q1 평균, 버스 승하차 2026년 10월, 정류장 위치 2025-08.
