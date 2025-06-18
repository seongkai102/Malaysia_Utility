import streamlit as st
import yfinance as yf
from streamlit_option_menu import option_menu
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd

# 숫자 확인함수
def check_float(n):
    try:
        float(n)
        return True
    except:
        return False
        
# 토크나이저
def tokenizer(s):
    tokens = []
    n = ""
    for i in range(len(s)):
        t = s[i]

        # 숫자, 소수점, 음수 부호
        if t.isdigit() or t == '.' or (t == '-' and (i == 0 or s[i - 1] in '+-*/(^')):
            n += t
        else:
            if n:
                tokens.append(n)
                n = ""
            tokens.append(t)

    if n:
        tokens.append(n)


    return tokens

#shunting yard알고리즘
def shunting_yard(tokens):
    # 연산자의 우선순위
    U = {'+':1, '-':1, '*':2, '/':2, '^':3}
    R = {'^'}
    result = []
    stack = []
    for token in tokens:
        #토큰이 숫자인경우
        if check_float(token):
            result.append(token)
        
        # 연산자인경우
        elif token in U:
            while stack and (stack[-1] in U ) and (U[stack[-1]] > U[token] or (U[stack[-1]] == U[token]) and token not in R):
                result.append(stack.pop())
            stack.append(token)

        # 괄호일경우-(
        elif token=='(':
            stack.append(token)

        # 괄호일경우-)
        elif token==')':
            while stack and stack[-1]!='(':
                result.append(stack.pop())
            stack.pop()

    # 남은 스택 결과에 추가
    while stack:
        result.append(stack.pop())

    return result

#후위계산법
def calc(spt):
    if len(spt)==1:
        return float(spt[0])
    
    stack = []
    for token in spt:
        if check_float(token):
            stack.append(token)
        else:
            try:
                v2 = float(stack.pop())
                v1 = float(stack.pop())

                # 연산
                if token=='+':
                    r = v1+v2
                elif token=='-':
                    r = v1-v2
                elif token=='*':
                    r = v1*v2
                elif token=='/':
                    r = v1/v2
                elif token=='^':
                    r = v1**v2
                
                if abs(r) > 1_000_000_000_000:
                    return "시스템 과부하로 인해 값은 최대로 1조 미만까지 입니다."

                stack.append(r)
            except IndexError:
                return "계산 오류: 수식을 재점검 해주세요."
            except ZeroDivisionError:
                return "계산 오류: 0으로 나눌수 없습니다."
            except Exception:
                return "알수없는 오류발생."

    # 결과 출력
    if stack:
        return stack[0]
    else:
        return f'입력된값이 없습니다. 현재스택: {stack}'

# 수식계산
def total_calc(sentence):
    # 토큰 분류
    spt = tokenizer(sentence)
    
    # 우선순위 만들기
    trans_spt = shunting_yard(spt)

    # 계산하기
    r = calc(trans_spt)

    # 결과 출력
    return r

# won to rm
def krw_to_myr(krw_amount, rate_float):
    return round(krw_amount / rate_float, 2)  # 소수점 2자리

# 말레이시아 환율 가져오기
def hw_time():
    url = "https://www.x-rates.com/calculator/?from=MYR&to=KRW&amount=1"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 환율 정보
    rate_elem = soup.select_one("span.ccOutputRslt")
    # 기준 시간 정보
    time_elem = soup.select_one("span.calOutputTS")

    rate = rate_elem.text.strip() if rate_elem else None
    timestamp = time_elem.text.strip() if time_elem else None

    return rate, timestamp

#### UI파트

# 사이드바
with st.sidebar:
    st.markdown(
        "<h1 style='color:#f4e9d8; font-size:28px;'>✨ Malaysia Utility</h1>",
        unsafe_allow_html=True
    )
    choose = option_menu(
        "",
        ["실시간 환율 계산", "링깃 구매 시기", "스쿨버스 시간표"],
        menu_icon="sun",  # 부드러운 느낌 아이콘
        default_index=0,
        styles={
            "container": {
                "padding": "4px",
                "background-color": "#FFE4C4",  # 따뜻한 베이지 배경
            },
            "icon": {
                "color": "#4e342e",  # 진한 브라운 (잘 보이고 부드러움)
                "font-size": "24px"
            },
            "nav-link": {
                "font-size": "16px",
                "color": "#4e342e",  # 글씨도 브라운
                "text-align": "left",
                "margin": "5px 0",
                "border-radius": "5px",
                "padding": "10px 20px",
                "--hover-color": "#fbe9e7"  # 아주 연한 코랄 계열
            },
            "nav-link-selected": {
                "background-color": "#ff7043",  # 코랄 오렌지
                "color": "white",
                "font-weight": "bold"
            }
        }
    )

