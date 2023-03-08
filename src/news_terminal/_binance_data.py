from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
from binance.client import Client
from pprint import pprint

from collections import defaultdict

DEFAULT_CHANNELS = ["kline_1m", "kline_5m", "kline_15m", "trade"]

STABLE_COINS = {
    "T",
    "BUSD",
    "USDT",
    "TUSD",
    "USDC",
    "UST",
    "USTC",
    "USDP",
    "USDS",
    "USDSB",
    "SUSD",
    "NU",
}

DISABLED_ENDS = ("BEAR", "DOWN", "UP", "BULL")


def subscribe_to_market(
    api_manager: BinanceWebSocketApiManager | None, stream: None | str, market: str
) -> tuple[BinanceWebSocketApiManager, str]:
    new_api_manager = BinanceWebSocketApiManager(
        exchange="binance.com-futures", output_default="dict", high_performance=True
    )
    if stream and api_manager:
        api_manager.stop_manager_with_all_streams()

    new_stream = new_api_manager.create_stream(
        channels=DEFAULT_CHANNELS, markets=market
    )
    return new_api_manager, new_stream


def get_all_future_pairs() -> list:
    client = Client()
    info = client.futures_exchange_info()
    return [symbol["symbol"] for symbol in info["symbols"]]


def get_all_spot_pairs() -> list:
    client = Client()
    info = client.get_exchange_info()
    return [symbol["symbol"] for symbol in info["symbols"]]


def build_actions_data() -> dict:
    future_pairs = get_all_future_pairs()
    spot_pairs = get_all_spot_pairs()

    actions_data = defaultdict(list)
    for pair in spot_pairs:
        if not pair.endswith("USDT") and not pair.endswith("BUSD"):
            continue
        ticker = pair[:-4]
        if ticker in STABLE_COINS:
            continue
        if ticker.endswith(DISABLED_ENDS):
            continue
        if ticker[-1].isdigit():
            continue

        for f_pair in future_pairs:
            if ticker == f_pair[:-4]:
                temp_action = {}
                formated_f_pair = f"{f_pair[:-4]}{f_pair[-4:]}"
                temp_action["title"] = f"{formated_f_pair} PERP"
                if temp_action not in actions_data[ticker]:
                    actions_data[ticker].append(temp_action)

        formated_pair = f"{pair[:-4]}/{pair[-4:]}"
        temp_action = {"title": formated_pair}
        if temp_action not in actions_data[ticker]:
            actions_data[ticker].append(temp_action)

    return actions_data
