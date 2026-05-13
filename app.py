import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="위드멤버 프리미엄 체험단", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS (화이트 톤 & 썸네일 갤러리 디자인)
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #212529; }
    .card-box { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #E9ECEF; }
    div.stButton > button { background-color: #4A90E2; color: white; border-radius: 6px; font-weight: bold; width: 100%; border: none; }
    div.stButton > button:hover { background-color: #357ABD; color: white; }
    .shop-title { font-size: 1.1rem; font-weight: 800; margin-bottom: 5px; color: #212529; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .offer-text { font-size: 0.9rem; color: #E74C3C; font-weight: bold; margin-bottom: 5px; }
    .info-text { font-size: 0.8rem; color: #6C757D; margin-bottom: 2px; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E9ECEF; }
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
# 🔒 왼쪽 사이드바 (관리자 구역)
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
        admin_menu = st.radio("메뉴 이동", ["새 캠페인 등록", "캠페인 관리(수정/삭제)", "현황 대시보드"])
        st.write("---")
        if st.button("로그아웃 (블로거 화면 보기)"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

# ==========================================
# 📱 메인 화면 분기
# ==========================================
if not st.session_state['admin_logged_in']:
    # ----------------------------------------
    # [블로거 화면 - 3.jpg 스타일 바둑판 배열]
    # ----------------------------------------
    st.image("https://via.placeholder.com/1200x200/F1F3F5/4A90E2?text=Premium+Review+Platform+Open", use_container_width=True) # 상단 배너 예시
    st.markdown("### ✨ 진행 중인 프리미엄 캠페인")
    st.write("로컬 비즈니스 성장을 함께할 상위 10% 리뷰어를 모십니다.")
    st.markdown("---")

    if not st.session_state['campaigns']:
        st.info("현재 준비 중인 캠페인이 없습니다.")
    else:
        # 4열 바둑판 그리드 생성
        cols = st.columns(4) 
        for idx, c in enumerate(st.session_state['campaigns']):
            with cols[idx % 4]: # 4개마다 줄바꿈
                st.markdown('<div class="card-box">', unsafe_allow_html=True)
                
                # 이미지 노출
                if c['image'] is not None:
                    st.image(c['image'], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
                
                # 정보 텍스트 (줄바꿈 없이 깔끔하게)
                st.markdown(f'<div class="shop-title">{c["shop"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="offer-text">{c["offer"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text">모집: {c["recruit_start"].strftime("%m.%d")} ~ {c["recruit_end"].strftime("%m.%d")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text">인원: {c["recruit_count"]}명 ({c["platform"]})</div>', unsafe_allow_html=True)
                
                st.write("") # 여백
                
                # 팝업 형태의 신청 버튼
                with st.popover("자세히 보기 및 신청", use_container_width=True):
                    st.markdown(f"#### 📍 {c['shop']}")
                    st.write(f"**키워드:** {c['keywords']}")
                    st.write(f"**체험기간:** {c['exp_start']} ~ {c['exp_end']}")
                    st.divider()
                    
                    # 탭 분리: 신청하기 / 리뷰제출
                    tab_apply, tab_submit = st.tabs(["신청서 작성", "리뷰 제출 (선정자)"])
                    with tab_apply:
                        with st.form(f"apply_{c['id']}"):
                            blog_url = st.text_input("운영 채널 URL")
                            contact = st.text_input("연락처 (010-0000-0000)")
                            if st.form_submit_button("신청 완료"):
                                st.session_state['applications'].append({
                                    "campaign_id": c['id'], "shop": c['shop'], "blog_url": blog_url, "contact": contact, "review_link": "", "status": "신청완료"
                                })
                                st.success("신청되었습니다.")
                    with tab_submit:
                        with st.form(f"submit_{c['id']}"):
                            my_contact = st.text_input("신청 연락처 확인")
                            final_link = st.text_input("리뷰 URL")
                            if st.form_submit_button("제출 완료"):
                                for app in st.session_state['applications']:
                                    if app['campaign_id'] == c['id'] and app['contact'] == my_contact:
                                        app['review_link'] = final_link
                                        app['status'] = "리뷰제출완료"
                                st.success("접수되었습니다.")
                st.markdown('</div>', unsafe_allow_html=True)

else:
    # ----------------------------------------
    # [관리자 전용 화면]
    # ----------------------------------------
    if admin_menu == "새 캠페인 등록":
        st.title("🏢 새 캠페인 등록")
        with st.form("campaign_form"):
            col1, col2 = st.columns(2)
            with col1:
                shop_name = st.text_input("매장명")
                offer = st.text_input("제공 내역 (예: 5만원 식사권)")
                uploaded_file = st.file_uploader("대표 이미지 (정사각형 권장)", type=['png', 'jpg', 'jpeg'])
            with col2:
                keywords = st.text_input("필수 노출 키워드")
                platform = st.selectbox("메인 타겟 플랫폼", ["네이버 블로그", "인스타그램 릴스", "유튜브 쇼츠"])
                recruit_count = st.number_input("모집 인원", min_value=1, value=10)
            st.write("---")
            col3, col4 = st.columns(2)
            with col3: recruit_dates = st.date_input("모집 기간", [today.date(), default_recruit_end.date()])
            with col4: exp_dates = st.date_input("체험 기간", [default_exp_start.date(), default_exp_end.date()])
            
            if st.form_submit_button("캠페인 등록하기"):
                if shop_name and len(recruit_dates) == 2 and len(exp_dates) == 2:
                    st.session_state['campaigns'].append({
                        "id": len(st.session_state['campaigns']) + 1, "shop": shop_name, 
                        "offer": offer, "keywords": keywords, "platform": platform,
                        "image": uploaded_file, "recruit_count": recruit_count,
                        "recruit_start": recruit_dates[0], "recruit_end": recruit_dates[1],
                        "exp_start": exp_dates[0], "exp_end": exp_dates[1], "status": "진행중"
                    })
                    st.success("등록 완료!")

    elif admin_menu == "캠페인 관리(수정/삭제)":
        st.title("🛠️ 캠페인 관리 (수정 및 삭제)")
        if not st.session_state['campaigns']:
            st.info("등록된 캠페인이 없습니다.")
        else:
            selected_shop = st.selectbox("수정/삭제할 캠페인을 선택하세요", [c['shop'] for c in st.session_state['campaigns']])
            
            # 선택한 캠페인의 인덱스 찾기
            idx = next(i for i, c in enumerate(st.session_state['campaigns']) if c['shop'] == selected_shop)
            c = st.session_state['campaigns'][idx]
            
            st.markdown("---")
            col_del1, col_del2 = st.columns([4, 1])
            with col_del2:
                if st.button("❌ 이 캠페인 완전 삭제", type="primary"):
                    st.session_state['campaigns'].pop(idx)
                    st.success(f"{selected_shop} 캠페인이 삭제되었습니다.")
                    st.rerun()

            st.write("### 캠페인 내용 수정")
            with st.form("edit_form"):
                new_offer = st.text_input("제공 내역 수정", value=c['offer'])
                new_keywords = st.text_input("키워드 수정", value=c['keywords'])
                new_recruit_count = st.number_input("모집 인원 수정", min_value=1, value=int(c['recruit_count']))
                
                if st.form_submit_button("수정 내용 저장"):
                    st.session_state['campaigns'][idx]['offer'] = new_offer
                    st.session_state['campaigns'][idx]['keywords'] = new_keywords
                    st.session_state['campaigns'][idx]['recruit_count'] = new_recruit_count
                    st.success("수정 사항이 성공적으로 저장되었습니다.")

    elif admin_menu == "현황 대시보드":
        st.title("📊 현황 대시보드 및 리포트")
        if not st.session_state['campaigns']:
            st.info("등록된 캠페인이 없습니다.")
        else:
            selected_shop = st.selectbox("캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            app_list = [app for app in st.session_state['applications'] if app['shop'] == selected_shop]
            
            if app_list:
                df = pd.DataFrame(app_list)[['contact', 'blog_url', 'status', 'review_link']]
                st.dataframe(df, use_container_width=True)
            else:
                st.write("아직 신청자가 없습니다.")
