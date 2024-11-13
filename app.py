import streamlit as st
import sqlite3
import requests
import pandas as pd
import matplotlib.pyplot as plt

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

def main():
    st.title('Платформа курсов валют')

    menu = ['Главная', 'Курс валют', 'Вход', 'Регистрация']
    choice = st.sidebar.selectbox('Меню', menu)

    if choice == 'Главная':
        st.subheader('Добро пожаловать на платформу курсов валют!')
    elif choice == 'Курс валют':
        show_currency_charts()
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

def show_currency_charts():
    st.subheader('Графики курсов валют')

    base_currency = st.selectbox('Базовая валюта', ['USD', 'EUR', 'GBP'])
    target_currency = st.selectbox('Целевая валюта', ['EUR', 'USD', 'GBP', 'JPY', 'AUD'])

    if st.button('Показать график'):
        data = get_exchange_rates(base_currency, target_currency)
        if data is not None:
            plot_exchange_rates(data, base_currency, target_currency)
        else:
            st.error('Не удалось получить данные')

def get_exchange_rates(base, target):
    url = f'https://api.exchangerate.host/timeseries?start_date=2023-01-01&end_date=2023-12-31&base={base}&symbols={target}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']
        df = pd.DataFrame(rates).T
        df = df.rename(columns={target: 'Rate'})
        df.index = pd.to_datetime(df.index)
        return df
    else:
        return None

def plot_exchange_rates(data, base, target):
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Rate'], marker='o')
    plt.title(f'Курс {base} к {target}')
    plt.xlabel('Дата')
    plt.ylabel('Курс')
    plt.grid(True)
    st.pyplot(plt)

if __name__ == '__main__':
    # Инициализация состояния сессии
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''

    main()
