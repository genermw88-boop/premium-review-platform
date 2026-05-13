import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 기본 설정
st.set_page_config(page_title="위드멤버 프리미엄 체험단", layout="wide", initial_sidebar_state="collapsed")

# 2. 깔끔한 화이트 테마 CSS 적용
st.markdown("""
<style>
    /* 전체 배경 화이트&라이트그레이 톤 */
    .stApp {
        background-color: #F8F9FA;
        color: #212529;
    }
    /* 버튼 디자인 (깔끔한 블루) */
    div.stButton > button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
    }
    div.stButton > button:hover {
        background-color: #357ABD;
        color: white;
    }
    /* 카드(박스) 디자인 */
    .card-box {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid #E9ECEF;
    }
    h1, h2, h3 { color: #212529 !important; font-weight: 800; }
    p, span, label, li { color: #495057 !important; }
    
    /* 사이드바 디자인 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E9ECEF;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 초기화
if 'campaigns' not in st.session_state:
    st.session_state['campaigns'] = []
if 'applications' not in st.session_state:
    st.session_state['applications'] = []
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

today = datetime.now()
default_recruit_end = today + timedelta(days=7)
default_exp_start = default_recruit_end + timedelta(days=1)
default_exp_end = default_exp_start + timedelta(weeks=4)

# ==========================================
# 🔒 왼쪽 사이드바 (관리자 전용 구역)
# ==========================================
with st.sidebar:
    if not st.session_state['admin_logged_in']:
        st.markdown("### ⚙️ 관리자 로그인")
        admin_id = st.text_input("아이디")
        admin_pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if admin_id == "admin" and admin_pw == "1234":
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("정보가 일치하지 않습니다.")
    else:
        st.markdown("### 👑 위드멤버 관리자")
        admin_menu = st.radio("메뉴 이동", ["현황 대시보드", "새 캠페인 등록"])
        st.write("---")
        if st.button("로그아웃"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

# ==========================================
# 📱 메인 화면 분기 (로그인 여부에 따라 다르게 표시)
# ==========================================
if not st.session_state['admin_logged_in']:
    # ----------------------------------------
    # [일반 방문자(블로거) 화면]
    # ----------------------------------------
    st.title("✨ 위드멤버 프리미엄 체험단")
    st.write("퀄리티 높은 리뷰로 로컬 매장과 함께 성장할 리뷰어님들을 모십니다.")
    st.markdown("---")

    if not st.session_state['campaigns']:
        st.info("현재 준비 중인 캠페인이 없습니다. 곧 새로운 캠페인으로 찾아뵙겠습니다!")
    else:
        for c in st.session_state['campaigns']:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            col_img, col_info = st.columns([1, 2.5])
            
            with col_img:
                if c['image'] is not None:
                    st.image(c['image'], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
            
            with col_info:
                st.markdown(f"### 📍 {c['shop']} ({c['status']})")
                st.write(f"**🎁 제공 내역:** {c['offer']}")
                st.write(f"**🔑 필수 키워드:** {c['keywords']}")
                st.write(f"**🗓️ 모집 기간:** {c['recruit_start']} ~ {c['recruit_end']} (총 {c['recruit_count']}명)")
                st.write(f"**🏃 체험 기간:** {c['exp_start']} ~ {c['exp_end']}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    with st.popover("👉 체험단 신청하기", use_container_width=True):
                        with st.form(f"apply_{c['id']}"):
                            st.write("#### 📝 신청서 작성")
                            blog_url = st.text_input("운영 중인 블로그/SNS URL")
                            contact = st.text_input("연락처 (010-0000-0000)")
                            if st.form_submit_button("신청 완료"):
                                if blog_url and contact:
                                    st.session_state['applications'].append({
                                        "campaign_id": c['id'], "shop": c['shop'], 
                                        "blog_url": blog_url, "contact": contact,
                                        "review_link": "", "status": "신청완료"
                                    })
                                    st.success("신청이 완료되었습니다!")
                                else:
                                    st.error("모든 항목을 입력해주세요.")
                with col_btn2:
                    with st.popover("✅ 리뷰 제출하기", use_container_width=True):
                        with st.form(f"review_{c['id']}"):
                            st.write("#### 🔗 작성 완료된 리뷰 제출")
                            my_contact = st.text_input("신청 시 연락처")
                            final_link = st.text_input("리뷰 URL")
                            if st.form_submit_button("제출 완료"):
                                submitted = False
                                for app in st.session_state['applications']:
                                    if app['campaign_id'] == c['id'] and app['contact'] == my_contact:
                                        app['review_link'] = final_link
                                        app['status'] = "리뷰제출완료"
                                        submitted = True
                                if submitted:
                                    st.success("리뷰 URL이 접수되었습니다.")
                                else:
                                    st.error("신청 내역을 찾을 수 없습니다.")
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # ----------------------------------------
    # [관리자 전용 화면]
    # ----------------------------------------
    if admin_menu == "새 캠페인 등록":
        st.title("🏢 새 캠페인 등록")
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        with st.form("campaign_form"):
            col1, col2 = st.columns(2)
            with col1:
                shop_name = st.text_input("매장명")
                offer = st.text_input("제공 내역 (예: 5만원 상당 식사권)")
                uploaded_file = st.file_uploader("대표 이미지 첨부", type=['png', 'jpg', 'jpeg'])
            with col2:
                keywords = st.text_input("필수 노출 키워드")
                platform = st.selectbox("메인 타겟 플랫폼", ["네이버 블로그", "인스타그램 릴스", "유튜브 쇼츠"])
                recruit_count = st.number_input("모집 인원", min_value=1, value=10)
            
            st.write("---")
            col3, col4 = st.columns(2)
            with col3:
                recruit_dates = st.date_input("모집 기간 (기본 7일)", [today.date(), default_recruit_end.date()])
            with col4:
                exp_dates = st.date_input("체험 기간 (기본 3~4주)", [default_exp_start.date(), default_exp_end.date()])
            
            if st.form_submit_button("캠페인 등록하기"):
                if shop_name and len(recruit_dates) == 2 and len(exp_dates) == 2:
                    st.session_state['campaigns'].append({
                        "id": len(st.session_state['campaigns']) + 1, "shop": shop_name, 
                        "offer": offer, "keywords": keywords, "platform": platform,
                        "image": uploaded_file, "recruit_count": recruit_count,
                        "recruit_start": recruit_dates[0], "recruit_end": recruit_dates[1],
                        "exp_start": exp_dates[0], "exp_end": exp_dates[1], "status": "진행중"
                    })
                    st.success(f"[{shop_name}] 캠페인이 등록되었습니다!")
        st.markdown('</div>', unsafe_allow_html=True)

    elif admin_menu == "현황 대시보드":
        st.title("📊 관리자 대시보드")
        if not st.session_state['campaigns']:
            st.info("등록된 캠페인이 없습니다.")
        else:
            selected_shop = st.selectbox("관리할 캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            current_campaign = next(c for c in st.session_state['campaigns'] if c['shop'] == selected_shop)
            
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.subheader("🗓️ 체험 기간 연장")
            col_ext1, col_ext2 = st.columns([3, 1])
            with col_ext1:
                new_exp_end = st.date_input("새로운 체험 종료일 선택", current_campaign['exp_end'])
            with col_ext2:
                st.write("") 
                st.write("")
                if st.button("기간 연장 적용"):
                    current_campaign['exp_end'] = new_exp_end
                    st.success("연장되었습니다.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.subheader("👥 신청 및 리뷰 제출 현황")
            app_list = [app for app in st.session_state['applications'] if app['shop'] == selected_shop]
            if app_list:
                df = pd.DataFrame(app_list)[['contact', 'blog_url', 'status', 'review_link']]
                df.columns = ['연락처', '블로그 URL', '상태', '제출된 링크']
                st.dataframe(df, use_container_width=True)
            else:
                st.write("아직 신청자가 없습니다.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.subheader("📑 마감 보고서 자동 생성")
            if st.button("보고서 출력하기"):
                completed = [app['review_link'] for app in app_list if app['review_link'] != ""]
                st.markdown(f"""
                <div style="background-color:#F8F9FA; padding:20px; border-radius:10px; border:1px solid #E9ECEF;">
                    <h3 style="text-align:center; color:#212529;">[{current_campaign['shop']}] 체험단 마감 리포트</h3>
                    <hr>
                    <p><b>■ 모집 및 완료:</b> 총 {current_campaign['recruit_count']}명 모집 / {len(completed)}건 완료</p>
                    <p><b>■ 플레이스 이슈 진단 5포인트 달성율 (100%)</b></p>
                    <ul>
                        <li>리뷰 활동성 (매장 분위기 어필)</li>
                        <li>키워드 부재 방지 (제목/본문 삽입)</li>
                        <li>사진 빈도 (가이드라인 충족)</li>
                        <li>새소식 업데이트 연계 반영</li>
                        <li>리뷰 전환율 (정중한 존댓말 및 후킹 문구)</li>
                    </ul>
                    <p><b>■ 제출된 리뷰 링크</b></p>
                </div>
                """, unsafe_allow_html=True)
                for idx, link in enumerate(completed):
                    st.write(f"{idx+1}. {link}")
            st.markdown('</div>', unsafe_allow_html=True)
