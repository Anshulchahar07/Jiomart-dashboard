"""
JioMart Catalogue — Interactive Streamlit Dashboard
-----------------------------------------------------
Run with:  streamlit run app.py

Two headline insights are built into this dashboard:
  1. Pricing & Discounts  -> where sale price undercuts market price, and why
  2. Ratings & Quality     -> which products/categories delight or disappoint

Styling is done with hand-written HTML/CSS (injected via st.markdown) rather
than default Streamlit widgets, so the UI reads like a bespoke retail
dashboard rather than a generic template.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="JioMart Catalogue Insights",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Design tokens & custom CSS
# --------------------------------------------------------------------------
INK = "#1F2A24"
BG = "#FAF8F3"
SURFACE = "#FFFFFF"
LINE = "#E4DFD2"
GREEN = "#2F5233"
GREEN_SOFT = "#E7EEE3"
MARIGOLD = "#C77B2C"
MARIGOLD_SOFT = "#FBEEDD"
BERRY = "#A63A46"
BERRY_SOFT = "#F7E6E4"
MUTED = "#6B7268"

PALETTE = [GREEN, MARIGOLD, "#4E7A63", "#D9A441", "#7A9B7E", BERRY]

st.markdown(
    f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"], .stApp, .stApp * {{
            font-family: 'Inter', sans-serif;
            color: {INK} !important;
        }}
        .stApp {{
            background: {BG} !important;
        }}
        #MainMenu, footer, header {{visibility: hidden;}}
        /* Force every native Streamlit text element to stay dark regardless of
           the browser/OS light-dark preference, so nothing washes out. */
        h1, h2, h3, h4, h5, h6, p, span, label, div, li,
        .stMarkdown, .stMarkdown p, .stMetric, .stTextInput label,
        .stSlider label, .stMultiSelect label, .stTabs [data-baseweb="tab"] p {{
            color: {INK} !important;
        }}
        .stTabs [aria-selected="true"] p {{
            color: {GREEN} !important;
            font-weight: 600 !important;
        }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
            color: {INK} !important;
        }}
        .stDataFrame, .stDataFrame * {{
            color: {INK} !important;
        }}
        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        /* ---- Masthead ---- */
        .masthead {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 2px solid {INK};
            padding-bottom: 14px;
            margin-bottom: 28px;
        }}
        .masthead h1 {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 2.1rem;
            margin: 0;
            letter-spacing: -0.01em;
        }}
        .masthead p {{
            margin: 4px 0 0 0;
            color: {MUTED};
            font-size: 0.95rem;
        }}
        .masthead .tag {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.8rem;
            color: {GREEN};
            background: {GREEN_SOFT};
            padding: 5px 12px;
            border-radius: 100px;
            font-weight: 600;
        }}

        /* ---- KPI cards ---- */
        .kpi-row {{ display: flex; gap: 14px; margin-bottom: 30px; }}
        .kpi {{
            flex: 1;
            background: {SURFACE};
            border: 1px solid {LINE};
            border-radius: 10px;
            padding: 18px 20px;
        }}
        .kpi .label {{
            font-size: 0.8rem;
            color: {MUTED};
            margin-bottom: 6px;
        }}
        .kpi .value {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.9rem;
            font-weight: 700;
            line-height: 1;
        }}
        .kpi .value.green {{ color: {GREEN}; }}
        .kpi .value.marigold {{ color: {MARIGOLD}; }}
        .kpi .sub {{ font-size: 0.78rem; color: {MUTED}; margin-top: 6px; }}

        /* ---- Section headers ---- */
        .section-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.25rem;
            margin: 6px 0 2px 0;
        }}
        .section-sub {{
            color: {MUTED};
            font-size: 0.88rem;
            margin-bottom: 14px;
        }}

        /* ---- Insight callouts ---- */
        .insight {{
            border-radius: 10px;
            padding: 18px 22px;
            margin: 10px 0 22px 0;
            border-left: 4px solid {GREEN};
            background: {GREEN_SOFT};
        }}
        .insight.marigold {{ border-left-color: {MARIGOLD}; background: {MARIGOLD_SOFT}; }}
        .insight.berry {{ border-left-color: {BERRY}; background: {BERRY_SOFT}; }}
        .insight .k {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.02rem;
            margin-bottom: 6px;
        }}
        .insight p {{ margin: 0; font-size: 0.92rem; color: {INK}; line-height: 1.5; }}

        /* ---- Table wrapper ---- */
        .stDataFrame {{ border: 1px solid {LINE}; border-radius: 8px; }}

        [data-testid="stSidebar"] {{
            background: {SURFACE};
            border-right: 1px solid {LINE};
        }}
        [data-testid="stSidebar"] .sidebar-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.05rem;
            margin-bottom: 2px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data.csv")
    df["discount_pct"] = (
        (df["market_price"] - df["sale_price"]) / df["market_price"] * 100
    ).round(1)
    df["discount_pct"] = df["discount_pct"].clip(lower=0)
    return df


df = load_data()

# --------------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">Filters</div>', unsafe_allow_html=True)
    st.caption("Narrow the catalogue, every chart updates live.")

    categories = sorted(df["category"].unique())
    picked_categories = st.multiselect("Category", categories, default=[])

    price_min, price_max = int(df["sale_price"].min()), int(df["sale_price"].max())
    price_range = st.slider(
        "Sale price (₹)", price_min, price_max, (price_min, price_max)
    )

    rating_range = st.slider("Rating", 1.0, 5.0, (1.0, 5.0), step=0.1)

    search = st.text_input("Search product name")

    st.divider()
    st.caption(f"{len(df):,} products in the full catalogue.")

filtered = df.copy()
if picked_categories:
    filtered = filtered[filtered["category"].isin(picked_categories)]
filtered = filtered[
    filtered["sale_price"].between(price_range[0], price_range[1])
    & filtered["rating"].between(rating_range[0], rating_range[1])
]
if search:
    filtered = filtered[filtered["product"].str.contains(search, case=False, na=False)]

# --------------------------------------------------------------------------
# Masthead
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="masthead">
        <div>
            <h1>JioMart Catalogue Insights</h1>
            <p>1,026 products across 12 categories · pricing &amp; rating analysis</p>
        </div>
        <div class="tag">{len(filtered):,} products in view</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No products match the current filters — try widening the price or rating range.")
    st.stop()

# --------------------------------------------------------------------------
# KPI row
# --------------------------------------------------------------------------
avg_rating = filtered["rating"].mean()
avg_discount = filtered["discount_pct"].mean()
avg_price = filtered["sale_price"].mean()
discounted_share = (filtered["discount_pct"] > 0).mean() * 100

st.markdown(
    f"""
    <div class="kpi-row">
        <div class="kpi">
            <div class="label">Products in view</div>
            <div class="value">{len(filtered):,}</div>
            <div class="sub">of {len(df):,} total</div>
        </div>
        <div class="kpi">
            <div class="label">Average rating</div>
            <div class="value green">{avg_rating:.2f} <span style="font-size:1rem; color:{MUTED};">/ 5</span></div>
            <div class="sub">{(filtered['rating'] >= 4).mean()*100:.0f}% rated 4.0+</div>
        </div>
        <div class="kpi">
            <div class="label">Average discount</div>
            <div class="value marigold">{avg_discount:.1f}%</div>
            <div class="sub">{discounted_share:.0f}% of products discounted</div>
        </div>
        <div class="kpi">
            <div class="label">Average sale price</div>
            <div class="value">₹{avg_price:,.0f}</div>
            <div class="sub">market avg ₹{filtered['market_price'].mean():,.0f}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_overview, tab_pricing, tab_ratings, tab_category, tab_explore = st.tabs(
    ["Overview", "Pricing & Discounts", "Ratings & Quality", "Category Explorer", "Explore Data"]
)

