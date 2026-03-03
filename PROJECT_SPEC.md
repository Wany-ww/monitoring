프로젝트 명세서: 실시간 설비 데이터 패턴 분석 웹 서비스
1. 프로젝트 개요
프로젝트 명: Equipment Data Pattern Analyzer (EDPA)
목표: 하위 폴더별로 저장된 설비 CSV 데이터를 통합하여 실시간으로 시각화하고, FP(Fiducial Point) 좌표 및 품질 등급(Bar Grade)의 패턴을 분석하는 웹 기반 대시보드 구축.
주요 기술 스택:
Language: Python 3.9+
Framework: Streamlit
Data Library: Pandas, NumPy
Visualization: Plotly (Interactive Charts)
Deployment: Streamlit Cloud
2. 데이터 구조 및 사양
2.1 디렉토리 구조
데이터는 다음의 계층 구조로 저장됨:
code
Text
/data/
└── {Equipment_Name}/          # 설비 이름 (예: EQ_001, EQ_002)
    ├── 2023-10-01.csv        # 파일명은 해당 데이터의 날짜
    ├── 2023-10-02.csv
    └── ...
2.2 CSV 스키마 (Header)
모든 CSV 파일은 아래 24개의 컬럼을 포함함:
Time: 데이터 기록 시간 (YYYY-MM-DD HH:MM:SS)
Model: 제품 모델명
Roll: 롤 번호
Bar No: 바 식별 번호
Layer No: 현재 레이어 번호
Total Layer: 전체 레이어 수
L Margin, W Margin: 여백 정보
Layer Pattern: 레이어 패턴 정보
AB Stack X, AB Stack Y: 스택 좌표
FP1 X, FP1 Y ~ FP6 X, FP6 Y: 6개 포인트의 X, Y 좌표 (총 12개 컬럼)
Bar Grade: 해당 바의 품질 등급 (숫자 또는 카테고리)
3. 핵심 기능 요구사항
3.1 실시간 데이터 파이프라인
데이터 로드: data/ 디렉토리 하위의 모든 .csv 파일을 재귀적으로 탐색하여 단일 데이터프레임으로 통합.
메타데이터 추출: 폴더명에서 Equipment 컬럼을, 파일명에서 Date 컬럼을 생성하여 데이터에 병합.
실시간성: st.cache_data(ttl=60)를 활용하여 1분 간격으로 새 파일 추가 여부를 확인하고 자동으로 데이터를 갱신.
3.2 필터링 기능 (Sidebar)
기간 선택: Time 컬럼 기준 범위 선택.
설비 선택: 다중 선택(Multi-select) 가능한 설비 리스트.
모델 선택: 다중 선택 가능한 제품 모델 리스트.
기타 필터: Roll 번호 및 Bar No 검색 기능.
3.3 시각화 대시보드 (Main)
FP 좌표 분석 (Scatter Plot):
FP1~FP6 중 사용자가 선택한 포인트의 X, Y 좌표 분포도.
설비별/모델별로 색상 구분.
시계열 추이 (Line/Scatter Plot):
시간에 따른 FP 좌표 변동 추이 관찰.
품질 분석 (Box Plot / Histogram):
설비별, 모델별 Bar Grade 분포도.
이상치(Outlier) 확인을 위한 인터랙티브 차트.
상관관계 분석:
Layer No와 Bar Grade 간의 상관관계 시각화.
4. 상세 로직 설계 (Logic Flow)
Initialization: 환경 변수 및 경로 설정.
Data Ingestion:
glob.glob 또는 os.walk를 사용하여 모든 경로의 CSV 수집.
Pandas를 이용해 통합하되, 파일 로드 실패 시 에러 핸들링 포함.
Preprocessing:
Time 컬럼의 datetime 변환.
결측치 처리 (필요 시).
UI Rendering:
st.sidebar를 통한 사용자 입력 인터페이스 생성.
st.tabs 또는 st.columns를 이용해 화면 분할.
Dynamic Updates:
데이터 변경 시 Plotly 차트가 즉시 반영되도록 구현.
5. 배포 및 환경 설정
5.1 requirements.txt
code
Text
streamlit
pandas
plotly
numpy
5.2 Streamlit Cloud 배포 설정
GitHub 리포지토리 루트에 app.py와 데이터 폴더 위치.
secrets.toml(선택 사항)을 통한 환경 변수 관리.
6. 특이 사항 (Edge Cases)
대용량 파일: 파일 개수가 많아질 경우를 대비해 pandas의 concat 최적화 수행.
파일 포맷 오류: 헤더가 일치하지 않는 파일은 스킵하고 경고 메시지 출력.
데이터 부재: 특정 필터 조건에 데이터가 없을 경우 "No Data" 메시지 표시.
상기 명세서를 바탕으로 Python - Streamlit 애플리케이션 개발을 진행한다.
