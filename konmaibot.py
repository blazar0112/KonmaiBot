import random
import schedule
import time
from datetime import datetime
from enum import Enum
import threading
from selenium import webdriver

# change path to where you put chromedriver.exe
chrome_driver_path = R'D:\install\chromedriver_win32\chromedriver.exe'

class Strategy(Enum):
    Fixed = 0
    Random = 1

class Move(Enum):
    Rock = 1
    Paper = 2
    Scissors = 3

class CardMove(Enum):
    Left = 0
    Center = 1
    Right = 2

# you can change strategy to Strategy.Fixed or Strategy.Random
strategy = Strategy.Random
# you can change fixed move, only used when strategy is Strategy.Fixed
fixed_move = Move.Scissors
# you can change fixed card move, only used when strategy is Strategy.Fixed
fixed_card_move = CardMove.Right

# =================================================================
# Don't modify anything below
# =================================================================

options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options, executable_path=chrome_driver_path)
driver.implicitly_wait(5)

eagate_url = 'https://p.eagate.573.jp/index.html'
eapass_url = 'https://p.eagate.573.jp/gate/eapass/menu.html'
janken_url = 'https://p.eagate.573.jp/game/bemani/bjm2020/janken/index.html'
card_game_url = 'https://p.eagate.573.jp/game/bemani/wbr2020/01/card.html'

card_list = []
driver.get(eapass_url)

def setup():
    driver.get(eapass_url)
    select = webdriver.support.ui.Select(driver.find_element_by_name('eapasslist'))
    for option in select.options:
        card_list.append(option.text)
    print('card list', card_list)

    card_index_now_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[1]/div[1]/span[1]')
    index = int(card_index_now_element.text)-1

    ref_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div['+card_index_now_element.text+']/div/div[3]/div')
    if ref_element.is_displayed():
        raise Exception('default tab of eapass is not referencing card.')

    print('current referencing card =', card_list[index])

manual_execute_work = False

def switch_card(index):
    driver.get(eapass_url)
    time.sleep(3)
    select = webdriver.support.ui.Select(driver.find_element_by_name('eapasslist'))
    select.select_by_value(str(index))
    div_index = str(index+1)

    button_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div['+div_index+']/div/div[2]/button')
    if button_element.is_displayed():
        button_element.click()
        print('switch to card['+str(index)+']', card_list[index])
    else:
        print('try to switch to card['+str(index)+']', card_list[index], 'but card is already referenced.')
 
japanese_names = { Move.Rock:'グー', Move.Paper:'パー', Move.Scissors:'チョキ' }

def print_stamp(name):
    try:
        stamp_element = driver.find_element_by_xpath('//*[@id="inc-janken"]/div/div/p[2]/strong')
        print('Current', name, 'stamp =', stamp_element.text+'.')
    except:
        print('Cannot find', name, 'stamp count.')

def run_janken_bot():
    driver.get(janken_url)
    try:
        error_element = driver.find_element_by_xpath('//*[@id="error"]')
        print('Login error, manually login!')
        foo = input('Type anything after login to continue: ')
    except:
        pass

    try:
        move = fixed_move
        if strategy==Strategy.Random:
            move = random.choice(list(Move))
        select_element = driver.find_element_by_xpath('//*[@id="janken-select"]/div/a['+str(move.value)+']')
    except:
        print('Already selected janken move.')
        print_stamp('Janken')
        return

    select_url = select_element.get_attribute('href')
    print('select_url: ', select_element.get_attribute('href'))
    driver.get(select_url)
    print('Move selected as', move.name, '[JP:', japanese_names[move]+']')
    driver.get(janken_url)
    print_stamp('Janken')

def run_card_game_bot():
    driver.get(card_game_url)
    try:
        error_element = driver.find_element_by_xpath('//*[@id="error"]')
        print('Login error, manually login!')
        foo = input('Type anything after login to continue: ')
    except:
        pass

    try:
        card_move = fixed_card_move
        if strategy==Strategy.Random:
            card_move = random.choice(list(CardMove))
        card_element = driver.find_element_by_xpath('//*[@id="card'+str(card_move.value)+'"]')
        card_element.click()
    except:
        print('Already selected CardGame move.')

    print_stamp('CardGame')

def do_background_work():
    this_thread = threading.currentThread()
    def work():
        print('\n'+datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), 'running bots...')
        for index in range(0, len(card_list)):
            switch_card(index)
            time.sleep(5)
            run_janken_bot()
            run_card_game_bot()
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), 'work finished.')

    schedule.every().hour.do(work)
    work()
    global manual_execute_work
    while getattr(this_thread, 'do_run', True):
        schedule.run_pending()
        time.sleep(1)
        if manual_execute_work:
            work()
            manual_execute_work = False

thread = threading.Thread(target=do_background_work)
thread.start()

print('Konmai Bot: auto execute web games every hour')
print('enter anything after login to start bot!')
print('enter h to see commands.')
print('enter q to quit.')

while True:
    try:
        command = input(datetime.now().strftime('[%Y-%m-%d %H:%M:%S] '))
        if command.startswith('h'):
            print('command: h, help  : print command help\n'
                  '         w        : immediate execute work.\n'
                  '         q        : quit.')
        if command=='q':
            break
        if len(card_list)==0:
            setup()
        if command=='w':
            manual_execute_work = True
    except KeyboardInterrupt:
        break
    except Exception as e:
        print('Exception:', str(e))
    
driver.quit()

thread.do_run = False
thread.join()