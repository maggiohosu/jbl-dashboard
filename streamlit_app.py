# -*- coding: utf-8 -*-
"""
JBL 실판매현황 Streamlit 대시보드 (모바일 최적화)
PC 판매현황_대시보드.html 과 동일한 내용 · 4탭 동일 구성
수정사항:
  1. 데이터 생성 버튼 → PC HTML도 함께 생성
  2. 월 선택 → st.selectbox (모바일 친화적)
  3. PC 대시보드 내용과 동일하게 정렬
  4. 터치 드릴다운 (expander/selectbox)
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="JBL 실판매현황",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: #F0F2F5; }
.block-container { padding: 12px 12px 32px 12px !important; max-width: 1400px; }

/* ── 요약 스트립 ── */
.sum-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px; margin-bottom: 14px;
}
.sum-card {
  background: #fff; border-radius: 10px; border: 1px solid #E2E6EA;
  padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,.07);
}
.sum-label { font-size: 10px; font-weight: 700; color: #6B7280;
             text-transform: uppercase; letter-spacing: .4px; margin-bottom: 6px; }
.sum-val   { font-size: 22px; font-weight: 700; color: #111827;
             font-family: 'Inter', sans-serif; line-height: 1; }
.sum-sub   { font-size: 11px; color: #6B7280; margin-top: 4px; }
.sum-tag   { display: inline-block; font-size: 11px; font-weight: 700;
             padding: 2px 8px; border-radius: 20px; margin-left: 4px; }
.sum-tag.green  { background: #F0FDF4; color: #16A34A; }
.sum-tag.yellow { background: #FFFBEB; color: #D97706; }
.sum-tag.red    { background: #FEF2F2; color: #DC2626; }

/* ── 마켓 KPI 그리드 ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px; margin-bottom: 14px;
}
.kpi-card {
  background: #fff; border-radius: 10px; border: 1px solid #E2E6EA;
  border-left: 4px solid #2563EB;
  padding: 13px 14px; box-shadow: 0 1px 3px rgba(0,0,0,.07);
}
.kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.kpi-name   { font-size: 13px; font-weight: 700; }
.kpi-badge  { font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 20px; }
.kpi-actual { font-size: 18px; font-weight: 700; color: #111827;
              font-family: 'Inter', sans-serif; }
.kpi-meta   { font-size: 11px; color: #6B7280; margin-top: 2px; }
.kpi-bar-bg { height: 4px; background: #F1F5F9; border-radius: 4px;
              margin-top: 8px; overflow: hidden; }
.kpi-bar-fill { height: 100%; border-radius: 4px; transition: width .4s; }

/* ── 탭 ── */
[data-testid="stTabs"] > div:first-child {
  overflow-x: auto; flex-wrap: nowrap !important; scrollbar-width: none;
}
[data-testid="stTabs"] > div:first-child::-webkit-scrollbar { display: none; }
[data-testid="stTabs"] > div:first-child button {
  font-size: 13px !important; font-weight: 600 !important;
  white-space: nowrap !important; padding: 10px 14px !important;
}

/* ── expander 터치 영역 확대 ── */
[data-testid="stExpander"] summary { min-height: 44px; display: flex; align-items: center; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  환경 감지 (PC 로컬 vs Streamlit Cloud)
# ══════════════════════════════════════════════════════
def _is_cloud():
    """Streamlit Cloud 환경이면 True"""
    return "STREAMLIT_SHARING_MODE" in os.environ or \
           st.secrets.get("GITHUB_TOKEN", "") != ""

# ══════════════════════════════════════════════════════
#  데이터 로드
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def load_data_cloud():
    """Streamlit Cloud 전용: GitHub 저장소에서 dash_data.json 읽기"""
    import urllib.request, json as _json
    token = st.secrets.get("GITHUB_TOKEN", "")
    repo  = st.secrets.get("GITHUB_REPO", "maggiohosu/jbl-dashboard")
    url   = f"https://raw.githubusercontent.com/{repo}/main/dash_data.json"
    req   = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return _json.loads(r.read())
    except Exception:
        return None

@st.cache_data(ttl=30, show_spinner=False)
def load_data_local():
    """PC 로컬 전용: process_sales 에서 직접 읽기"""
    import process_sales as ps
    return ps.get_dash_data()

def load_data():
    if _is_cloud():
        return load_data_cloud()
    return load_data_local()

def run_full_pipeline():
    """PC HTML 포함 전체 파이프라인 실행 — 출력 로그를 반환"""
    import io, sys, traceback
    import process_sales as ps

    buf = io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf
    try:
        ps.main()
        log = buf.getvalue()
        error = None
    except Exception:
        log = buf.getvalue()
        error = traceback.format_exc()
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

    return log, error

# ══════════════════════════════════════════════════════
#  헬퍼
# ══════════════════════════════════════════════════════
  def fmt_won(v):
      if not v: return "0"
      return f"{int(v):,}"

def fmt_qty(v):
    return f"{int(v):,}개" if v else "0개"

def pct_color(rate):
    if rate >= 1.0: return {"bg":"#F0FDF4","text":"#16A34A","fill":"#16A34A","tag":"green","lbl":"목표 달성"}
    if rate >= 0.7: return {"bg":"#FFFBEB","text":"#D97706","fill":"#D97706","tag":"yellow","lbl":"순조"}
    return          {"bg":"#FEF2F2","text":"#DC2626","fill":"#DC2626","tag":"red","lbl":"달성 필요"}

def sum_month(d: dict, month: int) -> int:
    if not d: return 0
    if month == 0: return sum(d.values())
    return sum(v for k, v in d.items()
               if isinstance(k, str) and len(k) >= 7 and k[5:7] == f"{month:02d}")

def filter_dates(dates: list, month: int) -> list:
    if month == 0: return dates
    return [d for d in dates if isinstance(d, str) and len(d) >= 7 and d[5:7] == f"{month:02d}"]

def linear_trend(ys):
    n = len(ys)
    if n < 2: return ys
    xs = list(range(n)); mx = sum(xs)/n; my = sum(ys)/n
    den = sum((x-mx)**2 for x in xs)
    if den == 0: return [my]*n
    s = sum((xs[i]-mx)*(ys[i]-my) for i in range(n)) / den
    b = my - s*mx
    return [s*x + b for x in xs]

PLT = dict(
    plot_bgcolor="#fff", paper_bgcolor="#fff",
    font_family="Noto Sans KR",
    margin=dict(l=0, r=0, t=10, b=0),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
)

def mkt_actual(D, mkt, month):
    return sum_month(D.get("mktDayRev",{}).get(mkt,{}), month)

def mkt_target(D, mkt, month):
    if month == 0:
        return sum(D.get("targets",{}).get(mkt,{}).values())
    mt = D.get("monthlyTargets",{}).get(mkt,{})
    return mt.get(str(month), mt.get(month, 0)) or 0

# ══════════════════════════════════════════════════════
#  ① 마켓별 매출 탭
# ══════════════════════════════════════════════════════
def tab_market(D, month):
    markets    = D.get("markets", [])
    mkt_colors = D.get("mktColors", {})
    wk_lbl     = D.get("weekLabels", {})
    wk_count   = int(D.get("weekCount", 5))
    mkt_wk_rev = D.get("mktWkRev", {})

    actuals = {m: mkt_actual(D, m, month) for m in markets}
    tgts    = {m: mkt_target(D, m, month) for m in markets}
    total_a = sum(actuals.values())
    total_t = sum(tgts.values())
    total_r = total_a / total_t if total_t else 0

    # 총 판매 수량
    models     = D.get("models", [])
    dates_all  = D.get("dates", [])
    filt_dates = filter_dates(dates_all, month)
    total_qty  = sum(
        sum(md.get(d, 0) for mk in m.get("dayData",{}).values()
            for d in [ds for ds in filt_dates if ds in mk])
        for m in models
        for md in [{}]  # placeholder — compute below
    )
    # 실제 수량 계산
    total_qty = 0
    for m in models:
        for mkt_d in m.get("dayData", {}).values():
            for d in filt_dates:
                total_qty += mkt_d.get(d, 0)

    period_lbl = f"{month}월 기준" if month else "전체 기간"
    pc = pct_color(total_r)

    # ── 요약 스트립 (PC와 동일) ──────────────────────
    st.markdown(f"""
    <div class="sum-strip">
      <div class="sum-card">
        <div class="sum-label">총 매출 ({period_lbl})</div>
        <div class="sum-val">{fmt_won(total_a)}원</div>
        <div class="sum-sub">목표 {fmt_won(total_t)}원</div>
      </div>
      <div class="sum-card">
        <div class="sum-label">목표 달성률</div>
        <div class="sum-val">{total_r*100:.1f}%</div>
        <div class="sum-sub">전체 마켓 합산
          <span class="sum-tag {pc['tag']}">{pc['lbl']}</span>
        </div>
      </div>
      <div class="sum-card">
        <div class="sum-label">판매 수량 ({period_lbl})</div>
        <div class="sum-val">{total_qty:,}개</div>
        <div class="sum-sub">{len(models)}개 모델</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 마켓 KPI 카드 (PC와 동일 구조, 터치 드릴다운 포함) ──
    cards_html = '<div class="kpi-grid">'
    for m in markets:
        col   = mkt_colors.get(m, "#607D8B")
        act   = actuals[m]; tgt = tgts[m]
        rate  = act/tgt if tgt else 0
        pct   = min(100, rate*100)
        pc    = pct_color(rate)
        cards_html += f"""
        <div class="kpi-card" style="border-left-color:{col}">
          <div class="kpi-header">
            <div class="kpi-name" style="color:{col}">{m}</div>
            <div class="kpi-badge" style="background:{pc['bg']};color:{pc['text']}">{rate*100:.1f}%</div>
          </div>
          <div class="kpi-actual">{fmt_won(act)}<span style="font-size:12px;color:#6B7280;font-weight:400;">원</span></div>
          <div class="kpi-meta">목표 {fmt_won(tgt)}원</div>
          <div class="kpi-bar-bg"><div class="kpi-bar-fill" style="width:{pct:.0f}%;background:{pc['fill']}"></div></div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── 달성률 바 차트 (PC와 동일: 달성률 % 기준) ────────
    rates  = [actuals[m]/tgts[m]*100 if tgts[m] else 0 for m in markets]
    colors = [pct_color(r/100)["fill"] for r in rates]

    fig = go.Figure()
    fig.add_bar(
        x=markets, y=rates,
        marker_color=colors, marker_line_width=0,
        text=[f"{r:.1f}%" for r in rates],
        textposition="outside", textfont_size=12,
        customdata=[[fmt_won(actuals[m]), fmt_won(tgts[m])] for m in markets],
        hovertemplate="<b>%{x}</b><br>달성률: %{y:.1f}%<br>실적: %{customdata[0]}원<br>목표: %{customdata[1]}원<extra></extra>",
    )
    # 100% 기준선
    fig.add_hline(y=100, line_dash="dot", line_color="rgba(22,163,74,.5)", line_width=1.5)
    fig.update_layout(
        **PLT, height=280,
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="달성률 (%)",
                   range=[0, max(max(rates)*1.15, 110)]),
        xaxis=dict(showgrid=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── 마켓별 드릴다운 (터치 → 주차별 상세) ─────────────
    st.markdown("#### 마켓별 주차 상세 _(터치해서 펼치기)_")
    wks = [str(w) for w in range(1, wk_count+1)]
    for m in markets:
        col   = mkt_colors.get(m, "#607D8B")
        act   = actuals[m]; rate = act/tgts[m]*100 if tgts[m] else 0
        pc    = pct_color(rate/100)
        with st.expander(f"**{m}** — {fmt_won(act)}원  |  달성률 {rate:.1f}%"):
            wk_data = mkt_wk_rev.get(m, {})
            if wk_data:
                # 주차별 바 차트
                wk_vals = [wk_data.get(w, 0)/10000 for w in wks]
                wk_lbls = [wk_lbl.get(w, f"{w}주차") for w in wks]
                fig2 = go.Figure()
                fig2.add_bar(x=wk_lbls, y=wk_vals,
                             marker_color=col, marker_opacity=0.8,
                             text=[f"{v:,.0f}만" for v in wk_vals],
                             textposition="outside", textfont_size=11)
                fig2.update_layout(**PLT, height=180, showlegend=False,
                                   yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="만원"),
                                   xaxis=dict(showgrid=False))
                st.plotly_chart(fig2, use_container_width=True)

                # 주차별 수치 테이블
                df_wk = pd.DataFrame({
                    "주차": wk_lbls,
                    "매출": [fmt_won(wk_data.get(w, 0))+"원" for w in wks],
                })
                st.dataframe(df_wk, use_container_width=True, hide_index=True)
            else:
                st.caption("데이터 없음")


# ══════════════════════════════════════════════════════
#  ② 매출 추이 탭
# ══════════════════════════════════════════════════════
def tab_trend(D, month):
    markets    = D.get("markets", [])
    mkt_colors = D.get("mktColors", {})

    c1, c2 = st.columns(2)
    with c1:
        view   = st.radio("기준", ["주문일자","판매일자"], horizontal=True, key="rv_view")
    with c2:
        metric = st.radio("지표",  ["매출","수량"],       horizontal=True, key="rv_metric")

    use_c = (view == "주문일자")
    raw   = D.get(("mktDayRevChart" if use_c else "mktDayRev") if metric=="매출"
                  else ("mktDayQtyChart" if use_c else "mktDayQty"), {})

    all_d  = sorted({d for m in markets for d in raw.get(m,{})})
    f_dates= filter_dates(all_d, month)
    if not f_dates:
        st.info("선택한 기간에 데이터가 없습니다."); return

    sel = st.multiselect("마켓 선택", markets, default=markets, key="rv_mkts")
    if not sel: sel = markets

    div    = 10000 if metric=="매출" else 1
    y_unit = "만원"  if metric=="매출" else "개"

    fig = go.Figure()
    for m in sel:
        vals = raw.get(m, {})
        y    = [vals.get(d,0)/div for d in f_dates]
        col  = mkt_colors.get(m, "#9CA3AF")
        fig.add_scatter(x=f_dates, y=y, name=m, mode="lines+markers",
                        line=dict(color=col, width=2), marker=dict(size=3),
                        hovertemplate=f"{m}<br>%{{x}}<br>%{{y:,.0f}}{y_unit}<extra></extra>")
        ty = linear_trend(y)
        fig.add_scatter(x=f_dates, y=ty, mode="lines", showlegend=False,
                        line=dict(color=col, width=1, dash="dot"), hoverinfo="skip")
    fig.update_layout(**PLT, height=380,
                      yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title=y_unit),
                      xaxis=dict(showgrid=False, tickangle=-45))
    st.plotly_chart(fig, use_container_width=True)

    # ── 마켓별 기간 합계 요약 (드릴다운) ─────────────────
    with st.expander("마켓별 기간 합계 보기"):
        rows = []
        for m in sel:
            vals = raw.get(m, {})
            total = sum(vals.get(d,0) for d in f_dates)
            rows.append({"마켓": m,
                         "합계": fmt_won(total)+"원" if metric=="매출" else fmt_qty(total)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
#  ③ 세그먼트 추이 탭
# ══════════════════════════════════════════════════════
def tab_segment(D, month):
    cats       = D.get("categories", [])
    cat_colors = D.get("catColors", {})

    c1, c2 = st.columns(2)
    with c1:
        view   = st.radio("기준", ["주문일자","판매일자"], horizontal=True, key="sg_view")
    with c2:
        metric = st.radio("지표",  ["매출","수량"],       horizontal=True, key="sg_metric")

    use_c = (view == "주문일자")
    raw   = D.get(("catDayRevChart" if use_c else "catDayRev") if metric=="매출"
                  else ("catDayQtyChart" if use_c else "catDayQty"), {})

    all_d  = sorted({d for c in cats for d in raw.get(c,{})})
    f_dates= filter_dates(all_d, month)
    if not f_dates:
        st.info("선택한 기간에 데이터가 없습니다."); return

    sel = st.multiselect("세그먼트 선택", cats, default=cats, key="sg_cats")
    if not sel: sel = cats

    div    = 10000 if metric=="매출" else 1
    y_unit = "만원"  if metric=="매출" else "개"

    fig = go.Figure()
    for cat in sel:
        vals = raw.get(cat, {})
        y    = [vals.get(d,0)/div for d in f_dates]
        col  = cat_colors.get(cat, "#9CA3AF")
        fig.add_scatter(x=f_dates, y=y, name=cat, mode="lines+markers",
                        line=dict(color=col, width=2), marker=dict(size=3),
                        hovertemplate=f"{cat}<br>%{{x}}<br>%{{y:,.0f}}{y_unit}<extra></extra>")
        ty = linear_trend(y)
        fig.add_scatter(x=f_dates, y=ty, mode="lines", showlegend=False,
                        line=dict(color=col, width=1, dash="dot"), hoverinfo="skip")
    fig.update_layout(**PLT, height=380,
                      yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title=y_unit),
                      xaxis=dict(showgrid=False, tickangle=-45))
    st.plotly_chart(fig, use_container_width=True)

    # ── 세그먼트별 합계 (드릴다운) ───────────────────────
    with st.expander("세그먼트별 기간 합계 보기"):
        rows = []
        for cat in sel:
            vals  = raw.get(cat, {})
            total = sum(vals.get(d,0) for d in f_dates)
            rows.append({"세그먼트": cat,
                         "합계": fmt_won(total)+"원" if metric=="매출" else fmt_qty(total)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
#  ④ 모델별 판매 탭
# ══════════════════════════════════════════════════════
def tab_models(D, month):
    models    = D.get("models", [])
    skus      = D.get("skus", [])
    markets   = D.get("markets", [])
    cats      = D.get("categories", [])
    wk_lbl    = D.get("weekLabels", {})
    wk_count  = int(D.get("weekCount", 5))
    dates_all = D.get("dates", [])
    qty_tgts  = D.get("modelQtyTargets", {})
    mkt_colors= D.get("mktColors", {})

    # ── 필터 (2행으로 나눔 — 모바일 대응) ──────────────
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        mode = st.radio("단위", ["모델명별","SKU별"], horizontal=True, key="tb_mode")
    with r1c2:
        view = st.radio("기간", ["주별","일별"],     horizontal=True, key="tb_view")

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        sel_mkt = st.selectbox("마켓", ["전체"]+markets, key="tb_mkt")
    with r2c2:
        sel_cat = st.selectbox("세그먼트", ["전체"]+cats, key="tb_cat")

    search = st.text_input("", placeholder="🔍 모델명 / SKU 검색",
                           key="tb_search", label_visibility="collapsed")

    source = models if mode == "모델명별" else skus

    # ── 기간 컬럼 ────────────────────────────────────
    if view == "주별":
        p_keys = [str(w) for w in range(1, wk_count+1)]
        p_lbls = {k: wk_lbl.get(k, f"{k}주차") for k in p_keys}
    else:
        p_keys = filter_dates(dates_all, month)
        p_lbls = {d: d[5:] for d in p_keys}

    # ── 데이터 빌드 ──────────────────────────────────
    rows = []
    for m in source:
        if sel_cat != "전체" and m.get("cat") != sel_cat: continue
        label = m.get("grp", m.get("sku",""))
        if search and search.lower() not in (label+m.get("sku","")).lower(): continue

        if sel_mkt == "전체":
            if view == "주별":
                p_vals = {k: m.get("totalWk",{}).get(k,0) for k in p_keys}
            else:
                day_all = {}
                for mk_d in m.get("dayData",{}).values():
                    for d,q in mk_d.items(): day_all[d] = day_all.get(d,0)+q
                p_vals = {k: day_all.get(k,0) for k in p_keys}
            total = sum(p_vals.values())
        else:
            if view == "주별":
                wk_d = m.get("mktWk",{}).get(sel_mkt,{})
                p_vals = {k: wk_d.get(k,0) for k in p_keys}
            else:
                mk_d = m.get("dayData",{}).get(sel_mkt,{})
                p_vals = {k: mk_d.get(k,0) for k in p_keys}
            total = sum(p_vals.values())

        if total == 0: continue

        sku_base = m.get("skuBase") or m.get("sku","")
        tgt_key  = f"{sku_base}*" if qty_tgts.get(f"{sku_base}*") else sku_base
        m_key    = str(month) if month else str(D.get("reportMonth",0))
        qty_tgt  = (qty_tgts.get(tgt_key) or {}).get(m_key, 0)

        row = {
            "_sku": m.get("sku",""),
            "_dayData": m.get("dayData",{}),
            "_mktWk":   m.get("mktWk",{}),
            "카테고리": m.get("cat",""),
            "모델명":   label,
            "합계(개)": total,
            "목표(개)": qty_tgt or None,
            "달성률":   f"{total/qty_tgt*100:.0f}%" if qty_tgt else "-",
        }
        for k in p_keys:
            row[p_lbls[k]] = p_vals.get(k,0) or None
        rows.append(row)

    if not rows:
        st.info("조건에 맞는 데이터가 없습니다."); return

    # 내부용 컬럼 분리
    detail_map = {r["모델명"]: r for r in rows}
    display_rows = [{k:v for k,v in r.items() if not k.startswith("_")} for r in rows]

    df = pd.DataFrame(display_rows).sort_values("합계(개)", ascending=False).reset_index(drop=True)

    p_cfg = {p_lbls[k]: st.column_config.NumberColumn(p_lbls[k], format="%d", width="small")
             for k in p_keys}
    col_cfg = {
        "카테고리": st.column_config.TextColumn(width="small"),
        "모델명":   st.column_config.TextColumn(width="large"),
        "합계(개)": st.column_config.NumberColumn("합계", format="%d", width="small"),
        "목표(개)": st.column_config.NumberColumn("목표", format="%d", width="small"),
        "달성률":   st.column_config.TextColumn(width="small"),
        **p_cfg,
    }
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config=col_cfg, height=460)
    st.caption(f"{len(df)}개 모델")

    # ── 모델 드릴다운 (터치 → 마켓별 상세) ──────────────
    st.markdown("#### 모델 상세 _(모델 선택 후 터치)_")
    model_names = [r["모델명"] for r in rows[:50]]   # 상위 50개
    sel_model   = st.selectbox("모델 선택", ["(선택)"] + model_names, key="tb_detail")

    if sel_model != "(선택)" and sel_model in detail_map:
        rd = detail_map[sel_model]
        day_data = rd["_dayData"]; mkt_wk = rd["_mktWk"]

        st.markdown(f"**{sel_model}** — 마켓별 상세")

        # 마켓별 합계 바 차트
        mkt_totals = {}
        for mk in markets:
            if view == "주별":
                mkt_totals[mk] = sum(mkt_wk.get(mk,{}).get(k,0) for k in p_keys)
            else:
                mk_d = day_data.get(mk,{})
                mkt_totals[mk] = sum(mk_d.get(k,0) for k in p_keys)

        mkt_totals = {k:v for k,v in mkt_totals.items() if v}
        if mkt_totals:
            fig = go.Figure()
            fig.add_bar(
                x=list(mkt_totals.keys()),
                y=list(mkt_totals.values()),
                marker_color=[mkt_colors.get(m,"#9CA3AF") for m in mkt_totals],
                text=[f"{v:,}개" for v in mkt_totals.values()],
                textposition="outside", textfont_size=11,
            )
            fig.update_layout(**PLT, height=220, showlegend=False,
                              yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="수량(개)"),
                              xaxis=dict(showgrid=False))
            st.plotly_chart(fig, use_container_width=True)

        # 마켓 × 주차 테이블
        if view == "주별":
            tbl = {"마켓": [], **{p_lbls[k]:[] for k in p_keys}}
            for mk in markets:
                wk_d = mkt_wk.get(mk,{})
                if not any(wk_d.get(k,0) for k in p_keys): continue
                tbl["마켓"].append(mk)
                for k in p_keys: tbl[p_lbls[k]].append(wk_d.get(k,0) or None)
            if tbl["마켓"]:
                st.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
#  메인
# ══════════════════════════════════════════════════════
def main():
    # ── 헤더 ─────────────────────────────────────────
    h1, h2, h3 = st.columns([4, 3, 2])
    with h1:
        st.markdown("## 📊 JBL 실판매현황")
    with h2:
        D_quick = load_data()
        if D_quick:
            st.caption(f"기간: {D_quick.get('period','-')}  |  업데이트: {D_quick.get('updated','-')}")
    with h3:
        bc1, bc2 = st.columns(2)
        with bc1:
            # 클라우드 환경에서는 생성 버튼 숨김
            if _is_cloud():
                if st.button("🔄 새로고침", help="최신 데이터로 새로고침"):
                    load_data_cloud.clear()
                    st.rerun()
            elif st.button("📊 생성", help="Excel·PC HTML·모바일 대시보드 모두 생성"):
                with st.spinner("데이터 생성 중... (30초~1분 소요)"):
                    log, err = run_full_pipeline()
                st.cache_data.clear()
                if err:
                    st.error("생성 중 오류가 발생했습니다.")
                    with st.expander("오류 상세 내용 (클릭해서 보기)"):
                        st.code(err, language="text")
                        if log:
                            st.text("--- 실행 로그 ---")
                            st.code(log, language="text")
                else:
                    # 성공 여부를 로그에서 판단 (HTML 생성 경고 여부 확인)
                    if "[경고] HTML 대시보드 생성 실패" in log:
                        st.warning("엑셀은 생성됐지만 HTML 대시보드 생성에 문제가 있습니다.")
                        with st.expander("실행 로그 확인"):
                            st.code(log, language="text")
                    else:
                        st.success("생성 완료!")
                    time.sleep(0.5)
                    st.rerun()
        with bc2:
            if st.button("🔄 새로고침", help="화면 데이터만 새로고침"):
                st.cache_data.clear()
                st.rerun()

    # ── 데이터 로드 ───────────────────────────────────
    D = load_data()
    if D is None:
        import os as _os
        FOLDER = _os.path.dirname(_os.path.abspath(__file__))
        master = _os.path.join(FOLDER, "데이터_마스터.xlsx")
        if not _os.path.exists(master):
            st.error("⚠️ `데이터_마스터.xlsx` 파일이 없습니다.")
            st.markdown("같은 폴더에 `데이터_마스터.xlsx` 파일을 넣은 뒤 **📊 생성** 버튼을 눌러주세요.")
        else:
            st.error("⚠️ 데이터 처리 중 오류가 발생했습니다.")
            st.markdown("""
