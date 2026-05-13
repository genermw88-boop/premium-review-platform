import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import json
import os
import base64
import random

# ==========================================
# 💾 자동 저장 데이터베이스 세팅 
# ==========================================
DATA_FILE = "reviewus_db.json"
OLD_DATA_FILE = "withmember_db.json"

def load_data():
    camps, apps = [], []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                camps = data.get('campaigns', [])
                apps = data.get('applications', [])
        except: pass
        
    if not camps and os.path.exists(OLD_DATA_FILE):
        try:
            with open(OLD_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                camps = data.get('campaigns', [])
                apps = data.get('applications', [])
        except: pass
        
    for c in camps:
        if isinstance(c.get('recruit_start'), str): c['recruit_start'] = datetime.strptime(c['recruit_start'], "%Y-%m-%d").date()
        if isinstance(c.get('recruit_end'), str): c['recruit_end'] = datetime.strptime(c['recruit_end'], "%Y-%m-%d").date()
        if isinstance(c.get('exp_start'), str): c['exp_start'] = datetime.strptime(c['exp_start'], "%Y-%m-%d").date()
        if isinstance(c.get('exp_end'), str): c['exp_end'] = datetime.strptime(c['exp_end'], "%Y-%m-%d").date()
        if 'category' not in c: c['category'] = '체험단'
            
    return camps, apps

def save_data(campaigns, applications):
    camps_to_save = []
    for c in campaigns:
        c_copy = c.copy()
        c_copy['recruit_start'] = c_copy['recruit_start'].strftime("%Y-%m-%d")
        c_copy['recruit_end'] = c_copy['recruit_end'].strftime("%Y-%m-%d")
        c_copy['exp_start'] = c_copy['exp_start'].strftime("%Y-%m-%d")
        c_copy['exp_end'] = c_copy['exp_end'].strftime("%Y-%m-%d")
        camps_to_save.append(c_copy)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({'campaigns': camps_to_save, 'applications': applications}, f, ensure_ascii=False)

def display_b64_image(b64_str):
    st.image(base64.b64decode(b64_str), use_container_width=True)

# 1. 페이지 설정
st.set_page_config(page_title="리뷰어스 프리미엄 체험단", layout="wide", initial_sidebar_state="collapsed")

# 2. 기본 CSS 세팅
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #212529; font-family: 'Pretendard', sans-serif; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important; border: 1px solid #EBEFEF !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.04) !important; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        background-color: #FFFFFF !important; padding: 18px 15px !important; margin-bottom: 20px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #4A90E2 !important; box-shadow: 0 16px 32px rgba(74, 144, 226, 0.12) !important; transform: translateY(-6px) !important;
    }
    [data-testid="stImage"] img { border-radius: 14px !important; object-fit: cover !important; }

    button[kind="tertiary"] { 
        background: #FFFFFF !important; 
        border: 2px solid #1A237E !important; 
        border-radius: 12px !important;
        padding: 10px 10px !important; 
        margin-bottom: 15px !important; 
        justify-content: center !important; 
        text-align: center !important; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important; 
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[kind="tertiary"] p, button[kind="tertiary"] span, button[kind="tertiary"] div {
        font-size: 1.25rem !important; 
        font-weight: 900 !important; 
        color: #1A237E !important; 
        letter-spacing: -0.5px !important; 
        margin: 0 !important;
        transition: color 0.2s ease-in-out !important;
    }
    button[kind="tertiary"]:hover { 
        background: #1A237E !important; 
        border-color: #1A237E !important;
    }
    button[kind="tertiary"]:hover p, button[kind="tertiary"]:hover span, button[kind="tertiary"]:hover div { 
        color: #FFFFFF !important; 
    }
    
    .badge-exp { background-color: #8E44AD; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; margin-right: 4px; box-shadow: 0 2px 4px rgba(142,68,173,0.2); }
    .badge-clip { background-color: #00C73C; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; margin-right: 4px; box-shadow: 0 2px 4px rgba(0,199,60,0.2); }
    .badge-press { background-color: #34495E; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; margin-right: 4px; box-shadow: 0 2px 4px rgba(52,73,94,0.2); }
    
    .d-day-badge { background-color: #E74C3C; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; margin-left: 2px; }
    .offer-text { font-size: 0.95rem; color: #2980B9; font-weight: 800; margin-top: 5px; }
    .app-count-text { font-size: 0.85rem; color: #555; margin-top: 12px; font-weight: 500; border-top: 1px dashed #EAECEF; padding-top: 10px; }
    
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #EAECEF; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로딩
if 'data_loaded' not in st.session_state:
    camps, apps = load_data()
    st.session_state['campaigns'] = camps
    st.session_state['applications'] = apps
    st.session_state['admin_logged_in'] = False
    st.session_state['data_loaded'] = True
    if camps: save_data(camps, apps)

today_date = datetime.now().date()
default_recruit_end = today_date + timedelta(days=7)
default_exp_start = default_recruit_end + timedelta(days=1)
default_exp_end = default_exp_start + timedelta(weeks=4)

# ==========================================
# 🎁 캠페인 상세 팝업창 
# ==========================================
@st.dialog("✨ 리뷰어스 상세 정보 및 신청", width="large") 
def open_campaign_modal(c):
    st.markdown(f"## 📍 {c['shop']}")
    col_info_1, col_info_2 = st.columns([1, 1.2])
    
    with col_info_1:
        if c.get('images'):
            display_b64_image(c['images'][0])
            if len(c['images']) > 1:
                cols = st.columns(len(c['images'])-1)
                for i, img_b64 in enumerate(c['images'][1:]):
                    with cols[i]: display_b64_image(img_b64)
        else:
            st.image("https://via.placeholder.com/300x300.png?text=No+Image", use_container_width=True)
            
    with col_info_2:
        place_link_html = f"<a href='{c.get('place_link', '#')}' target='_blank' style='color:#2980B9; text-decoration:underline; font-weight:900;'>👉 플레이스 바로가기</a>" if c.get('place_link') else "<span style='color:#999;'>등록된 링크가 없습니다.</span>"
        
        extend_days = c.get('exp_extend_days', 0)
        exp_start_val = c['exp_start']
        exp_end_val = c['exp_end']
        
        if extend_days > 0:
            if isinstance(exp_end_val, str): base_end_date = datetime.strptime(exp_end_val, "%Y-%m-%d").date()
            else: base_end_date = exp_end_val
            final_end_date = base_end_date + timedelta(days=extend_days)
            exp_period_display = f"{exp_start_val} ~ {exp_end_val} <span style='color:#E74C3C; font-weight:900;'>(🚨 {extend_days}일 연장됨 👉 {final_end_date.strftime('%Y-%m-%d')})</span>"
        else:
            exp_period_display = f"{exp_start_val} ~ {exp_end_val}"
            
        details_html = f"""
        <div style="font-size: 1.05rem; line-height: 2.1; color: #2C3E50; padding: 10px 0;">
            <div style="margin-bottom: 4px;"><b>📍 지 역 :</b> <span style="font-weight:700; color:#111;">{c.get('region', '전국')}</span></div>
            <div style="margin-bottom: 4px;"><b>🏷️ 분 류 :</b> <span style="font-weight:800; color:#8E44AD;">{c.get('category', '체험단')}</span></div>
            <div style="margin-bottom: 4px;"><b>🔗 매장 링크 :</b> {place_link_html}</div>
            <div style="margin-bottom: 4px;"><b>🎁 제공 내역 :</b> <span style="font-weight:900; color:#E74C3C; font-size:1.1rem;">{c['offer']}</span></div>
            <div style="margin-bottom: 4px;"><b>🔑 필수 키워드 :</b> <span style="font-weight:700; color:#111;">{c['keywords']}</span></div>
            <div style="margin-bottom: 4px;"><b>🗓️ 모집 기간 :</b> <span style="font-weight:700; color:#111;">{c['recruit_start']} ~ {c['recruit_end']}</span></div>
            <div style="margin-bottom: 4px;"><b>🏃 체험 기간 :</b> <span style="font-weight:700; color:#111;">{exp_period_display}</span></div>
            <div style="margin-bottom: 4px;"><b>👥 모집 인원 :</b> <span style="font-weight:900; color:#2980B9;">{c['recruit_count']}명</span></div>
        </div>
        """
        st.markdown(details_html, unsafe_allow_html=True)
        
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
                    save_data(st.session_state['campaigns'], st.session_state['applications'])
                    st.success("신청이 완료되었습니다!")
                else: st.error("성함, 연락처, URL은 필수 항목입니다.")

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
                if submitted: 
                    save_data(st.session_state['campaigns'], st.session_state['applications'])
                    st.success("리뷰가 정상적으로 제출되었습니다.")
                else: st.error("일치하는 신청 내역이 없습니다. 성함과 연락처를 확인해주세요.")

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
        st.markdown("### 👑 리뷰어스 관리자")
        admin_menu = st.radio("메뉴 이동", ["새 캠페인 등록", "캠페인 관리(수정/삭제)", "현황 대시보드"])
        st.write("---")
        if st.button("로그아웃 (블로거 화면 보기)"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

# ==========================================
# 📱 메인 화면 분기
# ==========================================
if not st.session_state['admin_logged_in']:
    
    # 🔴 [완벽 해결] translate="no"와 class="notranslate"를 적용하여 자동번역 100% 원천 차단
    st.markdown("""
        <div style="width:100%; padding: 60px 20px; background: linear-gradient(rgba(17, 17, 17, 0.7), rgba(17, 17, 17, 0.9)), url('https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=1200&auto=format&fit=crop') center/cover; border-radius:20px; text-align:center; margin-bottom:30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h1 translate="no" class="notranslate" style="color:#FFFFFF; margin:0; font-size:3.2rem; font-weight:900; letter-spacing: -1px;">REVIEW US</h1>
            <p style="color:#D4AF37; margin-top:10px; font-size:1.15rem; font-weight:bold;">상위 10% 리뷰어를 위한 프리미엄 매칭 플랫폼</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_search1, col_search2 = st.columns(2)
    with col_search1: search_region = st.text_input("📍 지역 검색", placeholder="예: 강남, 부천")
    with col_search2: search_shop = st.text_input("🏪 매장명 검색", placeholder="예: 매장 상호명 입력")
    
    selected_category = st.radio("카테고리 선택", ["전체", "체험단", "네이버 클립", "기자단"], horizontal=True, label_visibility="collapsed")
    
    color_map = {"전체": "#4A90E2", "체험단": "#8E44AD", "네이버 클립": "#00C73C", "기자단": "#34495E"}
    bg_color = color_map.get(selected_category, "#4A90E2")
    
    st.markdown(f"""
    <style>
        div.row-widget.stRadio > div {{ 
            display: flex; flex-direction: row; gap: 8px; justify-content: center; 
            background: #EAECEF; padding: 6px; border-radius: 12px; display: inline-flex; margin: 5px auto 30px auto; width: 100%; max-width: 600px;
        }}
        div.row-widget.stRadio > div > label {{
            background-color: transparent; padding: 10px 20px; border-radius: 8px; cursor: pointer; transition: 0.2s; margin: 0; flex: 1; text-align: center;
        }}
        div.row-widget.stRadio > div > label > div:first-child {{ display: none; }}
        div.row-widget.stRadio > div > label p {{ font-weight: 800; font-size: 1.05rem; margin: 0; color: #666; text-align: center; width: 100%; }}
        div.row-widget.stRadio > div > label[data-checked="true"] {{ background-color: {bg_color} !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        div.row-widget.stRadio > div > label[data-checked="true"] p {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)
    
    filtered_campaigns = []
    for c in st.session_state['campaigns']:
        match_region = search_region.lower() in c.get('region', '').lower() if search_region else True
        match_shop = search_shop.lower() in c['shop'].lower() if search_shop else True
        match_category = True if selected_category == "전체" else c.get('category', '체험단') == selected_category
        
        if match_region and match_shop and match_category:
            filtered_campaigns.append(c)
    
    if not filtered_campaigns: 
        st.info("조건에 맞는 캠페인이 없습니다. 다른 탭이나 검색어를 확인해보세요.")
    else:
        cols = st.columns(4) 
        for idx, c in enumerate(filtered_campaigns):
            with cols[idx % 4]: 
                with st.container(border=True):
                    # 1. 매장명 박스 (창)
                    region_text = f"[{c.get('region', '전국').split()[0]}]" if c.get('region') else ""
                    title_display = f"{region_text} {c['shop']}"
                    if st.button(title_display, key=f"btn_{c['id']}", type="tertiary", use_container_width=True):
                        open_campaign_modal(c)
                    
                    # 2. 썸네일
                    if c.get('images'): display_b64_image(c['images'][0])
                    else: st.markdown('<div style="height:200px; background:#F1F3F5; display:flex; align-items:center; justify-content:center; color:#ADB5BD; border-radius:14px;">No Image</div>', unsafe_allow_html=True)
                    
                    # 3. 카테고리 뱃지 & D-Day 
                    cat = c.get('category', '체험단')
                    if cat == "체험단": cat_badge_class = "badge-exp"
                    elif cat == "네이버 클립": cat_badge_class = "badge-clip"
                    elif cat == "기자단": cat_badge_class = "badge-press"
                    else: cat_badge_class = "badge-exp"
                    
                    r_end = c['recruit_end']
                    if isinstance(r_end, str): r_end = datetime.strptime(r_end, "%Y-%m-%d").date()
                    days_left = (r_end - today_date).days
                    d_day_str = f"D-{days_left}" if days_left > 0 else ("D-Day" if days_left == 0 else "마감")
                    
                    st.markdown(f'<div style="margin-top:16px;"><span class="{cat_badge_class}">{cat}</span><span class="d-day-badge">{d_day_str}</span></div>', unsafe_allow_html=True)
                    
                    # 4. 하단 정보
                    st.markdown(f'<div class="offer-text">🎁 {c["offer"]}</div>', unsafe_allow_html=True)
                    
                    app_count = len([a for a in st.session_state['applications'] if a['campaign_id'] == c['id']])
                    st.markdown(f'<div class="app-count-text">👥 신청 <b><span style="color:#2980B9;">{app_count}</span></b> / 모집 {c["recruit_count"]}명</div>', unsafe_allow_html=True)

else:
    # [관리자 전용 화면]
    if admin_menu == "새 캠페인 등록":
        st.title("🏢 새 캠페인 등록")
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            with col1:
                shop_name = st.text_input("매장명")
                region = st.text_input("지역 (예: 서울 강남구)") 
                place_link = st.text_input("매장 플레이스 링크 (URL)")
                offer = st.text_input("제공 내역")
                uploaded_files = st.file_uploader("이미지 첨부 (최대 4장)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            with col2:
                category = st.selectbox("📌 캠페인 유형 (메인 탭 분류용)", ["체험단", "네이버 클립", "기자단"])
                keywords = st.text_input("필수 키워드")
                recruit_count = st.number_input("블로거 모집 인원", min_value=1, value=10)
            
            default_guideline = """★체험가능 날짜 및 시간 : 15:00~17:00 브레이크 타임에는 체험이 불가능합니다.

★동영상 1개 이상 첨부 부탁드립니다.

1. 사진을 정성껏 다양하게 찍어 주세요.
2. 동영상을 포함하여 사진은 최소 10장 이상 사용해주세요
3. 하단에 지도 위치 링크를 꼭 넣어주세요.
4. 텍스트 1,000자 이상 서술해주세요
5. 리뷰 작성 시, 제목과 본문 내용에 지정된 키워드와 자율 키워드 1개를 3회 이상 기재해주세요.
6. 체험 후 매장 구글 및 카카오맵 후기도 간단하게 작성해주세요"""
            
            guideline = st.text_area("📝 리뷰 가이드라인", value=default_guideline, height=300)
            
            dcol1, dcol2, dcol3 = st.columns(3)
            with dcol1: recruit_dates = st.date_input("모집 기간", [today_date, default_recruit_end])
            with dcol2: exp_dates = st.date_input("체험 기간", [default_exp_start, default_exp_end])
            with dcol3: exp_extend_days = st.number_input("체험기간 연장 설정 (일 단위)", min_value=0, value=0)
            
            if st.form_submit_button("등록 완료"):
                if shop_name and len(recruit_dates) == 2 and len(exp_dates) == 2:
                    images_b64 = []
                    for uf in uploaded_files[:4]:
                        images_b64.append(base64.b64encode(uf.getvalue()).decode('utf-8'))
                        
                    st.session_state['campaigns'].append({
                        "id": len(st.session_state['campaigns']), "shop": shop_name, "region": region, 
                        "category": category, "place_link": place_link, "offer": offer, "images": images_b64, 
                        "keywords": keywords, "recruit_count": recruit_count, 
                        "guideline": guideline, "recruit_start": recruit_dates[0], "recruit_end": recruit_dates[1],
                        "exp_start": exp_dates[0], "exp_end": exp_dates[1], "exp_extend_days": exp_extend_days, "status": "진행중"
                    })
                    save_data(st.session_state['campaigns'], st.session_state['applications'])
                    st.success("성공적으로 등록되었습니다!")

    elif admin_menu == "캠페인 관리(수정/삭제)":
        st.title("🛠️ 캠페인 관리")
        if not st.session_state['campaigns']: st.info("등록된 캠페인이 없습니다.")
        else:
            search_shop_admin = st.text_input("🔍 관리할 매장명 검색")
            if search_shop_admin:
                matches = [c for c in st.session_state['campaigns'] if search_shop_admin.lower() in c['shop'].lower()]
                if not matches: st.warning("해당 매장명으로 등록된 캠페인이 없습니다.")
                else:
                    selected_shop = st.selectbox("검색된 캠페인 중 선택", [m['shop'] for m in matches]) if len(matches) > 1 else matches[0]['shop']
                    idx = next(i for i, c in enumerate(st.session_state['campaigns']) if c['shop'] == selected_shop)
                    c = st.session_state['campaigns'][idx]
                    
                    if st.button("❌ 이 캠페인 완전 삭제", type="primary"):
                        st.session_state['campaigns'].pop(idx)
                        save_data(st.session_state['campaigns'], st.session_state['applications'])
                        st.rerun()
                        
                    with st.form("edit_form"):
                        st.write(f"### '{c['shop']}' 캠페인 내용 수정")
                        
                        ecol1, ecol2 = st.columns(2)
                        with ecol1: edit_region = st.text_input("지역 수정", value=c.get('region', ''))
                        with ecol2:
                            current_cat = c.get('category', '체험단')
                            cat_options = ["체험단", "네이버 클립", "기자단"]
                            edit_category = st.selectbox("📌 캠페인 유형 수정", cat_options, index=cat_options.index(current_cat) if current_cat in cat_options else 0)

                        edit_place_link = st.text_input("매장 플레이스 링크 수정", value=c.get('place_link', ''))
                        edit_offer = st.text_input("제공 내역 수정", value=c['offer'])
                        edit_keywords = st.text_input("키워드 수정", value=c['keywords'])
                        edit_recruit = st.number_input("모집 인원 수정", value=int(c['recruit_count']))
                        edit_extend_days = st.number_input("⏳ 체험기간 연장 (일 단위)", min_value=0, value=int(c.get('exp_extend_days', 0)))
                        edit_guide = st.text_area("가이드라인 수정", value=c['guideline'], height=300)
                        
                        if st.form_submit_button("수정 내용 저장"):
                            st.session_state['campaigns'][idx].update({
                                "region": edit_region, "category": edit_category, "place_link": edit_place_link, 
                                "offer": edit_offer, "keywords": edit_keywords, "recruit_count": edit_recruit, 
                                "guideline": edit_guide, "exp_extend_days": edit_extend_days
                            })
                            save_data(st.session_state['campaigns'], st.session_state['applications'])
                            st.success(f"수정이 완료되었습니다! (연장 {edit_extend_days}일 적용)")
            else: st.info("👆 위 검색창에 관리할 매장명을 입력해주세요.")

    elif admin_menu == "현황 대시보드":
        st.title("📊 현황 대시보드")
        if not st.session_state['campaigns']: st.info("등록된 캠페인이 없습니다.")
        else:
            search_shop_dash = st.text_input("🔍 조회할 매장명 검색")
            if search_shop_dash:
                matches = [c for c in st.session_state['campaigns'] if search_shop_dash.lower() in c['shop'].lower()]
                if not matches: st.warning("해당 매장명으로 등록된 캠페인이 없습니다.")
                else:
                    selected_shop = st.selectbox("검색된 캠페인 중 선택", [m['shop'] for m in matches]) if len(matches) > 1 else matches[0]['shop']
                    current_cam = next(c for c in st.session_state['campaigns'] if c['shop'] == selected_shop)
                    apps = [a for a in st.session_state['applications'] if a['shop'] == selected_shop]
                    
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
                                    save_data(st.session_state['campaigns'], st.session_state['applications'])
                                    st.success("성공적으로 처리되었습니다!")
                                    st.rerun()
                                else: st.warning("선정할 블로거를 선택해주세요.")
                        else: st.info("현재 대기 중인 블로거가 없습니다.")

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
                        else: st.info("아직 선정된 블로거가 없습니다.")
                    
                    st.markdown("---")
                    if st.button("📈 자동 마감 보고서 생성"):
                        completed = [a['review_link'] for a in apps if a['review_link'] != ""]
                        
                        comments_pool = [
                            f"대표님, 안녕하십니까. 리뷰어스 마케팅팀입니다.<br>이번 <b>[{selected_shop}]</b> 캠페인이 성공적으로 마감되었습니다.<br><br>요청하신 메인 키워드 <b>'{current_cam['keywords']}'</b>(을)를 타겟으로 하여 총 <b>{len(completed)}명</b>의 검증된 프리미엄 리뷰어가 포스팅을 완료했습니다. 단순 조회수 증가를 넘어, 네이버 플레이스 5대 진단 포인트를 철저히 준수하고 잠재 고객의 방문을 유도하는 정중한 존댓말과 후킹 문구를 적용하여 실제 매장 유입을 극대화할 수 있도록 세팅을 완료하였습니다.",
                            f"안녕하세요 대표님, 리뷰어스 마케팅팀입니다.<br><b>[{selected_shop}]</b>의 체험단 프로젝트가 성황리에 마무리되어 최종 결과를 보고드립니다.<br><br>전달 주신 핵심 키워드 <b>'{current_cam['keywords']}'</b>에 맞춰 총 <b>{len(completed)}건</b>의 고품질 리뷰 발행이 완료되었습니다. 모든 포스팅은 단순 나열식 리뷰를 지양하고, 매장의 매력을 최대한 어필하는 활동성 있는 사진과 후킹 멘트로 구성되었습니다. 이를 통해 스마트플레이스로의 자연스러운 검색 유입 및 전환율 상승이 강력하게 기대됩니다.",
                            f"리뷰어스 마케팅팀에서 <b>[{selected_shop}]</b> 캠페인 최종 마감 현황을 안내해 드립니다.<br><br>총 <b>{len(completed)}명</b>의 우수 블로거들이 <b>'{current_cam['keywords']}'</b> 키워드를 중심으로 매장의 장점을 생생하게 포스팅하였습니다. 특히 당사의 까다로운 리뷰 가이드라인(존댓말 필수 사용, 새소식 연계 등)이 100% 반영되어, 검색 유저들에게 높은 신뢰감을 주고 실제 오프라인 방문으로 즉시 이어질 수 있는 탄탄한 온라인 마케팅 기반이 마련되었습니다."
                        ]
                        eval_comment = random.choice(comments_pool)

                        html_code = f"""
                        <html>
                        <head><script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script></head>
                        <body style="font-family: 'Malgun Gothic', sans-serif;">
                            <div id="rpt" style="background:#FFF; padding:40px; border:1px solid #EAECEF; border-radius:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
                                <h2 style="color:#1A1A1A; border-bottom: 2px solid #4A90E2; padding-bottom: 15px; margin-bottom: 25px;">📊 [{selected_shop}] 마케팅 결과 보고서</h2>
                                <p style="font-size: 1.05rem; color: #333;"><b>수신:</b> {selected_shop} 대표님<br><b>발신:</b> 리뷰어스(ReviewUs) 마케팅팀</p>
                                <div style="background:#F8F9FA; padding:25px; border-radius:10px; margin: 25px 0; line-height: 1.8; font-size: 0.95rem; color:#212529;">
                                    {eval_comment}
                                </div>
                                <h4 style="color:#2C3E50; margin-bottom: 15px; border-left: 4px solid #4A90E2; padding-left: 10px;">🔗 최종 발행된 리뷰 포스팅 링크</h4>
                                <div style="background:#FFF; border: 1px solid #EAECEF; padding: 20px; border-radius: 10px; word-break: break-all; line-height: 2.0; font-size: 0.95rem;">
                        """
                        
                        if len(completed) > 0:
                            for idx, link in enumerate(completed):
                                html_code += f"<div style='margin-bottom: 8px;'><b>{idx+1}.</b> <a href='{link}' target='_blank' style='color:#4A90E2; text-decoration:underline;'>{link}</a></div>"
                        else: html_code += "<div style='color:#868E96;'>아직 제출된 리뷰 포스팅이 없습니다.</div>"
                            
                        html_code += """
                                </div>
                            </div>
                            <button onclick="saveImg()" style="width:100%; margin-top:20px; padding:15px; background:#4A90E2; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size: 1.05rem;">📸 보고서 이미지로 즉시 다운로드</button>
                            <script>
                                function saveImg() {
                                    html2canvas(document.getElementById('rpt'), {scale:2, useCORS:true}).then(c => {
                                        var a = document.createElement('a'); a.download = '리뷰어스_{selected_shop}_마감보고서.png'; a.href = c.toDataURL('image/png'); a.click();
                                    });
                                }
                            </script>
                        </body>
                        </html>
                        """
                        components.html(html_code, height=900, scrolling=True)
            else: st.info("👆 위 검색창에 대시보드를 확인할 매장명을 입력해주세요.")
