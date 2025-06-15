import os
import tempfile
import unittest

# Здесь мы импортируем именно тот модуль, где написано `app = Flask(__name__)`.
import LW3 as app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Переводим Flask-приложение в тестовый режим
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

        # Создаём временный файл, куда будут писаться ответы вместо реального
        self.tmp_fd, self.tmp_path = tempfile.mkstemp(prefix="test_responses_", suffix=".txt")
        os.close(self.tmp_fd)

        # Переназначаем в модуле app переменную DATA_FILE
        app.DATA_FILE = self.tmp_path

    def tearDown(self):
        # Удаляем временный файл после теста
        try:
            os.remove(self.tmp_path)
        except OSError:
            pass

    def test_get_index(self):
        """
        GET "/" должен вернуть форму (код 200) и содержать нужные поля.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)
        # Проверяем, что в HTML-ответе есть хоть что-то из нашей формы
        self.assertIn('<form', html)
        self.assertIn('name="name"', html)
        self.assertIn('name="age"', html)
        self.assertIn('name="email"', html)
        self.assertIn('name="comment"', html)

    def test_post_index_and_file_write(self):
        """
        POST "/" с валидными данными должен:
        1) Сделать редирект на "/thanks" (код 302).
        2) Записать строку с этими данными в файл DATA_FILE.
        """
        test_data = {
            'name': 'Тестовый Студент',
            'age': '25',
            'email': 'test@example.com',
            'comment': 'Это тестовый комментарий.'
        }
        response = self.client.post('/', data=test_data, follow_redirects=False)

        # 1) проверяем редирект
        self.assertEqual(response.status_code, 302)
        location = response.headers.get('Location', '')
        self.assertTrue(location.endswith('/thanks'))

        # 2) читаем временный файл и убеждаемся, что там есть наши данные
        with open(self.tmp_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Тестовый Студент', content)
        self.assertIn('25', content)
        self.assertIn('test@example.com', content)
        self.assertIn('Это тестовый комментарий.', content)
        # Проверим формат «| name | age | email | comment»
        self.assertIn(' | Тестовый Студент | 25 | test@example.com |', content)

    def test_get_thanks(self):
        """
        GET "/thanks" должен вернуть страницу благодарности (код 200) и
        содержать слово "Спасибо".
        """
        response = self.client.get('/thanks')
        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)
        self.assertIn('Спасибо', html)
        self.assertIn('заполненную анкету', html)

if __name__ == '__main__':
    unittest.main()
