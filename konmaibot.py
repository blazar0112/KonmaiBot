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

eapass_url = 'https://p.eagate.573.jp/gate/eapass/menu.html'
janken_url = 'https://p.eagate.573.jp/game/bemani/bjm2020/janken/index.html'
card_game_url = 'https://p.eagate.573.jp/game/bemani/wbr2020/01/card.html'

japanese_names = { Move.Rock:'グー', Move.Paper:'パー', Move.Scissors:'チョキ' }
manual_execute_work = False

card_list = []
driver.get(eapass_url)

def setup():
    driver.get(eapass_url)
    time.sleep(3)
    list_element = driver.find_element_by_name('eapasslist')
    if list_element.is_displayed() is False:
        card_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div[7]/div/div[2]')
        card_list.append(card_element.text)
        print('current referencing card =', card_element.text)
        return

    select = webdriver.support.ui.Select(list_element)
    for option in select.options:
        card_list.append(option.text)
    print('card list', card_list)

    card_num_now_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[1]/div[1]/span[1]')
    index = int(card_num_now_element.text)-1

    print('current referencing card =', card_list[index])

def switch_card(index):
    driver.get(eapass_url)
    time.sleep(3)
    list_element = driver.find_element_by_name('eapasslist')
    if list_element.is_displayed():
        select = webdriver.support.ui.Select(list_element)
        select.select_by_value(str(index))
        div_index = str(index+1)
        button_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div['+div_index+']/div/div[2]/button')
    else:
        button_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div[2]/button')

    if button_element.is_displayed():
        button_element.click()
        print('switch to card['+str(index)+']', card_list[index])
    else:
        print('try to switch to card['+str(index)+']', card_list[index], 'but card is already referenced.')

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
        print('CardGame move selected:', card_move.name, 'card.')
    except:
        print('Already selected CardGame move.')

    print_stamp('CardGame')

def do_background_work():
    def work():
        print('\n'+datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), 'running bots...')
        try:
            if len(card_list)==0:
                setup()
                time.sleep(3)
            for index in range(0, len(card_list)):
                switch_card(index)
                time.sleep(5)
                #run_janken_bot()
                run_card_game_bot()
        except Exception as e:
            print('Exception in work thread:', str(e))
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), 'work finished.')

    schedule.every().hour.do(work).tag('work')

    this_thread = threading.currentThread()
    global manual_execute_work
    while getattr(this_thread, 'do_run', True):
        schedule.run_pending()
        time.sleep(1)
        if manual_execute_work:
            work()
            manual_execute_work = False

    schedule.clear('work')
    print('worker thread stopped.')

thread = threading.Thread(target=do_background_work)
thread.start()

print('Konmai Bot: auto execute web games every hour:')
print('enter anything after login to start bot!')
print('enter h to see commands.')
print('enter w to immediately execute work.')
print('enter r to restart thread if stuck.')
print('enter q to quit.')

while True:
    try:
        command = input(datetime.now().strftime('[%Y-%m-%d %H:%M:%S] '))
        if command.startswith('h'):
            print('command: h, help  : print command help\n'
                  '         w        : immediately execute work.\n'
                  '         r        : restart work thread.\n'
                  '         q        : quit.')
        if command=='q':
            break
        if command=='setup':
            setup()
        if command=='w':
            manual_execute_work = True
        if command=='r':
            thread.do_run = False
            thread.join()
            print('thread restarted.')
            thread = threading.Thread(target=do_background_work)
            thread.start()

        if command=='t':
            #card_element = driver.find_element_by_xpath('//*[@id="id_ea_common_content"]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div[7]/div/div[2]')
            #print('card =', card_element.text)
            print('list is visible = ', driver.find_element_by_name('eapasslist').is_displayed())

    except KeyboardInterrupt:
        break
    except Exception as e:
        print('Exception:', str(e))

driver.quit()

thread.do_run = False
thread.join()