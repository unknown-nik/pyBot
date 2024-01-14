import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message
from aiogram.filters import Command
import requests
from bs4 import BeautifulSoup
from aiogram.enums import ParseMode
from aiogram.types import URLInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import sql
from dotenv import load_dotenv
import os

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
                         "Для этого введите: <b>Сохранить <u>название дорамы транслитом</u></b> ✏️",
                         parse_mode=ParseMode.HTML)
    await message.answer("Могу удалить дораму ✅\n"
                         "Для этого введите: <b>Удалить <u>ключ дорамы</u></b> ✏️",
                         parse_mode=ParseMode.HTML)


@dp.message(F.text == "Кинуть кубик 🎲")
async def cmd_dice(message: Message):
    await message.answer_dice(emoji="🎲",)


@dp.message(lambda msg: any(word in msg.text.lower() for word in ["ghjdthm", "проверь"]))
async def parser(message: Message):
        get_mess_text = message.text.split()[1]
        url = f"https://doramalive.ru/dorama/{get_mess_text.lower()}/"
        headers = {"user-agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        #Проверка на фильм.
        film_check = soup.find("div", class_="col-lg-12")
        film = film_check.find("h1").text
        result = ""
        if film.split()[0] == "Фильм":
            try:
                href = soup.find("a", class_="btn btn-danger start")
                link = "https://doramalive.ru" + href["href"]
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
                image_from_url = URLInputFile("https://doramalive.ru" + link["src"])
                await message.answer_photo(image_from_url,
                                               caption=f"Статус перевода фильма\n🎬<b>{' '.join(film.split()[1:])}</b>: \n{result}",
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
                    image_from_url = URLInputFile("https://doramalive.ru" + link["src"])
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
            answer_block += (f"🔑 {str(struct[i][0])}      💾 <code>Проверь {str(struct[i][1])}</code>\n\n")
        await message.answer(answer_block, parse_mode=ParseMode.HTML)


@dp.message(lambda msg: any(word in msg.text.lower() for word in ["cj[hfybnm", "сохранить"]))
async def save_drams(message: Message):
    get_mess_text = message.text.split()[1]
    sql.set_value(get_mess_text)


@dp.message(lambda msg: any(word in msg.text.lower() for word in ["elfkbnm", "удалить"]))
async def delete(message: Message):
    get_mess_text = message.text.split()[1]
    try:
        sql.delete(get_mess_text)
    except:
        await message.answer("Таблица дорам пуста 🗒")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

