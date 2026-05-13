import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="위드멤버 프리미엄 체험단", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 
st.markdown("""
<style>
    .stApp { background-color: #F4F7F6; color: #212529; font-family: 'Pretendard', sans-serif; }
    .card-box { background-color: #FFFFFF; padding: 18px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.04); margin-bottom: 25px; border: 1px solid #EAECEF; transition: all 0.3s; }
    .card-box:hover { transform: translateY(-7px); box-shadow: 0 15px 35px rgba(0,0,0,0.08); }
    .badge-blog { background-color: #03C75A; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .badge-insta { background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .badge-yt { background-color: #FF0000; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .offer-text { font-size: 0.95rem; color: #4A90E2; font-weight: 800; margin-top: 5px; margin-bottom: 5px; }
    .info-text { font-size: 0.85rem; color: #666666; margin-bottom: 4px; }
    button[kind="tertiary"] { justify-content: flex-start !important; padding: 0px !important; margin-top: 10px !important; font-size: 1.25rem !important; font-weight: 900 !important; color: #1A1A1A !important; }
    button[kind="tertiary"]:hover { color: #4A90E2 !important; background-color: transparent !important; }
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
# 🎁 캠페인 상세 팝업창 (Modal)
# ==========================================
@st.dialog("✨ 캠페인 상세 정보 및 신청")
def open_campaign_modal(c):
    st.markdown(f"## 📍 {c['shop']}")
    col_img, col_info = st.columns([1, 1.5])
    with col_img:
        if c['image']: st.image(c['image'], use_container_width=True)
        else: st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
    with col_info:
        st.write(f"**🎁 제공 내역:** {c['offer']}")
        st.write(f"**🔑 필수 키워드:** {c['keywords']}")
        st.write(f"**🗓️ 모집 기간:** {c['recruit_start']} ~ {c['recruit_end']}")
        st.write(f"**🏃 체험 기간:** {c['exp_start']} ~ {c['exp_end']}")
        st.write(f"**👥 모집 인원:** {c['recruit_count']}명 ({c['platform']})")
    
    st.markdown("---")
    st.markdown("### 📝 리뷰 가이드라인")
    st.info(c.get('guideline', '등록된 가이드라인이 없습니다.'))
    
    tab_apply, tab_submit = st.tabs(["✍️ 체험단 신청하기", "✅ 리뷰 링크 제출(선정자)"])
    with tab_apply:
        with st.form(f"modal_apply_{c['id']}"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                name = st.text_input("이름 (실명)")
                contact = st.text_input("연락처 (- 없이)")
                address = st.text_input("거주 지역 (예: 서울 광진구)")
            with col_f2:
                blog_url = st.text_input("운영 채널 URL")
                visitors = st.number_input("일 평균 방문자 수", min_value=0, step=50)
            if st.form_submit_button("신청서 제출 완료"):
                if name and contact and blog_url:
                    st.session_state['applications'].append({
                        "campaign_id": c['id'], "shop": c['shop'], "name": name, "contact": contact, 
                        "address": address, "blog_url": blog_url, "visitors": visitors,
                        "review_link": "", "status": "신청완료"
                    })
                    st.success("신청이 완료되었습니다! 창을 닫아주세요.")
                else: st.error("이름, 연락처, 채널 URL은 필수 입력입니다.")
                    
    with tab_submit:
        with st.form(f"modal_submit_{c['id']}"):
            my_name = st.text_input("신청 시 이름")
            my_contact = st.text_input("신청 시 연락처")
            final_link = st.text_input("리뷰 URL (포스팅 링크)")
            if st.form_submit_button("리뷰 제출 완료"):
                submitted = False
                for app in st.session_state['applications']:
                    if app['campaign_id'] == c['id'] and app['name'] == my_name and app['contact'] == my_contact:
                        app['review_link'] = final_link
                        app['status'] = "리뷰제출완료"
                        submitted = True
                if submitted: st.success("리뷰 URL이 접수되었습니다! 창을 닫아주세요.")
                else: st.error("일치하는 신청 내역이 없습니다.")

# ==========================================
# 🔒 관리자 사이드바
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
            else: st.error("정보가 일치하지 않습니다.")
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
    st.markdown("""
        <div style="width:100%; padding: 50px 20px; background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=1200&auto=format&fit=crop') center/cover; border-radius:20px; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:40px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h1 style="color:#FFFFFF; margin:0; font-size:2.8rem; font-weight:900; letter-spacing: -1px;">PREMIUM CAMPAIGN</h1>
            <p style="color:#F1E5AC; margin-top:10px; font-size:1.15rem; font-weight:bold;">상위 10% 리뷰어를 위한 프라이빗 매칭 플랫폼</p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state['campaigns']: st.info("현재 모집 중인 캠페인이 없습니다.")
    else:
        cols = st.columns(4) 
        for idx, c in enumerate(st.session_state['campaigns']):
            with cols[idx % 4]: 
                st.markdown('<div class="card-box">', unsafe_allow_html=True)
                if c['image']: st.image(c['image'], use_container_width=True)
                else: st.markdown('<div style="height:200px; background:#F1F3F5; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#ADB5BD; font-weight:bold;">이미지 준비중</div>', unsafe_allow_html=True)
                
                badge_class = "badge-blog"
                if "인스타" in c['platform']: badge_class = "badge-insta"
                elif "유튜브" in c['platform']: badge_class = "badge-yt"
                st.markdown(f'<div style="margin-top:12px;"><span class="{badge_class}">{c["platform"]}</span></div>', unsafe_allow_html=True)
                
                if st.button(c['shop'], key=f"title_btn_{c['id']}", type="tertiary", use_container_width=True):
                    open_campaign_modal(c)
                
                st.markdown(f'<div class="offer-text">🎁 {c["offer"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text">🗓️ 마감: {c["recruit_end"].strftime("%m.%d")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text" style="color:#adb5bd; font-size:0.7rem;">👆 매장명을 클릭하면 신청창이 열립니다.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

else:
    if admin_menu == "새 캠페인 등록":
        st.title("🏢 새 캠페인 등록")
        with st.form("campaign_form"):
            col1, col2 = st.columns(2)
            with col1:
                shop_name = st.text_input("매장명")
                offer = st.text_input("제공 내역")
                uploaded_file = st.file_uploader("대표 이미지", type=['png', 'jpg', 'jpeg'])
            with col2:
                keywords = st.text_input("필수 노출 키워드")
                platform = st.selectbox("메인 타겟 플랫폼", ["네이버 블로그", "인스타그램 릴스", "유튜브 쇼츠"])
                recruit_count = st.number_input("모집 인원", min_value=1, value=10)
            
            default_guideline = """1. 리뷰 활동성: 매장 분위기 스케치
2. 키워드 부재 방지: 타겟 키워드 본문/제목 삽입
3. 사진 빈도: 충분한 매장/메뉴 사진 첨부
4. 새소식 업데이트 연계: 플레이스 새소식 언급
5. 리뷰 전환율: 잠재 고객 방문 유도를 위한 정중한 존댓말 필수 사용"""
            st.write("---")
            guideline = st.text_area("📝 리뷰 가이드라인", value=default_guideline, height=150)
            col3, col4 = st.columns(2)
            with col3: recruit_dates = st.date_input("모집 기간", [today.date(), default_recruit_end.date()])
            with col4: exp_dates = st.date_input("체험 기간", [default_exp_start.date(), default_exp_end.date()])
            
            if st.form_submit_button("캠페인 등록 완료"):
                if shop_name and len(recruit_dates) == 2 and len(exp_dates) == 2:
                    st.session_state['campaigns'].append({
                        "id": len(st.session_state['campaigns']) + 1, "shop": shop_name, 
                        "offer": offer, "keywords": keywords, "platform": platform,
                        "image": uploaded_file, "recruit_count": recruit_count,
                        "guideline": guideline, "recruit_start": recruit_dates[0], "recruit_end": recruit_dates[1],
                        "exp_start": exp_dates[0], "exp_end": exp_dates[1], "status": "진행중"
                    })
                    st.success("새로운 캠페인이 등록되었습니다!")

    elif admin_menu == "캠페인 관리(수정/삭제)":
        st.title("🛠️ 캠페인 관리 (수정 및 삭제)")
        if not st.session_state['campaigns']: st.info("등록된 캠페인이 없습니다.")
        else:
            selected_shop = st.selectbox("수정/삭제할 캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            idx = next(i for i, c in enumerate(st.session_state['campaigns']) if c['shop'] == selected_shop)
            c = st.session_state['campaigns'][idx]
            col_del1, col_del2 = st.columns([4, 1])
            with col_del2:
                if st.button("❌ 완전 삭제", type="primary"):
                    st.session_state['campaigns'].pop(idx)
                    st.rerun()

            with st.form("edit_form"):
                st.write("### 캠페인 내용 수정")
                new_offer = st.text_input("제공 내역 수정", value=c['offer'])
                new_keywords = st.text_input("키워드 수정", value=c['keywords'])
                new_recruit_count = st.number_input("모집 인원 수정", min_value=1, value=int(c['recruit_count']))
                new_guideline = st.text_area("가이드라인 수정", value=c.get('guideline', ''))
                if st.form_submit_button("수정 내용 저장"):
                    st.session_state['campaigns'][idx]['offer'] = new_offer
                    st.session_state['campaigns'][idx]['keywords'] = new_keywords
                    st.session_state['campaigns'][idx]['recruit_count'] = new_recruit_count
                    st.session_state['campaigns'][idx]['guideline'] = new_guideline
                    st.success("수정 사항이 성공적으로 저장되었습니다.")

    elif admin_menu == "현황 대시보드":
        st.title("📊 캠페인 신청자 현황 대시보드")
        if not st.session_state['campaigns']: st.info("등록된 캠페인이 없습니다.")
        else:
            selected_shop = st.selectbox("조회할 캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
            current_campaign = next(c for c in st.session_state['campaigns'] if c['shop'] == selected_shop)
            app_list = [app for app in st.session_state['applications'] if app['shop'] == selected_shop]
            
            if app_list:
                table_data = []
                for i, app in enumerate(app_list):
                    visitors = int(app.get('visitors', 0))
                    if visitors >= 500: grade = "고급"
                    elif visitors >= 100: grade = "중급"
                    else: grade = "초급"
                    submitted_link = app.get('review_link', '')
                    link_status = submitted_link if submitted_link != "" else "미제출"
                    eval_status = "평가완료" if submitted_link != "" else "대기중"
                    table_data.append({
                        "번호": i + 1, "계정URL": app.get('blog_url', ''), "이름": app.get('name', ''),
                        "등급": grade, "일 방문": f"{visitors:,}", "연락처": app.get('contact', ''),
                        "주소": app.get('address', ''), "링크주소": link_status,
                        "첨부자료": "자료없음", "평가": eval_status
                    })
                df = pd.DataFrame(table_data)
                st.dataframe(df, column_config={"계정URL": st.column_config.LinkColumn("계정URL"), "링크주소": st.column_config.LinkColumn("링크주소")}, hide_index=True, use_container_width=True)
            else: st.write("아직 이 캠페인에 신청한 블로거가 없습니다.")
            
            st.markdown("---")
            if st.button("📈 자동 마감 보고서 출력"):
                completed = [app['review_link'] for app in app_list if app['review_link'] != ""]
                keywords = current_campaign['keywords']
                target_count = current_campaign['recruit_count']
                completed_count = len(completed)
                
                eval_comment = f"본 캠페인은 목표 인원 {target_count}명 중 <b>{completed_count}명</b>의 검증된 리뷰어가 참여하여 성공적으로 포스팅을 완료했습니다. 전달해주신 메인 키워드 <b>'{keywords}'</b>를 중심으로 검색 노출이 최적화될 수 있도록 가이드되었으며, 리뷰 내 정중한 존댓말과 후킹 문구를 배치하여 네이버 플레이스 방문 전환율을 효과적으로 높일 수 있도록 세팅되었습니다."

                # HTML 코드의 띄어쓰기를 없애 오류를 완벽히 차단했습니다.
                report_html = f"""<div style="background-color:#FFFFFF; color:#212529; padding:40px; border-radius:12px; border:1px solid #EAECEF; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top:20px; font-family:'Pretendard', sans-serif;">
<div style="text-align:center; margin-bottom: 30px;">
<h2 style="color:#1A1A1A; font-weight:900; margin-bottom:5px;">[{selected_shop}] 캠페인 최종 마감 리포트</h2>
<p style="color:#868E96; font-size:0.9rem; margin-top:0;">위드멤버 프리미엄 체험단 마케팅 결과 보고</p>
</div>
<hr style="border: 0; border-top: 2px solid #4A90E2; margin-bottom: 30px;">
<h4 style="color:#2C3E50; border-left: 4px solid #4A90E2; padding-left: 10px; margin-bottom:15px;">1. 캠페인 종합 요약</h4>
<ul style="background-color:#F8F9FA; padding:20px 20px 20px 40px; border-radius:8px; line-height:1.8; color:#495057; font-size:0.95rem;">
<li><b>진행 매장명:</b> {selected_shop}</li>
<li><b>타겟 키워드:</b> <span style="color:#4A90E2; font-weight:bold;">{keywords}</span></li>
<li><b>리뷰 달성률:</b> 총 {completed_count}건 포스팅 완료 (목표 {target_count}명)</li>
</ul>
<h4 style="color:#2C3E50; border-left: 4px solid #4A90E2; padding-left: 10px; margin-top: 30px; margin-bottom:15px;">2. 마감 종합 평가 및 기대 효과</h4>
<div style="background-color:#F0F4F8; padding:20px; border-radius:8px; color:#333; line-height:1.6; font-size:0.95rem;">
{eval_comment}
</div>
<h4 style="color:#2C3E50; border-left: 4px solid #4A90E2; padding-left: 10px; margin-top: 30px; margin-bottom:15px;">3. 발행된 리뷰 링크 취합</h4>
<div style="padding-left:10px; line-height:1.8; font-size:0.95rem;">"""
                
                if len(completed) > 0:
                    for idx, link in enumerate(completed):
                        report_html += f"<div><b>{idx+1}.</b> <a href='{link}' target='_blank' style='color:#4A90E2; text-decoration:none;'>{link}</a></div>"
                else:
                    report_html += "<div style='color:#868E96;'>아직 제출된 리뷰 포스팅이 없습니다.</div>"
                
                report_html += "</div></div>"
                
                st.markdown(report_html, unsafe_allow_html=True)