plot_layout = dict(
    template="plotly_white",
    font=dict(family="Inter, sans-serif", color=INK, size=12),
    title_font=dict(family="Space Grotesk, sans-serif", color=INK, size=15),
    legend=dict(font=dict(color=INK, size=10)),
    plot_bgcolor=SURFACE,
    paper_bgcolor=SURFACE,
    margin=dict(l=10, r=10, t=40, b=10),
)

def style_axes(fig):
    """Force dark, readable axis text/ticks on every chart regardless of the
    viewer's browser/OS color-scheme preference."""
    fig.update_xaxes(color=INK, tickfont=dict(color=INK), title_font=dict(color=INK),
                      gridcolor=LINE, linecolor=LINE)
    fig.update_yaxes(color=INK, tickfont=dict(color=INK), title_font=dict(color=INK),
                      gridcolor=LINE, linecolor=LINE)
    return fig

# ---- Overview -------------------------------------------------------------
with tab_overview:
    st.markdown('<div class="section-title">Where the catalogue sits</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Category mix and how price relates to rating across the assortment.</div>',
        unsafe_allow_html=True,
    )

    search_col, _spacer = st.columns([1, 2])
    with search_col:
        product_search = st.text_input(
            "🔍 Search product name",
            value="",
            placeholder="e.g. garlic oil, shampoo, cooker...",
            key="overview_product_search",
        )

    if product_search:
        search_results = filtered[filtered["product"].str.contains(product_search, case=False, na=False)]
        st.markdown(
            f'<div class="section-sub" style="margin-top:-6px;">{len(search_results):,} product(s) match "{product_search}"</div>',
            unsafe_allow_html=True,
        )
        show_cols = search_results[["product", "category", "type", "sale_price", "market_price", "discount_pct", "rating"]].rename(
            columns={"product": "Product", "category": "Category", "type": "Type", "sale_price": "Sale ₹",
                     "market_price": "Market ₹", "discount_pct": "Discount %", "rating": "Rating"}
        )
        st.dataframe(show_cols, use_container_width=True, hide_index=True, height=300)
        st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        cat_counts = filtered["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        fig = px.bar(
            cat_counts.sort_values("count"),
            x="count", y="category", orientation="h",
            color_discrete_sequence=[GREEN],
        )
        fig.update_layout(**plot_layout, title="Products by category", height=430,
                           xaxis_title="Products", yaxis_title="")
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            filtered, x="sale_price", y="rating", color="category",
            hover_name="product", opacity=0.75,
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(**plot_layout, title="Price vs. rating", height=430,
                           xaxis_title="Sale price (₹)", yaxis_title="Rating")
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns([1, 1])
    with col3:
        avg_price_cat = filtered.groupby("category")["sale_price"].mean().sort_values().reset_index()
        fig = px.bar(
            avg_price_cat, x="sale_price", y="category", orientation="h",
            color_discrete_sequence=[MARIGOLD],
        )
        fig.update_layout(**plot_layout, title="Average sale price by category", height=430,
                           xaxis_title="Avg. sale price (₹)", yaxis_title="")
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        tm = filtered.groupby("category").agg(
            products=("product", "count"), avg_rating=("rating", "mean")
        ).reset_index()
        fig = px.treemap(
            tm, path=["category"], values="products", color="avg_rating",
            color_continuous_scale=["#A63A46", "#C77B2C", "#2F5233"],
            hover_data={"avg_rating": ":.2f"},
        )
        fig.update_layout(**plot_layout, title="Category size vs. average rating", height=430)
        fig.update_traces(textfont=dict(color="white", size=13))
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

