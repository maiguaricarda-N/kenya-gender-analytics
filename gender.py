import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


# Page setup
st.set_page_config(
    page_title="The Kenya Gender Parity & Empowerment Tracker",
    page_icon="📊",
    layout="wide",
)
st.title("📊 The Kenya Gender Parity & Empowerment Tracker")
st.caption(
    "Interactive dashboard: education parity, female labour force participation,"
    " and women in parliament."
)

# Core indicators from your analysis notebook
INDICATORS = {
    "primary": "School enrollment, primary (gross), gender parity index (GPI)",
    "secondary": (
        "School enrollment, secondary (gross), gender parity index (GPI)"
    ),
    "labor": (
        "Labor force participation rate, female (% of female population ages"
        " 15+) (modeled ILO estimate)"
    ),
    "parliament": "Proportion of seats held by women in national parliaments (%)",
}
SHORT_NAMES = {
    INDICATORS["primary"]: "Primary GPI",
    INDICATORS["secondary"]: "Secondary GPI",
    INDICATORS["labor"]: "Labor Force %",
    INDICATORS["parliament"]: "Parliament %",
}

DEFAULT_PATH = r"C:\Users\admin\Desktop\Kenya Gender Dev Analysis\Data\Raw\gender_ken pydata assignment.csv"


@st.cache_data
def load_data(source) -> pd.DataFrame:
    df = pd.read_csv(source)
    df = df[df["Year"] <= 2025]
    return df


def get_series(df: pd.DataFrame, key: str, year_range) -> pd.DataFrame:
    out = df[df["Indicator Name"] == INDICATORS[key]].sort_values("Year")
    return out[(out["Year"] >= year_range[0]) & (out["Year"] <= year_range[1])]


try:
    df = load_data(DEFAULT_PATH)
except Exception as e:
    st.error(
        f"Could not automatically load the dataset from path:\n`{DEFAULT_PATH}`\n\nError: {e}"
    )
    st.stop()

missing_cols = {"Indicator Name", "Year", "Value"} - set(df.columns)
if missing_cols:
    st.error(f"The CSV is missing required columns: {', '.join(missing_cols)}")
    st.stop()


# Sidebar Controls
st.sidebar.header("⚙️ Controls")

year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider(
    "Year range", year_min, year_max, (year_min, year_max), key="global_year_slider"
)

st.sidebar.subheader("Chart options")
show_markers = st.sidebar.checkbox("Show data points", value=True, key="global_markers")
show_reference = st.sidebar.checkbox(
    "Show reference lines (parity / 30% target)", value=True, key="global_ref"
)
fig_width = st.sidebar.slider("Chart width (inches)", 6, 14, 10, key="global_width")


primary = get_series(df, "primary", year_range)
secondary = get_series(df, "secondary", year_range)
labor = get_series(df, "labor", year_range)
parliament = get_series(df, "parliament", year_range)

marker = "o" if show_markers else None


def need_data(series: pd.DataFrame, name: str) -> bool:
    if series.empty:
        st.warning(f"No data for **{name}** in the selected year range.")
        return False
    return True


def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    return buf


# Dashboard Tabs
tabs = st.tabs([
    "🎒 Primary GPI",
    "📚 Primary vs Secondary",
    "💼 Labor Force",
    "🏛️ Parliament",
    "📌 Latest Values",
    "🔥 Correlations",
    "🗂️ Export Data",
])


with tabs[0]:
    st.subheader("Primary School Gender Parity Index Over Time - Kenya")
    if need_data(primary, "Primary GPI"):
        fig, ax = plt.subplots(figsize=(fig_width, 5))
        ax.plot(primary["Year"], primary["Value"], marker=marker)
        if show_reference:
            ax.axhline(
                y=1.0, color="gray", linestyle="--", label="Perfect Parity"
            )
            ax.legend()
        ax.set_xlabel("Year")
        ax.set_ylabel("GPI (1.0 = equal)")
        st.pyplot(fig)

        start, end = primary.iloc[0], primary.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Start ({int(start['Year'])})", f"{start['Value']:.2f}")
        c2.metric(f"End ({int(end['Year'])})", f"{end['Value']:.2f}")
        c3.metric("Change", f"{end['Value'] - start['Value']:+.2f}")

        st.write("")
        st.download_button(
            "🖼️ Download Chart as PNG",
            data=fig_to_bytes(fig),
            file_name="primary_gpi_chart.png",
            mime="image/png",
            key="dl_primary_chart",
        )


