import streamlit as st
import sqlite3
import ccxt
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Инициализация базы данных
conn = sqlite3.connect('data/users.db', check_same_thread=False)
c = conn.cursor()

def create_users_table():
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')

def add_user(username, password):
    c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    return c.fetchone()

def fetch_binance_data(symbol, start_date):
    exchange = ccxt.binance()
    if exchange.has['fetchOHLCV']:
        since = exchange.parse8601(start_date)
        all_orders = []
        limit = 1000  # Максимально допустимое значение на Binance
        while since < exchange.milliseconds():
            ohlcv = exchange.fetch_ohlcv(symbol=symbol, since=since, timeframe='1d', limit=limit)
            if len(ohlcv) > 0:
                since = ohlcv[-1][0] + 1
                all_orders += ohlcv
            else:
                break
        return all_orders
    else:
        return None

def clean_data(ohlcv_list):
    temp = []
    for i in ohlcv_list:
        timestamp_with_ms = i[0]
        dt = datetime.datetime.fromtimestamp(timestamp_with_ms / 1000)
        i[0] = dt
        temp.append(i)
    return temp

def get_ohlcv_df(symbol, start_date):
    data = fetch_binance_data(symbol, start_date)
    if data is not None:
        cleaned_data = clean_data(data)
        ohlcv_df = pd.DataFrame(cleaned_data, columns=["Дата", "Цена открытия", "Макс. цена", "Мин. цена", "Цена закрытия", "Объем торгов"])
        
        # Рассчитываем SMA и EWMA
        ohlcv_df['SMA'] = ohlcv_df['Цена закрытия'].rolling(window=20).mean()
        ohlcv_df['EWMA'] = ohlcv_df['Цена закрытия'].ewm(span=20, adjust=False).mean()
        
        return ohlcv_df
    else:
        return None

def plot_ohlcv_data(df, symbol):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Дата'], df['Цена закрытия'], label='Цена закрытия', color='blue')
    plt.plot(df['Дата'], df['SMA'], label='SMA (20 дней)', color='orange')
    plt.plot(df['Дата'], df['EWMA'], label='EWMA (20 дней)', color='green')
    plt.title(f'Цена закрытия и скользящие средние для {symbol}')
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

def show_crypto_charts():
    st.subheader('Графики курсов криптовалют с SMA и EWMA')

    symbol = st.selectbox('Выберите криптовалюту', ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'])
    start_date = st.date_input('Дата начала', datetime.date(2020, 11, 1))

    if st.button('Показать график'):
        start_date_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
        df = get_ohlcv_df(symbol, start_date_str)
        if df is not None:
            plot_ohlcv_data(df, symbol)
        else:
            st.error('Не удалось получить данные')

def main():
    st.title('Платформа курсов криптовалют')

    menu = ['Главная', 'Курс криптовалют', 'Вход', 'Регистрация']
    choice = st.sidebar.selectbox('Меню', menu)

    if choice == 'Главная':
        st.subheader('Добро пожаловать на платформу курсов криптовалют!')
    elif choice == 'Курс криптовалют':
        show_crypto_charts()
    elif choice == 'Вход':
        st.subheader('Авторизация')

        username = st.text_input('Имя пользователя')
        password = st.text_input('Пароль', type='password')

        if st.button('Войти'):
            user = login_user(username, password)
            if user:
                st.success(f'Добро пожаловать, {username}')
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
            else:
                st.warning('Неверное имя пользователя или пароль')

    elif choice == 'Регистрация':
        st.subheader('Создать новую учетную запись')

        new_user = st.text_input('Имя пользователя')
        new_password = st.text_input('Пароль', type='password')

        if st.button('Зарегистрироваться'):
            create_users_table()
            add_user(new_user, new_password)
            st.success('Вы успешно зарегистрировались')
            st.info('Теперь вы можете войти')

    # Опция выхода из аккаунта
    if st.sidebar.button('Выйти'):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.success('Вы вышли из системы.')

if __name__ == '__main__':
    # Инициализация состояния сессии
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''

    main()
