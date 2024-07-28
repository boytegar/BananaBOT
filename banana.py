import json
from colorama import Fore, Style
from datetime import datetime
from fake_useragent import FakeUserAgent
import pytz
import requests
import time

def print_timestamp(message, timezone='Asia/Jakarta'):
    local_tz = pytz.timezone(timezone)
    now = datetime.now(local_tz)
    timestamp = now.strftime(f'%x %X %Z')
    print(
        f"{Fore.BLUE + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{message}"
    )

class Banana:
    def __init__(self):
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': 'interface.carv.io',
            'Origin': 'https://banana.carv.io',
            'Referer': 'https://banana.carv.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': FakeUserAgent().random,
            'x-app-id': 'carv'
        }
    
    def login(self, query):
        url = 'https://interface.carv.io/banana/login'
        try:
            while True:
                time.sleep(3)
                payload = {
                        'tgInfo': query,
                        'InviteCode': ""
                    }
                time.sleep(2)
                response = requests.post(url=url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                token = f"{data['data']['token']}"
                return token
            
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def get_user_info(self, token: str):
        url = 'https://interface.carv.io/banana/get_user_info'
        self.headers.update({
            'Authorization': token
        })
        try:
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def get_lottery_info(self, token: str):
        url = 'https://interface.carv.io/banana/get_lottery_info'
        self.headers.update({
            'Authorization': token
        })
        try:
            get_user = self.get_user_info(token=token)
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
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
            if remaining_time_minutes > 0 or data['data']['countdown_end'] == False:
                hours, remainder = divmod(remaining_time_minutes * 60, 3600)
                minutes, seconds = divmod(remainder, 60)
                print_timestamp(f"{Fore.BLUE + Style.BRIGHT}[ Claim Your Banana In {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds ]{Style.RESET_ALL}")
            else:
                claim_lottery = self.claim_lottery(token=token, lottery_type=1)
                if claim_lottery['msg'] == "Success":
                    print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Lottery Claimed 🍌 ]{Style.RESET_ALL}")
                else:
                    print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {claim_lottery['msg']} ]{Style.RESET_ALL}")
            time.sleep(2)
            get_lottery = self.get_user_info(token=token)
            harvest = get_lottery['data']['lottery_info']['remain_lottery_count']
            while harvest > 0:
                time.sleep(2)
                self.do_lottery(token=token)
                harvest -= 1
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_click(self, token: str, click_count: int):
        url = 'https://interface.carv.io/banana/do_click'
        self.headers.update({
            'Authorization': token
        })
        payload = {
            'clickCount': click_count
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def claim_lottery(self, token: str, lottery_type: int):
        url = 'https://interface.carv.io/banana/claim_lottery'
        self.headers.update({
            'Authorization': token
        })
        payload = {
            'claimLotteryType': lottery_type
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_lottery(self, token: str):
        url = 'https://interface.carv.io/banana/do_lottery'
        self.headers.update({
            'Authorization': token
        })
        try:
            response = requests.post(url=url, headers=self.headers, json={})
            response.raise_for_status()
            data = response.json()
            if data['msg'] == "Success":
                print_timestamp(
                    f"{Fore.YELLOW + Style.BRIGHT}[ {data['data']['name']} 🍌 ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {data['data']['ripeness']} ]{Style.RESET_ALL}"
                )
                print_timestamp(f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {data['data']['daily_peel_limit']} ]{Style.RESET_ALL}")
                print_timestamp(
                    f"{Fore.YELLOW + Style.BRIGHT}[ Sell Price Peel {data['data']['sell_exchange_peel']} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ Sell Price USDT {data['data']['sell_exchange_usdt']} ]{Style.RESET_ALL}"
                )
            else:
                print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {data['msg']} ]{Style.RESET_ALL}")
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def get_banana_list(self, token: str):
        url = 'https://interface.carv.io/banana/get_banana_list'
        self.headers.update({
            'Authorization': token
        })
        try:
            get_user = self.get_user_info(token=token)
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            get_banana = response.json()
            filtered_banana_list = [banana for banana in get_banana['data']['banana_list'] if banana['count'] >= 1]
            highest_banana = max(filtered_banana_list, key=lambda x: x['banana_id'])
            if highest_banana['banana_id'] > get_user['data']['equip_banana']['banana_id']:
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
            count_banana = [banana for banana in get_banana['data']['banana_list'] if banana['count'] > 1]
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
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_equip(self, token: str, banana_id: int):
        url = 'https://interface.carv.io/banana/do_equip'
        self.headers.update({
            'Authorization': token
        })
        payload = {
            'bananaId': banana_id
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def do_sell(self, token: str, banana_id: int, sell_count: int):
        url = 'https://interface.carv.io/banana/do_sell'
        self.headers.update({
            'Authorization': token
        })
        payload = {
            'bananaId': banana_id,
            'sellCount': sell_count
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except (Exception, requests.JSONDecodeError, requests.RequestException) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    def achieve_quest(self, quest_id):
        achieve_url = f'https://interface.carv.io/banana/achieve_quest'
        achieve_payload = {"quest_id": quest_id}
        response = requests.post(achieve_url, headers=self.headers, json=achieve_payload)
        return response
    
    def claim_quest(self, quest_id):
        claim_url = f'https://interface.carv.io/banana/claim_quest'
        claim_payload = {"quest_id": quest_id}
        response = requests.post(claim_url, headers=self.headers, json=claim_payload)
        return response

    def claim_quest_lottery(self):
        url = 'https://interface.carv.io/banana/claim_quest_lottery'
        claim_payload = {}
        response = requests.post(url, headers=self.headers, json=claim_payload)
        return response
    
    def get_quest(self):
        quest_list_url = f'https://interface.carv.io/banana/get_quest_list'
        quest_list_response = requests.get(quest_list_url, headers=self.headers)
        time.sleep(1) 
        if quest_list_response.status_code <= 210:
            quest_list_data = quest_list_response.json()
            
        return quest_list_data

    def clear_quest(self, token):
        # Fetch quest list
            self.headers.update({
            'Authorization': token
            })
            # Extract and print quest names and claim statuses
            data_quest = self.get_quest()
            data = data_quest.get('data')
            quest_list = data.get('quest_list', [])

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
                        print_timestamp(f"{Fore.YELLOW}Skipping Quest, Please do by Yourself")
                        time.sleep(1)  # Sleep for 1 second
                        continue
                
                # Achieve quests if not achieved
                if not is_achieved:
                    # Automatically achieve the quest without prompting
                    while True:
                        time.sleep(2)
                        achieve_response = self.achieve_quest(quest_id)
                        if achieve_response.status_code <= 210:
                            response = achieve_response.json()
                            time.sleep(2)
                            if response.get('msg') == "Success":
                                response = self.claim_quest(quest_id)
                                res = response.json()
                                if res.get('msg') == "Success":
                                    print_timestamp(f"{Fore.GREEN}Quest {quest_name} Achieved and Claimed Successfully{Style.RESET_ALL}")
                                    break

                    time.sleep(2)  # Sleep for 1 second


                if is_achieved and not is_claimed:
                    # Automatically claim the quest without prompting
                    claim_response = self.claim_quest(quest_id)
                    res = claim_response.json()
                    if res.get('msg') == "Success":
                        print_timestamp(f"{Fore.GREEN}Quest {quest_name} Achieved and Claimed Successfully{Style.RESET_ALL}")
                    time.sleep(2)  # Sleep for 1 second

            is_claimed = data.get('is_claimed')
            while True:
                if is_claimed == True:
                    time.sleep(2)
                    dats = self.claim_quest_lottery().json()
                    if dats.get('msg') == "Success":
                        print_timestamp(f"{Fore.GREEN}Claim reward quest done")
                    time.sleep(2)
                    data_quest = self.get_quest()
                    data = data_quest.get('data')
                    is_claimed = data.get('is_claimed')
                else:
                    break
    

    