# 환율 계산 코드
if choose=='실시간 환율 계산':
    
    # 출력부분
    st.title("실시간 환율 계산")
    st.subheader("🧮 더치페이 및 수식계산을 활용하기 위해 개발")
    st.markdown("#### ")

    try:
        hw, time = hw_time()

        rate = float(hw.split()[0])

        st.markdown("## 💱현재 실시간 환율")

        if rate:
            st.markdown(f"### 💵실시간 MYR(링깃) = {rate}KRW(원)")
            st.success(f"🕒기준 시각: {time}")


        else:
            st.error("❌ 환율 정보를 가져오지 못했습니다.")

        st.markdown("#### ")

        st.subheader("➕수식 계산기➖")
        changer = st.selectbox(
            '💱환율 변환기(기준)',
            ('MYR(링깃) → KRW(원)', 'KRW(원) → MYR(링깃)', '일반 수식계산기'), 
            index=2
        )

        title = st.text_input(
            label=f'변환할 기준을 선택후 입력해주세요. (현재: {changer})', 
            placeholder='해당 칸에 수식 및 숫자 입력. (수식예시: (12*34.1)^2+56.9-78/90)'
        )

        result = total_calc(title)
        Tint = check_float(result)
        if changer=="일반 수식계산기" and not Tint:
            # st.subheader(f"{result}")
            pass
        
        # 일반 계산 결과
        elif changer=="일반 수식계산기" and Tint:
            st.markdown(f"## 일반 계산 결과: {result}")

        # 원 to 링깃
        elif changer=="KRW(원) → MYR(링깃)" and Tint:
            money = krw_to_myr(float(result), rate)
            st.markdown(f"## 💵:green[{result:.2f}]KRW -> :green[{money:.2f}]MYR")
        
        #링깃 to 원
        elif changer=="MYR(링깃) → KRW(원)" and Tint:
            money = round(float(result)*rate, 2)
            st.markdown(f"## 💵:green[{result:.2f}]MYR -> :green[{money:.2f}]KRW")

        #에러 처리코드
        else:
            st.error(result)

        st.title("")
        st.markdown("### Copyright ⓒ seongkai102")
        

    except:
        st.error("❌ 크롤링 실패")
    
elif choose=="링깃 구매 시기":
    st.title("💱환전 타이밍 추천")
    myr_usd = yf.download("MYRKRW=X", period="3mo", interval="1d", progress=False)

    df = myr_usd.iloc[:, :1].reset_index()

    if df.empty:
        st.error("환율 데이터를 불러오지 못했어요.")
    else:
        mean_3m = float(df['Close'].mean())
        date = df["Date"].iloc[-1]
        last_v = float(df['Close'].iloc[-1])

        st.subheader(f"💹 지난 3달간 평균환율: 1MYR - {mean_3m:.2f}KRW")
        st.subheader(f"📌 최신환율 ({str(date)[:10]}): 1MYR -  {last_v:.2f}KRW")
        st.subheader('')

        if last_v < mean_3m * 0.97:
            st.markdown("## ✅ 현재 환율이 평균보다 :blue[3% 이상] 낮습니다.", unsafe_allow_html=True)
            st.markdown("### 😊적극적으로 환전하기 좋은 시점입니다.")
        elif last_v < mean_3m * 0.99:
            st.markdown("## 🟢 현재 환율이 평균보다 :green[1~3%] 낮습니다.", unsafe_allow_html=True)
            st.markdown("### 🤔환전을 고려해볼 만한 시점입니다.")
        elif last_v > mean_3m * 1.03:
            st.markdown("## 🔴 현재 환율이 평균보다 :red[3%] 이상 높습니다.", unsafe_allow_html=True)
            st.markdown("### 🤯지금 환전은 피하는 것이 좋습니다.")
        elif last_v > mean_3m * 1.01:
            st.markdown("## 🟠 현재 환율이 평균보다 <span style='color:orange'>1~3%</span> 높습니다.", unsafe_allow_html=True)
            st.markdown("### 🙂‍↔️가격이 다소 높으니 신중히 판단하세요.")
        else:
            st.markdown("## 🟡 현재 환율이 <span style='color:gold'>평균</span>  수준입니다.", unsafe_allow_html=True)
            st.markdown("### 🕐급하지 않다면 조금 더 지켜보는 것도 좋습니다.")
        
        st.subheader('')
        st.markdown("### ※참고※")
        st.markdown("#### ✅ -> 적극추천🟢 -> 추천 🟡 -> 평균 🟠 -> 비추 🔴 -> 완전비추")
        st.subheader('')

        st.title("📈최근 3개월간 환율 추이")
        
        # 그래프 생성
        df = myr_usd
        fig, ax = plt.subplots()
        df["Close"].plot(ax=ax, title="Total 3month")
        plt.axhline(mean_3m, color='orange', linestyle='--', label='Mean')
        plt.scatter(df.index[-1], last_v, color='red', zorder=10, label='Now value')
        plt.ylabel("MYR-KRW")
        plt.legend(loc="best")
        st.pyplot(fig)

        st.title("")
        st.markdown("### Copyright ⓒ seongkai102")

elif choose=="스쿨버스 시간표":
    st.title("🚍스쿨버스 시간표")

    df = pd.DataFrame({"CP출발시간":['7:25', '7:55', '8:25', '8:55', '9:25', '9:55', "11:30",  '12:10', '12:50', '13:20', '13:50', '14:20', '14:50', '16:30', '17:10', '17:50', '18:30'],
              "T02도착시간":['7:40', '8:10', '8:40', '9:10', '9:40', '10:10', '11:50', '12:30', '13:05','13:35', '14:05', '14:35', '15:05', '16:50', '17:30', '18:10', '18:50']})
    
    st.dataframe(df, use_container_width=False)

    st.subheader(" ")
    st.markdown("## ❗중요 안내(READ_ME)❗")
    st.markdown("금요일, 토요일, 공휴일 및 학기 휴강 기간에는 버스 서비스가 제공되지 않습니다.")
    st.markdown("교통 상황으로 인해 도착 시간이 정확하지 않을 수 있습니다.")
    st.markdown("2023년 8월 10일부터 2026년 1월 31일까지 적용되는 일정입니다.")

    st.subheader(" ")
    st.markdown("## 📍버스 탑승 위치")

    df = pd.DataFrame({
        'lat': [1.5649594082871887],
        'lon': [103.65378791802235]
    })
    st.map(df, zoom=15)

    st.title("")
    st.markdown("### Copyright ⓒ seongkai102")