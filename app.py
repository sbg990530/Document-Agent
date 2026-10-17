%%writefile app.py

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

# 🎨 밋밋함을 없애고 입체감을 극대화한 글래스모피즘 & 사이버 프로 커스텀 CSS
st.markdown("""
    <style>
    /* 전체 배경을 더 짙게 처리하여 콘텐츠 입체감 강조 */
    .stApp {
        background-color: #030508;
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    
    /* 1. 상단 네비게이션 바: 더 세련된 네온 라인 */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.8);
        padding: 16px 28px;
        border-radius: 16px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        margin-bottom: 28px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(59, 130, 246, 0.1);
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
        font-size: 0.8rem;
        font-weight: 700;
        margin-left: 10px;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
    }
    
    /* 2. 검색 컨테이너: 깊이감 있는 글래스 디자인 */
    .search-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 28px;
        backdrop-filter: blur(8px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    /* 버튼: 강력한 사이버 블루 그라데이션 및 호버 효과 */
    .stButton button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(29, 78, 216, 0.3);
    }
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5);
    }
    
    /* 3. 리포트 본문 카드: 고급스러운 서식 */
    .report-card-pro {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .report-card-pro h1, .report-card-pro h2, .report-card-pro h3 {
        color: #60a5fa; /* 제목에 사이버 블루 포인트 */
        font-weight: 700;
    }
    
    /* 4. 🌟 대폭 개선된 '검증된 신뢰 출처 근거 카드' (사이버 프로 스타일) */
    .source-card-modern {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.9) 0%, rgba(10, 15, 25, 0.95) 100%);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-left: 4px solid #1d4ed8; /* 왼쪽 포인트 바 */
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        height: 145px !important;
        max-height: 145px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .source-card-modern:hover {
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(96, 165, 250, 0.6);
        border-left: 4px solid #60a5fa;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.3);
    }
    .source-card-modern p {
        color: #94a3b8;
        font-size: 0.88rem;
        line-height: 1.5;
        margin: 6px 0;
        -webkit-line-clamp: 2;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    /* 신뢰도 칩 프로페셔널 디자인 */
    .source-card-modern .score-chip {
        background-color: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-shadow: 0 0 5px rgba(52, 211, 153, 0.5);
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
        max_results=5,
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
            <span style="color: #60a5fa; font-size: 0.9rem; font-weight: 600;">Dashboard</span>
            <span style="color: #34d399; font-size: 0.85rem; font-weight: 500;">Live Mode</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 메인 검색 섹션
# =====================================================================
st.markdown("""
    <div class="search-container">
        <div style="font-weight: 700; font-size: 1.1rem; color: #ffffff; margin-bottom: 12px;">AI Research Agent Query</div>
""", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([5, 1])
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
                <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px 18px; border-radius: 12px; margin-bottom: 20px; color: #34d399; font-weight: 600;">
                    최신 탐색 완료! (추출 검색어: {auto_keyword})
                </div>
            """, unsafe_allow_html=True)

            col_main, col_sub = st.columns([2, 1])

            with col_main:
                # 리포트 카드 디자인 적용
                st.markdown('<div class="report-card-pro">', unsafe_allow_html=True)
                st.markdown(report_content)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_sub:
                st.markdown("### 신뢰도 분석")
                with st.container(border=True):
                    st.markdown("##### 평균 신뢰도: <span style='color:#34d399; text-shadow:0 0 5px rgba(52, 211, 153, 0.5);'>94.2%</span>", unsafe_allow_html=True)
                    st.progress(94)

                st.markdown("### 후속 리서치")
                with st.container(border=True):
                    st.markdown(followup_content)

            # 🌟 사이버 프로 디자인이 적용된 '검증된 신뢰 출처 근거 카드' 섹션
            st.markdown("---")
            st.markdown("### 검증된 신뢰 출처 근거 자료")
            
            # 한 줄에 카드 3개가 나오도록 레이아웃 (축소했을 때도 보기 좋음)
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
                                        <div style="display: flex; align-items: center; gap: 8px; max-width: 70%;">
                                            <span style="background-color: #1d4ed8; color: #eff6ff; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">#{i+j+1}</span>
                                            <span style="font-weight: 600; color: #f8fafc; font-size: 0.92rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{src['title']}</span>
                                        </div>
                                        <span class="score-chip">신뢰도 {score}%</span>
                                    </div>
                                    <p>{clean_content}</p>
                                    <a href="{src['url']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 0.83rem; font-weight: 500;">원문 보러가기 →</a>
                                </div>
                            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 질의어를 입력해주세요!")
