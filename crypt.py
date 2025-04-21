import requests

binance_base = 'https://api.binance.com'
kucoin_base = 'https://api.kucoin.com'


# to get binance ticker (symbol)
def binance_get_ticker(cur1: str, cur2: str) -> float | None:
    '''
    :param cur1: String (first currency)
    :param cur2: Sting (second currency)
    :return: Float or None (the price of the pair, or None if the symbol is unavailable)

    Getting the price of a trading pair from Binance API.

    First attempts the direct pair (cur1+cur2).
    If not found, tries the reverse pair (cur2+cur1) and returns the inverse price.
    '''

    url = binance_base + '/api/v3/ticker/price'

    resp = requests.get(url, params={'symbol': cur1 + cur2})

    if resp.status_code == 200:
        return float(resp.json()['price'])

    # if symbol doesn't exist
    # check transform Binance response
    new_resp = requests.get(url, params={'symbol': cur2 + cur1})

    # is transform symbol exist
    if new_resp.status_code == 200:
        # return transform price
        return 1 / float(new_resp.json()['price'])

    # if symbol doesn't exist
    return None


# to get binance ticker (symbols)
def binance_get_multi_tickers(symbols: list[str]) -> str or dict:
    '''
    :param symbols: List of String (a list of trading symbols (e.g., ['BTCUSDT', 'ETHUSDT']))
    :return: Dict or String (a dictionary of every symbol price, or an error message if the request fails)

    Getting prices for multiple trading pairs from Binance API.
    '''

    url = binance_base + '/api/v3/ticker/price'
    symbols_param = '[' + ','.join(f'"{s}"' for s in symbols) + ']'

    resp = requests.get(url, params={'symbols': symbols_param})

    if resp.status_code != 200:
        return f"Something wrong with symbols, result: { {s: '-' for s in symbols} }"

    return {item['symbol']: float(item['price']) for item in resp.json()}


# to get kucoin ticker
def kucoin_get_ticker(cur1: str, cur2: str) -> float | None:
    '''
    :param cur1: String (first currency)
    :param cur2: Sting (second currency)
    :return: Float or None (the price of the pair, or None if the symbol is unavailable)

    Getting the price of a trading pair from KuCoin API.

    First attempts the direct pair (cur1+cur2).
    If not found, tries the reverse pair (cur2+cur1) and returns the inverse price.
    '''

    url = kucoin_base + '/api/v1/market/orderbook/level1'

    resp = requests.get(url, params={'symbol': cur1 + '-' + cur2})
    data = resp.json()

    if data['code'] == '200000' and data['data']:
        return float(data['data']['price'])

    # if symbol doesn't exist
    # check transform response
    new_resp = requests.get(url, params={'symbol': cur2 + '-' + cur1})
    new_data = new_resp.json()

    # if transform symbol exists
    if new_data['code'] == '200000' and new_data['data']:
        # return transform price
        return 1 / float(new_data['data']['price'])

    # if symbol doesn't exist
    return None


# check all types of exchange
def get_price(cur1: str, cur2: str, get_price_func) -> float | None:
    '''
    :param cur1: String (first currency)
    :param cur2: Sting (second currency)
    :param get_price_func: Function ( function used to retrieve prices)
    :return:

    Calculates the exchange rate between two currencies in using different ways.
    Tries the direct or reverse pair. If not available, tries a two-step conversion:
    cur1 -> USDT -> cur2.
    '''

    # A->B or B->A
    direct = get_price_func(cur1, cur2)
    if direct:
        return direct

    # A->USDT->B
    cur1_to_usdt = get_price_func(cur1, 'USDT')
    usdt_to_cur2 = get_price_func('USDT', cur2)

    if cur1_to_usdt and usdt_to_cur2:
        return cur1_to_usdt * usdt_to_cur2

    # USDT->A, USDT->B
    usdt_to_cur1 = get_price_func('USDT', cur1)
    cur2_to_usdt = get_price_func(cur2, 'USDT')

    if usdt_to_cur1 and cur2_to_usdt:
        return (1 / usdt_to_cur1) * (1 / cur2_to_usdt)

    # symbol doesn't exist
    return None


# for a better exchange
def find_the_best(cur1: str, cur2: str) -> str:
    '''
    :param cur1: String (first currency)
    :param cur2: Sting (second currency)
    :return: String (a message with the best exchange and price, or an error if unavailable)

    Compares the price of a trading pair on Binance and KuCoin and picks the best rate.
    Supports direct and indirect (via USDT) conversion routes.
    '''

    binance_resp = get_price(cur1, cur2, binance_get_ticker)
    kucoin_resp = get_price(cur1, cur2, kucoin_get_ticker)

    if binance_resp is None and kucoin_resp is None:
        return "This symbol doesn't exist"

    if binance_resp is None:
        return ("This symbol doesn't exist on Binance\n"
                f"The best exchange: KuCoin - {kucoin_resp}")

    if kucoin_resp is None:
        return ("This symbol doesn't exist on KuCoin\n"
                f"The best exchange: Binance - {binance_resp}")

    # return the best exchange
    # if Binace is better than KuCoin
    if binance_resp > kucoin_resp:
        return f'The best exchange: Binance - {binance_resp}'

    # if KuCoin is better than Binance
    return f'The best exchange: KuCoin - {kucoin_resp}'


print(find_the_best('BTC', 'USDT'))
print(find_the_best('USDT', 'BTC'))
print(find_the_best('USDT', 'XYZ'))
print(find_the_best('DOGE', 'TRX'))
print(binance_get_multi_tickers(['BTCUSDT', 'ETHUSDT', 'XYZ']))
print(binance_get_multi_tickers(['BTCUSDT', 'ETHUSDT']))
