import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="千歳科技大 通学ナビ", layout="wide")

# ==========================================
# 1. UIスタイル定義（余白削減・タッチ最適化）
# ==========================================
st.markdown("""
<style>
    /* 画面上部の余白を削り、緑カードを最上部に直出し */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 緑色の案内カード */
    .hero-card {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        color: white;
        border-radius: 14px;
        padding: 18px;
        margin: 0 0 16px 0;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .hero-badge-header {
        display: inline-block;
        background: rgba(167, 243, 208, 0.25);
        color: #a7f3d0;
        font-size: 13px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-bottom: 6px;
    }
    .hero-time-val {
        font-size: 44px;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -1px;
    }
    .transit-step-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
        margin-top: 12px;
    }
    .step-card {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
        padding: 6px 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .step-type {
        font-size: 11px;
        color: #a7f3d0;
        font-weight: 600;
        margin-bottom: 2px;
    }
    .step-main {
        font-size: 14px;
        font-weight: 700;
        color: #ffffff;
    }
    .step-sub {
        font-size: 11px;
        color: #e2e8f0;
    }
    .step-arrow {
        color: #a7f3d0;
        font-size: 15px;
        font-weight: 900;
    }

    /* 設定エリア */
    .filter-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 14px;
        margin-top: 6px;
        margin-bottom: 16px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px;
        display: flex;
        flex-wrap: wrap;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 8px 12px !important;
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 8px;
        cursor: pointer;
        min-height: 42px;
        display: inline-flex;
        align-items: center;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #065f46 !important;
        color: #ffffff !important;
        border-color: #047857 !important;
    }
    div[data-testid="stSelectbox"] select, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        font-size: 18px !important;
        font-weight: 700 !important;
        min-height: 44px !important;
    }
    
    /* 時限クイックボタン */
    div[data-testid="stButton"] button {
        font-size: 13px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        min-height: 40px !important;
        border: 1.5px solid #065f46 !important;
        color: #065f46 !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #065f46 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. JRデータ定義
# ==========================================
JR_NAEBO_SAPPORO = [
    "06:19", "06:36", "06:42", "06:59", "07:04", "07:13", "07:26", "07:34", 
    "07:39", "07:44", "07:51", "07:56", "07:59", "08:05", "08:09", "08:13", 
    "08:16", "08:19", "08:26", "08:27", "08:32", "08:35", "08:40", "08:48", 
    "08:54", "09:09", "09:10", "09:24", "09:30", "09:40", "09:44", "09:58"
]

JR_NAEBO_SHINSAPPORO = [
    {"dep": "06:38", "arr": "06:48"}, {"dep": "07:03", "arr": "07:13"},
    {"dep": "07:18", "arr": "07:28"}, {"dep": "07:54", "arr": "08:04"},
    {"dep": "08:14", "arr": "08:24"}, {"dep": "08:29", "arr": "08:39"},
    {"dep": "09:13", "arr": "09:23"}, {"dep": "09:40", "arr": "09:50"}
]

JR_RAPID_UP = [
    {"dep_sap": "06:48", "dep_shin": "06:58", "arr_chi": "07:18", "arr_mchi": "07:22"},
    {"dep_sap": "07:00", "dep_shin": "07:09", "arr_chi": "07:29", "arr_mchi": "07:33"},
    {"dep_sap": "07:15", "dep_shin": "07:24", "arr_chi": "07:45", "arr_mchi": "07:49"},
    {"dep_sap": "07:30", "dep_shin": "07:40", "arr_chi": "08:00", "arr_mchi": "08:04"},
    {"dep_sap": "07:42", "dep_shin": "07:51", "arr_chi": "08:11", "arr_mchi": "08:15"},
    {"dep_sap": "07:55", "dep_shin": "08:04", "arr_chi": "08:24", "arr_mchi": "08:28"},
    {"dep_sap": "08:07", "dep_shin": "08:17", "arr_chi": "08:37", "arr_mchi": "08:41"},
    {"dep_sap": "08:20", "dep_shin": "08:30", "arr_chi": "08:50", "arr_mchi": "08:54"},
    {"dep_sap": "08:35", "dep_shin": "08:45", "arr_chi": "09:05", "arr_mchi": "09:09"},
    {"dep_sap": "08:50", "dep_shin": "09:00", "arr_chi": "09:20", "arr_mchi": "09:24"},
    {"dep_sap": "09:05", "dep_shin": "09:15", "arr_chi": "09:35", "arr_mchi": "09:39"},
    {"dep_sap": "09:20", "dep_shin": "09:30", "arr_chi": "09:50", "arr_mchi": "09:54"},
    {"dep_sap": "09:35", "dep_shin": "09:45", "arr_chi": "10:05", "arr_mchi": "10:09"},
    {"dep_sap": "09:50", "dep_shin": "10:00", "arr_chi": "10:20", "arr_mchi": "10:24"}
]

JR_RAPID_DOWN = [
    {'dep_mchi': '08:08', 'dep_chi': '08:12', 'arr_kita': '08:24', 'arr_shin': '08:33', 'arr_shiro': '08:38', 'arr_sap': '08:42'},
    {'dep_mchi': '08:22', 'dep_chi': '08:26', 'arr_kita': '08:38', 'arr_shin': '08:49', 'arr_shiro': '08:54', 'arr_sap': '08:58'},
    {'dep_mchi': '08:33', 'dep_chi': '08:37', 'arr_kita': '08:49', 'arr_shin': '08:58', 'arr_shiro': '09:03', 'arr_sap': '09:07'},
    {'dep_mchi': '08:44', 'dep_chi': '08:48', 'arr_kita': '09:00', 'arr_shin': '09:09', 'arr_shiro': '09:14', 'arr_sap': '09:18'},
    {'dep_mchi': '08:55', 'dep_chi': '08:59', 'arr_kita': '09:11', 'arr_shin': '09:21', 'arr_shiro': '09:26', 'arr_sap': '09:30'},
    {'dep_mchi': '09:09', 'dep_chi': '09:13', 'arr_kita': '09:25', 'arr_shin': '09:35', 'arr_shiro': '09:40', 'arr_sap': '09:44'},
    {'dep_mchi': '09:22', 'dep_chi': '09:26', 'arr_kita': '09:38', 'arr_shin': '09:48', 'arr_shiro': '09:53', 'arr_sap': '09:57'},
    {'dep_mchi': '09:32', 'dep_chi': '09:36', 'arr_kita': '09:48', 'arr_shin': '09:57', 'arr_shiro': '10:02', 'arr_sap': '10:06'},
    {'dep_mchi': '09:42', 'dep_chi': '09:46', 'arr_kita': '09:58', 'arr_shin': '10:13', 'arr_shiro': '10:18', 'arr_sap': '10:22'},
    {'dep_mchi': '10:02', 'dep_chi': '10:06', 'arr_kita': '10:18', 'arr_shin': '10:27', 'arr_shiro': '10:32', 'arr_sap': '10:36'},
    {'dep_mchi': '10:12', 'dep_chi': '10:16', 'arr_kita': '10:28', 'arr_shin': '10:43', 'arr_shiro': '10:48', 'arr_sap': '10:52'},
    {'dep_mchi': '10:24', 'dep_chi': '10:27', 'arr_kita': '10:39', 'arr_shin': '10:48', 'arr_shiro': '10:53', 'arr_sap': '10:57'},
    {'dep_mchi': '10:42', 'dep_chi': '10:46', 'arr_kita': '10:58', 'arr_shin': '11:13', 'arr_shiro': '11:18', 'arr_sap': '11:22'},
    {'dep_mchi': '11:02', 'dep_chi': '11:06', 'arr_kita': '11:18', 'arr_shin': '11:27', 'arr_shiro': '11:32', 'arr_sap': '11:36'},
    {'dep_mchi': '11:23', 'dep_chi': '11:27', 'arr_kita': '11:39', 'arr_shin': '11:48', 'arr_shiro': '11:53', 'arr_sap': '11:57'},
    {'dep_mchi': '11:42', 'dep_chi': '11:46', 'arr_kita': '11:58', 'arr_shin': '12:13', 'arr_shiro': '12:18', 'arr_sap': '12:22'},
    {'dep_mchi': '12:02', 'dep_chi': '12:06', 'arr_kita': '12:18', 'arr_shin': '12:27', 'arr_shiro': '12:32', 'arr_sap': '12:36'},
    {'dep_mchi': '12:23', 'dep_chi': '12:27', 'arr_kita': '12:39', 'arr_shin': '12:48', 'arr_shiro': '12:53', 'arr_sap': '12:57'},
    {'dep_mchi': '12:42', 'dep_chi': '12:46', 'arr_kita': '12:58', 'arr_shin': '13:13', 'arr_shiro': '13:18', 'arr_sap': '13:22'},
    {'dep_mchi': '13:02', 'dep_chi': '13:06', 'arr_kita': '13:18', 'arr_shin': '13:27', 'arr_shiro': '13:32', 'arr_sap': '13:36'},
    {'dep_mchi': '13:23', 'dep_chi': '13:27', 'arr_kita': '13:39', 'arr_shin': '13:48', 'arr_shiro': '13:53', 'arr_sap': '13:57'},
    {'dep_mchi': '13:42', 'dep_chi': '13:46', 'arr_kita': '13:58', 'arr_shin': '14:13', 'arr_shiro': '14:18', 'arr_sap': '14:22'},
    {'dep_mchi': '14:02', 'dep_chi': '14:06', 'arr_kita': '14:18', 'arr_shin': '14:27', 'arr_shiro': '14:32', 'arr_sap': '14:36'},
    {'dep_mchi': '14:23', 'dep_chi': '14:27', 'arr_kita': '14:39', 'arr_shin': '14:48', 'arr_shiro': '14:53', 'arr_sap': '14:57'},
    {'dep_mchi': '14:43', 'dep_chi': '14:46', 'arr_kita': '14:58', 'arr_shin': '15:13', 'arr_shiro': '15:18', 'arr_sap': '15:22'},
    {'dep_mchi': '15:02', 'dep_chi': '15:06', 'arr_kita': '15:18', 'arr_shin': '15:27', 'arr_shiro': '15:32', 'arr_sap': '15:36'},
    {'dep_mchi': '15:23', 'dep_chi': '15:27', 'arr_kita': '15:39', 'arr_shin': '15:48', 'arr_shiro': '15:53', 'arr_sap': '15:57'},
    {'dep_mchi': '15:42', 'dep_chi': '15:46', 'arr_kita': '15:58', 'arr_shin': '16:13', 'arr_shiro': '16:18', 'arr_sap': '16:22'},
    {'dep_mchi': '16:02', 'dep_chi': '16:06', 'arr_kita': '16:18', 'arr_shin': '16:27', 'arr_shiro': '16:32', 'arr_sap': '16:36'},
    {'dep_mchi': '16:23', 'dep_chi': '16:27', 'arr_kita': '16:39', 'arr_shin': '16:48', 'arr_shiro': '16:53', 'arr_sap': '16:57'},
    {'dep_mchi': '16:45', 'dep_chi': '16:49', 'arr_kita': '17:01', 'arr_shin': '17:12', 'arr_shiro': '17:17', 'arr_sap': '17:21'},
    {'dep_mchi': '17:09', 'dep_chi': '17:13', 'arr_kita': '17:25', 'arr_shin': '17:36', 'arr_shiro': '17:41', 'arr_sap': '17:45'},
    {'dep_mchi': '17:33', 'dep_chi': '17:37', 'arr_kita': '17:49', 'arr_shin': '18:00', 'arr_shiro': '18:05', 'arr_sap': '18:09'},
    {'dep_mchi': '17:57', 'dep_chi': '18:01', 'arr_kita': '18:13', 'arr_shin': '18:24', 'arr_shiro': '18:29', 'arr_sap': '18:33'},
    {'dep_mchi': '18:21', 'dep_chi': '18:25', 'arr_kita': '18:37', 'arr_shin': '18:48', 'arr_shiro': '18:53', 'arr_sap': '18:57'},
    {'dep_mchi': '18:45', 'dep_chi': '18:49', 'arr_kita': '19:01', 'arr_shin': '19:12', 'arr_shiro': '19:17', 'arr_sap': '19:21'},
    {'dep_mchi': '19:10', 'dep_chi': '19:14', 'arr_kita': '19:26', 'arr_shin': '19:37', 'arr_shiro': '19:42', 'arr_sap': '19:46'},
    {'dep_mchi': '19:33', 'dep_chi': '19:37', 'arr_kita': '19:49', 'arr_shin': '20:00', 'arr_shiro': '20:05', 'arr_sap': '20:09'},
    {'dep_mchi': '20:09', 'dep_chi': '20:13', 'arr_kita': '20:25', 'arr_shin': '20:34', 'arr_shiro': '20:39', 'arr_sap': '20:43'},
    {'dep_mchi': '20:35', 'dep_chi': '20:39', 'arr_kita': '20:51', 'arr_shin': '21:00', 'arr_shiro': '21:05', 'arr_sap': '21:09'},
    {'dep_mchi': '20:55', 'dep_chi': '20:59', 'arr_kita': '21:11', 'arr_shin': '21:16', 'arr_shiro': '21:21', 'arr_sap': '21:25'},
    {'dep_mchi': '21:22', 'dep_chi': '21:26', 'arr_kita': '21:38', 'arr_shin': '21:44', 'arr_shiro': '21:49', 'arr_sap': '21:53'},
    {'dep_mchi': '21:48', 'dep_chi': '21:52', 'arr_kita': '22:04', 'arr_shin': '22:11', 'arr_shiro': '22:16', 'arr_sap': '22:20'},
    {'dep_mchi': '22:09', 'dep_chi': '22:13', 'arr_kita': '22:25', 'arr_shin': '22:30', 'arr_shiro': '22:35', 'arr_sap': '22:39'},
    {'dep_mchi': '22:39', 'dep_chi': '22:43', 'arr_kita': '22:54', 'arr_shin': '22:59', 'arr_shiro': '23:04', 'arr_sap': '23:08'}
]

JR_SAPPORO_TO_NAEBO = [
    "08:52", "09:10", "09:23", "09:37", "09:46", "10:06", "10:07", "10:26", "10:37", "10:45",
    "11:06", "11:11", "11:23", "11:37", "11:45", "12:08", "12:11", "12:27", "12:38", "12:43",
    "13:07", "13:10", "13:26", "13:37", "13:43", "14:07", "14:10", "14:23", "14:37", "14:47",
    "15:07", "15:08", "15:23", "15:36", "15:37", "15:46", "15:53", "16:05", "16:15", "16:22", "16:37", "16:42", "16:53",
    "17:03", "17:05", "17:14", "17:23", "17:38", "17:39", "17:46", "17:53", "18:02", "18:04", "18:14", "18:23", "18:26", "18:38", "18:51", "18:53",
    "19:03", "19:14", "19:16", "19:25", "19:37", "19:43", "19:48", "20:03", "20:10", "20:11", "20:20", "20:24", "20:30", "20:39", "20:40", "20:52", "20:53",
    "21:04", "21:14", "21:15", "21:27", "21:34", "21:37", "21:47", "21:49", "22:02", "22:11", "22:25", "22:37", "22:47", "23:00", "23:05", "23:23", "23:34", "23:43"
]

JR_CHITOSE_LOCALS = [
    {'dep_chi': '08:18', 'dep_kita': '08:35', 'dep_shin': '08:50', 'dep_shiro': '08:56', 'arr_naebo': '09:00'},
    {'dep_chi': '08:42', 'dep_kita': '08:59', 'dep_shin': '09:14', 'dep_shiro': '09:20', 'arr_naebo': '09:24'},
    {'dep_chi': '09:16', 'dep_kita': '09:33', 'dep_shin': '09:48', 'dep_shiro': '09:54', 'arr_naebo': '09:58'},
    {'dep_chi': '09:45', 'dep_kita': '10:02', 'dep_shin': '10:18', 'dep_shiro': '10:24', 'arr_naebo': '10:28'},
    {'dep_chi': '10:15', 'dep_kita': '10:32', 'dep_shin': '10:47', 'dep_shiro': '10:53', 'arr_naebo': '10:57'},
    {'dep_chi': '10:55', 'dep_kita': '11:12', 'dep_shin': '11:27', 'dep_shiro': '11:33', 'arr_naebo': '11:37'},
    {'dep_chi': '11:36', 'dep_kita': '11:53', 'dep_shin': '12:08', 'dep_shiro': '12:14', 'arr_naebo': '12:18'},
    {'dep_chi': '12:05', 'dep_kita': '12:22', 'dep_shin': '12:37', 'dep_shiro': '12:43', 'arr_naebo': '12:47'},
    {'dep_chi': '12:34', 'dep_kita': '12:51', 'dep_shin': '13:06', 'dep_shiro': '13:12', 'arr_naebo': '13:16'},
    {'dep_chi': '13:00', 'dep_kita': '13:17', 'dep_shin': '13:32', 'dep_shiro': '13:38', 'arr_naebo': '13:42'},
    {'dep_chi': '13:34', 'dep_kita': '13:51', 'dep_shin': '14:06', 'dep_shiro': '14:12', 'arr_naebo': '14:16'},
    {'dep_chi': '13:55', 'dep_kita': '14:12', 'dep_shin': '14:27', 'dep_shiro': '14:33', 'arr_naebo': '14:37'},
    {'dep_chi': '14:34', 'dep_kita': '14:51', 'dep_shin': '15:06', 'dep_shiro': '15:12', 'arr_naebo': '15:16'},
    {'dep_chi': '15:00', 'dep_kita': '15:17', 'dep_shin': '15:32', 'dep_shiro': '15:38', 'arr_naebo': '15:42'},
    {'dep_chi': '15:34', 'dep_kita': '15:51', 'dep_shin': '16:06', 'dep_shiro': '16:12', 'arr_naebo': '16:16'},
    {'dep_chi': '16:06', 'dep_kita': '16:23', 'dep_shin': '16:38', 'dep_shiro': '16:44', 'arr_naebo': '16:48'},
    {'dep_chi': '16:33', 'dep_kita': '16:50', 'dep_shin': '17:05', 'dep_shiro': '17:11', 'arr_naebo': '17:15'},
    {'dep_chi': '17:03', 'dep_kita': '17:20', 'dep_shin': '17:35', 'dep_shiro': '17:41', 'arr_naebo': '17:45'},
    {'dep_chi': '17:29', 'dep_kita': '17:46', 'dep_shin': '18:01', 'dep_shiro': '18:07', 'arr_naebo': '18:11'},
    {'dep_chi': '18:00', 'dep_kita': '18:17', 'dep_shin': '18:32', 'dep_shiro': '18:38', 'arr_naebo': '18:42'},
    {'dep_chi': '18:30', 'dep_kita': '18:47', 'dep_shin': '19:02', 'dep_shiro': '19:08', 'arr_naebo': '19:12'},
    {'dep_chi': '18:53', 'dep_kita': '19:10', 'dep_shin': '19:25', 'dep_shiro': '19:31', 'arr_naebo': '19:35'},
    {'dep_chi': '19:18', 'dep_kita': '19:35', 'dep_shin': '19:50', 'dep_shiro': '19:56', 'arr_naebo': '20:00'},
    {'dep_chi': '19:54', 'dep_kita': '20:11', 'dep_shin': '20:26', 'dep_shiro': '20:32', 'arr_naebo': '20:36'},
    {'dep_chi': '20:18', 'dep_kita': '20:35', 'dep_shin': '20:50', 'dep_shiro': '20:56', 'arr_naebo': '21:00'},
    {'dep_chi': '20:46', 'dep_kita': '21:03', 'dep_shin': '21:18', 'dep_shiro': '21:24', 'arr_naebo': '21:28'},
    {'dep_chi': '21:17', 'dep_kita': '21:34', 'dep_shin': '21:49', 'dep_shiro': '21:55', 'arr_naebo': '21:59'},
    {'dep_chi': '21:46', 'dep_kita': '22:03', 'dep_shin': '22:18', 'dep_shiro': '22:24', 'arr_naebo': '22:28'},
    {'dep_chi': '22:05', 'dep_kita': '22:22', 'dep_shin': '22:37', 'dep_shiro': '22:43', 'arr_naebo': '22:47'},
    {'dep_chi': '22:30', 'dep_kita': '22:47', 'dep_shin': '23:02', 'dep_shiro': '23:08', 'arr_naebo': '23:12'}
]

# ==========================================
# 3. バスデータ定義（平日・土日祝）
# ==========================================
BUS_GO_HEIJITSU = [
    {'dep_station': '千歳駅', 'dep_time': '06:29', 'arr_kenkyu': '06:53', 'arr_honbu': '06:54', 'line': '空18'},
    {'dep_station': '南千歳駅', 'dep_time': '06:40', 'arr_kenkyu': '06:53', 'arr_honbu': '06:54', 'line': '空18'},
    {'dep_station': '千歳駅', 'dep_time': '06:59', 'arr_kenkyu': '07:23', 'arr_honbu': '07:24', 'line': '空18'},
    {'dep_station': '南千歳駅', 'dep_time': '07:10', 'arr_kenkyu': '07:23', 'arr_honbu': '07:24', 'line': '空18'},
    {'dep_station': '千歳駅', 'dep_time': '06:45', 'arr_kenkyu': '07:09', 'arr_honbu': '07:10', 'line': '空17'},
    {'dep_station': '南千歳駅', 'dep_time': '06:56', 'arr_kenkyu': '07:09', 'arr_honbu': '07:10', 'line': '空17'},
    {'dep_station': '南千歳駅', 'dep_time': '06:50', 'arr_kenkyu': '06:58', 'arr_honbu': '07:01', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '07:00', 'arr_kenkyu': '07:18', 'arr_honbu': '07:21', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '07:10', 'arr_kenkyu': '07:18', 'arr_honbu': '07:21', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '07:34', 'arr_kenkyu': '07:58', 'arr_honbu': '07:59', 'line': '空18'},
    {'dep_station': '南千歳駅', 'dep_time': '07:45', 'arr_kenkyu': '07:58', 'arr_honbu': '07:59', 'line': '空18'},
    {'dep_station': '千歳駅', 'dep_time': '07:15', 'arr_kenkyu': '07:39', 'arr_honbu': '07:40', 'line': '空17'},
    {'dep_station': '南千歳駅', 'dep_time': '07:26', 'arr_kenkyu': '07:39', 'arr_honbu': '07:40', 'line': '空17'},
    {'dep_station': '南千歳駅', 'dep_time': '07:25', 'arr_kenkyu': '07:33', 'arr_honbu': '07:36', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '07:29', 'arr_kenkyu': '07:47', 'arr_honbu': '07:50', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '07:30', 'arr_kenkyu': '07:38', 'arr_honbu': '07:41', 'line': '南17'},
    {'dep_station': '南千歳駅', 'dep_time': '07:50', 'arr_kenkyu': '07:58', 'arr_honbu': '08:01', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '07:50', 'arr_kenkyu': '08:08', 'arr_honbu': '08:11', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '08:00', 'arr_kenkyu': '08:18', 'arr_honbu': '08:21', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '08:05', 'arr_kenkyu': '08:13', 'arr_honbu': '08:16', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '08:10', 'arr_kenkyu': '08:28', 'arr_honbu': '08:31', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '08:16', 'arr_kenkyu': '08:34', 'arr_honbu': '08:37', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '08:19', 'arr_kenkyu': '08:37', 'arr_honbu': '08:40', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '08:24', 'arr_kenkyu': '08:42', 'arr_honbu': '08:45', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '08:29', 'arr_kenkyu': '08:47', 'arr_honbu': '08:50', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '08:35', 'arr_kenkyu': '08:43', 'arr_honbu': '08:46', 'line': '南17'},
    {'dep_station': '南千歳駅', 'dep_time': '08:40', 'arr_kenkyu': '08:48', 'arr_honbu': '08:51', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '08:50', 'arr_kenkyu': '09:08', 'arr_honbu': '09:11', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '08:55', 'arr_kenkyu': '09:03', 'arr_honbu': '09:06', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '09:04', 'arr_kenkyu': '09:22', 'arr_honbu': '09:25', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '09:19', 'arr_kenkyu': '09:37', 'arr_honbu': '09:40', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '09:25', 'arr_kenkyu': '09:33', 'arr_honbu': '09:36', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '09:34', 'arr_kenkyu': '09:52', 'arr_honbu': '09:55', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '09:40', 'arr_kenkyu': '09:48', 'arr_honbu': '09:51', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '09:50', 'arr_kenkyu': '10:14', 'arr_honbu': '10:15', 'line': '空17'},
    {'dep_station': '南千歳駅', 'dep_time': '10:01', 'arr_kenkyu': '10:14', 'arr_honbu': '10:15', 'line': '空17'},
    {'dep_station': '千歳駅', 'dep_time': '09:54', 'arr_kenkyu': '10:12', 'arr_honbu': '10:15', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '10:04', 'arr_kenkyu': '10:22', 'arr_honbu': '10:25', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '10:05', 'arr_kenkyu': '10:13', 'arr_honbu': '10:16', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '10:14', 'arr_kenkyu': '10:32', 'arr_honbu': '10:35', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '10:20', 'arr_kenkyu': '10:28', 'arr_honbu': '10:31', 'line': '南17'}
]

BUS_GO_HOLIDAY = [
    {'dep_station': '千歳駅', 'dep_time': '06:29', 'arr_kenkyu': '06:53', 'arr_honbu': '06:54', 'line': '空18'},
    {'dep_station': '南千歳駅', 'dep_time': '06:40', 'arr_kenkyu': '06:53', 'arr_honbu': '06:54', 'line': '空18'},
    {'dep_station': '南千歳駅', 'dep_time': '06:50', 'arr_kenkyu': '06:58', 'arr_honbu': '07:01', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '07:15', 'arr_kenkyu': '07:39', 'arr_honbu': '07:40', 'line': '空17'},
    {'dep_station': '南千歳駅', 'dep_time': '07:26', 'arr_kenkyu': '07:39', 'arr_honbu': '07:40', 'line': '空17'},
    {'dep_station': '千歳駅', 'dep_time': '07:34', 'arr_kenkyu': '07:58', 'arr_honbu': '07:59', 'line': '空18'},
    {'dep_station': '南千歳駅', 'dep_time': '07:45', 'arr_kenkyu': '07:58', 'arr_honbu': '07:59', 'line': '空18'},
    {'dep_station': '南千歳駅', 'dep_time': '07:50', 'arr_kenkyu': '07:58', 'arr_honbu': '08:01', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '07:50', 'arr_kenkyu': '08:08', 'arr_honbu': '08:11', 'line': '直17'},
    {'dep_station': '千歳駅', 'dep_time': '08:24', 'arr_kenkyu': '08:42', 'arr_honbu': '08:45', 'line': '直17'},
    {'dep_station': '南千歳駅', 'dep_time': '08:30', 'arr_kenkyu': '08:38', 'arr_honbu': '08:41', 'line': '南17'},
    {'dep_station': '千歳駅', 'dep_time': '09:50', 'arr_kenkyu': '10:14', 'arr_honbu': '10:15', 'line': '空17'}
]

BUS_BACK_HEIJITSU = [
    {'line': '空17', 'dep_honbu': '08:22', 'dep_kenkyu': '08:25', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '08:48', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '08:22', 'dep_kenkyu': '08:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '08:37', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '09:02', 'dep_kenkyu': '09:05', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '09:28', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '09:02', 'dep_kenkyu': '09:05', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '09:17', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '09:32', 'dep_kenkyu': '09:35', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '09:58', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '09:32', 'dep_kenkyu': '09:35', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '09:47', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '10:42', 'dep_kenkyu': '10:45', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '11:08', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '10:42', 'dep_kenkyu': '10:45', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '10:57', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '12:22', 'dep_kenkyu': '12:25', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '12:50', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '12:22', 'dep_kenkyu': '12:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '12:37', 'drop_detail': '南千歳駅（降車）'},
    {'line': '直17', 'dep_honbu': '12:27', 'dep_kenkyu': '12:30', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '12:49', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '空17', 'dep_honbu': '12:42', 'dep_kenkyu': '12:45', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '13:08', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '12:42', 'dep_kenkyu': '12:45', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '12:57', 'drop_detail': '南千歳駅（降車）'},
    {'line': '直17', 'dep_honbu': '13:07', 'dep_kenkyu': '13:10', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '13:29', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '空17', 'dep_honbu': '13:35', 'dep_kenkyu': '13:38', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '14:01', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '13:35', 'dep_kenkyu': '13:38', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '13:50', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '14:17', 'dep_kenkyu': '14:20', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '14:43', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '14:17', 'dep_kenkyu': '14:20', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '14:32', 'drop_detail': '南千歳駅（降車）'},
    {'line': '直17', 'dep_honbu': '14:52', 'dep_kenkyu': '14:55', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '15:14', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '空18', 'dep_honbu': '15:12', 'dep_kenkyu': '15:15', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '15:40', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '15:12', 'dep_kenkyu': '15:15', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '15:27', 'drop_detail': '南千歳駅（降車）'},
    {'line': '南17', 'dep_honbu': '15:17', 'dep_kenkyu': '15:20', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '15:31', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '空17', 'dep_honbu': '15:24', 'dep_kenkyu': '15:27', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '15:50', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '15:24', 'dep_kenkyu': '15:27', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '15:39', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '15:47', 'dep_kenkyu': '15:50', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '16:13', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '15:47', 'dep_kenkyu': '15:50', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '16:02', 'drop_detail': '南千歳駅（降車）'},
    {'line': '直17', 'dep_honbu': '16:02', 'dep_kenkyu': '16:05', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '16:24', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '南17', 'dep_honbu': '16:35', 'dep_kenkyu': '16:38', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '16:49', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '直17', 'dep_honbu': '16:42', 'dep_kenkyu': '16:45', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '17:04', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '南17', 'dep_honbu': '16:44', 'dep_kenkyu': '16:47', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '16:58', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '空17', 'dep_honbu': '16:47', 'dep_kenkyu': '16:50', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '17:13', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '16:47', 'dep_kenkyu': '16:50', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '17:02', 'drop_detail': '南千歳駅（降車）'},
    {'line': '直17', 'dep_honbu': '17:02', 'dep_kenkyu': '17:05', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '17:24', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '南17', 'dep_honbu': '17:07', 'dep_kenkyu': '17:10', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '17:21', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '南17', 'dep_honbu': '17:12', 'dep_kenkyu': '17:15', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '17:26', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '直17', 'dep_honbu': '17:17', 'dep_kenkyu': '17:20', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '17:39', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '直17', 'dep_honbu': '17:30', 'dep_kenkyu': '17:33', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '17:52', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '直17', 'dep_honbu': '17:42', 'dep_kenkyu': '17:45', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '18:04', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '南17', 'dep_honbu': '17:47', 'dep_kenkyu': '17:50', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '18:01', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '空18', 'dep_honbu': '18:07', 'dep_kenkyu': '18:10', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '18:35', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '18:07', 'dep_kenkyu': '18:10', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '18:22', 'drop_detail': '南千歳駅（降車）'},
    {'line': '南17', 'dep_honbu': '18:12', 'dep_kenkyu': '18:15', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '18:26', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '南17', 'dep_honbu': '18:22', 'dep_kenkyu': '18:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '18:36', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '直17', 'dep_honbu': '18:27', 'dep_kenkyu': '18:30', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '18:49', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '南17', 'dep_honbu': '18:32', 'dep_kenkyu': '18:35', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '18:46', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '直17', 'dep_honbu': '18:47', 'dep_kenkyu': '18:50', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '19:09', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '空18', 'dep_honbu': '18:59', 'dep_kenkyu': '19:02', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '19:27', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '18:59', 'dep_kenkyu': '19:02', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '19:14', 'drop_detail': '南千歳駅（降車）'},
    {'line': '南17', 'dep_honbu': '19:02', 'dep_kenkyu': '19:05', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '19:16', 'drop_detail': '南千歳駅北口（降車）'},
    {'line': '直17', 'dep_honbu': '19:12', 'dep_kenkyu': '19:15', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '19:34', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '空18', 'dep_honbu': '19:17', 'dep_kenkyu': '19:20', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '19:45', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '19:17', 'dep_kenkyu': '19:20', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '19:32', 'drop_detail': '南千歳駅（降車）'},
    {'line': '直17', 'dep_honbu': '19:32', 'dep_kenkyu': '19:35', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '19:54', 'drop_detail': '千歳駅前（降車専用）'},
    {'line': '空18', 'dep_honbu': '19:42', 'dep_kenkyu': '19:45', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '20:10', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '19:42', 'dep_kenkyu': '19:45', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '19:57', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '20:22', 'dep_kenkyu': '20:25', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '20:50', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '20:22', 'dep_kenkyu': '20:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '20:37', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '21:02', 'dep_kenkyu': '21:05', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '21:30', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '21:02', 'dep_kenkyu': '21:05', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '21:17', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '21:52', 'dep_kenkyu': '21:55', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '22:20', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '21:52', 'dep_kenkyu': '21:55', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '22:07', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '22:32', 'dep_kenkyu': '22:35', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '23:00', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '22:32', 'dep_kenkyu': '22:35', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '22:47', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '23:32', 'dep_kenkyu': '23:35', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '24:00', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '23:32', 'dep_kenkyu': '23:35', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '23:47', 'drop_detail': '南千歳駅（降車）'}
]

BUS_BACK_HOLIDAY = [
    {'line': '空17', 'dep_honbu': '08:22', 'dep_kenkyu': '08:25', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '08:48', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '08:22', 'dep_kenkyu': '08:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '08:37', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '09:02', 'dep_kenkyu': '09:05', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '09:28', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '09:02', 'dep_kenkyu': '09:05', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '09:17', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '09:32', 'dep_kenkyu': '09:35', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '09:58', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '09:32', 'dep_kenkyu': '09:35', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '09:47', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '10:42', 'dep_kenkyu': '10:45', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '11:08', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '10:42', 'dep_kenkyu': '10:45', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '10:57', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '11:36', 'dep_kenkyu': '11:39', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '12:02', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '11:36', 'dep_kenkyu': '11:39', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '11:51', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '12:22', 'dep_kenkyu': '12:25', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '12:50', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '12:22', 'dep_kenkyu': '12:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '12:37', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '13:35', 'dep_kenkyu': '13:38', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '14:01', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '13:35', 'dep_kenkyu': '13:38', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '13:50', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '14:32', 'dep_kenkyu': '14:35', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '14:58', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '14:32', 'dep_kenkyu': '14:35', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '14:47', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '15:12', 'dep_kenkyu': '15:15', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '15:40', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '15:12', 'dep_kenkyu': '15:15', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '15:27', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空17', 'dep_honbu': '16:47', 'dep_kenkyu': '16:50', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '17:13', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空17', 'dep_honbu': '16:47', 'dep_kenkyu': '16:50', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '17:02', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '18:07', 'dep_kenkyu': '18:10', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '18:35', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '18:07', 'dep_kenkyu': '18:10', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '18:22', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '18:42', 'dep_kenkyu': '18:45', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '19:10', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '18:42', 'dep_kenkyu': '18:45', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '18:57', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '19:17', 'dep_kenkyu': '19:20', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '19:45', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '19:17', 'dep_kenkyu': '19:20', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '19:32', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '20:22', 'dep_kenkyu': '20:25', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '20:50', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '20:22', 'dep_kenkyu': '20:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '20:37', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '21:22', 'dep_kenkyu': '21:25', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '21:50', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '21:22', 'dep_kenkyu': '21:25', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '21:37', 'drop_detail': '南千歳駅（降車）'},
    {'line': '空18', 'dep_honbu': '23:32', 'dep_kenkyu': '23:35', 'bus_arr_sta': '千歳駅', 'bus_arr_time': '24:00', 'drop_detail': '千歳駅前（降車）'},
    {'line': '空18', 'dep_honbu': '23:32', 'dep_kenkyu': '23:35', 'bus_arr_sta': '南千歳駅', 'bus_arr_time': '23:47', 'drop_detail': '南千歳駅（降車）'}
]

# ==========================================
# 4. 共通計算関数
# ==========================================
def t2m(t_str):
    if not t_str or t_str == '－': return 9999
    h, m = map(int, str(t_str).split(":"))
    return h * 60 + m

def m2t(m_int):
    return f"{(m_int // 60) % 24:02d}:{m_int % 60:02d}"

def get_bus_stop_detail(station, line):
    if "千歳駅" in station and "南" not in station:
        if "直17" in line: return "千歳駅前 4番のりば"
        elif "空" in line: return "千歳駅前 5番のりば"
        return "千歳駅前 バスのりば"
    elif "南千歳" in station:
        if "南17" in line: return "南千歳駅 北口のりば"
        return "南千歳駅 バスのりば"
    return f"{station} バスのりば"

# ==========================================
# 5. 往路（登校）計算
# ==========================================
def calculate_go_routes(bus_data, dest_building, walk_time):
    bus_df = pd.DataFrame(bus_data)
    routes = []
    
    # 札幌駅乗換
    for n_dep in JR_NAEBO_SAPPORO:
        n_dep_m = t2m(n_dep)
        home_dep_m = n_dep_m - walk_time
        sap_arr_m = n_dep_m + 3
        for rap in JR_RAPID_UP:
            rap_dep_m = t2m(rap["dep_sap"])
            if rap_dep_m >= sap_arr_m + 4:
                chi_arr_m = t2m(rap["arr_chi"])
                for _, b in bus_df[bus_df["dep_station"] == "千歳駅"].iterrows():
                    if t2m(b["dep_time"]) >= chi_arr_m + 3:
                        arr_time = b["arr_kenkyu"] if dest_building == "研究棟" else b["arr_honbu"]
                        routes.append({
                            "home_dep_m": home_dep_m, "home_dep": m2t(home_dep_m),
                            "naebo_dep": n_dep, "transfer_sta": "札幌駅", "rap_dep": rap["dep_sap"],
                            "bus_sta": "千歳駅", "bus_stop_detail": get_bus_stop_detail("千歳駅", b["line"]),
                            "bus_dep": b["dep_time"], "bus_line": b["line"],
                            "univ_arr": arr_time, "univ_arr_m": t2m(arr_time),
                            "pref_sapporo": 1, "pref_mchitose": 0
                        })
                        break
                mchi_arr_m = t2m(rap["arr_mchi"])
                for _, b in bus_df[bus_df["dep_station"] == "南千歳駅"].iterrows():
                    if t2m(b["dep_time"]) >= mchi_arr_m + 3:
                        arr_time = b["arr_kenkyu"] if dest_building == "研究棟" else b["arr_honbu"]
                        routes.append({
                            "home_dep_m": home_dep_m, "home_dep": m2t(home_dep_m),
                            "naebo_dep": n_dep, "transfer_sta": "札幌駅", "rap_dep": rap["dep_sap"],
                            "bus_sta": "南千歳駅", "bus_stop_detail": get_bus_stop_detail("南千歳駅", b["line"]),
                            "bus_dep": b["dep_time"], "bus_line": b["line"],
                            "univ_arr": arr_time, "univ_arr_m": t2m(arr_time),
                            "pref_sapporo": 1, "pref_mchitose": 1
                        })
                        break
                break

    # 新札幌駅乗換
    for tr in JR_NAEBO_SHINSAPPORO:
        n_dep_m = t2m(tr["dep"])
        home_dep_m = n_dep_m - walk_time
        shin_arr_m = t2m(tr["arr"])
        for rap in JR_RAPID_UP:
            rap_dep_m = t2m(rap["dep_shin"])
            if rap_dep_m >= shin_arr_m + 3:
                chi_arr_m = t2m(rap["arr_chi"])
                for _, b in bus_df[bus_df["dep_station"] == "千歳駅"].iterrows():
                    if t2m(b["dep_time"]) >= chi_arr_m + 3:
                        arr_time = b["arr_kenkyu"] if dest_building == "研究棟" else b["arr_honbu"]
                        routes.append({
                            "home_dep_m": home_dep_m, "home_dep": m2t(home_dep_m),
                            "naebo_dep": tr["dep"], "transfer_sta": "新札幌駅", "rap_dep": rap["dep_shin"],
                            "bus_sta": "千歳駅", "bus_stop_detail": get_bus_stop_detail("千歳駅", b["line"]),
                            "bus_dep": b["dep_time"], "bus_line": b["line"],
                            "univ_arr": arr_time, "univ_arr_m": t2m(arr_time),
                            "pref_sapporo": 0, "pref_mchitose": 0
                        })
                        break
                mchi_arr_m = t2m(rap["arr_mchi"])
                for _, b in bus_df[bus_df["dep_station"] == "南千歳駅"].iterrows():
                    if t2m(b["dep_time"]) >= mchi_arr_m + 3:
                        arr_time = b["arr_kenkyu"] if dest_building == "研究棟" else b["arr_honbu"]
                        routes.append({
                            "home_dep_m": home_dep_m, "home_dep": m2t(home_dep_m),
                            "naebo_dep": tr["dep"], "transfer_sta": "新札幌駅", "rap_dep": rap["dep_shin"],
                            "bus_sta": "南千歳駅", "bus_stop_detail": get_bus_stop_detail("南千歳駅", b["line"]),
                            "bus_dep": b["dep_time"], "bus_line": b["line"],
                            "univ_arr": arr_time, "univ_arr_m": t2m(arr_time),
                            "pref_sapporo": 0, "pref_mchitose": 1
                        })
                        break
                break
                
    return pd.DataFrame(routes)

# ==========================================
# 6. 復路（下校）計算（千歳駅乗車優先）
# ==========================================
def calculate_back_routes(bus_data, dep_building, walk_time):
    bus_df = pd.DataFrame(bus_data)
    routes = []
    
    for _, b in bus_df.iterrows():
        b_dep = b['dep_kenkyu'] if dep_building == '研究棟' else b['dep_honbu']
        if not b_dep or b_dep == 'None': continue
        b_dep_m = t2m(b_dep)
        b_arr_m = t2m(b['bus_arr_time'])
        bus_sta = b['bus_arr_sta']
        pref_chitose = 1 if bus_sta == '千歳駅' else 0
        
        # 千歳駅直通普通
        if bus_sta == '千歳駅':
            for loc in JR_CHITOSE_LOCALS:
                loc_dep_m = t2m(loc['dep_chi'])
                if loc_dep_m >= b_arr_m + 3:
                    naebo_arr_m = t2m(loc['arr_naebo'])
                    home_arr_m = naebo_arr_m + walk_time
                    routes.append({
                        'univ_dep': b_dep, 'univ_dep_m': b_dep_m,
                        'bus_line': b['line'], 'bus_arr_sta': bus_sta,
                        'bus_arr_time': b['bus_arr_time'], 'drop_detail': b['drop_detail'],
                        'rap_dep': loc['dep_chi'], 'transfer_sta': '直通（千歳より普通）', 'rap_arr': loc['arr_naebo'],
                        'local_dep': loc['dep_chi'], 'naebo_arr': loc['arr_naebo'],
                        'home_arr': m2t(home_arr_m), 'home_arr_m': home_arr_m,
                        'avoid_sapporo': 1, 'pref_chitose': 1
                    })
                    break

        # 快速エアポート接続
        for ap in JR_RAPID_DOWN:
            ap_dep_str = ap['dep_chi'] if bus_sta == '千歳駅' else ap['dep_mchi']
            if not ap_dep_str: continue
            ap_dep_m = t2m(ap_dep_str)
            
            if ap_dep_m >= b_arr_m + 3:
                # 北広島乗換
                kita_arr_m = t2m(ap['arr_kita'])
                for loc in JR_CHITOSE_LOCALS:
                    loc_kita_m = t2m(loc['dep_kita'])
                    if loc_kita_m >= kita_arr_m + 2:
                        naebo_arr_m = t2m(loc['arr_naebo'])
                        home_arr_m = naebo_arr_m + walk_time
                        routes.append({
                            'univ_dep': b_dep, 'univ_dep_m': b_dep_m,
                            'bus_line': b['line'], 'bus_arr_sta': bus_sta,
                            'bus_arr_time': b['bus_arr_time'], 'drop_detail': b['drop_detail'],
                            'rap_dep': ap_dep_str, 'transfer_sta': '北広島駅', 'rap_arr': ap['arr_kita'],
                            'local_dep': loc['dep_kita'], 'naebo_arr': loc['arr_naebo'],
                            'home_arr': m2t(home_arr_m), 'home_arr_m': home_arr_m,
                            'avoid_sapporo': 1, 'pref_chitose': pref_chitose
                        })
                        break

                # 新札幌乗換
                shin_arr_m = t2m(ap['arr_shin'])
                for loc in JR_CHITOSE_LOCALS:
                    loc_shin_m = t2m(loc['dep_shin'])
                    if loc_shin_m >= shin_arr_m + 3:
                        naebo_arr_m = t2m(loc['arr_naebo'])
                        home_arr_m = naebo_arr_m + walk_time
                        routes.append({
                            'univ_dep': b_dep, 'univ_dep_m': b_dep_m,
                            'bus_line': b['line'], 'bus_arr_sta': bus_sta,
                            'bus_arr_time': b['bus_arr_time'], 'drop_detail': b['drop_detail'],
                            'rap_dep': ap_dep_str, 'transfer_sta': '新札幌駅', 'rap_arr': ap['arr_shin'],
                            'local_dep': loc['dep_shin'], 'naebo_arr': loc['arr_naebo'],
                            'home_arr': m2t(home_arr_m), 'home_arr_m': home_arr_m,
                            'avoid_sapporo': 1, 'pref_chitose': pref_chitose
                        })
                        break

                # 白石乗換
                shiro_arr_m = t2m(ap['arr_shiro'])
                for loc in JR_CHITOSE_LOCALS:
                    loc_shiro_m = t2m(loc['dep_shiro'])
                    if loc_shiro_m >= shiro_arr_m + 3:
                        naebo_arr_m = t2m(loc['arr_naebo'])
                        home_arr_m = naebo_arr_m + walk_time
                        routes.append({
                            'univ_dep': b_dep, 'univ_dep_m': b_dep_m,
                            'bus_line': b['line'], 'bus_arr_sta': bus_sta,
                            'bus_arr_time': b['bus_arr_time'], 'drop_detail': b['drop_detail'],
                            'rap_dep': ap_dep_str, 'transfer_sta': '白石駅', 'rap_arr': ap['arr_shiro'],
                            'local_dep': loc['dep_shiro'], 'naebo_arr': loc['arr_naebo'],
                            'home_arr': m2t(home_arr_m), 'home_arr_m': home_arr_m,
                            'avoid_sapporo': 1, 'pref_chitose': pref_chitose
                        })
                        break

                # 札幌乗換
                sap_arr_m = t2m(ap['arr_sap'])
                for s_dep in JR_SAPPORO_TO_NAEBO:
                    s_dep_m = t2m(s_dep)
                    if s_dep_m >= sap_arr_m + 4:
                        naebo_arr_m = s_dep_m + 3
                        home_arr_m = naebo_arr_m + walk_time
                        routes.append({
                            'univ_dep': b_dep, 'univ_dep_m': b_dep_m,
                            'bus_line': b['line'], 'bus_arr_sta': bus_sta,
                            'bus_arr_time': b['bus_arr_time'], 'drop_detail': b['drop_detail'],
                            'rap_dep': ap_dep_str, 'transfer_sta': '札幌駅', 'rap_arr': ap['arr_sap'],
                            'local_dep': s_dep, 'naebo_arr': m2t(naebo_arr_m),
                            'home_arr': m2t(home_arr_m), 'home_arr_m': home_arr_m,
                            'avoid_sapporo': 0, 'pref_chitose': pref_chitose
                        })
                        break
                break
                
    return pd.DataFrame(routes)

# ==========================================
# 7. サイドバー設定（行き帰り・徒歩時間）
# ==========================================
st.sidebar.markdown("### 通学設定")
direction = st.sidebar.radio(
    "移動方向",
    ["登校（自宅 ➜ 大学）", "下校（大学 ➜ 自宅）"],
    index=0
)
walk_time = st.sidebar.slider("苗穂駅〜自宅 徒歩時間（分）", min_value=10, max_value=25, value=16)
is_holiday = st.sidebar.checkbox("土日祝ダイヤを使用", value=False)

# ==========================================
# 8. 日本時間の現在時刻とセッション管理
# ==========================================
jst = timezone(timedelta(hours=9))
now_jst = datetime.now(jst)
now_h_str = f"{now_jst.hour:02d}"
now_m_val = (now_jst.minute // 5) * 5
now_m_str = f"{now_m_val:02d}"

# 方向の切り替えを検知してデフォルト値を自動初期化
if "current_direction" not in st.session_state:
    st.session_state.current_direction = direction

if st.session_state.current_direction != direction:
    st.session_state.current_direction = direction
    if "登校" in direction:
        st.session_state.sel_h = "08"
        st.session_state.sel_m = "50"
    else:
        st.session_state.sel_h = now_h_str
        st.session_state.sel_m = now_m_str

if "sel_h" not in st.session_state:
    st.session_state.sel_h = "08" if "登校" in direction else now_h_str
if "sel_m" not in st.session_state:
    st.session_state.sel_m = "50" if "登校" in direction else now_m_str

def set_quick_time(h, m):
    st.session_state.sel_h = h
    st.session_state.sel_m = m

# ==========================================
# 9. 最上部コンテナ（緑色カードを即時表示）
# ==========================================
hero_container = st.container()

# ==========================================
# 10. メイン設定エリア
# ==========================================
st.markdown('<div class="filter-box">', unsafe_allow_html=True)

# 検索モード（登校側は逆算モード[index=1]をデフォルト、下校側は最速モード[index=0]をデフォルト）
default_search_idx = 1 if "登校" in direction else 0
search_mode = st.radio(
    "検索モード",
    ["現在時刻から最速（今すぐ出発）", "希望到着時刻から逆算（ギリギリ出発）"],
    index=default_search_idx,
    horizontal=True,
    key=f"search_mode_{direction}"
)

# 登校時：時限クイック選択ボタン（ワンタップ設定）
if "登校" in direction:
    st.caption("▼ 時限クイック選択（ワンタップで希望到着時刻を設定）")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.button("1限 (08:50着)", on_click=set_quick_time, args=("08", "50"), use_container_width=True)
    with q2:
        st.button("2限 (10:30着)", on_click=set_quick_time, args=("10", "30"), use_container_width=True)
    with q3:
        st.button("3限 (12:50着)", on_click=set_quick_time, args=("12", "50"), use_container_width=True)

    q4, q5, q6 = st.columns(3)
    with q4:
        st.button("4限 (14:30着)", on_click=set_quick_time, args=("14", "30"), use_container_width=True)
    with q5:
        st.button("5限 (16:10着)", on_click=set_quick_time, args=("16", "10"), use_container_width=True)
    with q6:
        st.button("放課後 (18:00着)", on_click=set_quick_time, args=("18", "00"), use_container_width=True)

# 5分刻みダイヤル式ピッカー
hours_list = [f"{h:02d}" for h in range(0, 24)]
minutes_list = [f"{m:02d}" for m in range(0, 60, 5)]

time_label = "希望到着時刻（5分刻み）" if "希望到着時刻" in search_mode else "出発基準時刻（5分刻み）"
st.caption(f"▼ {time_label}")

tc1, tc2 = st.columns(2)
with tc1:
    sel_h = st.selectbox("時", hours_list, key="sel_h")
with tc2:
    sel_m = st.selectbox("分", minutes_list, key="sel_m")
base_time_str = f"{sel_h}:{sel_m}"

# 大学の棟選択
b_label = "大学の棟（目的地）" if "登校" in direction else "大学の棟（出発地）"
target_building = st.radio(b_label, ["研究棟", "本部棟"], horizontal=True)

# 経由地フィルター
f1, f2 = st.columns([1.5, 1.2])
with f1:
    if "登校" in direction:
        filter_jr = st.radio("JR乗換駅", ["指定なし（最速）", "札幌駅経由", "新札幌駅経由"], horizontal=True)
    else:
        filter_jr = st.radio(
            "JR乗換駅（下校）",
            ["指定なし（最速）", "札幌を経由しない（手前乗換）", "北広島駅経由", "新札幌駅経由", "白石駅経由", "千歳直通（乗換なし）", "札幌駅経由"],
            horizontal=True
        )
with f2:
    b_filter_label = "バス乗車駅" if "登校" in direction else "バス降車駅（JR乗車駅）"
    filter_bus = st.radio(b_filter_label, ["指定なし（最速）", "千歳駅経由", "南千歳駅経由"], horizontal=True)

st.markdown('</div>', unsafe_allow_html=True)

base_m = t2m(base_time_str)

# ==========================================
# 11. ルート計算と画面描画
# ==========================================
if "登校" in direction:
    bus_data = BUS_GO_HOLIDAY if is_holiday else BUS_GO_HEIJITSU
    df_all = calculate_go_routes(bus_data, target_building, walk_time)
    
    filtered_df = df_all.copy()
    if filter_jr == "札幌駅経由": filtered_df = filtered_df[filtered_df["transfer_sta"] == "札幌駅"]
    elif filter_jr == "新札幌駅経由": filtered_df = filtered_df[filtered_df["transfer_sta"] == "新札幌駅"]
    
    if filter_bus == "千歳駅経由": filtered_df = filtered_df[filtered_df["bus_sta"] == "千歳駅"]
    elif filter_bus == "南千歳駅経由": filtered_df = filtered_df[filtered_df["bus_sta"] == "南千歳駅"]

    if not filtered_df.empty:
        routes_df = filtered_df.sort_values(
            by=["univ_arr_m", "home_dep_m", "pref_sapporo", "pref_mchitose"],
            ascending=[True, False, False, False]
        ).drop_duplicates(subset=["univ_arr_m"])
    else:
        routes_df = pd.DataFrame()

    best = None
    if not filtered_df.empty:
        if "現在時刻" in search_mode:
            cands = filtered_df[filtered_df["home_dep_m"] >= base_m]
            if not cands.empty:
                best = cands.sort_values(
                    by=["univ_arr_m", "home_dep_m", "pref_sapporo", "pref_mchitose"],
                    ascending=[True, False, False, False]
                ).iloc[0]
                status_header = f"{base_time_str} 以降の出発で一番早く着く便"
        else:
            cands = filtered_df[filtered_df["univ_arr_m"] <= base_m]
            if not cands.empty:
                best = cands.sort_values(
                    by=["home_dep_m", "pref_sapporo", "pref_mchitose", "univ_arr_m"],
                    ascending=[False, False, False, True]
                ).iloc[0]
                status_header = f"{base_time_str} までに着く一番ギリギリの出発便"

    # 画面最上部に緑色カードを表示
    with hero_container:
        if best is not None:
            total_min = best['univ_arr_m'] - best['home_dep_m']
            hero_html = f"""<div class="hero-card">
<div class="hero-badge-header">{status_header}</div>
<div style="display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap;">
<div>
<span style="font-size:13px; opacity:0.85;">自宅を出る時間</span>
<div class="hero-time-val">{best['home_dep']} <span style="font-size:20px; font-weight:normal;">発</span></div>
</div>
<div style="text-align:right;">
<span style="font-size:13px; opacity:0.85;">大学{target_building} 到着</span>
<div style="font-size:30px; font-weight:800; color:#a7f3d0;">{best['univ_arr']} <span style="font-size:16px; font-weight:normal;">着</span></div>
<div style="font-size:12px; opacity:0.85;">所要時間: 約{total_min}分</div>
</div>
</div>
<div class="transit-step-container">
<div class="step-card"><div class="step-type">徒歩</div><div class="step-main">{walk_time}分</div><div class="step-sub">自宅 ➜ 苗穂駅</div></div>
<div class="step-arrow">➜</div>
<div class="step-card"><div class="step-type">JR普通</div><div class="step-main">{best['naebo_dep']} 苗穂発</div><div class="step-sub">{best['transfer_sta']}乗換</div></div>
<div class="step-arrow">➜</div>
<div class="step-card"><div class="step-type">快速エアポート</div><div class="step-main">{best['rap_dep']} {best['transfer_sta']}発</div><div class="step-sub">{best['bus_sta']}下車</div></div>
<div class="step-arrow">➜</div>
<div class="step-card" style="background:rgba(16,185,129,0.25); border-color:#34d399;">
<div class="step-type" style="color:#6ee7b7;">バス（{best['bus_line']}）</div><div class="step-main">{best['bus_dep']} 発</div><div class="step-sub" style="color:#a7f3d0; font-weight:600;">{best['bus_stop_detail']}</div></div>
</div>
</div>"""
            st.markdown(hero_html, unsafe_allow_html=True)
        else:
            st.error("指定された条件・時刻に合致する便がありません。時刻や経由地を調整してください。")

    # 全便一覧表
    if not routes_df.empty:
        st.subheader("全便一覧（登校）")
        view_df = routes_df[["home_dep", "naebo_dep", "transfer_sta", "rap_dep", "bus_stop_detail", "bus_dep", "bus_line", "univ_arr"]].copy()
        view_df.columns = ["自宅発", "苗穂発", "JR乗換駅", "快速発", "バスのりば", "バス発", "系統", "大学着"]
        st.dataframe(view_df, hide_index=True, use_container_width=True)

else:
    bus_data = BUS_BACK_HOLIDAY if is_holiday else BUS_BACK_HEIJITSU
    df_all = calculate_back_routes(bus_data, target_building, walk_time)
    
    filtered_df = df_all.copy()
    if filter_jr == "札幌を経由しない（手前乗換）":
        filtered_df = filtered_df[filtered_df["avoid_sapporo"] == 1]
    elif filter_jr == "北広島駅経由":
        filtered_df = filtered_df[filtered_df["transfer_sta"] == "北広島駅"]
    elif filter_jr == "新札幌駅経由":
        filtered_df = filtered_df[filtered_df["transfer_sta"] == "新札幌駅"]
    elif filter_jr == "白石駅経由":
        filtered_df = filtered_df[filtered_df["transfer_sta"] == "白石駅"]
    elif filter_jr == "千歳直通（乗換なし）":
        filtered_df = filtered_df[filtered_df["transfer_sta"] == "直通（千歳より普通）"]
    elif filter_jr == "札幌駅経由":
        filtered_df = filtered_df[filtered_df["transfer_sta"] == "札幌駅"]
    
    if filter_bus == "千歳駅経由": filtered_df = filtered_df[filtered_df["bus_arr_sta"] == "千歳駅"]
    elif filter_bus == "南千歳駅経由": filtered_df = filtered_df[filtered_df["bus_arr_sta"] == "南千歳駅"]

    if not filtered_df.empty:
        routes_df = filtered_df.sort_values(
            by=["home_arr_m", "univ_dep_m", "pref_chitose", "avoid_sapporo"],
            ascending=[True, False, False, False]
        ).drop_duplicates(subset=["home_arr_m"])
    else:
        routes_df = pd.DataFrame()

    best = None
    if not filtered_df.empty:
        if "現在時刻" in search_mode:
            cands = filtered_df[filtered_df["univ_dep_m"] >= base_m]
            if not cands.empty:
                best = cands.sort_values(
                    by=["home_arr_m", "univ_dep_m", "pref_chitose", "avoid_sapporo"],
                    ascending=[True, False, False, False]
                ).iloc[0]
                status_header = f"{base_time_str} 以降の出発で一番早く帰れる便"
        else:
            cands = filtered_df[filtered_df["home_arr_m"] <= base_m]
            if not cands.empty:
                best = cands.sort_values(
                    by=["univ_dep_m", "pref_chitose", "avoid_sapporo", "home_arr_m"],
                    ascending=[False, False, False, True]
                ).iloc[0]
                status_header = f"{base_time_str} までに帰宅できる一番ギリギリの出発便"

    # 画面最上部に緑色カードを表示
    with hero_container:
        if best is not None:
            total_min = best['home_arr_m'] - best['univ_dep_m']
            
            if best['transfer_sta'] == '直通（千歳より普通）':
                jr_card_html = f"""<div class="step-card"><div class="step-type">JR普通（直通）</div><div class="step-main">{best['rap_dep']} 千歳発</div><div class="step-sub">苗穂まで乗換なし</div></div>"""
            else:
                jr_card_html = f"""<div class="step-card"><div class="step-type">快速エアポート</div><div class="step-main">{best['rap_dep']} {best['bus_arr_sta']}発</div><div class="step-sub">{best['transfer_sta']}乗換</div></div>
<div class="step-arrow">➜</div>
<div class="step-card"><div class="step-type">JR普通</div><div class="step-main">{best['local_dep']} {best['transfer_sta']}発</div><div class="step-sub">{best['naebo_arr']} 苗穂着</div></div>"""

            hero_html = f"""<div class="hero-card">
<div class="hero-badge-header">{status_header}</div>
<div style="display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap;">
<div>
<span style="font-size:13px; opacity:0.85;">大学{target_building}を出る時間</span>
<div class="hero-time-val">{best['univ_dep']} <span style="font-size:20px; font-weight:normal;">発</span></div>
</div>
<div style="text-align:right;">
<span style="font-size:13px; opacity:0.85;">自宅到着</span>
<div style="font-size:30px; font-weight:800; color:#a7f3d0;">{best['home_arr']} <span style="font-size:16px; font-weight:normal;">着</span></div>
<div style="font-size:12px; opacity:0.85;">所要時間: 約{total_min}分</div>
</div>
</div>
<div class="transit-step-container">
<div class="step-card" style="background:rgba(16,185,129,0.25); border-color:#34d399;">
<div class="step-type" style="color:#6ee7b7;">バス（{best['bus_line']}）</div><div class="step-main">{best['univ_dep']} 発</div><div class="step-sub" style="color:#a7f3d0; font-weight:600;">➜ {best['drop_detail']}</div></div>
<div class="step-arrow">➜</div>
{jr_card_html}
<div class="step-arrow">➜</div>
<div class="step-card"><div class="step-type">徒歩</div><div class="step-main">{walk_time}分</div><div class="step-sub">苗穂駅 ➜ 自宅</div></div>
</div>
</div>"""
            st.markdown(hero_html, unsafe_allow_html=True)
        else:
            st.error("指定された条件・時刻に合致する便がありません。時刻や経由地を調整してください。")

    # 全便一覧表
    if not routes_df.empty:
        st.subheader("全便一覧（下校）")
        view_df = routes_df[[
            "univ_dep", "bus_line", "drop_detail", "rap_dep", 
            "transfer_sta", "local_dep", "naebo_arr", "home_arr"
        ]].copy()
        view_df.columns = [
            "大学発", "系統", "バス降車場所", "快速/普通発", 
            "乗換駅", "乗換後発", "苗穂着", "自宅着"
        ]
        st.dataframe(view_df, hide_index=True, use_container_width=True)
