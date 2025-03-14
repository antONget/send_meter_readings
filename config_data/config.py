from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: str
    bot_name_for_link: str
    button_list: list
    support_id: str



@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admin_ids=env('ADMIN_IDS'),
                               bot_name_for_link=env('BOT_NAME_FOR_LINK'),
                               button_list=env('BUTTON_LIST'),
                               support_id=env('SUPPORT_ID')))