# ---- Pricing & Discounts ---------------------------------------------------
with tab_pricing:
    st.markdown('<div class="section-title">Insight 1 — Pricing &amp; discounts</div>', unsafe_allow_html=True)

    steep = filtered[filtered["discount_pct"] >= 30].sort_values("discount_pct", ascending=False)
    top_deal = filtered.sort_values("discount_pct", ascending=False).iloc[0] if len(filtered) else None

    st.markdown(
        f"""
        <div class="insight marigold">
            <div class="k">Where sale price undercuts market price most</div>
            <p>
                {len(steep):,} products ({len(steep)/len(filtered)*100:.0f}% of the current view) are discounted 30%
                or more below market price. The steepest cut is <strong>{top_deal['product']}</strong> in
                <strong>{top_deal['category']}</strong>, discounted {top_deal['discount_pct']:.0f}% — from
                ₹{top_deal['market_price']:.0f} down to ₹{top_deal['sale_price']:.0f}. Deep discounting concentrates in a
                handful of categories rather than being spread evenly, which points to clearance or
                volume-driven pricing in those lines — a retailer can lean into this with a "steal of the
                week" rail built from products already carrying a 30%+ cut, rather than manufacturing new discounts.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        fig = px.histogram(
            filtered, x="discount_pct", nbins=30,
            color_discrete_sequence=[MARIGOLD],
        )
        fig.update_layout(**plot_layout, title="Discount distribution", height=380,
                           xaxis_title="Discount (%)", yaxis_title="Products")
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        by_cat = filtered.groupby("category")["discount_pct"].mean().sort_values().reset_index()
        fig = px.bar(
            by_cat, x="discount_pct", y="category", orientation="h",
            color_discrete_sequence=[MARIGOLD],
        )
        fig.update_layout(**plot_layout, title="Average discount by category", height=380,
                           xaxis_title="Avg. discount (%)", yaxis_title="")
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:10px;">Top 15 deepest discounts</div>', unsafe_allow_html=True)
    top15 = filtered.sort_values("discount_pct", ascending=False).head(15)[
        ["product", "category", "market_price", "sale_price", "discount_pct", "rating"]
    ].rename(columns={
        "product": "Product", "category": "Category", "market_price": "Market ₹",
        "sale_price": "Sale ₹", "discount_pct": "Discount %", "rating": "Rating",
    })
    st.dataframe(top15, use_container_width=True, hide_index=True)

# ---- Ratings & Quality ------------------------------------------------------
with tab_ratings:
    st.markdown('<div class="section-title">Insight 2 — Ratings &amp; quality</div>', unsafe_allow_html=True)

    best = filtered.sort_values("rating", ascending=False).iloc[0]
    worst = filtered.sort_values("rating", ascending=True).iloc[0]
    low_rated = filtered[filtered["rating"] < 3.0]

    st.markdown(
        f"""
        <div class="insight">
            <div class="k">What ratings say about customer satisfaction</div>
            <p>
                The best-rated product in view is <strong>{best['product']}</strong>
                ({best['category']}) at {best['rating']:.1f}/5, while <strong>{worst['product']}</strong>
                ({worst['category']}) sits lowest at {worst['rating']:.1f}/5.
                {len(low_rated):,} products ({len(low_rated)/len(filtered)*100:.0f}%) fall below a 3.0 rating —
                these are the clearest early-warning signals for quality or listing issues, and worth a
                manual review before the next restock. Categories with tighter rating spreads suggest more
                consistent quality control, while wide spreads suggest inconsistent batches or descriptions
                that overpromise.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        fig = px.box(
            filtered, x="rating", y="category", orientation="h",
            color="category", color_discrete_sequence=PALETTE,
        )
        fig.update_layout(**plot_layout, title="Rating spread by category", height=430,
                           showlegend=False, xaxis_title="Rating", yaxis_title="")
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            filtered, x="rating", nbins=25,
            color_discrete_sequence=[GREEN],
        )
        fig.update_layout(**plot_layout, title="Rating distribution", height=430,
                           xaxis_title="Rating", yaxis_title="Products")
        style_axes(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title" style="font-size:1.05rem;">Top 10 rated</div>', unsafe_allow_html=True)
        top10 = filtered.sort_values("rating", ascending=False).head(10)[
            ["product", "category", "rating", "sale_price"]
        ].rename(columns={"product": "Product", "category": "Category", "rating": "Rating", "sale_price": "Sale ₹"})
        st.dataframe(top10, use_container_width=True, hide_index=True)
    with c2:
        st.markdown('<div class="section-title" style="font-size:1.05rem;">Lowest 10 rated</div>', unsafe_allow_html=True)
        bottom10 = filtered.sort_values("rating", ascending=True).head(10)[
            ["product", "category", "rating", "sale_price"]
        ].rename(columns={"product": "Product", "category": "Category", "rating": "Rating", "sale_price": "Sale ₹"})
        st.dataframe(bottom10, use_container_width=True, hide_index=True)

# ---- Category Explorer (interactive drill-down) -----------------------------
with tab_category:
    st.markdown('<div class="section-title">Category Explorer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Pick a category to drill into its product types, price band and rating profile.</div>',
        unsafe_allow_html=True,
    )

    cat_options = sorted(filtered["category"].unique())
    if not cat_options:
        st.info("No categories match the current filters.")
    else:
        picked = st.selectbox("Category", cat_options, index=0)
        cat_df = filtered[filtered["category"] == picked]

        m1, m2, m3, m4 = st.columns(4)
        for col, label, value in [
            (m1, "Products", f"{len(cat_df):,}"),
            (m2, "Avg. rating", f"{cat_df['rating'].mean():.2f}"),
            (m3, "Avg. sale price", f"₹{cat_df['sale_price'].mean():,.0f}"),
            (m4, "Avg. discount", f"{cat_df['discount_pct'].mean():.1f}%"),
        ]:
            col.markdown(
                f"""<div class="kpi"><div class="label">{label}</div>
                <div class="value green">{value}</div></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        colA, colB = st.columns([1, 1])
        with colA:
            type_counts = cat_df["type"].value_counts().head(12).sort_values().reset_index()
            type_counts.columns = ["type", "count"]
            fig = px.bar(
                type_counts, x="count", y="type", orientation="h",
                color_discrete_sequence=[GREEN],
            )
            fig.update_layout(**plot_layout, title=f"Top product types in {picked}", height=420,
                               xaxis_title="Products", yaxis_title="")
            style_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

        with colB:
            fig = px.scatter(
                cat_df, x="sale_price", y="rating", color="type",
                hover_name="product", opacity=0.8, size="discount_pct",
                size_max=18,
            )
            fig.update_layout(**plot_layout, title=f"Price, rating &amp; discount size — {picked}", height=420,
                               xaxis_title="Sale price (₹)", yaxis_title="Rating", showlegend=False)
            style_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f'<div class="section-title" style="font-size:1.05rem; margin-top:6px;">All products in {picked}</div>',
            unsafe_allow_html=True,
        )
        cat_table = cat_df[["product", "type", "sale_price", "market_price", "discount_pct", "rating"]].rename(
            columns={"product": "Product", "type": "Type", "sale_price": "Sale ₹",
                     "market_price": "Market ₹", "discount_pct": "Discount %", "rating": "Rating"}
        ).sort_values("Rating", ascending=False)
        st.dataframe(cat_table, use_container_width=True, hide_index=True, height=360)

# ---- Explore ----------------------------------------------------------------
with tab_explore:
    st.markdown('<div class="section-title">Explore the filtered catalogue</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Every row currently matching the sidebar filters.</div>',
        unsafe_allow_html=True,
    )
    show = filtered[["product", "category", "type", "market_price", "sale_price", "discount_pct", "rating"]].rename(
        columns={
            "product": "Product", "category": "Category", "type": "Type",
            "market_price": "Market ₹", "sale_price": "Sale ₹",
            "discount_pct": "Discount %", "rating": "Rating",
        }
    )
    st.dataframe(show, use_container_width=True, hide_index=True, height=500)
    st.download_button(
        "Download filtered data as CSV",
        show.to_csv(index=False).encode("utf-8"),
        file_name="jiomart_filtered.csv",
        mime="text/csv",
    )