with tabs[1]:
    st.subheader(
        "Gender Parity in Education Over Time (Primary vs Secondary) - Kenya"
    )
    choice = st.radio(
        "Show", ["Both", "Primary only", "Secondary only"], horizontal=True, key="edu_choice"
    )

    if need_data(primary, "Primary GPI") and need_data(
        secondary, "Secondary GPI"
    ):
        fig, ax = plt.subplots(figsize=(fig_width, 5))
        if choice in ("Both", "Primary only"):
            ax.plot(
                primary["Year"],
                primary["Value"],
                marker=marker,
                label="Primary School",
            )
        if choice in ("Both", "Secondary only"):
            ax.plot(
                secondary["Year"],
                secondary["Value"],
                marker=marker,
                label="Secondary School",
            )
        if show_reference:
            ax.axhline(
                y=1.0, color="gray", linestyle="--", label="Perfect Parity"
            )
        ax.set_xlabel("Year")
        ax.set_ylabel("GPI (1.0 = equal)")
        ax.legend()
        st.pyplot(fig)

        merged = pd.merge(
            primary[["Year", "Value"]],
            secondary[["Year", "Value"]],
            on="Year",
            suffixes=("_primary", "_secondary"),
        )
        if merged.empty:
            st.info("Primary and secondary have no overlapping years in this range.")
        else:
            merged["gap"] = merged["Value_primary"] - merged["Value_secondary"]
            closest_year = int(
                merged.loc[merged["gap"].abs().idxmin(), "Year"]
            )
            c1, c2 = st.columns(2)
            c1.metric(
                "Average gap (primary - secondary)",
                f"{merged['gap'].mean():.3f}",
            )
            c2.metric("Closest they ever got", closest_year)

        st.write("")
        st.download_button(
            "🖼️ Download Chart as PNG",
            data=fig_to_bytes(fig),
            file_name="education_parity_chart.png",
            mime="image/png",
            key="dl_edu_chart",
        )


with tabs[2]:
    st.subheader("Female Labor Force Participation Rate Over Time - Kenya")
    if need_data(labor, "Labor Force %"):
        fig, ax = plt.subplots(figsize=(fig_width, 5))
        ax.plot(labor["Year"], labor["Value"], color="green", marker=marker)
        ax.set_xlabel("Year")
        ax.set_ylabel("% of women (15+) in the labor force")

        peak = labor.loc[labor["Value"].idxmax()]
        low = labor.loc[labor["Value"].idxmin()]
        if st.checkbox("Highlight peak and lowest points", value=True, key="labor_highlight"):
            ax.scatter(
                [peak["Year"]],
                [peak["Value"]],
                color="darkgreen",
                s=90,
                zorder=5,
                label="Peak",
            )
            ax.scatter(
                [low["Year"]],
                [low["Value"]],
                color="red",
                s=90,
                zorder=5,
                label="Lowest",
            )
            ax.legend()
        st.pyplot(fig)

        c1, c2, c3 = st.columns(3)
        c1.metric(f"Peak ({int(peak['Year'])})", f"{peak['Value']:.1f}%")
        c2.metric(f"Lowest ({int(low['Year'])})", f"{low['Value']:.1f}%")
        c3.metric(
            "Peak-to-lowest difference", f"{peak['Value'] - low['Value']:.1f} pts"
        )

        st.write("")
        st.download_button(
            "🖼️ Download Chart as PNG",
            data=fig_to_bytes(fig),
            file_name="labor_force_chart.png",
            mime="image/png",
            key="dl_labor_chart",
        )


with tabs[3]:
    st.subheader("Proportion of Parliamentary Seats Held by Women - Kenya")
    target = st.slider(
        "Target line (%)", 0, 50, 30, help="Kenya's constitutional target is 30%", key="parliament_target"
    )

    if need_data(parliament, "Parliament %"):
        fig, ax = plt.subplots(figsize=(fig_width, 5))
        ax.plot(
            parliament["Year"], parliament["Value"], color="purple", marker=marker
        )
        if show_reference:
            ax.axhline(
                y=target, color="red", linestyle="--", label=f"{target}% Target"
            )
            ax.legend()
        ax.set_xlabel("Year")
        ax.set_ylabel("% of parliamentary seats")
        st.pyplot(fig)

        start, end = parliament.iloc[0], parliament.iloc[-1]
        gap = target - end["Value"]
        c1, c2, c3 = st.columns(3)
        c1.metric(
            f"Growth since {int(start['Year'])}",
            f"{end['Value'] - start['Value']:+.1f} pts",
        )
        c2.metric(f"Latest ({int(end['Year'])})", f"{end['Value']:.1f}%")
        c3.metric(
            f"Gap to {target}% target",
            f"{gap:.1f} pts" if gap > 0 else "Target reached ✅",
        )

        st.write("")
        st.download_button(
            "🖼️ Download Chart as PNG",
            data=fig_to_bytes(fig),
            file_name="parliament_chart.png",
            mime="image/png",
            key="dl_parliament_chart",
        )


