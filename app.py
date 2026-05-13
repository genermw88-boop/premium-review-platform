import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="위드멤버 프리미엄 체험단", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS (디자인 및 레이아웃)
st.markdown("""
<style>
    .stApp { background-color: #F4F7F6; color: #212529; font-family: 'Pretendard', sans-serif; }
    button[kind="tertiary"] { 
        background: #FFFFFF !important; border: 2px solid #4A90E2 !important; border-radius: 12px !important;
        padding: 10px 15px !important; margin-bottom: 10px !important; font-size: 1.1rem !important; 
        font-weight: 800 !important; color: #4A90E2 !important; justify-content: center !important; 
        box-shadow: 0 4px 6px rgba(74, 144, 226, 0.1) !important; width: 100% !important;
    }
    button[kind="tertiary"]:hover { background: #4A90E2 !important; color: #FFFFFF !important; }
    .card-box { background-color: #FFFFFF; padding: 18px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.04); border: 1px solid #EAECEF; }
    .badge-blog { background-color: #03C75A; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .badge-insta { background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .badge-yt { background-color: #FF0000; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .offer-text { font-size: 0.95rem; color: #4A90E2; font-weight: 800; margin-top: 10px; }
    .info-text { font-size: 0.85rem; color: #666666; margin-bottom: 4px; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #EAECEF; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 초기화
if 'campaigns' not in st.session_state: st.session_state['campaigns'] = []
if 'applications' not in st.session_state: st.session_state['applications'] = []
if 'admin_logged_in' not in st.session_state: st.session_state['admin_logged_in'] = False

today = datetime.now()
default_recruit_end = today + timedelta(days=7)
default_exp_start = default_recruit_end + timedelta(days=1)
default_exp_end = default_exp_start + timedelta(weeks=4)

# ==========================================
# 🎁 캠페인 상세 팝업창 (폭 확대 버전: Large)
# ==========================================
@st.dialog("✨ 캠페인 상세 정보 및 신청", width="large") 
def open_campaign_modal(c):
    st.markdown(f"## 📍 {c['shop']}")
    col_info_1, col_info_2 = st.columns([1, 1.2])
    
    with col_info_1:
        if c.get('images'):
            st.image(c['images'][0], use_container_width=True)
            if len(c['images']) > 1:
                cols = st.columns(len(c['images'])-1)
                for i, img in enumerate(c['images'][1:]):
                    with cols[i]: st.image(img, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
            
    with col_info_2:
        st.markdown(f"""
        **📍 지역:** {c.get('region', '전국')}  
        **🎁 제공 내역:** {c['offer']}  
        **🔑 필수 키워드:** {c['keywords']}  
        **🗓️ 모집 기간:** {c['recruit_start']} ~ {c['recruit_end']}  
        **🏃 체험 기간:** {c['exp_start']} ~ {c['exp_end']}  
        **👥 모집 인원:** {c['recruit_count']}명  
        """)
        st.markdown("---")
        st.markdown("### 📝 리뷰 가이드라인")
        st.info(c.get('guideline', ''))
    
    st.markdown("---")
    tab_apply, tab_submit = st.tabs(["✍️ 체험단 신청하기", "✅ 리뷰 제출 (선정자)"])
    
    with tab_apply:
        with st.form(f"apply_form_{c['id']}"):
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                name = st.text_input("성함 (실명)")
                contact = st.text_input("연락처 (- 없이)")
                address = st.text_input("거주 지역 (예: 서울 강남구)") 
            with fcol2:
                blog_url = st.text_input("SNS/블로그 URL")
                visitors = st.number_input("일 평균 방문자 수", min_value=0)
            if st.form_submit_button("신청 완료"):
                if name and contact and blog_url:
                    st.session_state['applications'].append({
                        "campaign_id": c['id'], "shop": c['shop'], "name": name, 
                        "contact": contact, "address": address, "blog_url": blog_url, 
                        "visitors": visitors, "review_link": "", "status": "신청완료"
                    })
                    st.success("신청이 완료되었습니다!")
                else:
                    st.error("성함, 연락처, URL은 필수 항목입니다.")

    with tab_submit:
        with st.form(f"submit_form_{c['id']}"):
            st.write("#### 리뷰 포스팅 제출")
            fcol3, fcol4 = st.columns(2)
            with fcol3: s_name = st.text_input("신청자 성함 확인")
            with fcol4: s_contact = st.text_input("신청자 연락처 확인 (- 없이)")
            s_link = st.text_input("작성한 리뷰 포스팅 URL")
            
            if st.form_submit_button("리뷰 제출하기"):
                submitted = False
                for app in st.session_state['applications']:
                    if app['campaign_id'] == c['id'] and app['name'] == s_name and app['contact'] == s_contact:
                        app['review_link'] = s_link
                        app['status'] = "리뷰제출완료"
                        submitted = True
                if submitted: st.success("리뷰가 정상적으로 제출되었습니다.")
                else: st.error("일치하는 신청 내역이 없습니다. 성함과 연락처를 확인해주세요.")

# ==========================================
# 🔒 관리자 및 메인 로직
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

if not st.session_state['admin_logged_in']:
    # [블로거 메인 화면]
    st.markdown('<div style="width:100%; padding: 50px 20px; background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url(\'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=1200&auto=format&fit=crop\') center/cover; border-radius:20px; text-align:center; margin-bottom:20px;"><h1 style="color:white;">PREMIUM CAMPAIGN</h1><p style="color:#F1E5AC;">위드멤버 프리미엄 체험단</p></div>', unsafe_allow_html=True)
    
    # [해결 1] 지역 및 매장명 검색창 추가
    search_query = st.text_input("🔍 지역 또는 매장명 검색", placeholder="예: 강남, 홍대, 혹은 특정 매장명 입력")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 검색 필터링 로직
    filtered_campaigns = []
    for c in st.session_state['campaigns']:
        target_text = c['shop'] + " " + c['keywords'] + " " + c.get('region', '')
        if not search_query or search_query.lower() in target_text.lower():
            filtered_campaigns.append(c)
    
    if not filtered_campaigns: 
        st.info("조건에 맞는 캠페인이 없습니다. 다른 키워드로 검색해보세요.")
    else:
        cols = st.columns(4) 
        for idx, c in enumerate(filtered_campaigns):
            with cols[idx % 4]: 
                with st.container(border=True):
                    if st.button(c['shop'], key=f"btn_{c['id']}", type="tertiary", use_container_width=True):
                        open_campaign_modal(c)
                    
                    if c.get('images'): st.image(c['images'][0], use_container_width=True)
                    else: st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
                    
                    st.markdown(f'<div class="info-text" style="margin-top:10px; font-weight:bold;">📍 {c.get("region", "전국")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="offer-text" style="margin-top:2px;">🎁 {c["offer"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-text">🗓️ 마감: {c["recruit_end"].strftime("%m.%d")}</div>', unsafe_allow_html=True)

else:
    # [관리자 전용 화면]
    if admin_menu == "새 캠페인 등록":
        st.title("🏢 새 캠페인 등록")
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            with col1:
                shop_name = st.text_input("매장명")
                # [해결 2] 캠페인 등록 시 지역 입력란 추가
                region = st.text_input("지역 (예: 서울 강남구)") 
                offer = st.text_input("제공 내역")
                uploaded_files = st.file_uploader("이미지 첨부 (최대 4장)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            with col2:
                keywords = st.text_input("필수 키워드")
                platform = st.selectbox("플랫폼", ["네이버 블로그", "인스타그램", "유튜브"])
                recruit_count = st.number_input("블로거 모집 인원", min_value=1, value=10)
            
            guideline = st.text_area("가이드라인", value="1. 플레이스 5대 진단 포인트 준수\n2. 정중한 존댓말 필수")
            dcol1, dcol2 = st.columns(2)
            with dcol1: recruit_dates = st.date_input("모집 기간", [today.date(), default_recruit_end.date()])
            with dcol2: exp_dates = st.date_input("체험 기간", [default_exp_start.date(), default_exp_end.date()])
            
            if st.form_submit_button("등록 완료"):
                if shop_name and len(recruit_dates) == 2 and len(exp_dates) == 2:
                    st.session_state['campaigns'].append({
                        "id": len(st.session_state['campaigns']), "shop": shop_name, "region": region, 
                        "offer": offer, "images": uploaded_files[:4], "keywords": keywords, "platform": platform,
                        "recruit_count": recruit_count, "guideline": guideline,
                        "recruit_start": recruit_dates[0], "recruit_end": recruit_dates[1],
                        "exp_start": exp_dates[0], "exp_end": exp_dates[1], "status": "진행중"
                    })
                    st.success("성공적으로 등록되었습니다!")

    elif admin_menu == "캠페인 관리(수정/삭제)":
        st.title("🛠️ 캠페인 관리")
        if not st.session_state['campaigns']: st.info("등록된 캠페인이 없습니다.")
        else:
            selected_shop = st.selectbox("관리할 캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            idx = next(i for i, c in enumerate(st.session_state['campaigns']) if c['shop'] == selected_shop)
            c = st.session_state['campaigns'][idx]
            
            if st.button("❌ 이 캠페인 완전 삭제", type="primary"):
                st.session_state['campaigns'].pop(idx)
                st.rerun()
                
            with st.form("edit_form"):
                st.write("### 캠페인 내용 수정")
                edit_region = st.text_input("지역 수정", value=c.get('region', ''))
                edit_offer = st.text_input("제공 내역 수정", value=c['offer'])
                edit_keywords = st.text_input("키워드 수정", value=c['keywords'])
                edit_recruit = st.number_input("모집 인원 수정", value=int(c['recruit_count']))
                edit_guide = st.text_area("가이드라인 수정", value=c['guideline'])
                if st.form_submit_button("수정 내용 저장"):
                    st.session_state['campaigns'][idx].update({"region": edit_region, "offer": edit_offer, "keywords": edit_keywords, "recruit_count": edit_recruit, "guideline": edit_guide})
                    st.success("수정이 완료되었습니다!")

    elif admin_menu == "현황 대시보드":
        st.title("📊 현황 대시보드")
        if not st.session_state['campaigns']:
            st.info("등록된 캠페인이 없습니다.")
        else:
            selected_shop = st.selectbox("캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            current_cam = next(c for c in st.session_state['campaigns'] if c['shop'] == selected_shop)
            apps = [a for a in st.session_state['applications'] if a['shop'] == selected_shop]
            
            # [해결 3] 대기 명단과 선정 명단을 분리하는 탭 생성
            tab_pending, tab_approved = st.tabs(["⏳ 대기 중인 신청자 및 선정", "🎉 선정된 블로거 명단"])
            
            with tab_pending:
                pending_apps = [a for a in apps if a['status'] == "신청완료"]
                if pending_apps:
                    table_data_p = []
                    for i, app in enumerate(pending_apps):
                        visitors = int(app.get('visitors', 0))
                        grade = "고급" if visitors >= 500 else "중급" if visitors >= 100 else "초급"
                        table_data_p.append({
                            "이름": app.get('name', ''), "계정URL": app.get('blog_url', ''), 
                            "등급": grade, "일 방문": f"{visitors:,}", "연락처": app.get('contact', ''),
                            "주소(지역)": app.get('address', ''), "상태": app['status']
                        })
                    st.dataframe(pd.DataFrame(table_data_p), column_config={"계정URL": st.column_config.LinkColumn("계정URL")}, hide_index=True, use_container_width=True)
                    
                    st.markdown("#### ✅ 블로거 선정 처리")
                    options = [f"{a['name']} ({a['blog_url']})" for a in pending_apps]
                    selected_to_approve = st.multiselect("선정할 블로거를 모두 선택하세요", options)
                    if st.button("선택 인원 선정 완료 처리"):
                        if selected_to_approve:
                            for app in st.session_state['applications']:
                                app_display = f"{app['name']} ({app['blog_url']})"
                                if app['shop'] == selected_shop and app['status'] == "신청완료" and app_display in selected_to_approve:
                                    app['status'] = "선정완료"
                            st.success("선택한 블로거들이 성공적으로 '선정완료' 상태로 변경되었습니다!")
                            st.rerun()
                        else:
                            st.warning("선정할 블로거를 선택해주세요.")
                else:
                    st.info("현재 대기 중인(신청완료) 블로거가 없습니다.")

            with tab_approved:
                approved_apps = [a for a in apps if a['status'] in ["선정완료", "리뷰제출완료"]]
                if approved_apps:
                    table_data_a = []
                    for i, app in enumerate(approved_apps):
                        visitors = int(app.get('visitors', 0))
                        grade = "고급" if visitors >= 500 else "중급" if visitors >= 100 else "초급"
                        submitted_link = app.get('review_link', '')
                        table_data_a.append({
                            "이름": app.get('name', ''), "계정URL": app.get('blog_url', ''), 
                            "등급": grade, "일 방문": f"{visitors:,}", "연락처": app.get('contact', ''),
                            "주소(지역)": app.get('address', ''), "상태": app['status'],
                            "제출된 링크": submitted_link if submitted_link else "미제출"
                        })
                    st.dataframe(pd.DataFrame(table_data_a), column_config={"계정URL": st.column_config.LinkColumn("계정URL"), "제출된 링크": st.column_config.LinkColumn("제출된 링크")}, hide_index=True, use_container_width=True)
                else:
                    st.info("아직 이 캠페인에 선정된 블로거가 없습니다.")
            
            # 마감 리포트
            st.markdown("---")
            if st.button("📈 자동 마감 보고서 생성"):
                completed = [a['review_link'] for a in apps if a['review_link'] != ""]
                html_code = f"""
                <html>
                <head><script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script></head>
                <body>
                    <div id="rpt" style="background:#FFF; padding:40px; border:1px solid #EEE; border-radius:15px;">
                        <h2 style="text-align:center;">[{selected_shop}] 마감 리포트</h2>
                        <hr style="border:1px solid #4A90E2;">
                        <p><b>매장명:</b> {selected_shop} | <b>키워드:</b> {current_cam['keywords']}</p>
                        <p><b>결과:</b> 총 {len(completed)}건 포스팅 완료</p>
                        <div style="background:#F8F9FA; padding:15px; border-radius:10px;">
                            <b>마감 총평:</b> 본 캠페인은 목표한 키워드 노출과 플레이스 활성화를 위해 가이드라인에 맞춰 정성스럽게 작성되었습니다.
                        </div>
                        <h4>발행 링크 취합</h4>
                        {"".join([f"<div>{idx+1}. {l}</div>" for idx, l in enumerate(completed)])}
                    </div>
                    <button onclick="saveImg()" style="width:100%; margin-top:20px; padding:15px; background:#4A90E2; color:white; border:none; border-radius:10px; cursor:pointer;">📸 보고서 이미지로 다운로드</button>
                    <script>
                        function saveImg() {{
                            html2canvas(document.getElementById('rpt'), {{scale:2}}).then(c => {{
                                var a = document.createElement('a'); a.download = '{selected_shop}_마감리포트.png'; a.href = c.toDataURL(); a.click();
                            }});
                        }}
                    </script>
                </body>
                </html>
                """
                components.html(html_code, height=700, scrolling=True)
