"""
src/ui.py
Reusable Tailwind CSS component renderers for Pricing Comparison Analytics.
Injects Tailwind CDN via st.components.v1.html for responsive headers, KPI metric cards, and alert boxes.
"""

import streamlit as st
import streamlit.components.v1 as components

TAILWIND_CDN = '<script src="https://cdn.tailwindcss.com"></script>'

def render_tailwind_header(title: str, subtitle: str, badge_text: str = "MCA Project"):
    """
    Renders a modern, responsive header container with Tailwind styling.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        {TAILWIND_CDN}
        <style>
            body {{ margin: 0; padding: 0; background-color: transparent; font-family: ui-sans-serif, system-ui, sans-serif; }}
        </style>
    </head>
    <body>
        <div class="bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-950 p-6 rounded-2xl shadow-lg border border-slate-700/50 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <div class="flex items-center gap-3">
                    <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-white">{title}</h1>
                    <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-400/30">
                        {badge_text}
                    </span>
                </div>
                <p class="text-slate-300 text-sm mt-1 font-medium">{subtitle}</p>
            </div>
            <div class="flex items-center gap-2 text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>SQLite DB: Connected</span>
            </div>
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=115, scrolling=False)


def render_kpi_card(title: str, value: str, delta: str = "", delta_type: str = "neutral", icon_svg: str = ""):
    """
    Renders a standalone Tailwind styled KPI card.
    delta_type: 'positive' (green), 'negative' (red), 'neutral' (slate)
    """
    delta_color = "text-emerald-600 bg-emerald-50 border-emerald-200"
    if delta_type == "negative":
        delta_color = "text-rose-600 bg-rose-50 border-rose-200"
    elif delta_type == "neutral":
        delta_color = "text-slate-600 bg-slate-50 border-slate-200"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        {TAILWIND_CDN}
        <style>
            body {{ margin: 0; padding: 0; background-color: transparent; font-family: ui-sans-serif, system-ui, sans-serif; }}
        </style>
    </head>
    <body class="p-1">
        <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-200 hover:shadow-md transition-shadow duration-200">
            <div class="flex justify-between items-start">
                <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
                {f'<span class="text-slate-400">{icon_svg}</span>' if icon_svg else ''}
            </div>
            <div class="mt-2 flex items-baseline justify-between">
                <span class="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
                {f'<span class="px-2 py-0.5 rounded text-xs font-medium border {delta_color}">{delta}</span>' if delta else ''}
            </div>
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=95, scrolling=False)


def render_alert_box(title: str, message: str, alert_type: str = "warning"):
    """
    Renders a prominent alert banner for margin bleed or system alerts.
    """
    styles = {
        "warning": "bg-amber-50 border-amber-300 text-amber-900",
        "danger": "bg-rose-50 border-rose-300 text-rose-900",
        "info": "bg-blue-50 border-blue-300 text-blue-900",
        "success": "bg-emerald-50 border-emerald-300 text-emerald-900"
    }
    box_style = styles.get(alert_type, styles["warning"])

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        {TAILWIND_CDN}
        <style>
            body {{ margin: 0; padding: 0; background-color: transparent; font-family: ui-sans-serif, system-ui, sans-serif; }}
        </style>
    </head>
    <body class="p-1">
        <div class="rounded-xl border p-4 {box_style} shadow-sm">
            <div class="flex items-center gap-2">
                <span class="font-bold text-sm tracking-wide uppercase">{title}</span>
            </div>
            <p class="text-xs mt-1 leading-relaxed">{message}</p>
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=85, scrolling=False)
