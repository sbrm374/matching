import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# サービスアカウント認証情報
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

# Google API認証
def authenticate_google_services():
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        service_account_info = json.load(f)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    return credentials

# Google Sheetsからデータを取得
def get_data_from_sheets(sheet_id, range_name):
    credentials = authenticate_google_services()
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        return pd.DataFrame()
    # ヘッダーを設定してDataFrameに変換
    df = pd.DataFrame(values[1:], columns=values[0])
    # 必要に応じてデータ型を変換
    if '希望単価' in df.columns:
        df['希望単価'] = pd.to_numeric(df['希望単価'], errors='coerce')
    return df

# Google Sheetsの設定
SHEET_ID = "1amJJDVMr3__OmLgWo1Z9w6FXZ9aMaNm0WRlx1_TYXnE"  
RANGE_NAME = "【人材】DB'!A:O"  

# ページの構成
st.set_page_config(layout="wide")  # 横幅広めのレイアウト

# サンプルデータ (人材一覧)
data = {
    "名前": ["OR", "Y.O", "K.T"],
    "スキル": ["C#, AWS, Docker", "PMO, HTML, MySQL", "Python, Django, React"],
    "役割": ["TL", "PMO", "開発者"],
    "希望単価": [75, 90, 85],
    "稼働条件": ["フルリモート", "フルリモート", "オンサイト"],
    "稼働開始日": ["2024-01-20", "2024-01-01", "2024-02-01"],
}
talent_df = pd.DataFrame(data)




# 左側：案件入力フォーム
with st.sidebar:
    st.header("案件入力フォーム")
    
    project_name = st.text_input("案件名")
    required_skills = st.text_area("必須スキル (カンマ区切り)")
    preferred_skills = st.text_area("歓迎スキル (カンマ区切り)")
    location = st.radio("作業場所", ["リモート", "オンサイト"])
    rate_range = st.text_input("単価目安（例: 75万～90万）")
    start_period = st.date_input("開始時期")
    billing_time = st.text_input("精算条件（例: 140h～180h）")
    if st.button("マッチング実行"):
        st.session_state['match_trigger'] = True

# 真ん中：人材一覧表示とマッチング結果
st.title("人材マッチングシステム")
st.subheader("人材一覧")


# Google Sheetsから人材データを取得
talent_df = get_data_from_sheets(SHEET_ID, RANGE_NAME)
if talent_df.empty:
    st.error("Google Sheetsからデータを取得できませんでした。")
else:
    st.subheader("人材一覧")
    st.dataframe(talent_df, use_container_width=True)
    
# 人材情報を真ん中に表示
st.dataframe(talent_df, use_container_width=True)

# マッチングロジック
if 'match_trigger' in st.session_state:
    st.header("マッチング結果")
    
    # フォームの入力データ処理
    required_skill_list = required_skills.split(",")
    preferred_skill_list = preferred_skills.split(",")
    
    # スコア計算
    def calculate_match_score(row):
        score = 0
        # 必須スキル一致
        for skill in required_skill_list:
            if skill.strip() in row["スキル"]:
                score += 20
        # 歓迎スキル一致
        for skill in preferred_skill_list:
            if skill.strip() in row["スキル"]:
                score += 10
        # 単価マッチング
        if rate_range:
            min_rate, max_rate = map(int, rate_range.replace("万", "").split("～"))
            if min_rate <= row["希望単価"] <= max_rate:
                score += 20
        # 稼働条件マッチング
        if row["稼働条件"] == location:
            score += 20
        return score

    talent_df["マッチングスコア"] = talent_df.apply(calculate_match_score, axis=1)
    sorted_df = talent_df.sort_values("マッチングスコア", ascending=False)
    
    # マッチング結果表示
    st.dataframe(sorted_df, use_container_width=True)
