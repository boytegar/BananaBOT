import random
from banana import Banana, print_timestamp
from colorama import Fore, Style, init
import time
import sys

def load_credentials():
    try:
        with open('query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query_id.txt tidak ditemukan.")
        return [  ]
    except Exception as e:
        print("Terjadi kesalahan saat memuat token:", str(e))
        return [  ]

def main():
    init(autoreset=True)
    delay = random.randint(14400, 14550)
    prints = """
    =========== t.me/sansxgroup ===========

"""
    ban = Banana()
    print(prints)
    while True:
        queries = load_credentials()
        
        start_time = time.time()
        assets = 0
        peels = 0
        for index, query in enumerate(queries):
            token = ban.login(query=query)
            time.sleep(2)
            get_user = ban.get_user_info(token=token)
            print_timestamp(
                f"{Fore.CYAN + Style.BRIGHT}[ {get_user['data']['username']} 🤖 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Peel {get_user['data']['peel']} 🍌 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}[ USDT {get_user['data']['usdt']} 🤑 ]{Style.RESET_ALL}"
            )
            assets += get_user['data']['usdt']
            peels += get_user['data']['peel']
            time.sleep(2)
            ban.clear_quest(token=token)
            time.sleep(2)
            ban.get_lottery_info(token=token)
            time.sleep(2)
            ban.get_banana_list(token=token)
            print_timestamp(f"{Fore.WHITE + Style.BRIGHT}=-={Style.RESET_ALL}" * 10)

        end_time = time.time()
        total = delay - (end_time-start_time)
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        print_timestamp(f"[ Total Assets : {assets} USDT | {peels} Peels ]")
        print(f"{Fore.YELLOW + Style.BRIGHT}[ {round(hours)} Hours {round(minutes)} Minutes {round(seconds)} Seconds Remaining To Process All Account ]{Style.RESET_ALL}", end="\r", flush=True)
        time.sleep(total)
        print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
    except KeyboardInterrupt:
        sys.exit(0)