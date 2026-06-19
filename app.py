import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(page_title="SET50 Shareholder Network", layout="wide", page_icon="📈")

st.markdown("""
<style>
.metric-card { background: #f8fafc; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.metric-value { font-size: 2rem; font-weight: 700; color: #0ea5e9; }
.metric-label { font-size: 0.8rem; color: #64748b; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📈 SET50 Social Network: Listed Companies & Major Stakeholders")
st.markdown("<p style='color:#64748b;margin-top:-12px;'>Interactive visualization of ownership relationships between SET50 companies and their top 5 shareholders (Stock Exchange of Thailand)</p>", unsafe_allow_html=True)

# ── DATA ───────────────────────────────────────────────────────────────────────

set50_companies = {
    "ADVANC": "Advanced Info Service", "AOT": "Airports of Thailand",
    "AWC": "Asset World Corp", "BANPU": "Banpu", "BBL": "Bangkok Bank",
    "BCP": "Bangchak Corporation", "BDMS": "Bangkok Dusit Medical Service",
    "BEM": "Bangkok Expressway and Metro", "BH": "Bumrungrad Hospital",
    "BJC": "Berli Jucker", "BTS": "BTS Group Holdings", "CBG": "Carabao Group",
    "COM7": "Com Seven", "CPALL": "CP All",
    "CPF": "Charoen Pokphand Foods", "CPN": "Central Pattana",
    "CRC": "Central Retail Corporation", "DELTA": "Delta Electronics",
    "EGCO": "Electricity Generating", "GPSC": "Global Power Synergy",
    "GULF": "Gulf Development", "HMPRO": "Home Product Center", "IVL": "Indorama Ventures",
    "KBANK": "Kasikornbank", "KCE": "KCE Electronics", "KKP": "Kiatnakin Phatra Bank",
    "KTB": "Krungthai Bank", "KTC": "Krungthai Card", "LH": "Land and Houses",
    "MINT": "Minor International", "MTC": "Muangthai Capital",
    "OR": "PTT Oil and Retail", "OSP": "Osotspa", "PTT": "PTT",
    "PTTEP": "PTT Exploration & Production", "PTTGC": "PTT Global Chemical",
    "RATCH": "Ratch Group", "SCB": "SCB X", "SCC": "Siam Cement Group",
    "SCGP": "SCG Packaging", "TCAP": "Thanachart Capital", "TIDLOR": "Tidlor Holdings",
    "TISCO": "Tisco Financial Group", "TLI": "Thai Life Insurance", "TOP": "Thai Oil",
    "TRUE": "TRUE Corporation", "TTB": "TMBThanachart Bank", "TU": "Thai Union Group",
    "VGI": "VGI", "WHA": "WHA Corporation",
}

shareholders_data = {
    "ADVANC": [("Gulf Development", 40.44), ("Singtel Strategic Investments", 24.77), ("Thai NVDR", 7.63), ("Raffle Nominees (Singtel)", 5.67), ("Vayupak Fund 1", 2.97)],
    "AOT":   [("Ministry of Finance", 70.00), ("Thai NVDR", 3.28), ("Vayupak Fund 1", 2.42), ("Social Security Office", 1.37), ("SEA UK Nominees", 1.20)],
    "AWC":   [("TCC Group", 74.94), ("Nomura Singapore", 4.47), ("UBS AG Singapore", 2.17), ("Vayupak Fund 1", 1.83), ("SEA UK Nominees", 1.50)],
    "BANPU": [("Vongkusolkit Family", 16.83), ("Thai NVDR", 7.21), ("Chanin Vongkusolkit", 3.63), ("Vanguard Group", 3.24), ("BlackRock", 1.56)],
    "BBL":   [("City Realty Co.", 4.70), ("Social Security Office", 4.00), ("First Eagle Investment", 3.64), ("Invesco", 2.01), ("BKI Holdings", 1.81)],
    "BCP":   [("Vayupak Fund 1", 15.37), ("Social Security Office", 14.13), ("Alpha Chartered Energy", 11.09), ("Thai NVDR", 9.74), ("Ministry of Finance", 4.45)],
    "BDMS":  [("Thai NVDR", 9.70), ("Prasert Prasarttong-Osoth", 9.30), ("Poramaporn Prasarttong-Osoth", 5.90), ("Bangkok Airways", 4.60), ("Viriyah Insurance", 4.30)],
    "BEM":   [("CH. Karnchang", 42.26), ("MRTA", 8.22), ("Krung Thai Bank", 5.33), ("Thai NVDR", 3.16), ("Social Security Office", 3.05)],
    "BH":    [("Bangkok Insurance", 9.95), ("Thai NVDR", 9.73), ("UOB Kay Hian", 7.76), ("Bangkok Bank", 6.69), ("SEA UK Nominees", 3.82)],
    "BJC":   [("TCC Corporation", 45.68), ("TCC Holdings", 29.32), ("Social Security Office", 4.10), ("Raffles Nominees", 3.92), ("BNY Nominees", 2.58)],
    "BTS":   [("Keeree Kanjanapas Group", 46.37), ("Thai NVDR", 4.93), ("Bangkok Bank", 4.48), ("Citibank Nominees (GIC)", 3.66), ("Social Security Office", 2.89)],
    "CBG":   [("Sathienthamholding", 25.01), ("Nutchamai Thanombooncharoen", 21.00), ("Yuenyong Opakul", 7.05), ("UBS AG Singapore", 4.59), ("Thai NVDR", 3.16)],
    "COM7":  [("Sura Khanittaweekul", 25.50), ("Pongsak Thammathataree", 20.20), ("Aree Preechanukul", 3.44), ("TISCO Asset Mgmt", 2.68), ("KTAM", 1.68)],
    "CPALL": [("CP Group", 35.92), ("Thai NVDR", 11.95), ("Social Security Office", 3.13), ("State Street Europe", 2.76), ("SEA UK Nominees", 2.71)],
    "CPF":   [("CP Group", 49.51), ("Thai NVDR", 10.59), ("Social Security Office", 2.86), ("Vayupak Fund 1", 2.21), ("State Street Europe", 2.08)],
    "CPN":   [("Central Holding", 26.21), ("Thai NVDR", 6.87), ("Vayupak Fund 1", 3.49), ("Social Security Office", 3.33), ("Niti Osathanugrah", 2.39)],
    "CRC":   [("Central Department Store", 35.10), ("Suthisarn Chirathivat", 12.40), ("Social Security Office", 3.28), ("KTAM", 2.77), ("BlackRock", 2.32)],
    "DELTA": [("Delta Electronics Int'l", 42.85), ("Delta Intl Holding BV", 14.17), ("CITI Nominees (CBHK)", 13.86), ("Delta Electronics Inc.", 5.54), ("UBS AG Hong Kong", 4.39)],
    "EGCO":  [("EGAT", 25.41), ("TEPDIA Generating", 22.42), ("EGAT Cooperative", 6.33), ("Thai NVDR", 5.08), ("Social Security Office", 4.58)],
    "GPSC":  [("PTT", 47.27), ("PTTGC", 10.00), ("TOP", 10.00), ("Siam Management Holding", 7.96), ("Social Security Office", 1.94)],
    "GULF":  [("Sarath Ratanavadi", 29.28), ("UBS AG Singapore", 10.12), ("Gulf Capital Holdings", 8.00), ("Singtel Global Investment", 7.73), ("Thai NVDR", 4.29)],
    "HMPRO": [("Land and Houses", 30.23), ("Quality Houses", 19.87), ("Niti Osathanugrah", 5.27), ("Social Security Office", 4.79), ("Thai NVDR", 3.68)],
    "IVL":   [("Indorama Resources", 65.69), ("Thai NVDR", 5.93), ("Bangkok Bank", 4.83), ("Vayupak Fund 1", 3.54), ("Social Security Office", 1.68)],
    "KBANK": [("Gulf Development", 5.33), ("Social Security Office", 3.31), ("MFC Asset Management", 1.83), ("EGAT Cooperative", 1.25), ("BBL Asset Mgmt", 0.86)],
    "KCE":   [("Ongkosit Group", 33.12), ("Thai NVDR", 6.32), ("Rattanawadee Senadisai", 4.88), ("BNY Mellon", 3.83), ("SEA UK Nominees", 3.01)],
    "KKP":   [("Thai NVDR", 14.44), ("Chodthanawat Co.", 5.27), ("Eastern Sugar", 4.57), ("Thitinan Wattanavekin", 4.20), ("Kiatnakin Phatra (Treasury)", 4.12)],
    "KTB":   [("FIDF", 55.07), ("Vayupak Fund 1", 4.68), ("BBL Asset Mgmt", 1.35), ("Kasikorn Asset Mgmt", 1.09), ("Government Savings Bank", 0.85)],
    "KTC":   [("Krung Thai Bank", 49.29), ("Thai NVDR", 6.85), ("Mongkol Prakitchaiwattana", 5.44), ("SEA UK Nominees", 2.07), ("Vayupak Fund 1", 1.72)],
    "LH":    [("Anant Asavabhokin", 24.23), ("Social Security Office", 6.39), ("Mayland Co.", 5.67), ("Thai NVDR", 5.37), ("BNY Mellon", 2.60)],
    "MINT":  [("Heinecke Family", 34.00), ("Niti Osathanugrah", 9.80), ("Thai NVDR", 7.90), ("SEA UK Nominees", 4.10), ("Social Security Office", 3.60)],
    "MTC":   [("Daonapa Patcharachai", 33.96), ("Parithad Petampai", 14.34), ("Suksit Patcharachai", 14.15), ("UBS AG Singapore", 5.20), ("Thai NVDR", 4.26)],
    "OR":    [("PTT", 75.00), ("Thai NVDR", 1.71), ("Vayupak Fund 1", 1.57), ("SEA UK Nominees", 0.87), ("Federation of Cooperatives", 0.63)],
    "OSP":   [("Niti Osathanugrah", 24.07), ("Bank Julius Baer", 8.69), ("Thai NVDR", 4.26), ("Pasuree Osathanugrah", 3.35), ("Quesara Osathanugrah", 3.14)],
    "PTT":   [("Ministry of Finance", 51.38), ("Vayupak Fund 1", 7.83), ("Thai NVDR", 5.95), ("Federation of Cooperatives", 2.06), ("Social Security Office", 1.77)],
    "PTTEP": [("PTT", 63.79), ("Thai NVDR", 6.69), ("Vayupak Fund 1", 1.76), ("State Street Europe", 1.70), ("Siam Management Holding", 1.50)],
    "PTTGC": [("PTT", 45.18), ("Thai NVDR", 5.28), ("Vayupak Fund 1", 3.36), ("Siam Management Holding", 3.00), ("State Street Europe", 2.53)],
    "RATCH": [("EGAT", 45.00), ("EGAT Cooperative", 6.19), ("Social Security Office", 4.68), ("Thai NVDR", 3.77), ("Prateep Tangmatitham", 1.26)],
    "SCB":   [("His Majesty the King", 23.58), ("Vayupak Fund 1", 23.32), ("Thai NVDR", 5.41), ("Social Security Office", 3.06), ("SEA UK Nominees", 3.04)],
    "SCC":   [("His Majesty the King", 33.64), ("Thai NVDR", 7.74), ("Social Security Office", 5.59), ("SEA UK Nominees", 3.29), ("State Street Europe", 1.80)],
    "SCGP":  [("Siam Cement Group (SCC)", 72.12), ("Thai NVDR", 2.32), ("Social Security Office", 1.81), ("Vayupak Fund 1", 1.80), ("CPB Equity", 1.75)],
    "TCAP":  [("MBK", 24.90), ("Thai NVDR", 8.03), ("Somchai Limthilakun", 2.55), ("SEA UK Nominees", 2.43), ("DBS Bank (PB)", 1.95)],
    "TIDLOR":[("Bank of Ayudhya", 46.51), ("Thai NVDR", 6.58), ("Vayupak Fund 1", 3.28), ("9 Basil Pte.", 3.08), ("SEA UK Nominees", 2.10)],
    "TISCO": [("Thai NVDR", 13.99), ("CDIB Partners", 10.00), ("Tokyo Century", 4.93), ("SEA UK Nominees", 3.53), ("State Street Europe", 2.09)],
    "TLI":   [("VC Property (Chaiyawan)", 50.81), ("Meiji Yasuda Life", 17.00), ("Her Sing (HK)", 5.60), ("Thai NVDR", 2.17), ("BNP Paribas SG", 1.93)],
    "TOP":   [("PTT", 45.03), ("Thai NVDR", 11.51), ("SEA UK Nominees", 3.37), ("Siam Management Holding", 2.97), ("BNY Mellon", 2.09)],
    "TRUE":  [("CP Group", 45.89), ("Thai NVDR", 11.68), ("China Mobile", 7.81), ("Telenor", 5.35), ("SEA UK Nominees", 3.00)],
    "TTB":   [("Thanachart Capital", 24.00), ("ING Bank", 23.00), ("Ministry of Finance", 11.00), ("Vayupak Fund 1", 7.00), ("Thai NVDR", 3.00)],
    "TU":    [("Chansiri Family", 17.70), ("Thai Union (Treasury)", 9.40), ("Thai NVDR", 8.70), ("Niruttinanon Family", 7.80), ("Mitsubishi UFJ", 5.60)],
    "VGI":   [("BTS Group", 33.51), ("CAI Optimum Fund", 14.50), ("Si Suk Alley", 12.90), ("Opus Chartered", 11.00), ("Thai NVDR", 6.15)],
    "WHA":   [("Jareeporn Jarukornsakul", 23.50), ("Chatchamol Anantaprayoon", 9.07), ("KTAM", 2.36), ("Vanguard Group", 2.31), ("Norges Bank", 1.90)],
}

sectors = {
    "ADVANC": "ICT", "AOT": "Transport", "AWC": "Property", "BANPU": "Energy", "BBL": "Banking",
    "BCP": "Energy", "BDMS": "Healthcare", "BEM": "Transport", "BH": "Healthcare", "BJC": "Commerce",
    "BTS": "Transport", "CBG": "Food & Beverage", "COM7": "Commerce", "CPALL": "Commerce",
    "CPF": "Food & Beverage", "CPN": "Property", "CRC": "Commerce", "DELTA": "Electronics", "EGCO": "Energy",
    "GPSC": "Energy", "GULF": "Energy", "HMPRO": "Commerce", "IVL": "Petrochemicals", "KBANK": "Banking",
    "KCE": "Electronics", "KKP": "Banking", "KTB": "Banking", "KTC": "Finance", "LH": "Property",
    "MINT": "Food & Beverage", "MTC": "Finance", "OR": "Energy", "OSP": "Food & Beverage", "PTT": "Energy",
    "PTTEP": "Energy", "PTTGC": "Petrochemicals", "RATCH": "Energy", "SCB": "Banking", "SCC": "Construction",
    "SCGP": "Packaging", "TCAP": "Banking", "TIDLOR": "Finance", "TISCO": "Banking", "TLI": "Insurance",
    "TOP": "Energy", "TRUE": "ICT", "TTB": "Banking", "TU": "Food & Beverage", "VGI": "Media", "WHA": "Property",
}

sector_colors = {
    "Energy": "#F59E0B", "Banking": "#EF4444", "Commerce": "#3B82F6", "Food & Beverage": "#10B981",
    "Property": "#F97316", "Healthcare": "#06B6D4", "Transport": "#8B5CF6", "ICT": "#60A5FA",
    "Electronics": "#FB923C", "Petrochemicals": "#6366F1", "Finance": "#EC4899", "Construction": "#94A3B8",
    "Media": "#F43F5E", "Packaging": "#14B8A6", "Insurance": "#A855F7",
}

# ── GRAPH BUILD ────────────────────────────────────────────────────────────────

def build_graph(selected_company="All", selected_holder="All", min_stake=0.0, selected_sector="All"):
    G = nx.Graph()
    for sym, name in set50_companies.items():
        G.add_node(sym, type="company", label=name, sector=sectors.get(sym, "Other"))

    for sym, holders in shareholders_data.items():
        for holder, pct in holders:
            if pct >= min_stake:
                if holder not in G.nodes():
                    G.add_node(holder, type="shareholder", label=holder)
                G.add_edge(holder, sym, weight=pct)

    if selected_company and selected_company != "All":
        keep = {selected_company} | {h for h, _ in shareholders_data[selected_company]}
        G.remove_nodes_from([n for n in list(G.nodes()) if n not in keep])
        return G

    if selected_holder and selected_holder != "All":
        keep = {selected_holder} | {sym for sym, holders in shareholders_data.items() for h, _ in holders if h == selected_holder}
        G.remove_nodes_from([n for n in list(G.nodes()) if n not in keep])
        return G

    if selected_sector and selected_sector != "All":
        syms_in_sector = {s for s, sec in sectors.items() if sec == selected_sector}
        keep = syms_in_sector | {h for sym in syms_in_sector for h, _ in shareholders_data.get(sym, [])}
        G.remove_nodes_from([n for n in list(G.nodes()) if n not in keep])

    return G

# ── DRAW ───────────────────────────────────────────────────────────────────────

def draw_network(G, layout_type="spring", uirev="0"):
    if G.number_of_nodes() == 0:
        return None

    company_nodes = [n for n, a in G.nodes(data=True) if a["type"] == "company"]
    shareholder_nodes = [n for n, a in G.nodes(data=True) if a["type"] == "shareholder"]

    if layout_type == "spring":
        pos = nx.spring_layout(G, k=2.2, iterations=120, seed=42)
    elif layout_type == "circular":
        pos = nx.circular_layout(G)
    else:
        pos = nx.kamada_kawai_layout(G)

    fig = go.Figure()
    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1
    many_sh = len([n for n, a in G.nodes(data=True) if a["type"] == "shareholder"]) > 30

    # ── Edges (3 weight tiers) — Scattergl for speed ──
    tiers = {
        "Major (>30%)": dict(color="#F59E0B", width=3.5, opacity=0.85, dash="solid"),
        "Mid (10–30%)": dict(color="#60A5FA", width=1.8, opacity=0.55, dash="solid"),
        "Minor (<10%)": dict(color="#9CA3AF", width=0.8, opacity=0.25, dash="dot"),
    }
    tier_data = {t: {"x": [], "y": []} for t in tiers}

    for u, v, data in G.edges(data=True):
        w = data.get("weight", 0)
        t = "Major (>30%)" if w > 30 else "Mid (10–30%)" if w > 10 else "Minor (<10%)"
        xu, yu = pos[u]; xv, yv = pos[v]
        tier_data[t]["x"].extend([xu, xv, None])
        tier_data[t]["y"].extend([yu, yv, None])

    for label, style in tiers.items():
        td = tier_data[label]
        if not td["x"]:
            continue
        fig.add_trace(go.Scattergl(
            x=td["x"], y=td["y"], mode="lines",
            line=dict(width=style["width"], color=style["color"], dash=style["dash"]),
            opacity=style["opacity"], hoverinfo="none", name=label,
            legendgroup="edges",
            legendgrouptitle_text="Edge (stake)" if label == "Major (>30%)" else None,
        ))

    # ── Company nodes ──
    sector_groups = {}
    for n in company_nodes:
        sec = G.nodes[n].get("sector", "Other")
        sector_groups.setdefault(sec, []).append(n)

    def company_hover(n, sec):
        nbrs = sorted(G.neighbors(n), key=lambda h: G[n][h].get("weight", 0), reverse=True)
        lines = [f"  • {h}:  <b>{G[n][h].get('weight',0):.2f}%</b>" for h in nbrs]
        return (
            f"<b>🏢 {n}</b> — {G.nodes[n].get('label', n)}<br>"
            f"Sector: {sec}<br>"
            f"Degree centrality: {degrees.get(n,0)} connections<br>"
            f"────────────────────<br>"
            f"<b>Top Shareholders:</b><br>" + "<br>".join(lines)
        )

    for sec, nodes in sector_groups.items():
        color = sector_colors.get(sec, "#94A3B8")
        sizes = [18 + 22 * (degrees.get(n, 1) / max_deg) for n in nodes]
        hover = [company_hover(n, sec) for n in nodes]
        node_mode = "markers+text"  # always show ticker inside circle
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes],
            mode=node_mode,
            marker=dict(size=sizes, color=color, line=dict(width=1.5, color="#1f2937"), opacity=0.95),
            text=[n for n in nodes],
            textposition="middle center",
            textfont=dict(size=7, color="white", family="Arial Black"),
            hovertext=hover, hoverinfo="text",
            customdata=[[n, "company"] for n in nodes],
            name=sec,
            legendgroup="sectors",
            legendgrouptitle_text="Sector" if sec == list(sector_groups.keys())[0] else None,
        ))

    # ── Shareholder nodes ──
    def shorten(name, maxlen=15):
        name = name.replace(" Group", "").replace(" Family", "").replace(" Holdings", "")
        return name if len(name) <= maxlen else name[:maxlen - 2] + ".."

    def shareholder_hover(n):
        nbrs = sorted(G.neighbors(n), key=lambda c: G[n][c].get("weight", 0), reverse=True)
        total_w = sum(G[n][c].get("weight", 0) for c in nbrs)
        lines = [
            f"  • <b>{c}</b> ({G.nodes[c].get('label', c)}):  <b>{G[n][c].get('weight',0):.2f}%</b>"
            for c in nbrs
        ]
        return (
            f"<b>♦ {n}</b><br>"
            f"ถือหุ้นใน <b>{len(nbrs)}</b> บริษัท<br>"
            f"รวม stake: <b>{total_w:.2f}%</b><br>"
            f"────────────────────<br>"
            f"<b>Companies held:</b><br>" + "<br>".join(lines)
        )

    sh_degrees = [degrees.get(n, 1) for n in shareholder_nodes]
    max_sh = max(sh_degrees) if sh_degrees else 1
    sh_sizes = [14 + 20 * (d / max_sh) for d in sh_degrees]
    sh_mode = "markers" if many_sh else "markers+text"

    fig.add_trace(go.Scatter(
        x=[pos[n][0] for n in shareholder_nodes],
        y=[pos[n][1] for n in shareholder_nodes],
        mode=sh_mode,
        marker=dict(size=sh_sizes, color="#F43F5E", symbol="diamond",
                    line=dict(width=1.5, color="#fca5a5"), opacity=0.92),
        text=[shorten(n) for n in shareholder_nodes],
        textposition="top center",
        textfont=dict(size=7, color="#be123c", family="Arial"),
        hovertext=[shareholder_hover(n) for n in shareholder_nodes],
        hoverinfo="text",
        customdata=[[n, "shareholder"] for n in shareholder_nodes],
        name="Shareholder",
        legendgroup="stakeholders",
        legendgrouptitle_text="Stakeholders",
    ))

    fig.update_layout(
        showlegend=True,
        hovermode="closest",
        uirevision=uirev,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=720,
        legend=dict(
            font=dict(size=10, color="#374151"),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            tracegroupgap=8,
        ),
        hoverlabel=dict(
            bgcolor="white", font_size=12, font_color="#1e293b",
            bordercolor="#0ea5e9", namelength=-1,
        ),
    )
    return fig

# ── DATA TABLE ─────────────────────────────────────────────────────────────────

rows = []
for sym, holders in shareholders_data.items():
    for holder, pct in holders:
        rows.append({"Symbol": sym, "Company": set50_companies[sym], "Sector": sectors.get(sym, ""),
                     "Shareholder": holder, "Stake (%)": pct})
df = pd.DataFrame(rows)

all_holders = sorted({h for holders in shareholders_data.values() for h, _ in holders})
all_sectors = sorted(set(sectors.values()))

# ── SESSION STATE ──────────────────────────────────────────────────────────────

for key, default in [("chart_key", 0), ("click_data", None),
                     ("filter_company", "All"), ("filter_holder", "All"),
                     ("filter_sector", "All")]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.click_data:
    name, typ = st.session_state.click_data
    st.session_state.click_data = None
    if typ == "company" and name in set50_companies:
        st.session_state.filter_company = name
        st.session_state.filter_holder = "All"
        st.session_state.filter_sector = "All"
    elif typ == "shareholder":
        st.session_state.filter_holder = name
        st.session_state.filter_company = "All"
        st.session_state.filter_sector = "All"

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔍 Filters")
    sel_company = st.selectbox("Company", ["All"] + sorted(set50_companies.keys()), key="filter_company")
    sel_holder  = st.selectbox("Shareholder", ["All"] + all_holders, key="filter_holder")
    sel_sector  = st.selectbox("Sector", ["All"] + all_sectors, key="filter_sector")
    min_stake   = st.slider("Min Stake (%)", 0.0, 80.0, 0.0, 0.5)
    st.caption("ตั้ง 30 = เห็นแค่คนที่ถือหุ้นเกิน 30%")
    layout_labels = {
        "spring": "🌐 Spring (กระจายอิสระ)",
        "circular": "⭕ Circular (วงกลม)",
        "kamada_kawai": "🔷 Balanced (สมดุล)",
    }
    layout_type = st.selectbox(
        "Layout (รูปแบบการจัดวาง)",
        list(layout_labels.keys()),
        format_func=lambda x: layout_labels[x],
    )

    st.divider()
    st.markdown("### ℹ️ Legend")
    st.markdown("""
<div style='font-size:12.5px;line-height:2;color:#374151'>

<b style='color:#1e293b'>🔵 วงกลม = บริษัท SET50</b><br>
<span style='color:#64748b'>
&nbsp;• <b>สี</b> = กลุ่มธุรกิจ (Sector)<br>
&nbsp;• <b>ขนาด</b> = มีผู้ถือหุ้นเชื่อมอยู่มากแค่ไหน<br>
&nbsp;&nbsp;&nbsp;&nbsp;→ วงใหญ่ = มีผู้ถือหุ้นใหญ่หลายราย
</span>

<div style='border-top:1px solid #e2e8f0;margin:6px 0'></div>

<b style='color:#e11d48'>♦ เพชร = ผู้ถือหุ้น (Stakeholder)</b><br>
<span style='color:#64748b'>
&nbsp;• <b>ขนาด</b> = ถือหุ้นในกี่บริษัท<br>
&nbsp;&nbsp;&nbsp;&nbsp;→ เพชรใหญ่ = กระจายถือหุ้นหลายบริษัท
</span>

<div style='border-top:1px solid #e2e8f0;margin:6px 0'></div>

<b style='color:#1e293b'>เส้นเชื่อม = สัดส่วนการถือหุ้น</b><br>
<span style='background:#F59E0B;display:inline-block;width:18px;height:3px;vertical-align:middle;border-radius:2px'></span>
<b style='color:#d97706'> เส้นทอง</b> = ถือ &gt;30%
<span style='color:#64748b;font-size:11px'>(ผู้ควบคุมหลัก)</span><br>
<span style='background:#60A5FA;display:inline-block;width:18px;height:2px;vertical-align:middle;border-radius:2px'></span>
<b style='color:#3b82f6'> เส้นฟ้า</b> = ถือ 10–30%
<span style='color:#64748b;font-size:11px'>(มีอิทธิพล)</span><br>
<span style='color:#9ca3af'>⋯</span>
<b style='color:#9ca3af'> จุดเทา</b> = ถือ &lt;10%
<span style='color:#64748b;font-size:11px'>(รายย่อย)</span>

<div style='border-top:1px solid #e2e8f0;margin:6px 0'></div>
<div style='background:#eff6ff;border-left:3px solid #3b82f6;border-radius:6px;padding:8px 10px;margin-top:2px'>
<span style='color:#1d4ed8;font-size:12px'>
💡 <b>กดคลิกที่จุดใดก็ได้ในกราฟ</b><br>
<span style='color:#3b82f6'>→ กราฟจะโฟกัสเฉพาะจุดนั้น<br>
&nbsp;&nbsp;&nbsp;และ node ที่เชื่อมต่อทั้งหมด</span><br><br>
<span style='color:#64748b'>ตัวอย่าง: คลิก <b style='color:#1d4ed8'>PTT</b><br>
→ เห็นแค่ PTT + ผู้ถือหุ้นของ PTT</span>
</span>
</div>
</div>
""", unsafe_allow_html=True)

# ── BUILD ──────────────────────────────────────────────────────────────────────

G = build_graph(sel_company, sel_holder, min_stake, sel_sector)

# ── KPI STRIP ──────────────────────────────────────────────────────────────────

n_co = sum(1 for _, a in G.nodes(data=True) if a["type"] == "company")
n_sh = sum(1 for _, a in G.nodes(data=True) if a["type"] == "shareholder")
n_ed = G.number_of_edges()
density = nx.density(G) if G.number_of_edges() > 0 else 0.0

k1, k2, k3, k4 = st.columns(4)
for col, val, label in [(k1, n_co, "Companies"), (k2, n_sh, "Shareholders"),
                         (k3, n_ed, "Ownership Links"), (k4, f"{density:.4f}", "Network Density")]:
    col.markdown(f"""
<div class='metric-card'>
  <div class='metric-value'>{val}</div>
  <div class='metric-label'>{label}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["🕸️  Network Graph", "📋  Data Table", "📊  SNA Analytics"])

