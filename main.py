import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
import asyncio
import time
from datetime import datetime


from aiocron import crontab
import pytz

TELEGRAM_BOT_TOKEN = '7654868943:AAGtm_nMvxf1m7e4A1Leoer-2iToHu65HVY'
TELEGRAM_CHANNEL_ID = '2631807828'  
CHECK_INTERVAL = 600  

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

published_news = {
    'riavrn': set(),
    'abireg': set(),
    'moibiz36': set(),
    'vestivrn': set(),
    'vrnoblduma': set()
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


daily_digest = []

async def parse_riavrn():
    url = 'https://riavrn.ru/economy/'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('div', class_='news-item')
        for item in reversed(news_items):
            title_tag = item.find('a', class_='title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = 'https://riavrn.ru' + title_tag['href'] if not title_tag['href'].startswith('http') else title_tag['href']
            if link not in published_news['riavrn']:
                message = f"📰 RiaVRN: {title}\n\n🔗 {link}"
                await send_to_channel(message)
                published_news['riavrn'].add(link)
    except Exception as e:
        print(f"Ошибка при парсинге riavrn.ru: {e}")

async def parse_abireg():
    url = 'https://abireg.ru/novosti-partnerov/'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('div', class_='news-item')
        for item in reversed(news_items):
            title_tag = item.find('a', class_='title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            if link not in published_news['abireg']:
                message = f"📰 Abireg: {title}\n\n🔗 {link}"
                await send_to_channel(message)
                published_news['abireg'].add(link)
    except Exception as e:
        print(f"Ошибка при парсинге abireg.ru: {e}")

async def parse_moibiz36():
    url = 'https://moibiz36.ru/category/novosti_portala/'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('article', class_='post')
        for item in reversed(news_items):
            title_tag = item.find('h2', class_='entry-title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag.find('a')['href']
            if link not in published_news['moibiz36']:
                message = f"📰 Moibiz36: {title}\n\n🔗 {link}"
                await send_to_channel(message)
                published_news['moibiz36'].add(link)
    except Exception as e:
        print(f"Ошибка при парсинге moibiz36.ru: {e}")

async def parse_vestivrn():
    url = 'https://vestivrn.ru/sections/economics/'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('div', class_='news-item')
        for item in reversed(news_items):
            title_tag = item.find('a', class_='title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            if link not in published_news['vestivrn']:
                message = f"📰 VestiVRN: {title}\n\n🔗 {link}"
                await send_to_channel(message)
                published_news['vestivrn'].add(link)
    except Exception as e:
        print(f"Ошибка при парсинге vestivrn.ru: {e}")

async def parse_vrnoblduma():
    url = 'http://www.vrnoblduma.ru/press-sluzhba/arkhiv-novostey/'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('div', class_='news-item')
        for item in reversed(news_items):
            title_tag = item.find('a')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = 'http://www.vrnoblduma.ru' + title_tag['href'] if not title_tag['href'].startswith('http') else title_tag['href']
            if link not in published_news['vrnoblduma']:
                message = f"📰 VrnOblDuma: {title}\n\n🔗 {link}"
                await send_to_channel(message)
                published_news['vrnoblduma'].add(link)
    except Exception as e:
        print(f"Ошибка при парсинге vrnoblduma.ru: {e}")


async def send_to_channel(message):
    try:
        await bot.send_message(TELEGRAM_CHANNEL_ID, message)
        daily_digest.append(message)  # ➕ добавляем в дайджест
        print(f"[{datetime.now()}] Отправлено сообщение в канал")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")

async def scheduled_news_check():
    while True:
        print(f"[{datetime.now()}] Начинаю проверку новостей...")
        await parse_riavrn()
        await parse_abireg()
        await parse_moibiz36()
        await parse_vestivrn()
        await parse_vrnoblduma()
        print(f"[{datetime.now()}] Проверка завершена. Ожидаю {CHECK_INTERVAL} сек.")
        await asyncio.sleep(CHECK_INTERVAL)

async def run_bot_with_restart():
    while True:
        try:
            print(f"[{datetime.now()}] Запуск бота...")
            asyncio.create_task(scheduled_news_check())
            await dp.start_polling(bot)
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Ошибка в боте: {e}")
            print(f"[{datetime.now()}] 🔁 Перезапуск через 10 секунд...")
            await asyncio.sleep(10)


@crontab('0 22 * * *', tz=pytz.timezone('Europe/Moscow'))
async def send_daily_digest():
    if daily_digest:
        digest_text = "🗞️ *Дайджест новостей за день:*\n\n" + "\n\n".join(daily_digest)
        try:
            # Сообщения Telegram ограничены 4096 символами
            for i in range(0, len(digest_text), 4000):
                await bot.send_message(TELEGRAM_CHANNEL_ID, digest_text[i:i+4000], parse_mode='Markdown')
            print(f"[{datetime.now()}] ✅ Отправлен дневной дайджест")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Ошибка при отправке дайджеста: {e}")
        daily_digest.clear()
    else:
        print(f"[{datetime.now()}] 📭 Новостей для дайджеста нет")

if __name__ == '__main__':
    asyncio.run(run_bot_with_restart())
