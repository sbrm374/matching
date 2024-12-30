import streamlit as st
import pandas as pd

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

# ページの構成
st.set_page_config(layout="wide")  # 横幅広めのレイアウト

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