with tab1:
    uirev = f"{sel_company}|{sel_holder}|{sel_sector}|{min_stake}|{layout_type}"
    fig = draw_network(G, layout_type, uirev)
    if fig:
        event = st.plotly_chart(fig, key=f"net_{st.session_state.chart_key}",
                                on_select="rerun", use_container_width=True)
        if event and event.selection and event.selection.points:
            pt = event.selection.points[0]
            cd = getattr(pt, "customdata", None)
            if cd and len(cd) >= 2:
                st.session_state.click_data = (cd[0], cd[1])
                st.session_state.chart_key += 1
                st.rerun()
    else:
        st.warning("No nodes match the current filters.")

with tab2:
    fdf = df.copy()
    if sel_company != "All": fdf = fdf[fdf["Symbol"] == sel_company]
    if sel_holder  != "All": fdf = fdf[fdf["Shareholder"] == sel_holder]
    if sel_sector  != "All": fdf = fdf[fdf["Sector"] == sel_sector]
    fdf = fdf[fdf["Stake (%)"] >= min_stake].sort_values("Stake (%)", ascending=False)
    st.dataframe(fdf, use_container_width=True, hide_index=True,
                 column_config={"Stake (%)": st.column_config.ProgressColumn(
                     "Stake (%)", format="%.2f%%", min_value=0, max_value=100)})

