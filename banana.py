import json
from Crypto.Cipher import AES
from Crypto import Random
from colorama import Fore, Style
from datetime import datetime
from fake_useragent import FakeUserAgent
import pytz
import time
import cloudscraper
import base64
import hashlib
requests = cloudscraper.create_scraper()

def print_timestamp(message, timezone='Asia/Jakarta'):
    local_tz = pytz.timezone(timezone)
    now = datetime.now(local_tz)
    timestamp = now.strftime(f'%x %X %Z')
    print(
        f"{Fore.BLUE + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{message}"
    )

def make_request(method, url, headers, json=None, data=None):
    retry_count = 0
    while True:
        time.sleep(2)
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, json=json)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json, data=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json, data=data)
        else:
            raise ValueError("Invalid method.")
        
        if response.status_code >= 500:
            if retry_count >= 4:
                print_timestamp(f"Status Code: {response.status_code} | Server Down")
                return None
            retry_count += 1
        elif response.status_code >= 400:
            print_timestamp(f"Status Code: {response.status_code} | Request Failed")
            return None
        elif response.status_code >= 200:
            return response.json()

class Banana:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://banana.carv.io',
            'Referer': 'https://banana.carv.io/',
            'Sec-CH-UA': '"Not A;Brand";v="99", "Android";v="12"',
            'Sec-CH-UA-Mobile': '?1',
            'Sec-CH-UA-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.73 Mobile Safari/537.36',
            'X-App-ID': 'carv',
        }
    
    def pad(self, s):
        block_size = 16
        padding = block_size - len(s.encode('utf-8')) % block_size
        return s + chr(padding) * padding

    def get_key_and_iv(self, password, salt, klen=32, ilen=16, msgdgst='md5'):
        password = password.encode('utf-8')
        maxlen = klen + ilen
        keyiv = b''
        prev = b''
        while len(keyiv) < maxlen:
            prev = hashlib.md5(prev + password + salt).digest()
            keyiv += prev
        key = keyiv[:klen]
        iv = keyiv[klen:klen+ilen]
        return key, iv

    def encrypt_timestamp(self, timestamp, password):
        salt = Random.new().read(8)
        key, iv = self.get_key_and_iv(password, salt)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_timestamp = self.pad(timestamp)
        encrypted = cipher.encrypt(padded_timestamp.encode('utf-8'))
        encrypted_data = b"Salted__" + salt + encrypted
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        return encrypted_b64



    def login(self, query):
        url = 'https://interface.carv.io/banana/login'
        headers = {
            **self.headers
        }
        while True:
            payload = {
                        'tgInfo': query,
                }
            time.sleep(2)
            response = make_request('post', url, headers=headers, json=payload)
            data = response
            token = f"{data['data']['token']}"
            return f"Bearer {token}"

    def get_user_info(self, token: str):
        url = 'https://interface.carv.io/banana/get_user_info'
        headers = {
            **self.headers,
            'authorization' : token
        }
        try:
            response = make_request('get', url, headers=headers)
            return response
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def get_lottery_info(self, token: str):
        url = 'https://interface.carv.io/banana/get_lottery_info'
        headers = {
            **self.headers,
            'authorization' : token
        }
        try:
            get_user = self.get_user_info(token=token)
            response = make_request('get', url, headers=headers)
            data = response
            if get_user['data']['max_click_count'] > get_user['data']['today_click_count']:
                click = self.do_click(token=token, click_count=get_user['data']['max_click_count'] - get_user['data']['today_click_count'])
                if click['msg'] == "Success":
                    print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Clicked {click['data']['peel']} 🍌 ]{Style.RESET_ALL}")
                else:
                    print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {click['msg']} ]{Style.RESET_ALL}")
            else:
                print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Out Of Clicks, Banana Break 😋 ]{Style.RESET_ALL}")

            now = datetime.now()
            last_countdown_start_time = datetime.fromtimestamp(data['data']['last_countdown_start_time'] / 1000)
            countdown_interval_minutes = data['data']['countdown_interval']

            elapsed_time_minutes = (now - last_countdown_start_time).total_seconds() / 60
            remaining_time_minutes = max(countdown_interval_minutes - elapsed_time_minutes, 0)
            if remaining_time_minutes > 0 and data['data']['countdown_end'] == False:
                hours, remainder = divmod(remaining_time_minutes * 60, 3600)
                minutes, seconds = divmod(remainder, 60)
                print_timestamp(f"{Fore.BLUE + Style.BRIGHT}[ Claim Your Banana In {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds ]{Style.RESET_ALL}")
            else:
                claim_lottery = self.claim_lottery(token=token, lottery_type=1)
                if claim_lottery['msg'] == "Success":
                    print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Lottery Claimed 🍌 ]{Style.RESET_ALL}")
                    time.sleep(2)
                    print_timestamp('Claim Ads')
                    ads = self.claim_ads(token=token, type=2)
                    if ads is not None:
                        code = ads.get('code',0)
                        if code == 0:
                            data = ads.get('data',{})
                            print_timestamp(f"income : {data.get('income',0)} | peels :  {data.get('peels',0)} | speedup :  {data.get('speedup',0)}")
                        else:
                            print_timestamp(f"Code : {code} | msg : {ads.get('msg')}")
                    speedup_count = get_user['data']['speedup_count']
                    if speedup_count > 0:
                        # time.sleep(2)
                        # ads = self.claim_ads(token=token, type=1)
                        # if ads is not None:
                        #     code = ads.get('code',0)
                        #     if code == 0:
                        #         data = ads.get('data',{})
                        #         print_timestamp(f"income : {data.get('income',0)} | peels :  {data.get('peels',0)} | speedup :  {data.get('speedup',0)}")
                        #     else:
                        #         print_timestamp(f"Code : {code} | msg : {ads.get('msg')}")
                        time.sleep(2)
                        speedup = self.do_speedup(token=token)
                        if speedup['msg'] == "Success":
                            print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Speedup Applied ]")
                    else:
                        time.sleep(2)
                        ads = self.claim_ads(token=token, type=1)
                        if ads is not None:
                            code = ads.get('code',0)
                            if code == 0:
                                data = ads.get('data',{})
                                print_timestamp(f"income : {data.get('income',0)} | peels :  {data.get('peels',0)} | speedup :  {data.get('speedup',0)}")
                                speedup = {data.get('speedup',0)}
                                if speedup != 0:
                                    time.sleep(2)
                                    speedup = self.do_speedup(token=token)
                                    if speedup['msg'] == "Success":
                                        print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Speedup Applied ]")
                            else:
                                print_timestamp(f"Code : {code} | msg : {ads.get('msg')}")
                else:
                    print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {claim_lottery['msg']} ]{Style.RESET_ALL}")
            time.sleep(2)
           

            get_lottery = self.get_user_info(token=token)
            harvest = get_lottery['data']['lottery_info']['remain_lottery_count']
            while harvest > 0:
                time.sleep(10)
                self.do_lottery(token=token)
                harvest -= 1
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_click(self, token: str, click_count: int):
        url = 'https://interface.carv.io/banana/do_click'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'clickCount': click_count
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_speedup(self, token: str):
        url = 'https://interface.carv.io/banana/do_speedup'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {}
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def claim_lottery(self, token: str, lottery_type: int):
        url = 'https://interface.carv.io/banana/claim_lottery'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'claimLotteryType': lottery_type
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_lottery(self, token: str):
        url = 'https://interface.carv.io/banana/do_lottery'
        timestamp = str(int(time.time() * 1000))
        encrypted_timestamp = self.encrypt_timestamp(timestamp, "1,1,0")
        headers = {
            **self.headers,
            'authorization' : token,
            "Request-Time": encrypted_timestamp
        }
        payload = {}

        response = make_request('post', url, headers=headers, json=payload)
        data = response
        if data['msg'] == "Success":
            print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ {data['data']['banana_info']['name']} 🍌 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {data['data']['banana_info']['ripeness']} ]{Style.RESET_ALL}"
            )
            print_timestamp(f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {data['data']['banana_info']['daily_peel_limit']} ]{Style.RESET_ALL}")
            print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ Sell Price Peel {data['data']['banana_info']['sell_exchange_peel']} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}[ Sell Price USDT {data['data']['banana_info']['sell_exchange_usdt']} ]{Style.RESET_ALL}"
            )
        else:
            print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {data['msg']} ]{Style.RESET_ALL}")
 

    def get_banana_list(self, token: str):
        url = 'https://interface.carv.io/banana/get_banana_list/v2?page_num=1&page_size=15'
        headers = {
            **self.headers,
            'authorization' : token
        }
        try:
            get_user = self.get_user_info(token=token)
            response = make_request('get', url, headers=headers)
            if response is not None:
                get_banana = response
                filtered_banana_list = [banana for banana in get_banana['data']['list'] if banana['count'] >= 1]
                highest_banana = max(filtered_banana_list, key=lambda x: x['daily_peel_limit'])
                if highest_banana['daily_peel_limit'] > get_user['data']['equip_banana']['daily_peel_limit']:
                    print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Equipping Banana ]{Style.RESET_ALL}")
                    equip_banana = self.do_equip(token=token, banana_id=highest_banana['banana_id'])
                    if equip_banana['msg'] == "Success":
                        print_timestamp(
                            f"{Fore.YELLOW + Style.BRIGHT}[ {highest_banana['name']} 🍌 ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {highest_banana['ripeness']} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {highest_banana['daily_peel_limit']} ]{Style.RESET_ALL}"
                        )
                    else:
                        print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {equip_banana['msg']} ]{Style.RESET_ALL}")
                else:
                    print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Currently Using ]{Style.RESET_ALL}")
                    print_timestamp(
                        f"{Fore.YELLOW + Style.BRIGHT}[ {highest_banana['name']} 🍌 ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {highest_banana['ripeness']} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {highest_banana['daily_peel_limit']} ]{Style.RESET_ALL}"
                    )
                count_banana = [banana for banana in get_banana['data']['list'] if banana['count'] > 1]
                for sell in count_banana:
                    sell_banana = self.do_sell(token=token, banana_id=sell['banana_id'], sell_count=sell['count'] - 1)
                    if sell_banana['msg'] == "Success":
                        print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Only One {sell['name']} Remaining ]{Style.RESET_ALL}")
                        print_timestamp(
                            f"{Fore.YELLOW + Style.BRIGHT}[ Sell Got {sell_banana['data']['sell_got_peel']} Peel 🍌 ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}[ Sell Got {sell_banana['data']['sell_got_usdt']} USDT 🤑 ]{Style.RESET_ALL}"
                        )
                        print_timestamp(
                            f"{Fore.YELLOW + Style.BRIGHT}[ {sell_banana['data']['peel']} Peel 🍌 ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}[ {sell_banana['data']['usdt']} USDT 🤑 ]{Style.RESET_ALL}"
                        )
                    else:
                        print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {sell_banana['msg']} ]{Style.RESET_ALL}")
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_equip(self, token: str, banana_id: int):
        url = 'https://interface.carv.io/banana/do_equip'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'bananaId': banana_id
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_sell(self, token: str, banana_id: int, sell_count: int):
        url = 'https://interface.carv.io/banana/do_sell'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {
            'bananaId': banana_id,
            'sellCount': sell_count
        }
        try:
            response = make_request('post', url, headers=headers, json=payload)
            return response
        except (Exception) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def achieve_quest(self, quest_id, token):
        url = f'https://interface.carv.io/banana/achieve_quest'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {"quest_id": quest_id}
        response = make_request('post', url, headers=headers, json=payload)
        return response
    
    def claim_quest(self, quest_id, token):
        url = f'https://interface.carv.io/banana/claim_quest'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {"quest_id": quest_id}
        response = make_request('post', url, headers=headers, json=payload)
        return response

    def claim_quest_lottery(self, token):
        url = 'https://interface.carv.io/banana/claim_quest_lottery'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {}
        response = make_request('post', url, headers=headers, json=payload)
        return response
    
    def get_quest(self, token):
        url = f'https://interface.carv.io/banana/get_quest_list/v2?page_num=1&page_size=15'
        headers = {
            **self.headers,
            'authorization' : token
        }
        response = make_request('get', url, headers=headers)
        return response

    def claim_ads(self, token, type):
        url = 'https://interface.carv.io/banana/claim_ads_income'
        headers = {
            **self.headers,
            'authorization' : token
        }
        payload = {'type':type}
        response = make_request('post', url, headers=headers, json=payload)
        return response

    def clear_quest(self, token):
        # Fetch quest list
            self.headers.update({
            'Authorization': token
            })
            # Extract and print quest names and claim statuses
            data_quest = self.get_quest(token)
            data = data_quest.get('data')
            quest_list = data.get('list', [])

            for index, quest in enumerate(quest_list, start=1):
                quest_name = quest.get('quest_name', 'N/A')
                is_achieved = quest.get('is_achieved', False)
                is_claimed = quest.get('is_claimed', False)
                quest_id = quest.get('quest_id')
                
                # Convert boolean to Yes/No
                achieved_status = "Yes" if is_achieved else "No"
                claimed_status = "Yes" if is_claimed else "No"
                
                # Color coding for quest details
                quest_name_color = Fore.CYAN
                achieved_color = Fore.GREEN if is_achieved else Fore.RED
                claimed_color = Fore.GREEN if is_claimed else Fore.RED
                
                print_timestamp(f"{Fore.BLUE}[Quest {index}] : {quest_name_color}{quest_name} {Fore.BLUE}")
                
                # Skip the achievement process for 'bind' quests
                if 'bind' in quest_name.lower():
                    if not is_achieved:
                        print_timestamp(f"{Fore.YELLOW}Skipping Quest")
                        continue
                if 'badge' in quest_name.lower():
                    if not is_achieved:
                        print_timestamp(f"{Fore.YELLOW}Skipping Quest")
                        continue
                if 'premium' in quest_name.lower():
                    if not is_achieved:
                        print_timestamp(f"{Fore.YELLOW}Skipping Quest")
                        continue
                if 'pvp' in quest_name.lower():
                    if not is_achieved:
                        print_timestamp(f"{Fore.YELLOW}Skipping Quest")
                        continue
                if 'mobile' in quest_name.lower():
                    if not is_achieved:
                        print_timestamp(f"{Fore.YELLOW}Skipping Quest")
                        continue
                if 'telgather' in quest_name.lower():
                    if not is_achieved:
                        print_timestamp(f"{Fore.YELLOW}Skipping Quest")
                        continue

                if not is_achieved:
                    trys = 3
                    while True:
                        if trys <= 0:
                            break
                        time.sleep(2)
                        achieve_response = self.achieve_quest(quest_id, token=token)
                        response = achieve_response
                        time.sleep(2)
                        if response.get('msg') == "Success":
                            response = self.claim_quest(quest_id, token=token)
                            res = response
                            if res.get('msg') == "Success":
                                print_timestamp(f"{Fore.GREEN}Quest {quest_name} Achieved and Claimed Successfully{Style.RESET_ALL}")
                                break
                        trys -= 1

                    time.sleep(2)  # Sleep for 1 second


                if is_achieved and not is_claimed:
                    # Automatically claim the quest without prompting
                    claim_response = self.claim_quest(quest_id, token=token)
                    res = claim_response
                    if res.get('msg') == "Success":
                        print_timestamp(f"{Fore.GREEN}Quest {quest_name} Achieved and Claimed Successfully{Style.RESET_ALL}")
                    time.sleep(2)  # Sleep for 1 second

            is_claimed = data.get('is_claimed')
            trys = 3
            while True:
                if trys <= 0:
                            break
                if is_claimed == True:
                    time.sleep(2)
                    dats = self.claim_quest_lottery(token=token)
                    if dats.get('msg') == "Success":
                        print_timestamp(f"{Fore.GREEN}Claim reward quest done")
                    time.sleep(2)
                    data_quest = self.get_quest(token)
                    data = data_quest.get('data')
                    is_claimed = data.get('is_claimed')
                    trys -= 1
                else:
                    break
                trys -= 1
    

    