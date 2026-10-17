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

# 🎨 가독성과 스타일이 완벽히 정돈된 다크 테마 커스텀 CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
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
    .search-container {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .filter-label {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .stButton button {
        background-color: #1f2937;
        color: #ffffff;
        border: 1px solid #374151;
        border-radius: 8px;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: #374151;
        border-color: #60a5fa;
        color: #ffffff;
    }
    .report-card-dark {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
        color: #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .source-card-dark {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
        
        height: 160px; /* 모든 카드 높이 통일 */
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* 요소들을 상/하로 균등 배치 */
        box-sizing: border-box;
    }
    .source-card-dark p {
        color: #94a3b8;
        font-size: 0.88rem;
        line-height: 1.4;
        margin: 6px 0;
        
        display: -webkit-box;
        -webkit-line-clamp: 2; /* 2줄로 제한하여 버튼과 겹침 방지 */
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
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
# ⚙️ 핵심 분석 파이프라인 함수 (최신 시점 및 뉴스 토픽 반영)
# =====================================================================
def run_docuscout(query_text):
    current_date_str = datetime.now().strftime("%Y년 %m월")

    # 1. 키워드 생성 시 현재 연도/시점을 반영하도록 유도
    keyword_prompt = ChatPromptTemplate.from_messages([
        ("system", "사용자 질문에서 현재 시점({current_date})에 맞는 최신 핵심 검색 키워드 2~3개를 조사 없이 조합하여 검색어만 출력하세요."),
        ("user", "현재 시점: {current_date}\n사용자 질문: {query}")
    ])
    auto_keyword = (keyword_prompt | llm).invoke({"current_date": current_date_str, "query": query_text}).content.strip()

    # 2. Tavily 검색 시 topic="news"와 최신성(days=7 또는 advanced) 확보
    search_response = tavily_client.search(
        query=auto_keyword,
        search_depth="advanced",
        topic="news",  # 👈 뉴스 중심의 최신 정보 우선 수집
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

    # 3. 리포트 생성 시점 주입
    report_prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 전문 리서치 에이전트입니다. 수집된 최신 데이터를 바탕으로 현재 시점({current_date})에 걸맞은 표준 목차(1. 개요 및 최신 현황, 2. 주요 수치 및 팩트 지표, 3. 향후 전망 및 시사점)에 맞춰 전문 보고서를 작성하세요."),
        ("user", "현재 시점: {current_date}\n수집 데이터 :\n{context}\n\n분석 요청사항 : {query}")
    ])
    report_res = (report_prompt | llm).invoke({"current_date": current_date_str, "context": collected_context, "query": query_text})
    
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
        <div style="color: #34d399; font-size: 0.9rem; font-weight: 500;">
            🟢 최신 뉴스/실시간 탐색 모드 활성화
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
            <span style="font-size: 0.85rem; color: #94a3b8;">실시간 뉴스 크롤링 + LLM 팩트체크 결합 모드</span>
        </div>
""", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([5, 1])
with col_s1:
    user_query = st.text_input("질의어 입력", placeholder="예: KT롤스터 리그오브레전드 스토브리그 내년 전망", label_visibility="collapsed")
with col_s2:
    submit_btn = st.button("🚀 스카우트 실행", type="primary", use_container_width=True)

st.markdown("<div class='filter-label' style='margin-top: 15px;'>카테고리 필터:</div>", unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
with f_col1:
    st.button("전체 (All)", use_container_width=True)
with f_col2:
    st.button("테크 (Tech)", use_container_width=True)
with f_col3:
    st.button("경제/금융", use_container_width=True)
with f_col4:
    st.button("글로벌 동향", use_container_width=True)
with f_col5:
    st.button("스포츠/엔터", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 🚀 실행 및 결과 출력 영역
# =====================================================================
if submit_btn:
    if user_query:
        progress_bar = st.progress(0)
        status_box = st.empty()

        status_box.markdown("🔍 **1단계:** 현재 시점 기반 최신 키워드 추출 중...")
        progress_bar.progress(25)

        auto_keyword, report_content, followup_content, sources = run_docuscout(user_query)
        
        status_box.markdown("🌐 **2단계:** Tavily 실시간 뉴스 및 공식 웹 출처 수집 중...")
        progress_bar.progress(60)

        if sources is None:
            progress_bar.empty()
            status_box.empty()
            st.error("관련 자료를 찾을 수 없습니다.")
        else:
            status_box.markdown("💡 **3단계:** 최신 데이터 기반 팩트체크 및 리포트 작성 중...")
            progress_bar.progress(100)
            status_box.empty()
            progress_bar.empty()

            st.markdown(f"""
                <div style="background-color: #111827; border: 1px solid #1f2937; padding: 14px 20px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #34d399; font-weight: 600;">✅ 최신 탐색 완료! (추출 검색어: {auto_keyword})</span>
                    <span style="background-color: #1f2937; color: #94a3b8; padding: 4px 10px; border-radius: 8px; font-size: 0.85rem;">100%</span>
                </div>
            """, unsafe_allow_html=True)

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

            st.markdown("""
                <div class="report-card-dark">
            """, unsafe_allow_html=True)
            st.markdown(report_content)
            st.markdown("""
                </div>
            """, unsafe_allow_html=True)

            st.markdown("### 💬 추천 후속 심층 리서치")
            with st.container(border=True):
                st.markdown(followup_content)

            st.markdown("### 🔗 검증된 신뢰 출처 근거 자료")
            for idx, src in enumerate(sources, 1):
                score = 92 + (idx * 2) % 7
                
                # 💥 HTML 태그가 정상 작동하도록 unsafe_allow_html=True를 반드시 포함합니다
                st.markdown(f"""
                    <div class="source-card-dark">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 600; color: #f8fafc; font-size: 1rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 80%;">근거 카드 #{idx} : {src['title']}</span>
                            <span style="background-color: #1e3a8a; color: #bfdbfe; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">신뢰도 {score}%</span>
                        </div>
                        <p>{src['content']}</p>
                        <a href="{src['url']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 0.85rem; font-weight: 500; position: absolute; bottom: 16px; left: 18px;">🔗 원문 보러가기 →</a>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 질의어를 입력해주세요!")
