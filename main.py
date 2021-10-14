import asyncio
import aioschedule
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from config import Config
from device import DeviceStatus
from util import log, has_children, load_json_to_obj

bot = Bot(token=Config.TOKEN)
dp = Dispatcher(bot)

main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(KeyboardButton('/update'))


@dp.message_handler(commands=['start', 'update'])
async def process_start_command(msg: types.Message):
    load_json_to_obj()
    for network in Config.USER['networks'].keys():
        set_ping_task(msg, network)
    await msg.reply(f'Scheduled ping every {Config.TIME_TO_PING} minutes.',
                    reply_markup=main_kb, parse_mode=ParseMode.HTML)
    if not Config.USER['is_schedule']:
        Config.USER['is_schedule'] = True
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)


def set_ping_task(msg: types.Message, network: str):
    aioschedule.clear(f'{network}')
    aioschedule \
        .every(Config.TIME_TO_PING) \
        .minutes \
        .do(lambda:
            check_status(msg, network, Config.USER['networks'][network])) \
        .tag(f'{network}')


async def notify(msg: types.Message, network: str, node):
    await msg.reply(
        f'{network}_{node.index}/{node.name} : <b>{node.status.value}</b>',
        reply_markup=main_kb, parse_mode=ParseMode.HTML
    )


async def check_status(msg: types.Message, network: str, node):
    previous_status = node.status
    node.status = DeviceStatus.UP if node.ping() else DeviceStatus.DOWN

    # was UP,   now DOWN
    if previous_status == DeviceStatus.UP and node.status == DeviceStatus.DOWN:
        await notify(msg, network, node)
        log(network, node)
    # was DOWN, now UP
    if previous_status == DeviceStatus.DOWN and node.status == DeviceStatus.UP:
        await notify(msg, network, node)
        log(network, node)
    # was DOWN, now DOWN
    elif previous_status == node.status == DeviceStatus.DOWN:
        log(network, node, 'STILL DOWN')
    # was UP,   now UP
    elif previous_status == node.status == DeviceStatus.UP:
        log(network, node, 'OK')

    if has_children(node):
        for child in node.children:
            await check_status(msg, network, child)


if __name__ == '__main__':
    executor.start_polling(dp)
