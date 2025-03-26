import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Streamlit 기본 설정 (WIDE 모드)
st.set_page_config(layout="wide")

# 데이터베이스 초기화
conn = sqlite3.connect('ya_geun_app.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS ya_geun_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    weekday TEXT,
    payer TEXT,
    amount INTEGER,
    sophia TEXT,
    rosa TEXT,
    arumi TEXT,
    nina TEXT,
    jjun TEXT,
    olaf TEXT,
    esther TEXT,
    angela TEXT,
    rk TEXT,
    note TEXT
)''')
conn.commit()

st.title('미디어1팀 야식 관리앱')

# 팀원 캐릭터 아이콘 매핑
icon_options = ['🦊', '🐻', '🐰', '🐤', '🐼', '🐧', '🐱', '🦄', '🐺', '🦁', '🐯', '🐨', '🐵', '🐸', '🐔', '🐲']
team_icons = {
    '소피아': '🦊', '로사': '🐻', '아루미': '🐰', '니나': '🐤',
    '쭌': '🐼', '올라프': '🐧', '에스더': '🐱', '안젤라': '🦄', 'RK': '🐺'
}

st.sidebar.header('팀원 목록')
for name in team_icons.keys():
    selected_icon = st.sidebar.selectbox(f'{name} 아이콘 선택', icon_options, index=icon_options.index(team_icons[name]))
    team_icons[name] = selected_icon
    st.sidebar.write(f'{selected_icon} {name}')

# 기록하기

# 기록 입력
st.header('기록 입력')
date = st.date_input('날짜 선택', datetime.today())
yo_il = date.strftime('%a')
payer = st.selectbox('결제자 선택', list(team_icons.keys()))
amount = st.number_input('사용 금액', min_value=0)
attendees = {name: st.checkbox(f'{icon} {name}') for name, icon in team_icons.items()}
note = st.text_area('특이사항')

if st.button('기록 추가'):
    total_checked = sum(attendees.values())
    if total_checked > 0 and amount > total_checked * 13000:
        st.warning(f'⚠️ 인당 금액 초과입니다. 총 금액: {amount}원 / 인원 수: {total_checked}명 / 인당 금액: {amount / total_checked:.2f}원 (허용 금액: {total_checked * 13000}원)')
        st.stop()
    total_checked = sum(attendees.values())
    if total_checked > 0 and amount > total_checked * 13000:
        st.warning(f'⚠️ 인당 금액 초과입니다. 총 금액: {amount}원 / 인원 수: {total_checked}명 = {amount / total_checked:.2f}원')
        st.stop()
    new_data = (date.strftime('%Y-%m-%d'), yo_il, payer, amount)
    attendance = [attendees[name] for name in team_icons.keys()]
    query = '''INSERT INTO ya_geun_records (date, weekday, payer, amount, sophia, rosa, arumi, nina, jjun, olaf, esther, angela, rk, note)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cursor.execute(query, new_data + tuple(icon if a else '' for a, icon in zip(attendance, team_icons.values())) + (note,))
    conn.commit()
    st.success('기록이 추가되었습니다')

# 기록 조회 및 수정
st.header('기록 조회 및 수정')
cursor.execute('SELECT * FROM ya_geun_records WHERE amount > 0')
data = cursor.fetchall()
df = pd.DataFrame(data, columns=['ID', '날짜', '요일', '결제자', '사용금액', '소피아', '로사', '아루미', '니나', '쭌', '올라프', '에스더', '안젤라', 'RK', '특이사항'])

# 팀원 아이콘으로 변환
for name, icon in team_icons.items():
    df[name] = df[name].apply(lambda x: icon if x else '')

st.dataframe(df)

# 수정 기능
def update_record(record_id, new_payer, new_amount, new_note):
    cursor.execute('''UPDATE ya_geun_records SET payer=?, amount=?, note=? WHERE id=?''', (new_payer, new_amount, new_note, record_id))
    conn.commit()
    st.success('기록이 수정되었습니다')

record_id = st.number_input('수정할 기록 ID', min_value=1, step=1)
new_payer = st.text_input('수정할 결제자')
new_amount = st.number_input('수정할 사용 금액', min_value=0)
new_note = st.text_area('수정할 특이사항')
if st.button('기록 수정'):
    update_record(record_id, new_payer, new_amount, new_note)

# 월별 합산
st.header('월별 합산')
month = st.selectbox('월 선택', sorted(set([row[1][:7] for row in data])))
monthly_total = sum([row[4] for row in data if row[1].startswith(month)])
st.write(f'{month} 총 식사비: {monthly_total:,}원')

conn.close()
