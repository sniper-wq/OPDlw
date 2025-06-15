from flask import Flask, request, redirect, url_for, render_template_string
import os
import datetime

app = Flask(__name__)

# Шаблон HTML-страницы с формой
INDEX_HTML = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Анкета</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }
        h1 {
            color: #333;
        }
        form {
            max-width: 500px;
        }
        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
        }
        input[type="text"],
        input[type="email"],
        textarea {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            box-sizing: border-box;
            font-size: 14px;
        }
        textarea {
            resize: vertical;
            height: 100px;
        }
        button {
            margin-top: 20px;
            padding: 10px 18px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Заполните, пожалуйста, анкету</h1>
    <form method="post">
        <label for="name">Ваше имя:</label>
        <input type="text" id="name" name="name" required>

        <label for="age">Ваш возраст:</label>
        <input type="text" id="age" name="age" required>

        <label for="email">E-mail:</label>
        <input type="email" id="email" name="email" required>

        <label for="comment">Ваш комментарий:</label>
        <textarea id="comment" name="comment"></textarea>

        <button type="submit">Отправить</button>
    </form>
</body>
</html>
"""

THANKS_HTML = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Спасибо!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            text-align: center;
        }
        h1 {
            color: #2a7b2a;
        }
        a {
            display: inline-block;
            margin-top: 20px;
            text-decoration: none;
            color: #0066cc;
        }
    </style>
</head>
<body>
    <h1>Спасибо за заполненную анкету!</h1>
    <p>Ваши ответы были успешно сохранены.</p>
    <a href="{{ url_for('index') }}">Заполнить ещё раз</a>
</body>
</html>
"""

# Путь к файлу, куда мы будем сохранять ответы
DATA_FILE = "responses.txt"

# Главная страница: показывает форму (GET) и обрабатывает отправку (POST)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Получаем данные из формы
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        email = request.form.get("email", "").strip()
        comment = request.form.get("comment", "").strip()

        # Формируем строку, которую запишем в файл
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = f"{timestamp} | {name} | {age} | {email} | {comment}\n"

        # Открываем файл в режиме "append"
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(record)

        # После сохранения редиректим на страницу благодарности
        return redirect(url_for("thanks"))

    # Если GET-запрос, просто показываем HTML-форму
    return render_template_string(INDEX_HTML)

# Страница "Спасибо"
@app.route("/thanks")
def thanks():
    return render_template_string(THANKS_HTML)

# Точка запуска приложения
if __name__ == "__main__":
    # При запуске сайт будет доступен по адресу http://127.0.0.1:5000/
    app.run(debug=True)
