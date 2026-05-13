import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="위드멤버 프리미엄 체험단", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS (현재 사이트 화이트 톤에 맞춘 딥 블루 & 실버 테마)
st.markdown("""
<style>
    .stApp { background-color: #F4F7F6; color: #212529; font-family: 'Pretendard', sans-serif; }
    
    /* 매장명 타이틀 버튼: 화이트 톤에 잘 어울리는 딥 블루 테두리 & 실버 그레이 배경 */
    button[kind="tertiary"] { 
        background: #FFFFFF !important;
        border: 2px solid #4A90E2 !important;
        border-radius: 12px !important;
        padding: 10px 15px !important; 
        margin-bottom: 15px !important; 
        font-size: 1.1rem !important; 
        font-weight: 800 !important; 
        color: #4A90E2 !important; 
        justify-content: center !important; 
        box-shadow: 0 4px 6px rgba(74, 144, 226, 0.1) !important;
        width: 100% !important;
    }
    button[kind="tertiary"]:hover { 
        background: #4A90E2 !important; 
        color: #FFFFFF !important;
    }
    
    .card-box { background-color: #FFFFFF; padding: 18px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.04); border: 1px solid #EAECEF; }
    .badge-blog { background-color: #03C75A; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .badge-insta { background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .badge-yt { background-color: #FF0000; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    .offer-text { font-size: 0.95rem; color: #4A90E2; font-weight: 800; margin-top: 10px; }
    
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
    
    # 이미지 여러 장 보여주기 (슬라이더 대신 리스트 형태)
    if c.get('images'):
        cols = st.columns(len(c['images']))
        for i, img in enumerate(c['images']):
            with cols[i]:
                st.image(img, use_container_width=True)
    else:
        st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
        
    st.write(f"**🎁 제공 내역:** {c['offer']}")
    st.write(f"**🔑 필수 키워드:** {c['keywords']}")
    st.write(f"**🗓️ 모집:** {c['recruit_start']} ~ {c['recruit_end']} | **🏃 체험:** {c['exp_start']} ~ {c['exp_end']}")
    
    st.markdown("---")
    st.markdown("### 📝 리뷰 가이드라인")
    st.info(c.get('guideline', ''))
    
    tab_apply, tab_submit = st.tabs(["✍️ 신청하기", "✅ 리뷰 제출"])
    with tab_apply:
        with st.form(f"apply_{c['id']}"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                name, contact = st.text_input("이름"), st.text_input("연락처")
            with col_f2:
                blog_url, visitors = st.text_input("URL"), st.number_input("방문자수", min_value=0)
            if st.form_submit_button("제출"):
                st.session_state['applications'].append({
                    "campaign_id": c['id'], "shop": c['shop'], "name": name, "contact": contact, 
                    "blog_url": blog_url, "visitors": visitors, "review_link": "", "status": "신청완료"
                })
                st.success("신청되었습니다!")

# ==========================================
# 🔒 관리자 및 메인 로직
# ==========================================
with st.sidebar:
    if not st.session_state['admin_logged_in']:
        admin_id, admin_pw = st.text_input("ID"), st.text_input("PW", type="password")
        if st.button("로그인"):
            if admin_id == "admin" and admin_pw == "1234":
                st.session_state['admin_logged_in'] = True
                st.rerun()
    else:
        admin_menu = st.radio("메뉴", ["새 캠페인 등록", "캠페인 관리", "현황 대시보드"])
        if st.button("로그아웃"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

if not st.session_state['admin_logged_in']:
    # [블로거 메인 화면]
    st.markdown('<div style="width:100%; padding: 50px 20px; background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url(\'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=1200&auto=format&fit=crop\') center/cover; border-radius:20px; text-align:center; margin-bottom:40px;"><h1 style="color:white;">PREMIUM CAMPAIGN</h1><p style="color:#F1E5AC;">위드멤버 프리미엄 체험단</p></div>', unsafe_allow_html=True)
    
    if not st.session_state['campaigns']: st.info("모집 중인 캠페인이 없습니다.")
    else:
        cols = st.columns(4) 
        for idx, c in enumerate(st.session_state['campaigns']):
            with cols[idx % 4]: 
                with st.container(border=True):
                    if st.button(c['shop'], key=f"btn_{idx}", type="tertiary", use_container_width=True):
                        open_campaign_modal(c)
                    
                    if c.get('images'): st.image(c['images'][0], use_container_width=True)
                    else: st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
                    
                    st.markdown(f'<div class="offer-text">🎁 {c["offer"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-text">🗓️ 마감: {c["recruit_end"].strftime("%m.%d")}</div>', unsafe_allow_html=True)

else:
    if admin_menu == "새 캠페인 등록":
        st.title("🏢 새 캠페인 등록")
        with st.form("reg_form"):
            shop_name = st.text_input("매장명")
            offer = st.text_input("제공 내역")
            # [업데이트] 이미지 4장까지 첨부 가능
            uploaded_files = st.file_uploader("이미지 첨부 (최대 4장)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            keywords = st.text_input("필수 키워드")
            platform = st.selectbox("플랫폼", ["네이버 블로그", "인스타그램", "유튜브"])
            guideline = st.text_area("가이드라인", value="1. 플레이스 5대 진단 포인트 준수\n2. 정중한 존댓말 필수")
            
            if st.form_submit_button("등록 완료"):
                st.session_state['campaigns'].append({
                    "id": len(st.session_state['campaigns']), "shop": shop_name, "offer": offer,
                    "images": uploaded_files[:4], "keywords": keywords, "platform": platform,
                    "guideline": guideline, "recruit_start": today.date(), "recruit_end": default_recruit_end.date(),
                    "exp_start": default_exp_start.date(), "exp_end": default_exp_end.date()
                })
                st.success("등록되었습니다!")

    elif admin_menu == "현황 대시보드":
        st.title("📊 대시보드")
        selected_shop = st.selectbox("캠페인 선택", [c['shop'] for c in st.session_state['campaigns']])
        current_cam = next(c for c in st.session_state['campaigns'] if c['shop'] == selected_shop)
        apps = [a for a in st.session_state['applications'] if a['shop'] == selected_shop]
        
        st.dataframe(pd.DataFrame(apps), use_container_width=True)
        
        if st.button("📈 자동 마감 보고서 생성"):
            completed = [a['review_link'] for a in apps if a['review_link'] != ""]
            
            # [업데이트] 깔끔한 화이트 톤 이미지 캡처 보고서
            html_code = f"""
            <html>
            <head><script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script></head>
            <body>
                <div id="rpt" style="background:#FFF; padding:40px; border:1px solid #EEE; border-radius:15px; font-family:sans-serif;">
                    <h2 style="text-align:center; color:#1A1A1A;">[{selected_shop}] 마감 리포트</h2>
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
                            var a = document.createElement('a'); a.download = '리포트.png'; a.href = c.toDataURL(); a.click();
                        }});
                    }}
                </script>
            </body>
            </html>
            """
            components.html(html_code, height=600, scrolling=True)
