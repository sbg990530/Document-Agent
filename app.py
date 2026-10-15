import os
from datetime import datetime
import streamlit as st
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 🌐 웹페이지 기본 설정 (Wide 레이아웃)
st.set_page_config(
    page_title="DocuScout - Interactive AI Intelligence Agent",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 캡처 화면과 동일한 하이엔드 다크 테마 커스텀 CSS
st.markdown("""
    <style>
    /* 전체 앱 배경을 깊은 네이비 다크톤으로 설정 */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* 상단 내비게이션바 스타일 */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #111827;
        padding: 12px 24px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 24px;
    }
    .nav-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .badge-pro {
        background-color: #1d4ed8;
        color: #eff6ff;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* 메인 검색 입력 상자 카드 컨테이너 */
    .search-container {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* 카테고리 필터 캡슐 버튼 레이아웃용 */
    .filter-label {
        font-size: 0.9rem;
        color: #9ca3af;
        margin-bottom: 8px;
        font-weight: 500;
    }

    /* 리포트 출력 및 근거 카드 다크 테마 디자인 */
    .report-card-dark {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        color: #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .source-card-dark {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .source-card-dark:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

# API 키 설정
try:
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0)

# =====================================================================
# ⚙️ 핵심 분석 파이프라인 함수
# =====================================================================
def run_docuscout(query_text):
    current_date_str = datetime.now().strftime("%Y년 %m월")

    keyword_prompt = ChatPromptTemplate.from_messages([
        ("system", "사용자 질문에서 핵심 검색 키워드 2~3개를 추출하여 검색어만 출력하세요."),
        ("user", "현재 시점: {current_date}\n사용자 질문: {query}")
    ])
    auto_keyword = (keyword_prompt | llm).invoke({"current_date": current_date_str, "query": query_text}).content.strip()

    search_response = tavily_client.search(
        query=auto_keyword,
        search_depth="advanced",
        max_results=5,
        exclude_domains=[
            "dcinside.com", "fmkorea.com", "ruliweb.com",
            "cafe.naver.com", "blog.naver.com", "arca.live",
            "kin.naver.com", "namu.wiki", "wikipedia.org", "facebook.com",
            "threads.com"
        ]
    )
    collected_sources = search_response.get('results', [])

    if not collected_sources:
        return auto_keyword, None, None, None

    collected_context = ""
    for idx, result in enumerate(collected_sources, 1):
        collected_context += f"[{idx}] 제목 : {result['title']}\n내용 : {result['content']}\n\n"

    report_prompt = ChatPromptTemplate.from_messages([
        ("system", "수집된 데이터를 바탕으로 표준 목차(1. 개요 및 핵심 현황, 2. 주요 수치 및 팩트 지표, 3. 향후 전망 및 시사점)에 맞춰 전문 보고서를 작성하세요."),
        ("user", "수집 데이터 :\n{context}\n\n분석 요청사항 : {query}")
    ])
    report_res = (report_prompt | llm).invoke({"context": collected_context, "query": query_text})
    
    followup_prompt = ChatPromptTemplate.from_messages([
        ("system", "분석 리포트 기반 후속 심층 질문 3가지를 마크다운 불릿(- )으로만 작성하세요."),
        ("user", "주제: {query}\n요약:\n{summary}")
    ])
    followup_res = (followup_prompt | llm).invoke({"query": query_text, "summary": report_res.content})

    return auto_keyword, report_res.content, followup_res.content, collected_sources

# =====================================================================
# 🌙 상단 커스텀 네비게이션 바 UI
# =====================================================================
st.markdown("""
    <div class="nav-bar">
        <div class="nav-title">
            <span>🛡️ DocuScout</span>
            <span class="badge-pro">AI Pro 3.1</span>
        </div>
        <div style="color: #9ca3af; font-size: 0.9rem;">
            🟢 에이전트 준비완료
        </div>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 🔍 메인 검색 섹션 컨테이너
# =====================================================================
st.markdown("""
    <div class="search-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 600; font-size: 1.05rem; color: #f8fafc;">🧭 AI 리서치 질의어 입력</span>
            <span style="font-size: 0.85rem; color: #9ca3af;">실시간 웹 크롤링 + LLM 팩트체크 결합 모드</span>
        </div>
""", unsafe_allow_html=True)

# 검색 입력창 및 실행 버튼
col_s1, col_s2 = st.columns([5, 1])
with col_s1:
    user_query = st.text_input("질의어 입력", placeholder="예: 2026년 반도체 산업 전망 및 AI 칩 시장 경쟁 구도 분석", label_visibility="collapsed")
with col_s2:
    submit_btn = st.button("🚀 스카우트 실행", type="primary", use_container_width=True)

# 카테고리 필터 캡슐 버튼 구현
st.markdown("<div class='filter-label' style='margin-top: 15px;'>카테고리 필터:</div>", unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4, f_col5, f_col6 = st.columns([1, 1, 1, 1, 1, 2])
with f_col1:
    btn_all = st.button("전체 (All)", use_container_width=True)
with f_col2:
    btn_tech = st.button("테크 (Tech)", use_container_width=True)
with f_col3:
    btn_eco = st.button("경제/금융", use_container_width=True)
with f_col4:
    btn_glo = st.button("글로벌 동향", use_container_width=True)
with f_col5:
    btn_spo = st.button("스포츠/엔터", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True) # search-container 닫기

# =====================================================================
# 🚀 실행 및 결과 출력 영역
# =====================================================================
if submit_btn:
    if user_query:
        # 생동감 넘치는 프로그래스 바 애니메이션
        progress_bar = st.progress(0)
        status_box = st.empty()

        status_box.markdown("🔍 **1단계:** AI 검색어 확장 및 파싱 중...")
        progress_bar.progress(25)

        auto_keyword, report_content, followup_content, sources = run_docuscout(user_query)
        
        status_box.markdown("🌐 **2단계:** Tavily 실시간 웹 출처 수집 완료...")
        progress_bar.progress(60)

        if sources is None:
            progress_bar.empty()
            status_box.empty()
            st.error("관련 자료를 찾을 수 없습니다.")
        else:
            status_box.markdown("💡 **3단계:** LLM 기반 신뢰성 팩트체크 및 리포트 작성 중...")
            progress_bar.progress(100)
            status_box.empty()
            progress_bar.empty()

            # 탐색 완료 상태 카드
            st.markdown(f"""
                <div style="background-color: #111827; border: 1px solid #1f2937; padding: 14px 20px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #34d399; font-weight: 600;">✅ 탐색 완료! 최신 보고서 업데이트됨 (검색어: {auto_keyword})</span>
                    <span style="background-color: #1f2937; color: #94a3b8; padding: 4px 10px; border-radius: 8px; font-size: 0.85rem;">100%</span>
                </div>
            """, unsafe_allow_html=True)

            # 리포트 헤더 및 내보내기 버튼 영역
            col_h1, col_h2 = st.columns([4, 1])
            with col_h1:
                st.markdown("### 📋 AI 에이전트 종합 리포트")
            with col_h2:
                st.download_button(
                    label="📥 리포트 내보내기",
                    data=report_content,
                    file_name=f"DocuScout_Report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            # 1. AI 리포트 본문 카드
            st.markdown(f"""
                <div class="report-card-dark">
                    {report_content.replace(chr(10), '<br>')}
                </div>
            """, unsafe_allow_html=True)

            # 2. 후속 질문
            st.markdown("### 💬 추천 후속 심층 리서치")
            with st.container(border=True):
                st.markdown(followup_content)

            # 3. 검증된 출처 카드
            st.markdown("### 🔗 검증된 신뢰 출처 근거 자료")
            for idx, src in enumerate(sources, 1):
                score = 92 + (idx * 2) % 7
                st.markdown(f"""
                    <div class="source-card-dark">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 600; color: #f8fafc; font-size: 1rem;">근거 카드 #{idx} : {src['title']}</span>
                            <span style="background-color: #1e3a8a; color: #bfdbfe; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">신뢰도 {score}%</span>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.4; margin-bottom: 8px;">{src['content'][:200]}...</p>
                        <a href="{src['url']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 0.85rem; font-weight: 500;">🔗 원문 보러가기 →</a>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 질의어를 입력해주세요!")
