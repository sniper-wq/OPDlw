import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "7549198402:AAFx4qfQ8f6JlQPN_bHxcPLlTIAUWxEEkls"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# «База данных» студентов
students_data = {
    "Иван Иванов": {
        "Математика":       {"attendance": "8/10",  "score": 85},
        "Физика":           {"attendance": "9/10",  "score": 92},
        "Программирование": {"attendance": "10/10", "score": 99},
    },
    "Пётр Петров": {
        "Математика":  {"attendance": "7/10",  "score": 76},
        "Информатика": {"attendance": "10/10", "score": 88},
    },
    "Анна Смирнова": {
        "Химия":            {"attendance": "9/10",  "score": 90},
        "Биология":         {"attendance": "8/10",  "score": 81},
        "Программирование": {"attendance": "9/10",  "score": 95},
    },
}


# FSM-состояния
class Form(StatesGroup):
    CHOOSING_STUDENT    = State()
    CHOOSING_DISCIPLINE = State()


# Основная асинхронная точка входа
async def main():
    # Инициализируем Bot и Dispatcher
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Хэндлер для команды /start
    @dp.message(Command(commands=["start"]))
    async def cmd_start(message: types.Message, state: FSMContext):
        """
        Отправляем приветствие и формируем ReplyKeyboardMarkup со списком студентов.
        Устанавливаем состояние Form.CHOOSING_STUDENT.
        """
        # Построим список кнопок — по одному имени студента в строке
        keyboard = [
            [types.KeyboardButton(text=name)]
            for name in students_data.keys()
        ]
        markup = types.ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer(
            "👋 Привет! Я — бот для студентов.\n"
            "Покажу посещаемость и баллы по выбранной дисциплине.\n\n"
            "Сначала выберите студента из списка:",
            reply_markup=markup
        )
        # Переходим в состояние выбора студента
        await state.set_state(Form.CHOOSING_STUDENT)

    # Хэндлер на выбор студента (Form.CHOOSING_STUDENT)
    @dp.message(Form.CHOOSING_STUDENT)
    async def process_student_choice(message: types.Message, state: FSMContext):
        """
        Пользователь выбрал (или ввёл) имя студента.
        Проверяем корректность, запоминаем и показываем список дисциплин.
        """
        chosen_name = message.text.strip()

        if chosen_name not in students_data:
            await message.answer(
                "⚠️ Я не нашёл такого студента. Пожалуйста, выберите из списка."
            )
            return  # остаёмся в том же состоянии

        # Сохраняем выбранного студента в FSMContext
        await state.update_data(chosen_student=chosen_name)

        # Построим клавиатуру с дисциплинами этого студента
        keyboard = [
            [types.KeyboardButton(text=discipline)]
            for discipline in students_data[chosen_name].keys()
        ]
        markup = types.ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer(
            f"✏️ Выбран студент: *{chosen_name}*.\n\n"
            "Теперь выберите дисциплину:",
            parse_mode="Markdown",
            reply_markup=markup
        )
        # Переходим в состояние выбора дисциплины
        await state.set_state(Form.CHOOSING_DISCIPLINE)

    # Хэндлер на выбор дисциплины (Form.CHOOSING_DISCIPLINE)
    @dp.message(Form.CHOOSING_DISCIPLINE)
    async def process_discipline_choice(message: types.Message, state: FSMContext):
        """
        Пользователь выбрал (или ввёл) название дисциплины.
        Проверяем, есть ли она у выбранного студента. Если да — показываем данные.
        """
        data = await state.get_data()
        student_name = data.get("chosen_student")
        chosen_discipline = message.text.strip()

        if student_name is None or chosen_discipline not in students_data[student_name]:
            await message.answer(
                "⚠️ Такой дисциплины нет. Пожалуйста, выберите ещё раз."
            )
            return  # остаёмся в том же состоянии

        info = students_data[student_name][chosen_discipline]
        attendance = info.get("attendance", "—")
        score = info.get("score", "—")

        result_text = (
            f"📋 *Студент:* {student_name}\n"
            f"📚 *Дисциплина:* {chosen_discipline}\n"
            f"🗓 *Посещаемость:* {attendance}\n"
            f"🏅 *Баллы:* {score}"
        )

        # Отправляем результат, убираем клавиатуру и сбрасываем FSM
        await message.answer(
            result_text,
            parse_mode="Markdown",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()

        # Предложим начать заново
        await message.answer("Если хотите проверить другого студента — введите /start")

    # Фолбэк для любых других сообщений
    @dp.message()
    async def fallback(message: types.Message):
        await message.answer("Я пока не знаю, как это обработать. Введите /start для начала.")

    # Запускаем polling
    await dp.start_polling(bot)

# Точка запуска
if __name__ == "__main__":
    asyncio.run(main())
