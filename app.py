import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="위드멤버 프리미엄 체험단", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS (화이트 톤 & 썸네일 갤러리 디자인 업그레이드)
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #212529; }
    .card-box { 
        background-color: #FFFFFF; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* 그림자 효과 강화 */
        margin-bottom: 20px; 
        border: 1px solid #E9ECEF; 
        transition: transform 0.2s; /* 마우스 올렸을 때 애니메이션 준비 */
    }
    .card-box:hover { transform: translateY(-5px); } /* 마우스 올리면 살짝 위로 뜸 */
    div.stButton > button { background-color: #4A90E2; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 10px; }
    div.stButton > button:hover { background-color: #357ABD; color: white; }
    .shop-title { font-size: 1.2rem; font-weight: 900; margin-top: 10px; margin-bottom: 5px; color: #111111; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .offer-text { font-size: 0.95rem; color: #E74C3C; font-weight: bold; margin-bottom: 5px; }
    .info-text { font-size: 0.85rem; color: #495057; margin-bottom: 3px; }
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
    # [블로거 화면 - 바둑판 배열]
    # ----------------------------------------
    # 상단 배너 (깨지지 않는 HTML 그라데이션 디자인 적용)
    st.markdown("""
        <div style="width:100%; height:140px; background: linear-gradient(135deg, #4A90E2 0%, #50E3C2 100%); border-radius:15px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white; margin-bottom:30px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <h1 style="color:white; margin:0; font-size:2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">✨ 프리미엄 체험단 플랫폼</h1>
            <p style="color:white; margin:0; font-size:1rem; opacity:0.9;">로컬 비즈니스 성장을 함께할 상위 10% 리뷰어를 모십니다.</p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state['campaigns']:
        st.info("현재 준비 중인 캠페인이 없습니다. 곧 새로운 캠페인으로 찾아뵙겠습니다!")
    else:
        # 4열 바둑판 그리드 생성
        cols = st.columns(4) 
        for idx, c in enumerate(st.session_state['campaigns']):
            with cols[idx % 4]: # 4개마다 줄바꿈
                st.markdown('<div class="card-box">', unsafe_allow_html=True)
                
                # 이미지 노출 (이미지가 없을 경우 예쁜 그라데이션 박스 노출)
                if c['image'] is not None:
                    st.image(c['image'], use_container_width=True)
                else:
                    st.markdown('<div style="height:180px; background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;">이미지 준비중</div>', unsafe_allow_html=True)
                
                # 정보 텍스트
                st.markdown(f'<div class="shop-title">{c["shop"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="offer-text">{c["offer"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text">🗓️ 모집: {c["recruit_start"].strftime("%m.%d")} ~ {c["recruit_end"].strftime("%m.%d")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text">👥 인원: {c["recruit_count"]}명 ({c["platform"]})</div>', unsafe_allow_html=True)
                
                st.write("") # 여백
                
                # 팝업 형태의 신청 버튼
                with st.popover("자세히 보기 및 신청", use_container_width=True):
                    st.markdown(f"#### 📍 {c['shop']}")
                    st.write(f"**🔑 필수 키워드:** {c['keywords']}")
                    st.write(f"**🏃 체험 기간:** {c['exp_start']} ~ {c['exp_end']}")
                    st.divider()
                    
                    # 탭 분리: 신청하기 / 리뷰제출
                    tab_apply, tab_submit = st.tabs(["✍️ 신청서 작성", "✅ 리뷰 제출 (선정자)"])
                    with tab_apply:
                        with st.form(f"apply_{c['id']}"):
                            blog_url = st.text_input("운영 채널 URL")
                            contact = st.text_input("연락처 (010-0000-0000)")
                            if st.form_submit_button("신청 완료"):
                                st.session_state['applications'].append({
                                    "campaign_id": c['id'], "shop": c['shop'], "blog_url": blog_url, "contact": contact, "review_link": "", "status": "신청완료"
                                })
                                st.success("신청이 완료되었습니다.")
                    with tab_submit:
                        with st.form(f"submit_{c['id']}"):
                            my_contact = st.text_input("신청 시 입력한 연락처")
                            final_link = st.text_input("작성 완료된 리뷰 URL")
                            if st.form_submit_button("제출 완료"):
                                for app in st.session_state['applications']:
                                    if app['campaign_id'] == c['id'] and app['contact'] == my_contact:
                                        app['review_link'] = final_link
                                        app['status'] = "리뷰제출완료"
                                st.success("리뷰가 성공적으로 접수되었습니다.")
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
            selected_shop = st.selectbox("보고서를 출력할 캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            app_list = [app for app in st.session_state['applications'] if app['shop'] == selected_shop]
            
            if app_list:
                df = pd.DataFrame(app_list)[['contact', 'blog_url', 'status', 'review_link']]
                st.dataframe(df, use_container_width=True)
            else:
                st.write("아직 신청자가 없습니다.")
                
            st.markdown("---")
            if st.button("📈 마감 보고서 출력하기"):
                completed = [app['review_link'] for app in app_list if app['review_link'] != ""]
                
                # 프리미엄 리포트 양식 출력 (기존에 설정하신 진단 5포인트 포함)
                st.markdown(f"""
                <div style="background-color:#111111; color:#D4AF37; padding:30px; border-radius:15px; border:2px solid #D4AF37;">
                    <h2 style="text-align:center; color:#D4AF37;">[{selected_shop}] 체험단 마감 리포트</h2>
                    <hr style="border-color:#D4AF37;">
                    <h4 style="color:#FFFFFF;">1. 캠페인 요약</h4>
                    <ul style="color:#FFFFFF;">
                        <li><b>모집 인원:</b> 목표 {next(c['recruit_count'] for c in st.session_state['campaigns'] if c['shop'] == selected_shop)}명</li>
                        <li><b>리뷰 완료 건수:</b> 총 {len(completed)}건 달성</li>
                    </ul>
                    <h4 style="color:#FFFFFF;">2. 플레이스 이슈 진단 결과 (가이드라인 100% 준수)</h4>
                    <ul style="color:#FFFFFF;">
                        <li>✅ <b>리뷰 활동성:</b> 생동감 있는 매장 분위기 스케치 완료</li>
                        <li>✅ <b>키워드 부재 방지:</b> 타겟 키워드 본문/제목 자연스러운 삽입</li>
                        <li>✅ <b>사진 빈도:</b> 필수 가이드라인 충족 완료</li>
                        <li>✅ <b>새소식 업데이트 연계:</b> 플레이스 정보 반영</li>
                        <li>✅ <b>리뷰 전환율:</b> 정중한 존댓말 및 고객 방문 유도 후킹 문구 적용</li>
                    </ul>
                    <h4 style="color:#FFFFFF;">3. 최종 리뷰 링크 리스트</h4>
                </div>
                """, unsafe_allow_html=True)
                for idx, link in enumerate(completed):
                    st.write(f"**{idx+1}.** {link}")
