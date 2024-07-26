import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message
from aiogram.filters import Command
import requests
from bs4 import BeautifulSoup
from aiogram.enums import ParseMode
from aiogram.types import URLInputFile, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import sql
from dotenv import load_dotenv
import os
import random
from PIL import Image


load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Что ты умеешь? 💼"),
        types.KeyboardButton(text="Кинуть кубик 🎲")
    )
    builder.row(types.KeyboardButton(text="Cписок сохраненных дорам 🗃️"))
    builder.row(types.KeyboardButton(text="Случайный скриншот из Киберпанка 📸"))
    await message.answer(f"Nice to see you, mate {message.from_user.first_name}",
                         reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(F.photo)
async def photo_msg(message: Message):
    await message.answer("Это точно какое-то изображение!")


@dp.message(F.text == "Что ты умеешь? 💼")
async def opportunity(message: Message):
    await message.answer("Могу кинуть кубик ✅")
    await message.answer("Могу скинуть статус вышедших серий дорамы на выбор ✅\n"
                         "Нужно ввести: <b>Проверь <u>название дорамы транслитом</u></b> ✏️",
                         parse_mode=ParseMode.HTML)
    await message.answer("Могу вывести сохраненные дорамы ✅")
    await message.answer("Могу сохранить дораму ✅\n"
                         "Для этого введите: <b>Сохранить <u>название дорамы транслитом</u> КЛЮЧ</b> ✏️",
                         parse_mode=ParseMode.HTML)
    await message.answer("Могу удалить дораму ✅\n"
                         "Для этого введите: <b>Удалить <u>ключ дорамы</u></b> ✏️",
                         parse_mode=ParseMode.HTML)
    await message.answer("Могу отправить скрин ✅\n"
                         "Для этого введите: <b>Скриншот</b> ✏️",
                         parse_mode=ParseMode.HTML)


@dp.message(F.text == "Кинуть кубик 🎲")
async def cmd_dice(message: Message):
    await message.answer_dice(emoji="🎲",)


@dp.message(lambda msg: any(word in msg.text.lower() for word in ["ghjdthm", "проверь"]))
async def parser(message: Message):
        get_mess_text = message.text.split()[1]
        url = f"https://doramalive.info/dorama/{get_mess_text.lower()}/"
        headers = {"user-agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "lxml")
        #Проверка на фильм.
        film_check = soup.find("div", class_="col-lg-12")
        film = film_check.find("h1").text
        result = ""
        if film.split()[0] == "Фильм":
            try:
                href = soup.find("a", class_="btn btn-danger start")
                link = "https://doramalive.info" + href["href"]
                #name_f означает что действие происходит на странице фильма
                response_f = requests.get(link, headers=headers)
                html_f = response_f.text
                soup_f = BeautifulSoup(html_f, "html.parser")
                table = soup_f.find("table", class_="table table-hover table-trans")
                tbody = table.find("tbody")
                for i in tbody:
                    if i == "\n":
                        continue
                    else:
                        result += (f""
                                   f"Переводчик: {' '.join(i.text.split()[:2])}\n"
                                   f"Тип озвучки: {' '.join(i.text.split()[2:-1])}\n\n"
                                   f"")
                img = soup.find("div", class_="cover-dorama")
                link = img.find("img")
                image_from_url = URLInputFile("https://doramalive.info" + link["src"])
                await message.answer_photo(image_from_url,
                                               caption=f"Статус перевода фильма\n🎬<b>{' '.join(film.split()[1:])}</b>:"
                                                       f"\n{result}",
                                               parse_mode=ParseMode.HTML)
            except AttributeError:
                await message.answer(f"Cтраницы {get_mess_text.lower()} не найдена.")
            except TypeError:
                premiere = soup.find("div", class_="alert-new premieres")
                await message.answer(premiere.text)
        else:
            try:
                    series = soup.find("ul", class_="dropdown-menu min episodes-list")
                    lines = series.find_all('li')
                    img = soup.find("div", class_="cover-dorama")
                    link = img.find("img")
                    image_from_url = URLInputFile("https://doramalive.info" + link["src"])
                    for line in lines:
                        result += line.text + "\n"
                    await message.answer_photo(image_from_url,
                                               caption=f"Статус серий дорамы\n🎬<b>{' '.join(film.split()[1:])}</b>:"
                                                       f" \n{result}",
                                               parse_mode=ParseMode.HTML)
            except:
                premiere = soup.find("div", class_="alert-new premieres")
                if premiere:
                    await message.answer("Ждем перевод")
                else:
                    await message.answer(f"Cтраницы {get_mess_text.lower()} не найдена.")



@dp.message(F.text == "Cписок сохраненных дорам 🗃️")
async def get_drams(message: Message):
    struct = sql.get_value()
    if not struct:
        await message.answer("Нет сохраненных дорам 🗒")

    else:
        answer_block = ""
        for i in range(len(struct)):
            answer_block += (f"🔑 {str(struct[i][0])}  💾 <code>Проверь {str(struct[i][1])}</code>\n\n")
        await message.answer(answer_block, parse_mode=ParseMode.HTML)


@dp.message(lambda msg: any(word in msg.text.lower() for word in ["cj[hfybnm", "сохранить"]))
async def save_drams(message: Message):
    get_mess_text = message.text.split()[1]
    index = message.text.split()[2]
    try:
        sql.set_value(get_mess_text, index)
        await message.answer("Дорама успешно сохранена📝")
    except Exception as error:
        await message.answer(f'Ошибка в работе с базой данных ({error})')

@dp.message(lambda msg: any(word in msg.text.lower() for word in ["elfkbnm", "удалить"]))
async def delete(message: Message):
    get_mess_text = message.text.split()[1]
    try:
        sql.delete(get_mess_text)
        await message.answer("Удаление выполнено успешно 🗑")
    except Exception as error:
        await message.answer(f"Таблица дорам пуста 🗒\n Или возникла ошибка при удалении ({error}).")


#Код для скринов, в случие, если папка в директории
@dp.message(lambda msg: any(word in msg.text.lower() for word in ["crhbyijn", "скриншот"]))
async def random_scr_cyber(message: Message):
    try:
        file = os.listdir('C:/Users/morga/PycharmProjects/Pitonchik/Screenshots')
        random_choice = random.choice(file)
        image_path = os.path.join("C:/Users/morga/PycharmProjects/Pitonchik/Screenshots/", random_choice)
        #print(int(os.path.getsize(image_path)) / 1048576)
        if int(os.path.getsize(image_path)) / 1048576 > 2:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img.save(image_path, "JPEG", quality=100)
        #print(int(os.path.getsize(image_path)) / 1048576)
        img_to_send = FSInputFile(image_path)
        await message.answer_photo(img_to_send)
    except Exception as error:
        await message.answer(f"Скринов нет или произошла какая-то ошибка ({error}).")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