**조치 방법**
1. **📊 생성** 버튼을 눌러서 데이터를 다시 생성해보세요.
2. 생성 후 오류 메시지가 표시되면 내용을 확인해주세요.
3. `데이터_마스터.xlsx` 파일이 Excel에서 열려있으면 닫은 후 다시 시도해주세요.
            """)
            # 상세 오류 표시
            import io, sys, traceback
            import process_sales as _ps
            buf = io.StringIO()
            old_out = sys.stdout; sys.stdout = buf
            try:
                _ps.get_dash_data()
            except Exception:
                pass
            finally:
                sys.stdout = old_out
            detail = buf.getvalue()
            if detail:
                with st.expander("오류 상세 (클릭)"):
                    st.code(detail, language="text")
        return

    # ── 월 선택 (selectbox — 모바일 친화) ────────────
    report_month = D.get("reportMonth", 0)
    month_opts   = [0] + list(range(1, 13))
    month_fmt    = {0:"전체"} | {m:f"{m}월" for m in range(1,13)}
    default_idx  = month_opts.index(report_month) if report_month in month_opts else 0

    sel_month = st.selectbox(
        "기간 선택",
        month_opts,
        index=default_idx,
        format_func=lambda x: month_fmt[x],
        key="global_month",
    )

    # ── 4개 탭 ───────────────────────────────────────
    t1, t2, t3, t4 = st.tabs([
        "📊 마켓별 매출",
        "📈 매출 추이",
        "🎯 세그먼트 추이",
        "📋 모델별 판매",
    ])
    with t1: tab_market(D, sel_month)
    with t2: tab_trend(D, sel_month)
    with t3: tab_segment(D, sel_month)
    with t4: tab_models(D, sel_month)


if __name__ == "__main__":
    main()
