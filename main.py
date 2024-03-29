import asyncio
import json
import re

from aiogram import Bot, Dispatcher, types
import logging

logging.basicConfig(level=logging.INFO)


def get_token():
    with open('secr.json', 'r') as file:
        token = json.load(file)['TOKEN']
    return token


def correct_cad_num(cad_num: str) -> str:
    """Исправляет написание кадастрового номера - удаляет лишние нули и пробелы"""
    p1, p2, p3, p4 = [str(int(''.join([char for char in part if char.isdigit()]))) for part in cad_num.split(':')]
    p2 = p2.zfill(2)
    p3 = p3.zfill(7)
    if set(p4) == {'0'}:
        return None
    return f'{p1}:{p2}:{p3}:{p4}'


def find_cad_nums(text: str):
    """ Выделяет из текста кадастровые номера, игнорируя повторы """
    pattern = r"\d{2}\s*:\s*\d\s*\d\s*:\s*\d\s*(?:\d\s*){0,10}\s*:\s*\d{1,6}"

    result, bullshit, corrected = [], [], {}
    for cad_num in re.findall(pattern, text):
        corrected_cad_num = correct_cad_num(cad_num) 
        if corrected_cad_num is None:
            bullshit.append(cad_num)
            continue
        if corrected_cad_num not in result:
            result.append(corrected_cad_num)
        if corrected_cad_num != cad_num:
            corrected[cad_num] = (corrected_cad_num)
    
    return result, bullshit, corrected


async def catch_cad_nums(message: types.Message):
    if not message.text:
        return
    correct, _bullshit, corrected = find_cad_nums(message.text)
    cad_nums = correct + list(corrected.values())
    if not cad_nums:
        await message.answer('Номеров не найдено')
        return
    msg = "```" + '\n'.join(sorted(set(cad_nums))) + "```"
    await message.answer(msg, parse_mode='Markdown')


async def main():
    bot = Bot(token=get_token())
    dp = Dispatcher()
    dp.message.register(catch_cad_nums)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
