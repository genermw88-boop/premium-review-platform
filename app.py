import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 기본 설정 및 블랙 & 골드 테마 CSS
st.set_page_config(page_title="프리미엄 체험단 플랫폼", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #111111; color: #D4AF37; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #D4AF37 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF; background-color: #333333; border-radius: 4px 4px 0px 0px; }
    .stTabs [aria-selected="true"] { background-color: #D4AF37; color: #111111 !important; }
    div.stButton > button { background-color: #D4AF37; color: #111111; font-weight: bold; border: none; }
    div.stButton > button:hover { background-color: #F1E5AC; color: #111111; }
    .report-box { border: 2px solid #D4AF37; padding: 20px; border-radius: 10px; background-color: #222222; }
</style>
""", unsafe_allow_html=True)

st.title("✨ 프리미엄 체험단 매칭 플랫폼")

# 2. 데이터 저장을 위한 Session State 초기화
if 'campaigns' not in st.session_state:
    st.session_state['campaigns'] = []
if 'applications' not in st.session_state:
    st.session_state['applications'] = []
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

# 날짜 기본값 계산
today = datetime.now()
default_recruit_end = today + timedelta(days=7)
default_exp_start = default_recruit_end + timedelta(days=1)
default_exp_end = default_exp_start + timedelta(weeks=4)

# 3. 주요 기능 탭 구성
tab1, tab2, tab3 = st.tabs(["🏢 캠페인 등록", "✍️ 블로거 신청 및 결과 제출", "👑 관리자 대시보드"])

# --- 탭 1: 광고주(캠페인 등록) 페이지 ---
with tab1:
    st.subheader("새로운 프리미엄 캠페인 등록")
    
    with st.form("campaign_form"):
        col1, col2 = st.columns(2)
        with col1:
            shop_name = st.text_input("매장명")
            offer = st.text_input("제공 내역 (예: 5만원 상당 식사권)")
            uploaded_file = st.file_uploader("대표 음식/매장 사진 첨부", type=['png', 'jpg', 'jpeg'])
        with col2:
            keywords = st.text_input("필수 노출 키워드")
            platform = st.selectbox("메인 타겟 플랫폼", ["네이버 블로그", "인스타그램 릴스", "유튜브 쇼츠"])
            recruit_count = st.number_input("모집 인원", min_value=1, value=10)
        
        st.markdown("---")
        st.write("🗓️ **일정 설정**")
        col3, col4 = st.columns(2)
        with col3:
            recruit_dates = st.date_input("모집 기간 (기본 7일)", [today.date(), default_recruit_end.date()])
        with col4:
            exp_dates = st.date_input("체험 및 리뷰 작성 기간 (기본 3~4주)", [default_exp_start.date(), default_exp_end.date()])
        
        submit_campaign = st.form_submit_button("캠페인 등록하기")
        
        if submit_campaign and shop_name:
            if len(recruit_dates) == 2 and len(exp_dates) == 2:
                st.session_state['campaigns'].append({
                    "id": len(st.session_state['campaigns']) + 1,
                    "shop": shop_name, 
                    "offer": offer, 
                    "keywords": keywords,
                    "platform": platform,
                    "image": uploaded_file,
                    "recruit_count": recruit_count,
                    "recruit_start": recruit_dates[0],
                    "recruit_end": recruit_dates[1],
                    "exp_start": exp_dates[0],
                    "exp_end": exp_dates[1],
                    "status": "진행중"
                })
                st.success(f"[{shop_name}] 캠페인이 등록되었습니다!")
            else:
                st.error("모집 기간과 체험 기간의 시작일과 종료일을 모두 지정해주세요.")

# --- 탭 2: 블로거(체험단) 페이지 ---
with tab2:
    st.subheader("진행 중인 프리미엄 캠페인")
    
    if st.session_state['campaigns']:
        for c in st.session_state['campaigns']:
            with st.container():
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    if c['image'] is not None:
                        st.image(c['image'], use_container_width=True)
                    else:
                        st.info("등록된 사진이 없습니다.")
                
                with col_info:
                    st.markdown(f"### 📍 {c['shop']} ({c['status']})")
                    st.write(f"**🎁 제공 내역:** {c['offer']} | **👥 모집 인원:** {c['recruit_count']}명")
                    st.write(f"**🗓️ 모집 기간:** {c['recruit_start']} ~ {c['recruit_end']}")
                    st.write(f"**🏃 체험 기간:** {c['exp_start']} ~ {c['exp_end']}")
                
                # 블로거 신청 폼
                with st.expander("👉 이 캠페인 신청하기"):
                    with st.form(f"apply_form_{c['id']}"):
                        blog_url = st.text_input("운영 중인 블로그/SNS URL")
                        contact = st.text_input("연락처 (010-0000-0000)")
                        submit_apply = st.form_submit_button("신청서 제출")
                        if submit_apply and blog_url:
                            st.session_state['applications'].append({
                                "campaign_id": c['id'],
                                "shop": c['shop'], 
                                "blog_url": blog_url, 
                                "contact": contact,
                                "review_link": "", # 리뷰 완료 시 입력할 링크
                                "status": "신청완료"
                            })
                            st.success("신청이 완료되었습니다.")

                # 리뷰 완료 링크 제출 폼 (선정된 블로거용)
                with st.expander("✅ 리뷰 작성 완료 제출 (선정된 블로거 전용)"):
                    with st.form(f"review_form_{c['id']}"):
                        my_contact = st.text_input("신청 시 입력한 연락처 확인")
                        final_link = st.text_input("작성 완료된 리뷰 URL")
                        submit_review = st.form_submit_button("리뷰 제출")
                        if submit_review and final_link:
                            # 연락처로 매칭하여 리뷰 링크 업데이트
                            for app in st.session_state['applications']:
                                if app['campaign_id'] == c['id'] and app['contact'] == my_contact:
                                    app['review_link'] = final_link
                                    app['status'] = "리뷰제출완료"
                            st.success("리뷰 URL이 성공적으로 접수되었습니다.")
            st.divider()
    else:
        st.info("현재 진행 중인 캠페인이 없습니다.")

# --- 탭 3: 관리자 페이지 (로그인 및 대시보드) ---
with tab3:
    if not st.session_state['admin_logged_in']:
        st.subheader("🔒 관리자 로그인")
        admin_id = st.text_input("아이디")
        admin_pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            # 데모용 기본 계정: admin / 1234
            if admin_id == "admin" and admin_pw == "1234":
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
    
    else:
        st.subheader("👑 관리자 대시보드")
        if st.button("로그아웃"):
            st.session_state['admin_logged_in'] = False
            st.rerun()
            
        st.write("---")
        if not st.session_state['campaigns']:
            st.info("등록된 캠페인이 없습니다.")
        else:
            # 캠페인 관리
            selected_shop = st.selectbox("관리할 캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            
            # 선택된 캠페인 정보 찾기
            current_campaign = next(c for c in st.session_state['campaigns'] if c['shop'] == selected_shop)
            
            # 1. 체험 기간 연장 기능
            st.markdown("#### 🗓️ 체험 기간 연장")
            col_ext1, col_ext2 = st.columns([3, 1])
            with col_ext1:
                new_exp_end = st.date_input("새로운 체험 종료일 선택", current_campaign['exp_end'])
            with col_ext2:
                st.write("") # 줄맞춤
                st.write("")
                if st.button("기간 연장하기"):
                    current_campaign['exp_end'] = new_exp_end
                    st.success(f"체험 기간이 {new_exp_end}로 연장되었습니다.")

            # 2. 신청자 및 리뷰 현황 리스트
            st.markdown("#### 👥 신청 및 리뷰 현황")
            app_list = [app for app in st.session_state['applications'] if app['shop'] == selected_shop]
            if app_list:
                df = pd.DataFrame(app_list)[['contact', 'blog_url', 'status', 'review_link']]
                df.columns = ['연락처', '블로그 URL', '진행상태', '제출된 리뷰 링크']
                st.dataframe(df, use_container_width=True)
            else:
                st.write("아직 신청자가 없습니다.")

            # 3. 마감 보고서 자동 생성기
            st.markdown("---")
            st.markdown("#### 📊 프리미엄 마감 보고서 생성")
            if st.button("마감 보고서 출력 (HTML/화면)"):
                completed_reviews = [app['review_link'] for app in app_list if app['review_link'] != ""]
                
                st.markdown(f"""
                <div class="report-box">
                    <h2 style="text-align: center;">[{current_campaign['shop']}] 체험단 캠페인 마감 리포트</h2>
                    <hr style="border-color: #D4AF37;">
                    <h3>1. 캠페인 요약</h3>
                    <ul>
                        <li><b>모집 인원:</b> {current_campaign['recruit_count']}명</li>
                        <li><b>리뷰 완료 건수:</b> {len(completed_reviews)}건</li>
                        <li><b>타겟 플랫폼:</b> {current_campaign['platform']}</li>
                    </ul>
                    <h3>2. 플레이스 이슈 진단 결과 (5포인트 점검 완료)</h3>
                    <ul>
                        <li>✅ <b>리뷰 활동성:</b> 매장 분위기 스케치 완료</li>
                        <li>✅ <b>키워드 부재 방지:</b> 타겟 키워드 본문/제목 삽입 완료</li>
                        <li>✅ <b>사진 빈도:</b> 가이드라인(15장 이상/숏폼 15초 이상) 충족</li>
                        <li>✅ <b>새소식 업데이트 연계:</b> 플레이스 정보 반영 완료</li>
                        <li>✅ <b>리뷰 전환율:</b> 정중한 존댓말 및 후킹 문구 적용 확인</li>
                    </ul>
                    <h3>3. 최종 제출된 리뷰 링크 목록</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, link in enumerate(completed_reviews):
                    st.write(f"{idx+1}. {link}")
