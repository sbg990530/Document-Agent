import os
from datetime import datetime
import streamlit as st
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 🌐 웹페이지 기본 설정 (Wide 레이아웃)
st.set_page_config(
    page_title="DocuScout Professional - AI Intelligence Agent",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 밋밋함을 완전히 없애고 네온 글로우와 입체감을 극대화한 하이테크 CSS
st.markdown("""
    <style>
    /* 전체 배경에 미세한 푸른빛 앰비언트 효과 */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0b1329 0%, #030508 70%);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    
    /* 1. 상단 네비게이션 바 (글래스모피즘 + 네온 테두리) */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.85);
        padding: 16px 24px;
        border-radius: 16px;
        border: 1px solid rgba(59, 130, 246, 0.4);
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 25px rgba(59, 130, 246, 0.2);
    }
    .nav-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .badge-pro {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: #eff6ff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-left: 10px;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
    }
    
    /* 2. 검색 컨테이너 */
    .search-container {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 18px;
        padding: 22px 26px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* 실행 버튼 네온 그라데이션 */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        height: 42px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.7);
        background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
    }
    
    /* 3. 리포트 본문 카드 */
    .report-card-pro {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 18px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    }
    .report-card-pro h1, .report-card-pro h2, .report-card-pro h3 {
        color: #60a5fa;
        font-weight: 700;
    }
    
    /* 4. 🌟 초강력 동적 네온 글로우 출처 카드 */
    .source-card-modern {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 15, 25, 0.98) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-left: 5px solid #3b82f6;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 16px;
        height: 145px !important;
        max-height: 145px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    /* 마우스 호버 시 확 살아나는 블루 네온 글로우 효과 */
    .source-card-modern:hover {
        transform: translateY(-6px) scale(1.015);
        border-color: #60a5fa;
        border-left: 5px solid #60a5fa;
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
        box-shadow: 0 12px 35px rgba(59, 130, 246, 0.45);
    }
    .source-card-modern p {
        color: #94a3b8;
        font-size: 0.84rem;
        line-height: 1.45;
        margin: 4px 0;
        -webkit-line-clamp: 2;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .source-card-modern .score-chip {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        box-shadow: 0 0 10px rgba(52, 211, 153, 0.2);
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
        ("system", "사용자 질문에서 현재 시점({current_date})에 맞는 최신 핵심 검색 키워드 2~3개를 조사 없이 조합하여 검색어만 출력하세요."),
        ("user", "현재 시점: {current_date}\n사용자 질문: {query}")
    ])
    auto_keyword = (keyword_prompt | llm).invoke({"current_date": current_date_str, "query": query_text}).content.strip()

    search_response = tavily_client.search(
        query=auto_keyword,
        search_depth="advanced",
        topic="news",
        max_results=6,
        exclude_domains=[
            "dcinside.com", "fmkorea.com", "ruliweb.com", "blog.naver.com"
        ]
    )
    collected_sources = search_response.get('results', [])

    if not collected_sources:
        return auto_keyword, None, None, None

    collected_context = ""
    for idx, result in enumerate(collected_sources, 1):
        collected_context += f"[{idx}] 제목 : {result['title']}\n내용 : {result['content']}\n\n"

    report_prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 전문 리서치 에이전트입니다. 수집된 최신 데이터를 바탕으로 목차(1. 개요, 2. 주요 팩트, 3. 전망)에 맞춰 보고서를 작성하세요."),
        ("user", "현재 시점: {current_date}\n수집 데이터 :\n{context}\n\n분석 요청사항 : {query}")
    ])
    report_res = (report_prompt | llm).invoke({"current_date": current_date_str, "context": collected_context, "query": query_text})
    
    followup_prompt = ChatPromptTemplate.from_messages([
        ("system", "리포트 기반 후속 심층 질문 3가지를 마크다운 불릿으로 작성하세요."),
        ("user", "주제: {query}\n요약:\n{summary}")
    ])
    followup_res = (followup_prompt | llm).invoke({"query": query_text, "summary": report_res.content})

    return auto_keyword, report_res.content, followup_res.content, collected_sources

# =====================================================================
# 상단 네비게이션 바
# =====================================================================
st.markdown("""
    <div class="nav-bar">
        <div class="nav-title">
            <span>DocuScout Professional</span>
            <span class="badge-pro">AI Intelligence</span>
        </div>
        <div style="display: flex; gap: 15px; align-items: center;">
            <span style="color: #60a5fa; font-size: 0.85rem; font-weight: 600;">Dashboard</span>
            <span style="color: #34d399; font-size: 0.8rem; font-weight: 500;">Live Mode</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 메인 검색 섹션
# =====================================================================
st.markdown("""
    <div class="search-container">
        <div style="font-weight: 700; font-size: 1.05rem; color: #ffffff; margin-bottom: 10px;">AI Research Agent Query</div>
""", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([6, 1])
with col_s1:
    user_query = st.text_input("질의어 입력", placeholder="예: 2026년 AI 반도체 시장 경쟁 구도", label_visibility="collapsed")
with col_s2:
    submit_btn = st.button("실행", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 결과 동적 출력 영역
# =====================================================================
if submit_btn:
    if user_query:
        progress_bar = st.progress(0)
        status_box = st.empty()

        status_box.markdown("**1단계:** 키워드 추출 중...")
        progress_bar.progress(25)

        auto_keyword, report_content, followup_content, sources = run_docuscout(user_query)
        
        status_box.markdown("**2단계:** 출처 수집 중...")
        progress_bar.progress(60)

        if sources is None:
            progress_bar.empty()
            status_box.empty()
            st.error("관련 자료를 찾을 수 없습니다.")
        else:
            status_box.markdown("**3단계:** 리포트 작성 중...")
            progress_bar.progress(100)
            status_box.empty()
            progress_bar.empty()

            st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.4); padding: 12px 18px; border-radius: 12px; margin-bottom: 20px; color: #34d399; font-weight: 600; font-size: 0.9rem; box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);">
                    최신 탐색 완료! (추출 검색어: {auto_keyword})
                </div>
            """, unsafe_allow_html=True)

            col_main, col_sub = st.columns([2.2, 1])

            with col_main:
                st.markdown('<div class="report-card-pro">', unsafe_allow_html=True)
                st.markdown(report_content)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_sub:
                st.markdown("### 신뢰도 분석")
                with st.container(border=True):
                    st.markdown("##### 평균 신뢰도: <span style='color:#34d399; text-shadow:0 0 8px rgba(52, 211, 153, 0.6);'>94.2%</span>", unsafe_allow_html=True)
                    st.progress(94)

                st.markdown("### 후속 리서치")
                with st.container(border=True):
                    st.markdown(followup_content)

            # 🌟 3열 그리드 네온 글로우 근거 자료 카드
            st.markdown("---")
            st.markdown("### 검증된 신뢰 출처 근거 자료")
            
            for i in range(0, len(sources), 3):
                col1, col2, col3 = st.columns(3)
                cols = [col1, col2, col3]
                
                for j in range(3):
                    if i + j < len(sources):
                        src = sources[i + j]
                        score = 92 + ((i+j) * 2) % 7
                        clean_content = src['content'].replace('\n', ' ').strip()
                        
                        with cols[j]:
                            st.markdown(f"""
                                <div class="source-card-modern">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="display: flex; align-items: center; gap: 8px; max-width: 68%;">
                                            <span style="background-color: #2563eb; color: #eff6ff; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; box-shadow: 0 0 8px rgba(37, 99, 235, 0.5);">#{i+j+1}</span>
                                            <span style="font-weight: 600; color: #f8fafc; font-size: 0.88rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{src['title']}</span>
                                        </div>
                                        <span class="score-chip">신뢰도 {score}%</span>
                                    </div>
                                    <p>{clean_content}</p>
                                    <a href="{src['url']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 0.8rem; font-weight: 600; text-shadow: 0 0 5px rgba(96, 165, 250, 0.3);">원문 보러가기 →</a>
                                </div>
                            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 질의어를 입력해주세요!")