with tabs[4]:
    st.subheader("Latest Value by Indicator - Kenya")
    if all(not s.empty for s in (primary, secondary, labor, parliament)):
        gpi = {
            "Primary GPI": primary.iloc[-1]["Value"],
            "Secondary GPI": secondary.iloc[-1]["Value"],
        }
        pct = {
            "Labor Force %": labor.iloc[-1]["Value"],
            "Parliament %": parliament.iloc[-1]["Value"],
        }

        fig, (ax1, ax2) = plt.subplots(
            1, 2, figsize=(fig_width, 5), gridspec_kw={"width_ratios": [1, 1]}
        )
        b1 = ax1.bar(gpi.keys(), gpi.values(), color=["blue", "orange"])
        ax1.axhline(1.0, color="gray", linestyle="--")
        ax1.set_ylabel("GPI (1.0 = equal)")
        ax1.set_title("Education parity")
        ax1.bar_label(b1, fmt="%.2f")

        b2 = ax2.bar(pct.keys(), pct.values(), color=["green", "purple"])
        ax2.set_ylabel("%")
        ax2.set_title("Participation & representation")
        ax2.bar_label(b2, fmt="%.1f")
        fig.tight_layout()
        st.pyplot(fig)
        st.caption(
            "Split into two panels because GPI ratios and percentages use"
            " different units."
        )

        st.write("")
        st.download_button(
            "🖼️ Download Chart as PNG",
            data=fig_to_bytes(fig),
            file_name="latest_values_chart.png",
            mime="image/png",
            key="dl_latest_chart",
        )
    else:
        st.warning("One or more indicators have no data in the selected year range.")


with tabs[5]:
    st.subheader("Correlation Heatmap: How the 4 Indicators Relate")
    method = st.selectbox("Correlation method", ["pearson", "spearman", "kendall"], key="corr_method")

    in_range = df[
        (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])
    ]
    pivot = (
        in_range[in_range["Indicator Name"].isin(INDICATORS.values())]
        .pivot_table(index="Year", columns="Indicator Name", values="Value")
        .dropna()
    )
    pivot = pivot.rename(columns=SHORT_NAMES)

    if len(pivot) < 3 or pivot.shape[1] < 2:
        st.warning(
            "Not enough overlapping years across the indicators to compute"
            " correlations."
        )
    else:
        corr = pivot.corr(method=method)
        fig, ax = plt.subplots(figsize=(7, 6))
        sns.heatmap(
            corr,
            annot=True,
            cmap="coolwarm",
            center=0,
            fmt=".2f",
            vmin=-1,
            vmax=1,
            ax=ax,
        )
        st.pyplot(fig)

        pairs = (
            corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
            .stack()
        )
        best = pairs.idxmax()
        worst = pairs.idxmin()
        c1, c2 = st.columns(2)
        c1.metric(
            "Strongest positive",
            f"{best[0]} & {best[1]}",
            f"r = {pairs[best]:.2f}",
        )
        c2.metric(
            "Strongest negative",
            f"{worst[0]} & {worst[1]}",
            f"r = {pairs[worst]:.2f}",
        )
        st.caption(f"Based on {len(pivot)} years where all indicators have data.")

        st.write("")
        st.download_button(
            "🖼️ Download Chart as PNG",
            data=fig_to_bytes(fig),
            file_name="correlation_heatmap.png",
            mime="image/png",
            key="dl_corr_chart",
        )


with tabs[6]:
    st.subheader("Download Raw Data as CSV")
    st.write(
        "If you also want the underlying numbers, you can select and download"
        " the filtered dataset below."
    )

    picks = st.multiselect(
        "Indicators to include",
        options=list(SHORT_NAMES.values()),
        default=list(SHORT_NAMES.values()),
        key="export_picks",
    )
    reverse = {v: k for k, v in SHORT_NAMES.items()}
    chosen = [reverse[p] for p in picks]

    story_df = df[
        df["Indicator Name"].isin(chosen)
        & (df["Year"] >= year_range[0])
        & (df["Year"] <= year_range[1])
    ].sort_values(["Indicator Name", "Year"])

    st.dataframe(story_df, use_container_width=True)    

    st.write("")
    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        story_df.to_csv(index=False).encode("utf-8"),
        file_name="kenya_gender_filtered.csv",
        mime="text/csv",
        key="dl_combined",
    )