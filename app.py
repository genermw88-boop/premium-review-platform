import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 및 블랙 & 골드 테마 CSS
st.set_page_config(page_title="프리미엄 체험단 플랫폼", layout="wide")

st.markdown("""
<style>
    /* 전체 배경을 블랙으로, 기본 텍스트를 골드로 설정 */
    .stApp {
        background-color: #111111;
        color: #D4AF37;
    }
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: #D4AF37 !important;
    }
    /* 탭 디자인 변경 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF;
        background-color: #333333;
        border-radius: 4px 4px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D4AF37;
        color: #111111 !important;
    }
    /* 버튼 디자인 변경 */
    div.stButton > button {
        background-color: #D4AF37;
        color: #111111;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #F1E5AC;
        color: #111111;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ 프리미엄 체험단 매칭 플랫폼 (MVP)")

# 2. 임시 데이터 저장을 위한 Session State 초기화
if 'campaigns' not in st.session_state:
    st.session_state['campaigns'] = []
if 'applications' not in st.session_state:
    st.session_state['applications'] = []

# 3. 주요 기능 탭 구성
tab1, tab2, tab3 = st.tabs(["🏢 사장님 (캠페인 등록)", "✍️ 블로거 (캠페인 신청)", "👑 관리자 대시보드"])

# --- 탭 1: 광고주(사장님) 페이지 ---
with tab1:
    st.subheader("새로운 체험단 캠페인 등록")
    st.write("매장 정보와 제공 내역을 입력하여 블로거를 모집하세요.")
    
    with st.form("campaign_form"):
        col1, col2 = st.columns(2)
        with col1:
            shop_name = st.text_input("매장명 / 상호명")
            offer = st.text_input("제공 내역 (예: 5만원 상당 식사권)")
        with col2:
            keywords = st.text_input("필수 노출 키워드 (쉼표로 구분)")
            platform = st.selectbox("메인 타겟 플랫폼", ["네이버 블로그", "인스타그램 릴스", "유튜브 쇼츠"])
        
        st.markdown("""
        **[블로거 리뷰 가이드라인 - 플레이스 이슈 진단 5포인트 필수 반영]**
        1. **리뷰 활동성:** 생동감 있는 매장 분위기 스케치
        2. **키워드 부재 방지:** 제목 및 본문에 필수 키워드 자연스럽게 배치
        3. **사진 빈도:** 매장 및 메뉴 사진 15장 이상 첨부 (숏폼의 경우 15초 이상)
        4. **새소식 업데이트 연계:** 플레이스 새소식 이벤트 내용 언급
        5. **리뷰 전환율:** 고객의 방문을 유도하는 후킹 문구 및 정중한 존댓말 사용
        """)
        
        submit_campaign = st.form_submit_button("캠페인 등록하기")
        if submit_campaign and shop_name:
            st.session_state['campaigns'].append({
                "shop": shop_name, 
                "offer": offer, 
                "keywords": keywords,
                "platform": platform
            })
            st.success(f"[{shop_name}] 캠페인이 성공적으로 등록되었습니다!")

# --- 탭 2: 블로거(체험단) 페이지 ---
with tab2:
    st.subheader("진행 중인 프리미엄 캠페인")
    
    if st.session_state['campaigns']:
        for idx, c in enumerate(st.session_state['campaigns']):
            with st.container():
                st.markdown(f"### 📍 {c['shop']}")
                st.write(f"**🎁 제공 내역:** {c['offer']} | **🔑 필수 키워드:** {c['keywords']} | **📱 플랫폼:** {c['platform']}")
                
                with st.expander("이 캠페인 신청하기"):
                    with st.form(f"apply_form_{idx}"):
                        blog_url = st.text_input("운영 중인 블로그/SNS URL")
                        contact = st.text_input("연락처 (010-0000-0000)")
                        message = st.text_area("선정되어야 하는 이유 (본인 채널의 강점)")
                        
                        submit_apply = st.form_submit_button("신청서 제출")
                        if submit_apply and blog_url:
                            st.session_state['applications'].append({
                                "shop": c['shop'], 
                                "blog_url": blog_url, 
                                "contact": contact,
                                "message": message
                            })
                            st.success("신청이 완료되었습니다. 선정 시 개별 연락드립니다.")
            st.divider()
    else:
        st.info("현재 진행 중인 캠페인이 없습니다. 곧 새로운 캠페인이 오픈됩니다!")

# --- 탭 3: 관리자 페이지 ---
with tab3:
    st.subheader("체험단 신청 현황 중앙 관리")
    st.write("각 캠페인별 블로거 신청 내역을 확인하고 선정을 진행하세요.")
    
    if st.session_state['applications']:
        df = pd.DataFrame(st.session_state['applications'])
        df.columns = ['캠페인 매장명', '블로그 URL', '연락처', '신청 메시지']
        st.dataframe(df, use_container_width=True)
        
        # 엑셀 다운로드 기능
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="엑셀(CSV)로 다운로드",
            data=csv,
            file_name='blogger_applications.csv',
            mime='text/csv',
        )
    else:
        st.info("아직 등록된 블로거 신청 내역이 없습니다.")