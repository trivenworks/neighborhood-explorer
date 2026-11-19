# 여기저기 · GitHub / Vercel 배포용

가고 싶은 동네와 닮은 곳을 찾아요.

기존 `ABA_1st_proj/index-improved.html`과 개선 화면용 EDA·인사이트를 별도 폴더로 복제했습니다. 원본 프로젝트·노트북·원본 데이터·학습 환경·Git 이력·API 키는 포함하지 않았습니다. 현재 화면에서 사용하는 저장된 소비 프로필·상권 경계·추천 목록만 포함합니다. 새 모델 학습은 하지 않습니다.

## 주요 파일

| 파일/폴더 | 역할 |
| --- | --- |
| `index.html` | 개선 메인 지도 |
| `eda.html`, `insights.html` | 같은 디자인의 분석·활용 페이지 |
| `assets/` | CSS·JS·저장된 화면 데이터·폰트·그래프·다운로드 PDF |
| `api/map-config.py` | 브라우저에 지도용 공개 Client ID 전달 |
| `api/local-search.py` | NAVER 지역검색 중계, 상권 경계/약 500m 필터 |
| `server_lib/` | 기존 검색·좌표·경계 로직과 필요한 경계 데이터 |
| `vercel.json` | 정적 화면과 Python API 배포 설정 |
| `scripts/` | 정적 파일 빌드와 로컬 미리보기 |
| `.env.example` | 실제 값이 없는 설정 항목 |

화면을 수정할 때 `index.html`, `assets/main.css`, `assets/main-ui.js`를 사용합니다. 문서 화면 스타일은 `assets/eda.css`, `assets/insights.css`입니다. 분석 값·추천 결과는 `assets/data.js`, `assets/neighbors.js`에 있습니다. `public/`은 빌드 결과이므로 직접 수정하지 않습니다.

## GitHub 업로드

이 폴더 **안의 파일들**을 새 GitHub 저장소 루트에 업로드합니다. `.env.example`, `.gitignore`, `.python-version`, `.vercelignore`도 포함합니다. 실제 `.env`, API 키, `public/`, `__pycache__/`, `.vercel/`은 업로드하지 않습니다. 현재 이 폴더에는 GitHub 저장소 연결이나 자동 push를 설정하지 않았습니다.

## Vercel 연결

1. GitHub 저장소를 Vercel에서 Import합니다.
2. Framework Preset은 **Other**, Root Directory는 저장소 루트(`./`)입니다.
3. `vercel.json`의 Build Command `python3 scripts/build_static.py`, Output Directory `public`을 사용합니다. 별도의 npm 설치나 프론트엔드 프레임워크는 필요하지 않습니다.
4. Vercel의 Environment Variables에 아래 값을 설정합니다. Preview/Production 모두에서 필요하면 각 환경을 선택합니다.

| 환경변수 | 필요한 값 | 브라우저 노출 |
| --- | --- | --- |
| `NAVER_MAP_CLIENT_ID` | Maps Dynamic Map용 공개 Client ID | 지도 SDK 연결에 사용 |
| `NAVER_SEARCH_CLIENT_ID` | 기존 로컬 서버에서 사용하던 NAVER API HUB 지역검색 ID | 서버 전용 |
| `NAVER_SEARCH_CLIENT_SECRET` | 같은 지역검색의 Secret | 서버 전용 |

5. 네이버 Maps의 Web 서비스 URL에 **실제 Vercel 배포 도메인**을 등록합니다. 커스텀 도메인을 쓰면 그 도메인도 등록합니다. 도메인이 바뀌면 등록 목록도 확인합니다.
6. 키 또는 설정을 바꾼 뒤에는 재배포합니다.

`GITLAB_API_KEY`는 이 웹사이트 실행에 필요하지 않습니다. 이 폴더로 복제하지 않았습니다. 지도 키가 없으면 경계 지도는 볼 수 있고, 주변 매장은 검색 키 설정 전까지 안내 메시지를 표시합니다. 네이버 검색 결과만으로 실제 영업·독립 브랜드·팝업·제휴 여부를 보장하지 않습니다.

## 로컬에서 이어서 보기

`start.command`를 더블클릭하거나 다음 명령을 실행합니다.

```sh
python3 scripts/dev_server.py --port 8767
```

브라우저에서 `http://localhost:8767/`을 엽니다. 키가 필요하면 `.env.example`을 `.env`로 복사해 실제 값을 채웁니다. `.env`는 Git에서 제외됩니다. 기존 프로젝트의 8766 서버와 별개 포트를 사용합니다. Python 3.12 이상을 권장합니다.

## 확인 범위

정적 파일 경로, 개선 메인↔EDA↔인사이트, PDF 원본 일치, 저장 경계/프로필/추천의 동일성, API 키 미포함을 점검했습니다. 실제 Vercel 배포와 네이버 API 인증은 배포 도메인·환경변수를 등록한 뒤 확인해야 합니다. GitHub 업로드·Vercel 배포는 아직 수행하지 않았습니다.

Vercel 공식 기준: [Python runtime](https://vercel.com/docs/functions/runtimes/python), [api directory functions](https://vercel.com/docs/functions/runtimes/python/api-directory), [vercel.json](https://vercel.com/docs/project-configuration/vercel-json).