with tab3:
    if G.number_of_edges() == 0:
        st.info("No data to analyse with current filters.")
    else:
        # ── Row 1: two charts side by side ──
        col_sh, col_co = st.columns(2)

        deg_c = nx.degree_centrality(G)
        sh_nodes_all = [n for n, a in G.nodes(data=True) if a["type"] == "shareholder"]
        co_nodes_all = [n for n, a in G.nodes(data=True) if a["type"] == "company"]

        def _bar(names, vals, color, title, subtitle, xlabel, fmt=".3f"):
            fig = go.Figure(go.Bar(
                x=list(vals), y=list(names), orientation="h",
                marker=dict(
                    color=list(vals),
                    colorscale=[[0, "#fde8ec"], [1, color]],
                    showscale=False,
                    line=dict(width=0),
                ),
                text=[f"{v:{fmt}}" for v in vals],
                textposition="outside",
                textfont=dict(color="#374151", size=10),
                hovertemplate="<b>%{y}</b><br>" + xlabel + ": %{x:" + fmt + "}<extra></extra>",
            ))
            fig.update_layout(
                title=dict(text=f"<b>{title}</b><br><sup style='color:#64748b'>{subtitle}</sup>",
                           font=dict(color="#1e293b", size=13), x=0),
                paper_bgcolor="white", plot_bgcolor="#fafafa",
                xaxis=dict(color="#9ca3af", gridcolor="#f1f5f9", title=xlabel,
                           title_font=dict(size=11, color="#6b7280"), tickfont=dict(size=10)),
                yaxis=dict(color="#374151", autorange="reversed", tickfont=dict(size=10)),
                height=420, margin=dict(l=10, r=70, t=65, b=30),
                showlegend=False,
            )
            return fig

        # Shareholder — degree centrality (กี่บริษัทที่ถือ)
        with col_sh:
            top_sh = sorted([(n, deg_c[n]) for n in sh_nodes_all if n in deg_c],
                            key=lambda x: x[1], reverse=True)[:10]
            if top_sh:
                sn, sv = zip(*top_sh)
                st.plotly_chart(
                    _bar(sn, sv, "#F43F5E",
                         "♦ Shareholder Reach",
                         "ผู้ถือหุ้นที่ปรากฏในหลายบริษัทมากที่สุด",
                         "Degree Centrality"),
                    use_container_width=True,
                )

        # Company — weighted degree (รับ stake รวมสูงสุด = concentration สูง)
        with col_co:
            co_wdeg = [(n, G.degree(n, weight="weight")) for n in co_nodes_all]
            top_co = sorted(co_wdeg, key=lambda x: x[1], reverse=True)[:10]
            if top_co:
                cn, cv = zip(*top_co)
                fig_co = go.Figure(go.Bar(
                    x=list(cv), y=list(cn), orientation="h",
                    marker=dict(
                        color=list(cv),
                        colorscale=[[0, "#dbeafe"], [1, "#2563eb"]],
                        showscale=False,
                        line=dict(width=0),
                    ),
                    text=[f"{v:.1f}%" for v in cv],
                    textposition="outside",
                    textfont=dict(color="#374151", size=10),
                    hovertemplate="<b>%{y}</b><br>รวม stake ที่ถือโดยผู้ถือหุ้น 5 อันดับแรก: %{x:.1f}%<extra></extra>",
                ))
                fig_co.update_layout(
                    title=dict(
                        text="<b>🏢 Ownership Concentration</b><br><sup style='color:#64748b'>บริษัทที่มีผู้ถือหุ้นกระจุกตัวสูงสุด</sup>",
                        font=dict(color="#1e293b", size=13), x=0,
                    ),
                    paper_bgcolor="white", plot_bgcolor="#fafafa",
                    xaxis=dict(color="#9ca3af", gridcolor="#f1f5f9", title="รวม Stake (%)",
                               title_font=dict(size=11, color="#6b7280"), tickfont=dict(size=10)),
                    yaxis=dict(color="#374151", autorange="reversed", tickfont=dict(size=10)),
                    height=420, margin=dict(l=10, r=70, t=65, b=30),
                    showlegend=False,
                )
                st.plotly_chart(fig_co, use_container_width=True)

        st.divider()
        c_left, c_right = st.columns(2)

        # ── Shareholder influence bar ──
        with c_left:
            sh_nodes = [n for n, a in G.nodes(data=True) if a["type"] == "shareholder"]
            inf = sorted([(n, G.degree(n, weight="weight")) for n in sh_nodes], key=lambda x: x[1], reverse=True)[:12]
            if inf:
                names_i, vals_i = zip(*inf)
                fig_inf = go.Figure(go.Bar(
                    x=list(vals_i), y=list(names_i), orientation="h",
                    marker=dict(color=list(vals_i), colorscale="Reds", showscale=False),
                    text=[f"{v:.1f}%" for v in vals_i], textposition="outside",
                    textfont=dict(color="#374151", size=9),
                    hovertemplate="<b>%{y}</b><br>Weighted Influence: %{x:.1f}%<extra></extra>",
                ))
                fig_inf.update_layout(
                    title=dict(text="Shareholder Weighted Influence", font=dict(color="#1e293b", size=13)),
                    paper_bgcolor="white", plot_bgcolor="white",
                    xaxis=dict(color="#6b7280", gridcolor="#f1f5f9"),
                    yaxis=dict(color="#374151", autorange="reversed"),
                    height=400, margin=dict(l=10, r=60, t=50, b=20), showlegend=False,
                )
                st.plotly_chart(fig_inf, use_container_width=True)

        # ── Sector distribution pie ──
        with c_right:
            co_nodes = [n for n, a in G.nodes(data=True) if a["type"] == "company"]
            sec_counts = {}
            for n in co_nodes:
                s = G.nodes[n].get("sector", "Other")
                sec_counts[s] = sec_counts.get(s, 0) + 1
            if sec_counts:
                fig_pie = go.Figure(go.Pie(
                    labels=list(sec_counts.keys()),
                    values=list(sec_counts.values()),
                    marker=dict(colors=[sector_colors.get(s, "#94A3B8") for s in sec_counts]),
                    textfont=dict(color="white", size=11),
                    hole=0.4,
                    hovertemplate="<b>%{label}</b><br>%{value} companies (%{percent})<extra></extra>",
                ))
                fig_pie.update_layout(
                    title=dict(text="Companies by Sector", font=dict(color="#1e293b", size=13)),
                    paper_bgcolor="white", plot_bgcolor="white",
                    legend=dict(font=dict(color="#374151", size=9), bgcolor="rgba(255,255,255,0)"),
                    height=400, margin=dict(l=10, r=10, t=50, b=20),
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # ── Betweenness centrality ──
        st.divider()
        try:
            btwn = nx.betweenness_centrality(G, k=min(80, G.number_of_nodes()), weight="weight", normalized=True)
            top_b = sorted(btwn.items(), key=lambda x: x[1], reverse=True)[:12]
            nodes_b, vals_b = zip(*top_b)
            colors_b = ["#F43F5E" if G.nodes[n].get("type") == "shareholder" else "#4fc3f7" for n in nodes_b]
            fig_btwn = go.Figure(go.Bar(
                x=list(vals_b), y=list(nodes_b), orientation="h",
                marker_color=colors_b,
                text=[f"{v:.4f}" for v in vals_b], textposition="outside",
                textfont=dict(color="#374151", size=9),
                hovertemplate="<b>%{y}</b><br>Betweenness: %{x:.4f}<extra></extra>",
            ))
            fig_btwn.update_layout(
                title=dict(text="Top 12 Bridge Nodes — Betweenness Centrality  🌉", font=dict(color="#1e293b", size=13)),
                paper_bgcolor="white", plot_bgcolor="white",
                xaxis=dict(color="#6b7280", gridcolor="#f1f5f9"),
                yaxis=dict(color="#374151", autorange="reversed"),
                height=400, margin=dict(l=10, r=80, t=50, b=20), showlegend=False,
            )
            st.plotly_chart(fig_btwn, use_container_width=True)
            st.caption("🔴 Red = Shareholder node  |  🔵 Blue = Company node  |  Higher betweenness = more influential bridge in the network")
        except Exception:
            st.info("Betweenness centrality unavailable (graph too small).")
