# -*- coding: utf-8 -*-
"""
JBL 실판매 대시보드 v2 (app_new.py)
8개 탭 구성: 개요 / 마켓별 / 모델별 / 세그먼트별 / 추이 / 성장/하락 / 반품
"""

import os, json, urllib.request
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="JBL 실판매 대시보드",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════
#  공통 CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: #F0F2F5; }
.block-container { padding: 12px 12px 40px 12px !important; max-width: 1400px; }

/* KPI 카드 */
.kpi-card {
  background: #fff; border-radius: 12px; border: 1px solid #E5E7EB;
  padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.08);
  margin-bottom: 10px;
}
.kpi-value { font-size: 24px; font-weight: 700; color: #111827; line-height: 1.2; }
.kpi-label { font-size: 11px; font-weight: 600; color: #6B7280;
             text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }
.kpi-delta-pos { color: #16A34A; font-size: 13px; font-weight: 700; }
.kpi-delta-neg { color: #DC2626; font-size: 13px; font-weight: 700; }
.kpi-delta-neu { color: #6B7280; font-size: 13px; font-weight: 700; }
.kpi-sub { font-size: 12px; color: #6B7280; margin-top: 2px; }

/* 섹션 헤더 */
.section-header {
  font-size: 15px; font-weight: 700; color: #1F2937;
  border-left: 4px solid #2563EB; padding-left: 10px;
  margin: 18px 0 10px 0;
}

/* 요약 그리드 */
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
.sum-val   { font-size: 22px; font-weight: 700; color: #111827; line-height: 1; }
.sum-sub   { font-size: 11px; color: #6B7280; margin-top: 4px; }
.sum-tag   { display: inline-block; font-size: 11px; font-weight: 700;
             padding: 2px 8px; border-radius: 20px; margin-left: 4px; }
.sum-tag.green  { background: #F0FDF4; color: #16A34A; }
.sum-tag.yellow { background: #FFFBEB; color: #D97706; }
.sum-tag.red    { background: #FEF2F2; color: #DC2626; }

/* 마켓 KPI 그리드 */
.mkt-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px; margin-bottom: 14px;
}
.mkt-kpi-card {
  background: #fff; border-radius: 10px; border: 1px solid #E2E6EA;
  border-left: 4px solid #2563EB;
  padding: 13px 14px; box-shadow: 0 1px 3px rgba(0,0,0,.07);
}
.mkt-kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.mkt-kpi-name   { font-size: 13px; font-weight: 700; }
.mkt-kpi-badge  { font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 20px; }
.mkt-kpi-actual { font-size: 18px; font-weight: 700; color: #111827; }
.mkt-kpi-meta   { font-size: 11px; color: #6B7280; margin-top: 2px; }
.mkt-kpi-bar-bg { height: 4px; background: #F1F5F9; border-radius: 4px;
                  margin-top: 8px; overflow: hidden; }
.mkt-kpi-bar-fill { height: 100%; border-radius: 4px; }

/* 탭 */
[data-testid="stTabs"] > div:first-child {
  overflow-x: auto; flex-wrap: nowrap !important; scrollbar-width: none;
}
[data-testid="stTabs"] > div:first-child::-webkit-scrollbar { display: none; }
[data-testid="stTabs"] > div:first-child button {
  font-size: 13px !important; font-weight: 600 !important;
  white-space: nowrap !important; padding: 10px 14px !important;
}
/* expander 터치 */
[data-testid="stExpander"] summary { min-height: 44px; display: flex; align-items: center; }

/* 랭킹 카드 */
.rank-card {
  background: #fff; border-radius: 10px; border: 1px solid #E5E7EB;
  padding: 12px 14px; margin-bottom: 8px;
  display: flex; align-items: center; gap: 12px;
}
.rank-medal { font-size: 22px; min-width: 28px; }
.rank-name  { font-size: 14px; font-weight: 700; color: #111827; }
.rank-sub   { font-size: 12px; color: #6B7280; margin-top: 2px; }

/* 성장/하락 배지 */
.badge-grow { background: #F0FDF4; color: #16A34A; font-size: 12px;
              font-weight: 700; padding: 2px 8px; border-radius: 20px; }
.badge-drop { background: #FEF2F2; color: #DC2626; font-size: 12px;
              font-weight: 700; padding: 2px 8px; border-radius: 20px; }

/* 테이블 */
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #F9FAFB; color: #374151; font-weight: 700;
                 padding: 8px 10px; border-bottom: 2px solid #E5E7EB; text-align: left; }
.data-table td { padding: 8px 10px; border-bottom: 1px solid #F3F4F6; color: #374151; }
.data-table tr:hover td { background: #F9FAFB; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  상수
# ══════════════════════════════════════════════════════
POSITIVE_COLOR = "#16A34A"
NEGATIVE_COLOR = "#DC2626"
NEUTRAL_COLOR  = "#6B7280"
PRIMARY_COLOR  = "#1D4ED8"
GITHUB_REPO    = "maggiohosu/jbl-dashboard"

CHART_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Noto Sans KR, sans-serif", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
)

FOLDER     = os.path.dirname(os.path.abspath(__file__))
LOCAL_JSON = os.path.join(FOLDER, "dash_data.json")

# ══════════════════════════════════════════════════════
#  데이터 로드
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def load_data():
    if os.path.exists(LOCAL_JSON):
        with open(LOCAL_JSON, encoding="utf-8") as f:
            return json.load(f)
    try:
        url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/dash_data.json"
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except Exception:
        return None

# ══════════════════════════════════════════════════════
#  헬퍼 함수
# ══════════════════════════════════════════════════════
def fmt_won(v, unit="원"):
    if not v: return f"0{unit}"
    if abs(v) >= 100_000_000:
        return f"{v/100_000_000:.1f}억{unit}"
    if abs(v) >= 10_000:
        return f"{v/10_000:.0f}만{unit}"
    return f"{int(v):,}{unit}"

def fmt_qty(v):
    return f"{int(v):,}개" if v else "0개"

def fmt_pct(v):
    if v is None: return "-"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v*100:.1f}%"

def growth_color(v):
    if v is None or v == 0: return NEUTRAL_COLOR
    return POSITIVE_COLOR if v > 0 else NEGATIVE_COLOR

def growth_tag(v):
    if v is None: return ""
    pct = v * 100
    sign = "▲" if pct >= 0 else "▼"
    color = POSITIVE_COLOR if pct >= 0 else NEGATIVE_COLOR
    return f'<span style="color:{color};font-weight:700">{sign}{abs(pct):.1f}%</span>'

def pct_color(rate):
    if rate >= 1.0: return {"bg":"#F0FDF4","text":"#16A34A","fill":"#16A34A","tag":"green","lbl":"목표 달성"}
    if rate >= 0.7: return {"bg":"#FFFBEB","text":"#D97706","fill":"#D97706","tag":"yellow","lbl":"순조"}
    return              {"bg":"#FEF2F2","text":"#DC2626","fill":"#DC2626","tag":"red","lbl":"달성 필요"}

def linear_trend(ys):
    n = len(ys)
    if n < 2: return ys
    xs = list(range(n)); mx = sum(xs)/n; my = sum(ys)/n
    den = sum((x-mx)**2 for x in xs)
    if den == 0: return [my]*n
    s = sum((xs[i]-mx)*(ys[i]-my) for i in range(n)) / den
    b = my - s*mx
    return [s*x + b for x in xs]

def sum_by_month(data: dict, month_str: str) -> float:
    """월별 집계 딕셔너리에서 특정 월 값 반환"""
    if not data: return 0
    return data.get(month_str, 0) or 0

def section_header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)

def no_data(msg="데이터가 없습니다."):
    st.info(msg)

# ══════════════════════════════════════════════════════
#  차트 공통 함수
# ══════════════════════════════════════════════════════
def make_mom_chart(month_rev: dict, mom_data: dict, color: str, name: str = "", height: int = 300):
    """MoM bar+line 혼합 차트"""
    months = sorted(month_rev.keys())
    if not months:
        return None
    revs  = [month_rev[m] / 10000 for m in months]
    rates = [mom_data.get(m, 0) * 100 if mom_data.get(m) is not None else 0 for m in months]

    fig = go.Figure()
    fig.add_bar(
        x=months, y=revs,
        name=f"{name} 매출(만원)", marker_color=color, opacity=0.8,
        yaxis="y1",
        hovertemplate="%{x}<br>매출: %{y:,.0f}만원<extra></extra>",
    )
    fig.add_scatter(
        x=months, y=rates,
        name="MoM(%)", mode="lines+markers+text",
        text=[f"{r:+.1f}%" for r in rates],
        textposition="top center",
        textfont=dict(size=10, color="#374151"),
        line=dict(color="#374151", width=2), marker=dict(size=6),
        yaxis="y2",
        hovertemplate="%{x}<br>MoM: %{y:+.1f}%<extra></extra>",
    )
    fig.update_layout(
        **CHART_LAYOUT,
        height=height,
        yaxis=dict(title="매출(만원)", showgrid=True, gridcolor="#F3F4F6"),
        yaxis2=dict(
            title="전월대비(%)", overlaying="y", side="right",
            showgrid=False, zeroline=True, zerolinecolor="#9CA3AF",
        ),
    )
    return fig

def make_wow_chart(wk_rev: dict, wow_data: dict, wk_labels: dict, color: str, name: str = "", height: int = 300):
    """WoW bar+line 혼합 차트"""
    wks = sorted(wk_rev.keys(), key=lambda x: int(x))
    if not wks:
        return None
    lbls  = [wk_labels.get(w, f"{w}주차") for w in wks]
    revs  = [wk_rev[w] / 10000 for w in wks]
    rates = [wow_data.get(w, 0) * 100 if wow_data.get(w) is not None else 0 for w in wks]

    fig = go.Figure()
    fig.add_bar(
        x=lbls, y=revs,
        name=f"{name} 매출(만원)", marker_color=color, opacity=0.8,
        yaxis="y1",
        hovertemplate="%{x}<br>매출: %{y:,.0f}만원<extra></extra>",
    )
    fig.add_scatter(
        x=lbls, y=rates,
        name="WoW(%)", mode="lines+markers+text",
        text=[f"{r:+.1f}%" for r in rates],
        textposition="top center",
        textfont=dict(size=10, color="#374151"),
        line=dict(color="#374151", width=2), marker=dict(size=6),
        yaxis="y2",
        hovertemplate="%{x}<br>WoW: %{y:+.1f}%<extra></extra>",
    )
    fig.update_layout(
        **CHART_LAYOUT,
        height=height,
        yaxis=dict(title="매출(만원)", showgrid=True, gridcolor="#F3F4F6"),
        yaxis2=dict(
            title="전주대비(%)", overlaying="y", side="right",
            showgrid=False, zeroline=True, zerolinecolor="#9CA3AF",
        ),
    )
    return fig

def show_top3_cards(top3_data, col_name="model"):
    medals = ["🥇", "🥈", "🥉"]
    for i, item in enumerate(top3_data[:3]):
        name = item.get(col_name, item.get("cat", item.get("model", "")))
        rev  = item.get("rev", 0)
        qty  = item.get("qty", 0)
        st.markdown(f"""
        <div class="rank-card">
          <div class="rank-medal">{medals[i]}</div>
          <div>
            <div class="rank-name">{name}</div>
            <div class="rank-sub">{fmt_won(rev)} · {qty:,}개</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def show_growth_list(items, name_key, prefix="▲"):
    """성장/하락 목록 표시"""
    if not items:
        no_data(); return
    rows = []
    for item in items:
        name = item.get(name_key, "")
        prev = item.get("prevRev", 0)
        curr = item.get("currRev", 0)
        rate = item.get("growthRate", 0)
        rows.append({
            "이름": name,
            "전기": fmt_won(prev),
            "현기": fmt_won(curr),
            "증감율": fmt_pct(rate),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════
#  TAB 1: 개요 (Overview)
# ══════════════════════════════════════════════════════
def tab_overview(D):
    markets      = D.get("markets", [])
    mkt_colors   = D.get("mktColors", {})
    report_year  = D.get("reportYear", 2026)
    report_month = D.get("reportMonth", 4)
    data_months  = D.get("dataMonths", [])
    cur_m        = f"{report_year}-{report_month:02d}"
    prev_m_idx   = data_months.index(cur_m) - 1 if cur_m in data_months and data_months.index(cur_m) > 0 else -1
    prev_m       = data_months[prev_m_idx] if prev_m_idx >= 0 else None

    mkt_month_rev = D.get("mktMonthRev", {})
    mkt_month_qty = D.get("mktMonthQty", {})
    monthly_tgts  = D.get("monthlyTargets", {})

    # 전체 이번달/전월 매출
    total_curr = sum(mkt_month_rev.get(m, {}).get(cur_m, 0) or 0 for m in markets)
    total_prev = sum(mkt_month_rev.get(m, {}).get(prev_m, 0) or 0 for m in markets) if prev_m else 0
    total_qty  = sum(mkt_month_qty.get(m, {}).get(cur_m, 0) or 0 for m in markets)

    # 전체 기간 매출
    all_rev = sum(
        v for m in markets
        for v in mkt_month_rev.get(m, {}).values()
        if v
    )

    mom_rate = (total_curr - total_prev) / total_prev if total_prev else None
    mom_html = growth_tag(mom_rate) if mom_rate is not None else ""

    # 이번달 목표 / 달성률
    total_tgt = sum(
        (monthly_tgts.get(m, {}).get(str(report_month), 0) or 0)
        for m in markets
    )
    ach_rate = total_curr / total_tgt if total_tgt else 0

    # ── KPI 카드 행 ─────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">전체 누적 매출</div>
          <div class="kpi-value">{fmt_won(all_rev)}</div>
          <div class="kpi-sub">{D.get("period", "-")}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{report_month}월 매출</div>
          <div class="kpi-value">{fmt_won(total_curr)}</div>
          <div class="kpi-sub">전월 대비 {mom_html}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        pc = pct_color(ach_rate)
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{report_month}월 목표 달성률</div>
          <div class="kpi-value" style="color:{pc['text']}">{ach_rate*100:.1f}%</div>
          <div class="kpi-sub">목표: {fmt_won(total_tgt)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{report_month}월 판매 수량</div>
          <div class="kpi-value">{total_qty:,}개</div>
          <div class="kpi-sub">{len(D.get("modelList", []))}개 모델</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── 마켓별 목표 달성률 게이지 ────────────────────────
    section_header(f"마켓별 목표 달성률 ({report_month}월)")
    cards_html = '<div class="mkt-kpi-grid">'
    for m in markets:
        col   = mkt_colors.get(m, "#607D8B")
        act   = mkt_month_rev.get(m, {}).get(cur_m, 0) or 0
        tgt   = monthly_tgts.get(m, {}).get(str(report_month), 0) or 0
        rate  = act / tgt if tgt else 0
        pct   = min(100, rate * 100)
        pc    = pct_color(rate)
        cards_html += f"""
        <div class="mkt-kpi-card" style="border-left-color:{col}">
          <div class="mkt-kpi-header">
            <div class="mkt-kpi-name" style="color:{col}">{m}</div>
            <div class="mkt-kpi-badge" style="background:{pc['bg']};color:{pc['text']}">{rate*100:.1f}%</div>
          </div>
          <div class="mkt-kpi-actual">{fmt_won(act)}</div>
          <div class="mkt-kpi-meta">목표 {fmt_won(tgt)}</div>
          <div class="mkt-kpi-bar-bg">
            <div class="mkt-kpi-bar-fill" style="width:{pct:.0f}%;background:{pc['fill']}"></div>
          </div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── 달성률 바 차트 ──────────────────────────────────
    rates_list  = []
    colors_list = []
    for m in markets:
        act = mkt_month_rev.get(m, {}).get(cur_m, 0) or 0
        tgt = monthly_tgts.get(m, {}).get(str(report_month), 0) or 0
        r   = act / tgt * 100 if tgt else 0
        rates_list.append(r)
        colors_list.append(pct_color(r/100)["fill"])

    fig = go.Figure()
    fig.add_bar(
        x=markets, y=rates_list,
        marker_color=colors_list, marker_line_width=0,
        text=[f"{r:.1f}%" for r in rates_list],
        textposition="outside", textfont_size=12,
        hovertemplate="<b>%{x}</b><br>달성률: %{y:.1f}%<extra></extra>",
    )
    fig.add_hline(y=100, line_dash="dot", line_color="rgba(22,163,74,.5)", line_width=1.5)
    fig.update_layout(
        **CHART_LAYOUT, height=280,
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="달성률(%)",
                   range=[0, max(max(rates_list) * 1.2, 120)]),
        xaxis=dict(showgrid=False),
        showlegend=False,
        title=dict(text=f"{report_month}월 마켓별 달성률", font=dict(size=14), x=0.01),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── 이번주 / 최근 주차 요약 ─────────────────────────
    section_header("주차별 매출 요약")
    wk_labels = D.get("weekLabels", {})
    wk_count  = int(D.get("weekCount", 0))
    mkt_wk_rev = D.get("mktWkRev", {})

    if wk_count and wk_labels:
        wks  = [str(w) for w in range(1, wk_count + 1)]
        lbls = [wk_labels.get(w, f"{w}주차") for w in wks]
        totals = [
            sum(mkt_wk_rev.get(m, {}).get(w, 0) or 0 for m in markets)
            for w in wks
        ]
        fig2 = go.Figure()
        colors_w = [PRIMARY_COLOR] * (len(wks) - 1) + ["#F97316"]
        fig2.add_bar(
            x=lbls, y=[t / 10000 for t in totals],
            marker_color=colors_w, marker_line_width=0,
            text=[f"{t/10000:,.0f}만" for t in totals],
            textposition="outside",
            hovertemplate="%{x}<br>%{y:,.0f}만원<extra></extra>",
        )
        fig2.update_layout(
            **CHART_LAYOUT, height=240, showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="만원"),
            xaxis=dict(showgrid=False),
            title=dict(text=f"{report_month}월 주차별 전체 매출", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # 현재 주차 KPI
        last_w    = wks[-1]
        last_rev  = sum(mkt_wk_rev.get(m, {}).get(last_w, 0) or 0 for m in markets)
        prev_w    = wks[-2] if len(wks) >= 2 else None
        prev_rev  = sum(mkt_wk_rev.get(m, {}).get(prev_w, 0) or 0 for m in markets) if prev_w else 0
        wow       = (last_rev - prev_rev) / prev_rev if prev_rev else None

        st.markdown(f"""
        <div class="kpi-card" style="max-width:320px">
          <div class="kpi-label">최근 주차 ({wk_labels.get(last_w, "")})</div>
          <div class="kpi-value">{fmt_won(last_rev)}</div>
          <div class="kpi-sub">전주 대비 {growth_tag(wow)}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        no_data("주차 데이터가 없습니다.")

    # ── TOP3 모델 (이번달) ───────────────────────────────
    st.markdown("---")
    section_header(f"{report_month}월 TOP3 모델")
    top3_model = D.get("top3ModelMonth", {}).get(cur_m, [])
    if top3_model:
        show_top3_cards(top3_model, col_name="model")
    else:
        no_data("TOP3 모델 데이터가 없습니다.")

# ══════════════════════════════════════════════════════
#  TAB 2: 마켓별 분석
# ══════════════════════════════════════════════════════
def tab_market(D):
    markets       = D.get("markets", [])
    mkt_colors    = D.get("mktColors", {})
    data_months   = D.get("dataMonths", [])
    report_month  = D.get("reportMonth", 4)
    report_year   = D.get("reportYear", 2026)
    cur_m         = f"{report_year}-{report_month:02d}"
    wk_labels     = D.get("weekLabels", {})
    wk_count      = int(D.get("weekCount", 0))

    mkt_month_rev = D.get("mktMonthRev", {})
    mkt_month_qty = D.get("mktMonthQty", {})
    mkt_mom       = D.get("mktMoM", {})
    mkt_wk_rev    = D.get("mktWkRev", {})
    mkt_wk_qty    = D.get("mktWkQty", {})
    mkt_wow       = D.get("mktWoW", {})
    monthly_tgts  = D.get("monthlyTargets", {})
    cat_share     = D.get("mktCatShareMonth", {})
    mkt_share     = D.get("mktShareMonth", {})
    return_rate   = D.get("returnRateMkt", {})
    return_qty    = D.get("returnQtyMkt", {})
    return_rev    = D.get("returnRevMkt", {})
    return_rate_m = D.get("returnRateMktMonth", {})

    # ── (1) 마켓별 MoM 추이 ────────────────────────────
    section_header("(1) 마켓별 전월대비(MoM) 추이")
    sel_mkt_mom = st.selectbox("마켓 선택", markets, key="mkt_mom_sel")
    col = mkt_colors.get(sel_mkt_mom, PRIMARY_COLOR)
    fig = make_mom_chart(
        mkt_month_rev.get(sel_mkt_mom, {}),
        mkt_mom.get(sel_mkt_mom, {}),
        color=col, name=sel_mkt_mom,
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        no_data()

    # ── (2) 마켓별 WoW 추이 ────────────────────────────
    section_header("(2) 마켓별 전주대비(WoW) 추이")
    sel_mkt_wow = st.selectbox("마켓 선택 (WoW)", markets, key="mkt_wow_sel")
    col2 = mkt_colors.get(sel_mkt_wow, PRIMARY_COLOR)
    fig2 = make_wow_chart(
        mkt_wk_rev.get(sel_mkt_wow, {}),
        mkt_wow.get(sel_mkt_wow, {}),
        wk_labels, color=col2, name=sel_mkt_wow,
    )
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
    else:
        no_data()

    # ── (7) 마켓별 매출 비중 ─────────────────────────────
    st.markdown("---")
    section_header("(7) 마켓별 매출 비중")
    sel_month_share = st.selectbox("기준 월", data_months, index=len(data_months)-1, key="mkt_share_month")
    share_data = mkt_share.get(sel_month_share, {})
    if share_data:
        labels = list(share_data.keys())
        values = [share_data[k] * 100 for k in labels]
        colors_pie = [mkt_colors.get(l, "#9CA3AF") for l in labels]
        fig3 = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.4, marker_colors=colors_pie,
            textinfo="label+percent",
            hovertemplate="%{label}<br>비중: %{value:.1f}%<extra></extra>",
        ))
        fig3.update_layout(
            **CHART_LAYOUT, height=320,
            title=dict(text=f"{sel_month_share} 마켓 비중", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        no_data()

    # ── (9) 마켓별 세그먼트 비중 (스택 바) ──────────────
    st.markdown("---")
    section_header("(9) 마켓별 세그먼트 비중")
    sel_seg_month = st.selectbox("기준 월", data_months, index=len(data_months)-1, key="mkt_seg_month")
    seg_share_data = D.get("mktCatShareMonth", {}).get(sel_seg_month, {})
    cats      = D.get("categories", [])
    cat_colors = D.get("catColors", {})

    if seg_share_data and cats:
        fig4 = go.Figure()
        for cat in cats:
            vals = [seg_share_data.get(m, {}).get(cat, 0) * 100 for m in markets]
            fig4.add_bar(
                name=cat, x=markets, y=vals,
                marker_color=cat_colors.get(cat, "#9CA3AF"),
                hovertemplate=f"{cat}<br>%{{x}}<br>%{{y:.1f}}%<extra></extra>",
            )
        fig4.update_layout(
            **CHART_LAYOUT, height=320,
            barmode="stack",
            yaxis=dict(title="비중(%)", showgrid=True, gridcolor="#F3F4F6"),
            xaxis=dict(showgrid=False),
            title=dict(text=f"{sel_seg_month} 마켓별 세그먼트 비중", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        no_data()

    # ── (12) 마켓별 매출 MoM 비교 ──────────────────────
    st.markdown("---")
    section_header("(12) 마켓별 월별 매출 비교")
    sel_mkts_cmp = st.multiselect("비교할 마켓 선택", markets, default=markets[:3], key="mkt_cmp_sel")
    if sel_mkts_cmp:
        fig5 = go.Figure()
        for m in sel_mkts_cmp:
            m_data = mkt_month_rev.get(m, {})
            months_s = sorted(m_data.keys())
            revs_s   = [m_data[mo] / 10000 for mo in months_s]
            fig5.add_scatter(
                x=months_s, y=revs_s, name=m, mode="lines+markers",
                line=dict(color=mkt_colors.get(m, "#9CA3AF"), width=2),
                marker=dict(size=6),
                hovertemplate=f"{m}<br>%{{x}}<br>%{{y:,.0f}}만원<extra></extra>",
            )
        fig5.update_layout(
            **CHART_LAYOUT, height=320,
            yaxis=dict(title="매출(만원)", showgrid=True, gridcolor="#F3F4F6"),
            xaxis=dict(showgrid=False),
            title=dict(text="마켓별 월별 매출 추이", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        no_data("마켓을 선택해주세요.")

    # ── (15) 마켓별 반품율 ───────────────────────────────
    st.markdown("---")
    section_header("(15) 마켓별 반품율")
    if return_rate:
        r_markets = list(return_rate.keys())
        r_rates   = [return_rate[m] * 100 for m in r_markets]
        r_colors  = [mkt_colors.get(m, "#9CA3AF") for m in r_markets]
        fig6 = go.Figure()
        fig6.add_bar(
            x=r_markets, y=r_rates,
            marker_color=r_colors, marker_line_width=0,
            text=[f"{r:.1f}%" for r in r_rates],
            textposition="outside",
            hovertemplate="%{x}<br>반품율: %{y:.1f}%<extra></extra>",
        )
        fig6.update_layout(
            **CHART_LAYOUT, height=260, showlegend=False,
            yaxis=dict(title="반품율(%)", showgrid=True, gridcolor="#F3F4F6"),
            xaxis=dict(showgrid=False),
            title=dict(text="마켓별 반품율", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig6, use_container_width=True)

        # 반품 상세 테이블
        rows_r = []
        for m in r_markets:
            rows_r.append({
                "마켓": m,
                "반품율": f"{return_rate.get(m,0)*100:.1f}%",
                "반품수량": fmt_qty(return_qty.get(m, 0)),
                "반품금액": fmt_won(return_rev.get(m, 0)),
            })
        st.dataframe(pd.DataFrame(rows_r), use_container_width=True, hide_index=True)
    else:
        no_data()

# ══════════════════════════════════════════════════════
#  TAB 3: 모델별 분석
# ══════════════════════════════════════════════════════
def tab_model(D):
    model_list     = D.get("modelList", [])
    data_months    = D.get("dataMonths", [])
    report_month   = D.get("reportMonth", 4)
    report_year    = D.get("reportYear", 2026)
    cur_m          = f"{report_year}-{report_month:02d}"
    wk_labels      = D.get("weekLabels", {})
    wk_count       = int(D.get("weekCount", 0))

    model_month_rev = D.get("modelMonthRev", {})
    model_month_qty = D.get("modelMonthQty", {})
    model_mom       = D.get("modelMoM", {})
    model_wk_rev    = D.get("modelWkRev", {})
    model_wk_qty    = D.get("modelWkQty", {})
    model_wow       = D.get("modelWoW", {})
    model_mkt_growth= D.get("modelMktGrowth", {})
    growth_model_m  = D.get("growthModelMonth", {})
    decline_model_m = D.get("declineModelMonth", {})
    growth_model_w  = D.get("growthModelWeek", {})
    decline_model_w = D.get("declineModelWeek", {})
    top3_model_m    = D.get("top3ModelMonth", {})
    top3_model_w    = D.get("top3ModelWeek", {})

    if not model_list:
        no_data("모델 목록이 없습니다."); return

    # ── (1) 모델별 MoM 추이 ────────────────────────────
    section_header("(1) 모델별 전월대비(MoM) 추이")
    sel_model_mom = st.selectbox("모델 선택", model_list, key="mdl_mom_sel")
    fig = make_mom_chart(
        model_month_rev.get(sel_model_mom, {}),
        model_mom.get(sel_model_mom, {}),
        color=PRIMARY_COLOR, name=sel_model_mom,
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        no_data()

    # ── (2) 모델별 WoW 추이 ────────────────────────────
    section_header("(2) 모델별 전주대비(WoW) 추이")
    sel_model_wow = st.selectbox("모델 선택 (WoW)", model_list, key="mdl_wow_sel")
    fig2 = make_wow_chart(
        model_wk_rev.get(sel_model_wow, {}),
        model_wow.get(sel_model_wow, {}),
        wk_labels, color="#7C3AED", name=sel_model_wow,
    )
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
    else:
        no_data()

    # ── (3) 주별/월별 TOP3 모델 ────────────────────────
    st.markdown("---")
    section_header("(3) TOP3 모델")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("월별 TOP3")
        sel_top3_month = st.selectbox("기준 월", data_months, index=len(data_months)-1, key="mdl_top3_month")
        top3_m = top3_model_m.get(sel_top3_month, [])
        if top3_m:
            show_top3_cards(top3_m, col_name="model")
        else:
            no_data()
    with c2:
        st.caption("주별 TOP3")
        wk_opts = [wk_labels.get(str(w), f"{w}주차") for w in range(1, wk_count+1)] if wk_count else []
        if wk_opts:
            sel_top3_wk_lbl = st.selectbox("기준 주차", wk_opts, key="mdl_top3_wk")
            sel_top3_wk = str(wk_opts.index(sel_top3_wk_lbl) + 1) if sel_top3_wk_lbl in wk_opts else "1"
            top3_w = top3_model_w.get(sel_top3_wk, [])
            if top3_w:
                show_top3_cards(top3_w, col_name="model")
            else:
                no_data()
        else:
            no_data("주차 데이터가 없습니다.")

    # ── (5) 성장 모델 ───────────────────────────────────
    st.markdown("---")
    section_header("(5) 전월 대비 성장 모델")
    growth_data = growth_model_m.get(cur_m, [])
    if growth_data:
        sorted_growth = sorted(growth_data, key=lambda x: x.get("growthRate", 0), reverse=True)
        show_growth_list(sorted_growth, "model")
    else:
        no_data()

    # ── (6) 하락 모델 ───────────────────────────────────
    section_header("(6) 전월 대비 하락 모델")
    decline_data = decline_model_m.get(cur_m, [])
    if decline_data:
        sorted_decline = sorted(decline_data, key=lambda x: x.get("growthRate", 0))
        show_growth_list(sorted_decline, "model")
    else:
        no_data()

    # ── (10) 모델별 성장/하락 마켓 ─────────────────────
    st.markdown("---")
    section_header("(10) 전월대비 마켓 성장/하락 (모델별)")
    sel_model_mkt = st.selectbox("모델 선택", model_list, key="mdl_mkt_sel")
    mkt_data = model_mkt_growth.get(sel_model_mkt, {})
    c1, c2 = st.columns(2)
    with c1:
        st.caption("성장 마켓 BEST3")
        best3 = mkt_data.get("best3", [])
        if best3:
            show_growth_list(best3, "market")
        else:
            no_data()
    with c2:
        st.caption("하락 마켓 WORST3")
        worst3 = mkt_data.get("worst3", [])
        if worst3:
            show_growth_list(worst3, "market")
        else:
            no_data()

    # ── (13) 멀티 모델 MoM 비교 ─────────────────────────
    st.markdown("---")
    section_header("(13) 모델별 월별 매출 비교")
    sel_models_cmp = st.multiselect(
        "비교할 모델 선택", model_list,
        default=model_list[:3] if len(model_list) >= 3 else model_list,
        key="mdl_cmp_sel",
    )
    if sel_models_cmp:
        fig5 = go.Figure()
        palette = ["#1D4ED8","#7C3AED","#059669","#DC2626","#D97706","#0891B2","#9D174D","#92400E"]
        for i, mdl in enumerate(sel_models_cmp):
            m_data  = model_month_rev.get(mdl, {})
            months_s= sorted(m_data.keys())
            revs_s  = [m_data[mo] / 10000 for mo in months_s]
            fig5.add_scatter(
                x=months_s, y=revs_s, name=mdl, mode="lines+markers",
                line=dict(color=palette[i % len(palette)], width=2),
                marker=dict(size=6),
                hovertemplate=f"{mdl}<br>%{{x}}<br>%{{y:,.0f}}만원<extra></extra>",
            )
        fig5.update_layout(
            **CHART_LAYOUT, height=320,
            yaxis=dict(title="매출(만원)", showgrid=True, gridcolor="#F3F4F6"),
            xaxis=dict(showgrid=False),
            title=dict(text="모델별 월별 매출 비교", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        no_data("모델을 선택해주세요.")

# ══════════════════════════════════════════════════════
#  TAB 4: 세그먼트별 분석
# ══════════════════════════════════════════════════════
def tab_segment(D):
    cats        = D.get("categories", [])
    cat_colors  = D.get("catColors", {})
    data_months = D.get("dataMonths", [])
    report_month= D.get("reportMonth", 4)
    report_year = D.get("reportYear", 2026)
    cur_m       = f"{report_year}-{report_month:02d}"
    wk_labels   = D.get("weekLabels", {})
    wk_count    = int(D.get("weekCount", 0))
    markets     = D.get("markets", [])
    mkt_colors  = D.get("mktColors", {})

    cat_month_rev = D.get("catMonthRev", {})
    cat_month_qty = D.get("catMonthQty", {})
    cat_mom       = D.get("catMoM", {})
    cat_wk_rev    = D.get("catWkRev", {})
    cat_wk_qty    = D.get("catWkQty", {})
    cat_wow       = D.get("catWoW", {})
    growth_cat_m  = D.get("growthCatMonth", {})
    decline_cat_m = D.get("declineCatMonth", {})
    top3_cat_m    = D.get("top3CatMonth", {})
    top3_cat_w    = D.get("top3CatWeek", {})
    cat_share_m   = D.get("catShareMonth", {})
    mkt_cat_share = D.get("mktCatShareMonth", {})

    if not cats:
        no_data("세그먼트 데이터가 없습니다."); return

    # ── (1) 세그먼트별 MoM 추이 ────────────────────────
    section_header("(1) 세그먼트별 전월대비(MoM) 추이")
    sel_cat_mom = st.selectbox("세그먼트 선택", cats, key="seg_mom_sel")
    col = cat_colors.get(sel_cat_mom, PRIMARY_COLOR)
    fig = make_mom_chart(
        cat_month_rev.get(sel_cat_mom, {}),
        cat_mom.get(sel_cat_mom, {}),
        color=col, name=sel_cat_mom,
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        no_data()

    # ── (2) 세그먼트별 WoW 추이 ────────────────────────
    section_header("(2) 세그먼트별 전주대비(WoW) 추이")
    sel_cat_wow = st.selectbox("세그먼트 선택 (WoW)", cats, key="seg_wow_sel")
    col2 = cat_colors.get(sel_cat_wow, PRIMARY_COLOR)
    fig2 = make_wow_chart(
        cat_wk_rev.get(sel_cat_wow, {}),
        cat_wow.get(sel_cat_wow, {}),
        wk_labels, color=col2, name=sel_cat_wow,
    )
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
    else:
        no_data()

    # ── (3) TOP3 세그먼트 ───────────────────────────────
    st.markdown("---")
    section_header("(3) TOP3 세그먼트")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("월별 TOP3")
        sel_top3_month = st.selectbox("기준 월", data_months, index=len(data_months)-1, key="seg_top3_month")
        top3_m = top3_cat_m.get(sel_top3_month, [])
        if top3_m:
            show_top3_cards(top3_m, col_name="cat")
        else:
            no_data()
    with c2:
        st.caption("주별 TOP3")
        wk_opts = [wk_labels.get(str(w), f"{w}주차") for w in range(1, wk_count+1)] if wk_count else []
        if wk_opts:
            sel_top3_wk_lbl = st.selectbox("기준 주차", wk_opts, key="seg_top3_wk")
            sel_top3_wk = str(wk_opts.index(sel_top3_wk_lbl) + 1)
            top3_w = top3_cat_w.get(sel_top3_wk, [])
            if top3_w:
                show_top3_cards(top3_w, col_name="cat")
            else:
                no_data()
        else:
            no_data()

    # ── (5) 성장 세그먼트 ──────────────────────────────
    st.markdown("---")
    section_header("(5) 전월 대비 성장 세그먼트")
    growth_data = growth_cat_m.get(cur_m, [])
    if growth_data:
        show_growth_list(sorted(growth_data, key=lambda x: x.get("growthRate",0), reverse=True), "cat")
    else:
        no_data()

    # ── (6) 하락 세그먼트 ──────────────────────────────
    section_header("(6) 전월 대비 하락 세그먼트")
    decline_data = decline_cat_m.get(cur_m, [])
    if decline_data:
        show_growth_list(sorted(decline_data, key=lambda x: x.get("growthRate",0)), "cat")
    else:
        no_data()

    # ── 카테고리별 매출 비중 ───────────────────────────
    st.markdown("---")
    section_header("카테고리별 매출 비중")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("파이 차트 (월별)")
        sel_share_month = st.selectbox("기준 월", data_months, index=len(data_months)-1, key="seg_share_month")
        share_data = cat_share_m.get(sel_share_month, {})
        if share_data:
            labels = list(share_data.keys())
            values = [share_data[k] * 100 for k in labels]
            colors_pie = [cat_colors.get(l, "#9CA3AF") for l in labels]
            fig3 = go.Figure(go.Pie(
                labels=labels, values=values,
                hole=0.4, marker_colors=colors_pie,
                textinfo="label+percent",
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
            ))
            fig3.update_layout(
                **CHART_LAYOUT, height=300,
                title=dict(text=f"{sel_share_month} 카테고리 비중", font=dict(size=13), x=0.01),
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            no_data()

    with c2:
        st.caption("월별 스택 바")
        if cat_month_rev and data_months:
            fig4 = go.Figure()
            for cat in cats:
                vals = [cat_month_rev.get(cat, {}).get(mo, 0) or 0 for mo in data_months]
                # 비중으로 변환
                totals_mo = [
                    sum(cat_month_rev.get(c, {}).get(mo, 0) or 0 for c in cats)
                    for mo in data_months
                ]
                pcts = [v / t * 100 if t else 0 for v, t in zip(vals, totals_mo)]
                fig4.add_bar(
                    name=cat, x=data_months, y=pcts,
                    marker_color=cat_colors.get(cat, "#9CA3AF"),
                    hovertemplate=f"{cat}<br>%{{x}}<br>%{{y:.1f}}%<extra></extra>",
                )
            fig4.update_layout(
                **CHART_LAYOUT, height=300,
                barmode="stack",
                yaxis=dict(title="비중(%)", showgrid=True, gridcolor="#F3F4F6"),
                xaxis=dict(showgrid=False),
                title=dict(text="월별 세그먼트 비중", font=dict(size=13), x=0.01),
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            no_data()

    # ── (9) 마켓별 세그먼트 비중 ─────────────────────────
    st.markdown("---")
    section_header("(9) 마켓 선택 → 세그먼트 비중")
    sel_mkt_seg = st.selectbox("마켓 선택", markets, key="seg_mkt_sel")
    sel_seg_month2 = st.selectbox("기준 월", data_months, index=len(data_months)-1, key="seg_mkt_month")
    seg_mkt_data = mkt_cat_share.get(sel_seg_month2, {}).get(sel_mkt_seg, {})
    if seg_mkt_data:
        labels = list(seg_mkt_data.keys())
        values = [seg_mkt_data[k] * 100 for k in labels]
        colors_pie2 = [cat_colors.get(l, "#9CA3AF") for l in labels]
        fig5 = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.35, marker_colors=colors_pie2,
            textinfo="label+percent",
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
        ))
        fig5.update_layout(
            **CHART_LAYOUT, height=300,
            title=dict(text=f"{sel_mkt_seg} ({sel_seg_month2}) 세그먼트 비중", font=dict(size=13), x=0.01),
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        no_data()

    # ── (14) 세그먼트별 MoM 비교 ─────────────────────────
    st.markdown("---")
    section_header("(14) 세그먼트별 월별 매출 비교")
    sel_cats_cmp = st.multiselect(
        "비교할 세그먼트 선택", cats,
        default=cats[:3] if len(cats) >= 3 else cats,
        key="seg_cmp_sel",
    )
    if sel_cats_cmp:
        fig6 = go.Figure()
        for cat in sel_cats_cmp:
            m_data  = cat_month_rev.get(cat, {})
            months_s= sorted(m_data.keys())
            revs_s  = [m_data[mo] / 10000 for mo in months_s]
            fig6.add_scatter(
                x=months_s, y=revs_s, name=cat, mode="lines+markers",
                line=dict(color=cat_colors.get(cat, "#9CA3AF"), width=2),
                marker=dict(size=6),
                hovertemplate=f"{cat}<br>%{{x}}<br>%{{y:,.0f}}만원<extra></extra>",
            )
        fig6.update_layout(
            **CHART_LAYOUT, height=320,
            yaxis=dict(title="매출(만원)", showgrid=True, gridcolor="#F3F4F6"),
            xaxis=dict(showgrid=False),
            title=dict(text="세그먼트별 월별 매출 비교", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        no_data("세그먼트를 선택해주세요.")

# ══════════════════════════════════════════════════════
#  TAB 5: 추이 분석
# ══════════════════════════════════════════════════════
def tab_trend(D):
    markets     = D.get("markets", [])
    cats        = D.get("categories", [])
    model_list  = D.get("modelList", [])
    mkt_colors  = D.get("mktColors", {})
    cat_colors  = D.get("catColors", {})
    data_months = D.get("dataMonths", [])

    mkt_day_rev = D.get("mktDayRev", {})
    mkt_day_qty = D.get("mktDayQty", {})
    cat_day_rev = D.get("catDayRev", {})
    cat_day_qty = D.get("catDayQty", {})

    section_header("일별 매출 추이 분석")

    c1, c2, c3 = st.columns(3)
    with c1:
        view_type = st.radio("분류 기준", ["마켓별", "세그먼트별"], horizontal=True, key="tr_view")
    with c2:
        metric = st.radio("지표", ["매출", "수량"], horizontal=True, key="tr_metric")
    with c3:
        sel_month_tr = st.selectbox("기준 월", ["전체"] + data_months, key="tr_month")

    use_market = (view_type == "마켓별")
    use_rev    = (metric == "매출")

    if use_market:
        raw    = mkt_day_rev if use_rev else mkt_day_qty
        items  = markets
        colors = mkt_colors
        lbl    = "마켓"
    else:
        raw    = cat_day_rev if use_rev else cat_day_qty
        items  = cats
        colors = cat_colors
        lbl    = "세그먼트"

    all_dates = sorted({d for item in items for d in raw.get(item, {})})
    if sel_month_tr != "전체":
        all_dates = [d for d in all_dates if d.startswith(sel_month_tr)]

    if not all_dates:
        no_data("선택한 기간에 데이터가 없습니다."); return

    sel_items = st.multiselect(f"{lbl} 선택", items, default=items, key="tr_items")
    show_trend = st.checkbox("추세선 표시", value=False, key="tr_trend")

    if not sel_items:
        no_data(f"{lbl}를 선택해주세요."); return

    div    = 10000 if use_rev else 1
    y_unit = "만원" if use_rev else "개"

    fig = go.Figure()
    for item in sel_items:
        vals = raw.get(item, {})
        y    = [vals.get(d, 0) / div for d in all_dates]
        col  = colors.get(item, "#9CA3AF")
        fig.add_scatter(
            x=all_dates, y=y, name=item, mode="lines+markers",
            line=dict(color=col, width=2), marker=dict(size=3),
            hovertemplate=f"{item}<br>%{{x}}<br>%{{y:,.1f}}{y_unit}<extra></extra>",
        )
        if show_trend:
            ty = linear_trend(y)
            fig.add_scatter(
                x=all_dates, y=ty, mode="lines", showlegend=False,
                line=dict(color=col, width=1, dash="dot"), hoverinfo="skip",
            )
    fig.update_layout(
        **CHART_LAYOUT, height=400,
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title=y_unit),
        xaxis=dict(showgrid=False, tickangle=-45),
        title=dict(text=f"일별 {view_type} {metric} 추이", font=dict(size=14), x=0.01),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 기간 합계 요약
    with st.expander("기간 합계 보기"):
        rows = []
        for item in sel_items:
            vals  = raw.get(item, {})
            total = sum(vals.get(d, 0) for d in all_dates)
            rows.append({
                lbl: item,
                "합계": fmt_won(total) if use_rev else fmt_qty(total),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════
#  TAB 6: 성장/하락 분석
# ══════════════════════════════════════════════════════
def tab_growth(D):
    data_months   = D.get("dataMonths", [])
    report_month  = D.get("reportMonth", 4)
    report_year   = D.get("reportYear", 2026)
    cur_m         = f"{report_year}-{report_month:02d}"
    wk_labels     = D.get("weekLabels", {})
    wk_count      = int(D.get("weekCount", 0))
    markets       = D.get("markets", [])
    mkt_colors    = D.get("mktColors", {})
    cats          = D.get("categories", [])
    cat_colors    = D.get("catColors", {})

    growth_model_m  = D.get("growthModelMonth", {})
    decline_model_m = D.get("declineModelMonth", {})
    growth_model_w  = D.get("growthModelWeek", {})
    decline_model_w = D.get("declineModelWeek", {})
    growth_cat_m    = D.get("growthCatMonth", {})
    decline_cat_m   = D.get("declineCatMonth", {})
    mkt_mom         = D.get("mktMoM", {})
    mkt_month_rev   = D.get("mktMonthRev", {})

    # ── 전월 대비 성장/하락 TOP10 ─────────────────────
    section_header("전월 대비 성장/하락 분석")
    tab1, tab2 = st.tabs(["모델", "세그먼트"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"성장 TOP10 ({cur_m})")
            gdata = sorted(
                growth_model_m.get(cur_m, []),
                key=lambda x: x.get("growthRate", 0), reverse=True
            )[:10]
            if gdata:
                rows = [{"모델": i.get("model",""), "전기": fmt_won(i.get("prevRev",0)),
                         "현기": fmt_won(i.get("currRev",0)), "증감율": fmt_pct(i.get("growthRate"))}
                        for i in gdata]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                no_data()
        with c2:
            st.caption(f"하락 TOP10 ({cur_m})")
            ddata = sorted(
                decline_model_m.get(cur_m, []),
                key=lambda x: x.get("growthRate", 0)
            )[:10]
            if ddata:
                rows = [{"모델": i.get("model",""), "전기": fmt_won(i.get("prevRev",0)),
                         "현기": fmt_won(i.get("currRev",0)), "증감율": fmt_pct(i.get("growthRate"))}
                        for i in ddata]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                no_data()

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"성장 세그먼트 ({cur_m})")
            gdata2 = sorted(
                growth_cat_m.get(cur_m, []),
                key=lambda x: x.get("growthRate", 0), reverse=True
            )
            if gdata2:
                rows = [{"세그먼트": i.get("cat",""), "전기": fmt_won(i.get("prevRev",0)),
                         "현기": fmt_won(i.get("currRev",0)), "증감율": fmt_pct(i.get("growthRate"))}
                        for i in gdata2]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                no_data()
        with c2:
            st.caption(f"하락 세그먼트 ({cur_m})")
            ddata2 = sorted(
                decline_cat_m.get(cur_m, []),
                key=lambda x: x.get("growthRate", 0)
            )
            if ddata2:
                rows = [{"세그먼트": i.get("cat",""), "전기": fmt_won(i.get("prevRev",0)),
                         "현기": fmt_won(i.get("currRev",0)), "증감율": fmt_pct(i.get("growthRate"))}
                        for i in ddata2]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                no_data()

    # ── 전주 대비 성장/하락 TOP10 ─────────────────────
    st.markdown("---")
    section_header("전주 대비 성장/하락 분석")
    if wk_count:
        wk_opts = [str(w) for w in range(1, wk_count + 1)]
        wk_lbl_opts = [wk_labels.get(w, f"{w}주차") for w in wk_opts]
        sel_wk_lbl = st.selectbox("기준 주차", wk_lbl_opts, index=len(wk_lbl_opts)-1, key="gr_wk_sel")
        sel_wk = wk_opts[wk_lbl_opts.index(sel_wk_lbl)]

        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"성장 TOP10 ({sel_wk_lbl})")
            gw = sorted(
                growth_model_w.get(sel_wk, []),
                key=lambda x: x.get("growthRate", 0), reverse=True
            )[:10]
            if gw:
                rows = [{"모델": i.get("model",""), "전주": fmt_won(i.get("prevRev",0)),
                         "이번주": fmt_won(i.get("currRev",0)), "증감율": fmt_pct(i.get("growthRate"))}
                        for i in gw]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                no_data()
        with c2:
            st.caption(f"하락 TOP10 ({sel_wk_lbl})")
            dw = sorted(
                decline_model_w.get(sel_wk, []),
                key=lambda x: x.get("growthRate", 0)
            )[:10]
            if dw:
                rows = [{"모델": i.get("model",""), "전주": fmt_won(i.get("prevRev",0)),
                         "이번주": fmt_won(i.get("currRev",0)), "증감율": fmt_pct(i.get("growthRate"))}
                        for i in dw]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                no_data()
    else:
        no_data("주차 데이터가 없습니다.")

    # ── 히트맵: 마켓 × 월별 성장율 ─────────────────────
    st.markdown("---")
    section_header("히트맵: 마켓 × 월별 MoM 성장율")
    if mkt_mom and markets and data_months:
        z_vals = []
        text_vals = []
        for m in markets:
            row = []
            text_row = []
            for mo in data_months[1:]:  # 첫 달은 MoM 없음
                v = mkt_mom.get(m, {}).get(mo)
                row.append(v * 100 if v is not None else 0)
                text_row.append(fmt_pct(v) if v is not None else "-")
            z_vals.append(row)
            text_vals.append(text_row)

        x_months = data_months[1:]
        fig_hm = go.Figure(go.Heatmap(
            z=z_vals,
            x=x_months,
            y=markets,
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=11),
            colorscale=[
                [0.0, "#DC2626"],
                [0.5, "#FFFFFF"],
                [1.0, "#16A34A"],
            ],
            zmid=0,
            colorbar=dict(title="MoM(%)"),
            hovertemplate="%{y}<br>%{x}<br>MoM: %{z:.1f}%<extra></extra>",
        ))
        fig_hm.update_layout(
            **CHART_LAYOUT,
            height=max(280, len(markets) * 40 + 60),
            title=dict(text="마켓별 월별 MoM 히트맵", font=dict(size=14), x=0.01),
            xaxis=dict(title="월"),
            yaxis=dict(title="마켓"),
        )
        st.plotly_chart(fig_hm, use_container_width=True)
    else:
        no_data()

# ══════════════════════════════════════════════════════
#  TAB 7: 반품 분석
# ══════════════════════════════════════════════════════
def tab_return(D):
    markets       = D.get("markets", [])
    mkt_colors    = D.get("mktColors", {})
    data_months   = D.get("dataMonths", [])

    return_rate   = D.get("returnRateMkt", {})
    return_qty    = D.get("returnQtyMkt", {})
    return_rev    = D.get("returnRevMkt", {})
    return_rate_m = D.get("returnRateMktMonth", {})

    # ── 마켓별 반품율 바 차트 ───────────────────────────
    section_header("마켓별 반품율")
    if return_rate:
        r_markets = [m for m in markets if m in return_rate]
        r_rates   = [return_rate[m] * 100 for m in r_markets]
        r_colors  = [mkt_colors.get(m, "#9CA3AF") for m in r_markets]

        fig = go.Figure()
        fig.add_bar(
            x=r_markets, y=r_rates,
            marker_color=r_colors, marker_line_width=0,
            text=[f"{r:.1f}%" for r in r_rates],
            textposition="outside", textfont_size=12,
            hovertemplate="%{x}<br>반품율: %{y:.2f}%<extra></extra>",
        )
        fig.update_layout(
            **CHART_LAYOUT, height=300, showlegend=False,
            yaxis=dict(title="반품율(%)", showgrid=True, gridcolor="#F3F4F6",
                       range=[0, max(r_rates) * 1.3 if r_rates else 10]),
            xaxis=dict(showgrid=False),
            title=dict(text="마켓별 반품율", font=dict(size=14), x=0.01),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        no_data("반품율 데이터가 없습니다.")

    # ── 월별 반품율 추이 ────────────────────────────────
    st.markdown("---")
    section_header("월별 반품율 추이 (마켓별)")
    if return_rate_m and data_months:
        sel_mkts_ret = st.multiselect(
            "마켓 선택", markets, default=markets[:4] if len(markets) >= 4 else markets,
            key="ret_mkts_sel",
        )
        if sel_mkts_ret:
            fig2 = go.Figure()
            for m in sel_mkts_ret:
                rates_mo = [
                    (return_rate_m.get(mo, {}).get(m, 0) or 0) * 100
                    for mo in data_months
                ]
                fig2.add_scatter(
                    x=data_months, y=rates_mo, name=m, mode="lines+markers",
                    line=dict(color=mkt_colors.get(m, "#9CA3AF"), width=2),
                    marker=dict(size=6),
                    hovertemplate=f"{m}<br>%{{x}}<br>반품율: %{{y:.2f}}%<extra></extra>",
                )
            fig2.update_layout(
                **CHART_LAYOUT, height=320,
                yaxis=dict(title="반품율(%)", showgrid=True, gridcolor="#F3F4F6"),
                xaxis=dict(showgrid=False),
                title=dict(text="월별 마켓 반품율 추이", font=dict(size=14), x=0.01),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            no_data("마켓을 선택해주세요.")
    else:
        no_data()

    # ── 반품 상세 테이블 ────────────────────────────────
    st.markdown("---")
    section_header("마켓별 반품 상세")
    rows_r = []
    for m in markets:
        rate = return_rate.get(m)
        qty  = return_qty.get(m, 0)
        rev  = return_rev.get(m, 0)
        if rate is not None or qty or rev:
            rows_r.append({
                "마켓": m,
                "반품율": f"{rate*100:.2f}%" if rate is not None else "-",
                "반품수량": fmt_qty(qty),
                "반품금액": fmt_won(rev),
            })
    if rows_r:
        st.dataframe(pd.DataFrame(rows_r), use_container_width=True, hide_index=True)
    else:
        no_data()

    # ── 월별 반품 상세 테이블 ────────────────────────────
    if return_rate_m and data_months:
        st.markdown("---")
        section_header("월별 반품율 상세 테이블")
        sel_ret_month = st.selectbox("기준 월", data_months, index=len(data_months)-1, key="ret_month_sel")
        month_data = return_rate_m.get(sel_ret_month, {})
        if month_data:
            rows_m = []
            for m in markets:
                rate = month_data.get(m)
                if rate is not None:
                    rows_m.append({"마켓": m, "반품율": f"{rate*100:.2f}%"})
            if rows_m:
                st.dataframe(pd.DataFrame(rows_m), use_container_width=True, hide_index=True)
            else:
                no_data()
        else:
            no_data()

# ══════════════════════════════════════════════════════
#  메인
# ══════════════════════════════════════════════════════
def main():
    # 헤더
    col1, col2, col3 = st.columns([4, 3, 2])
    with col1:
        st.markdown("## 🎵 JBL 실판매 대시보드")
    with col2:
        pass  # 데이터 로드 후 표시
    with col3:
        refresh = st.button("🔄 새로고침", use_container_width=True)
        if refresh:
            st.cache_data.clear()
            st.rerun()

    # 데이터 로드
    with st.spinner("데이터 로딩 중..."):
        D = load_data()

    if D is None:
        st.error("데이터를 불러올 수 없습니다. dash_data.json 파일을 확인해주세요.")
        return

    # 헤더 메타 정보
    with col2:
        st.caption(f"기간: {D.get('period', '-')} | 업데이트: {D.get('updated', '-')}")

    # 탭
    tabs = st.tabs([
        "📊 개요",
        "🏪 마켓별",
        "📦 모델별",
        "🎯 세그먼트별",
        "📈 추이",
        "🔄 성장/하락",
        "↩️ 반품",
    ])

    with tabs[0]:
        tab_overview(D)
    with tabs[1]:
        tab_market(D)
    with tabs[2]:
        tab_model(D)
    with tabs[3]:
        tab_segment(D)
    with tabs[4]:
        tab_trend(D)
    with tabs[5]:
        tab_growth(D)
    with tabs[6]:
        tab_return(D)


if __name__ == "__main__":
    main()
