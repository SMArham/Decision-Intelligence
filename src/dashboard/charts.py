"""
High-End Dark-Theme Plotly Visualizations for P&G Decision Intelligence Portal.
"""

from typing import Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Design Constants
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
BG_COLOR = "#0f172a"        # Slate 900
CARD_BG = "#1e293b"         # Slate 800
GRID_COLOR = "#334155"      # Slate 700
TEXT_MAIN = "#f8fafc"       # Slate 50
TEXT_MUTED = "#94a3b8"      # Slate 400

ACTION_COLORS = {
    "ADVERTISE": "#10b981",       # Emerald Green
    "TEST": "#06b6d4",            # Cyan Blue
    "RESTOCK_FIRST": "#f59e0b",   # Amber / Orange
    "MAINTAIN": "#8b5cf6",        # Purple / Violet
    "STOP": "#f43f5e",            # Rose Red
}


def _apply_dark_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    """Applies a bespoke, polished dark theme to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font=dict(family=FONT_FAMILY, color=TEXT_MAIN, size=12),
        margin=dict(l=40, r=40, t=55, b=65),
        height=height,
        legend=dict(
            bgcolor="rgba(30, 41, 59, 0.7)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_MAIN, size=11),
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_MUTED, size=11),
            title_font=dict(color=TEXT_MAIN, size=12, family=FONT_FAMILY)
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_MUTED, size=11),
            title_font=dict(color=TEXT_MAIN, size=12, family=FONT_FAMILY)
        )
    )
    return fig


def plot_need_share_by_department(df_need_share: pd.DataFrame) -> go.Figure:
    """Creates a sleek horizontal bar chart of P&G Need Share with Wilson 95% CI error bounds."""
    df_sorted = df_need_share.groupby("segment").agg(
        pg_need_share=("pg_need_share", "mean"),
        ci_lower=("wilson_ci_lower", "mean"),
        ci_upper=("wilson_ci_upper", "mean"),
        total_need_items=("total_need_zone_items", "sum"),
    ).reset_index().sort_values("pg_need_share", ascending=True)

    df_sorted["error_plus"] = (df_sorted["ci_upper"] - df_sorted["pg_need_share"]) * 100
    df_sorted["error_minus"] = (df_sorted["pg_need_share"] - df_sorted["ci_lower"]) * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted["segment"].str.title(),
        x=df_sorted["pg_need_share"] * 100,
        orientation="h",
        marker=dict(
            color=df_sorted["pg_need_share"],
            colorscale=[[0, "#1e3a8a"], [0.5, "#3b82f6"], [1.0, "#06b6d4"]],
            showscale=True,
            colorbar=dict(
                title=dict(text="Need Share %", font=dict(color=TEXT_MUTED, size=11)),
                tickfont=dict(color=TEXT_MUTED, size=10),
                thickness=12,
                len=0.75
            )
        ),
        error_x=dict(
            type="data",
            symmetric=False,
            array=df_sorted["error_plus"],
            arrayminus=df_sorted["error_minus"],
            color="#f8fafc",
            thickness=1.5,
            width=4
        ),
        hovertemplate="<b>Category:</b> %{y}<br><b>P&G Need Share:</b> %{x:.1f}%<br><b>95% Wilson CI:</b> ±%{error_x.array:.1f}%<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="<b>P&G Need Basket Share by Category (with 95% Wilson CI Bounds)</b>", font=dict(size=14, color=TEXT_MAIN)),
        xaxis_title="P&G Need Zone Share (%)",
        yaxis_title=""
    )
    return _apply_dark_theme(fig, height=440)


def plot_need_share_trend(df_need_share: pd.DataFrame) -> go.Figure:
    """Plots trend lines of P&G Need Share across proxy periods."""
    df_trend = df_need_share.groupby(["proxy_period", "segment"])["pg_need_share"].mean().reset_index()

    fig = px.line(
        df_trend,
        x="proxy_period",
        y="pg_need_share",
        color="segment",
        markers=True,
        color_discrete_sequence=["#38bdf8", "#34d399", "#fbbf24", "#f472b6", "#a78bfa", "#f87171", "#fb923c"],
        labels={"pg_need_share": "P&G Need Share", "proxy_period": "Time Proxy Period", "segment": "Category"}
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
    fig.update_layout(
        title=dict(text="<b>P&G Need Share Temporal Stability Across Proxy Periods</b>", font=dict(size=14, color=TEXT_MAIN)),
        yaxis_tickformat=".0%",
        xaxis_title="Proxy Period",
        yaxis_title="Need Share (%)"
    )
    return _apply_dark_theme(fig, height=400)


def plot_supply_demand_matrix(df_recommendations: pd.DataFrame) -> go.Figure:
    """Plots 4-Quadrant Supply Availability vs Demand Need Share decision space."""
    fig = px.scatter(
        df_recommendations,
        x="supply_score",
        y="pg_need_share",
        color="action_label",
        color_discrete_map=ACTION_COLORS,
        size="recommended_ad_budget",
        size_max=36,
        hover_name="segment",
        hover_data={
            "supply_score": ":.2f",
            "pg_need_share": ":.1%",
            "final_recommended_budget": ":$,.0f",
            "expected_roas": ":.2f",
            "expected_profit_roi": ":.2f"
        },
        labels={
            "supply_score": "Supply Availability Score (0.0 to 1.2)",
            "pg_need_share": "P&G Need Basket Share",
            "action_label": "Decision Action",
            "final_recommended_budget": "Optimized Budget ($)"
        }
    )

    # Reference Thresholds
    fig.add_vline(x=0.80, line_dash="dot", line_color="#94a3b8", line_width=1.2, annotation_text="Supply Hurdle (0.80)", annotation_font_color="#cbd5e1")
    fig.add_hline(y=0.30, line_dash="dot", line_color="#94a3b8", line_width=1.2, annotation_text="Need Baseline (30%)", annotation_font_color="#cbd5e1")

    fig.update_layout(
        title=dict(text="<b>Supply vs Demand Decision Matrix (Bubble Size = Recommended Budget $)</b>", font=dict(size=14, color=TEXT_MAIN)),
        yaxis_tickformat=".0%",
        xaxis=dict(range=[0.4, 1.25])
    )
    return _apply_dark_theme(fig, height=480)


def plot_budget_allocations(df_recommendations: pd.DataFrame) -> go.Figure:
    """Plots grouped bar chart comparing Base vs Optimized Ad Budget by category."""
    df_agg = df_recommendations.groupby("segment").agg(
        base_budget=("base_ad_budget", "mean"),
        recommended_budget=("final_recommended_budget", "sum"),
    ).reset_index().sort_values("recommended_budget", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Baseline Budget ($)",
        x=df_agg["segment"].str.title(),
        y=df_agg["base_budget"],
        marker=dict(color="#475569", line=dict(color="#64748b", width=1)),
        hovertemplate="<b>%{x}</b><br>Base Budget: $%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Optimized Ad Budget ($)",
        x=df_agg["segment"].str.title(),
        y=df_agg["recommended_budget"],
        marker=dict(
            color=df_agg["recommended_budget"],
            colorscale=[[0, "#2563eb"], [1.0, "#06b6d4"]],
            line=dict(color="#38bdf8", width=1)
        ),
        hovertemplate="<b>%{x}</b><br>Optimized Budget: $%{y:,.0f}<extra></extra>"
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text="<b>Category Ad Budget Optimization ($ Allocation Comparison)</b>", font=dict(size=14, color=TEXT_MAIN)),
        yaxis_title="Ad Budget ($)",
        xaxis_title="",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f"
    )
    return _apply_dark_theme(fig, height=420)


def plot_before_after_comparison(df_before_after: pd.DataFrame) -> go.Figure:
    """Plots high-contrast bar comparison for ROAS and Wasted Spend Rate."""
    metrics_of_interest = ["Return on Ad Spend (ROAS)", "Wasted Spend Rate"]
    filtered = df_before_after[df_before_after["metric"].isin(metrics_of_interest)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Traditional Blind Marketing",
        x=filtered["metric"],
        y=filtered["baseline_blind_marketing"],
        marker=dict(color="#f43f5e", line=dict(color="#fda4af", width=1)),
        text=filtered["baseline_blind_marketing"].apply(lambda x: f"{x:.1f}"),
        textposition="auto",
        textfont=dict(color="#ffffff", size=12, family=FONT_FAMILY),
        hovertemplate="<b>%{x}</b><br>Baseline: %{y:.1f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Data-Driven Optimized Engine",
        x=filtered["metric"],
        y=filtered["optimized_data_driven"],
        marker=dict(color="#10b981", line=dict(color="#6ee7b7", width=1)),
        text=filtered["optimized_data_driven"].apply(lambda x: f"{x:.1f}"),
        textposition="auto",
        textfont=dict(color="#ffffff", size=12, family=FONT_FAMILY),
        hovertemplate="<b>%{x}</b><br>Optimized: %{y:.1f}<extra></extra>"
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text="<b>Before vs After Marketing Efficiency Benchmark (ROAS & Waste %)</b>", font=dict(size=14, color=TEXT_MAIN)),
        yaxis_title="Value (ROAS Multiplier / Waste %)",
        xaxis_title=""
    )
    return _apply_dark_theme(fig, height=400)


def plot_diminishing_returns(df_curve: pd.DataFrame) -> go.Figure:
    """Plots diminishing returns response curve with shaded area and profit margin."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_curve["spend"],
        y=df_curve["projected_revenue"],
        mode="lines",
        name="Projected Gross Revenue ($)",
        line=dict(color="#38bdf8", width=3),
        fill="tozeroy",
        fillcolor="rgba(56, 189, 248, 0.08)",
        hovertemplate="<b>Spend:</b> $%{x:,.0f}<br><b>Revenue:</b> $%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=df_curve["spend"],
        y=df_curve["projected_profit"],
        mode="lines",
        name="Projected Net Profit ($)",
        line=dict(color="#10b981", width=2.5, dash="dash"),
        hovertemplate="<b>Spend:</b> $%{x:,.0f}<br><b>Profit:</b> $%{y:,.0f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="<b>Ad Spend Diminishing Returns Response Curve ($ Saturation Model)</b>", font=dict(size=14, color=TEXT_MAIN)),
        xaxis_title="Total Ad Spend ($)",
        yaxis_title="Incremental Value ($)",
        xaxis_tickprefix="$",
        xaxis_tickformat=",.0f",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f"
    )
    return _apply_dark_theme(fig, height=400)
