from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import datetime

def get_sports_reference_games():
    driver_path = ChromeDriverManager().install()
    chrome_options = Options()
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-certificate-errors-spki-list")
    chrome_options.add_argument("--ignore-ssl-errors")
    browser = webdriver.Chrome(executable_path=driver_path, options = chrome_options)
    browser.maximize_window()
    date = datetime.date(2021, 3, 20)
    gameUrls = []
    while(date < datetime.date(2023, 4, 1)):
        browser.get("https://www.sports-reference.com/cbb/boxscores/index.cgi?month=" + str(date.month) + "&day=" + str(date.day) + "&year=" + str(date.year))
        print ("1")
        time.sleep(3.5)
        try:
            browser.find_element(By.XPATH, "//*[@id='content']/div[3]/div[2]/a").click()
        except:
            pass
        print ("2")
        time.sleep(3.5)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        print ("3")
        games = soup.find_all(class_="game_summary nohover gender-m")
        for game in games:
            with open("sports-reference_games.txt", "a") as f:
                try:
                    f.write(game.find(class_="right gamelink").find("a")["href"] + "\n")
                except TypeError:
                    pass
        date = date + datetime.timedelta(days=1)
        print (date)
        if (date.month == 5):
            date = datetime.date(date.year, 10, 1)


#After you already have the games from the above fcn
def get_sports_reference_stats():
    games = []
    with open('sports-reference_games.txt') as f:
        for line in f.readlines():
            if (line not in games):
                games.append(line)
    print (games)
    driver_path = ChromeDriverManager().install()
    chrome_options = Options()
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-certificate-errors-spki-list")
    chrome_options.add_argument("--ignore-ssl-errors")
    browser = webdriver.Chrome(executable_path=driver_path, options = chrome_options)
    browser.maximize_window()
    dict = {"Date":[],"Home":[],"Away":[],"Neutral":[],"Home Rtg":[],"Away Rtg":[],"Poss":[],"URL":[]}
    home_court_map = {}
    for game in games:
        browser.get("https://www.sports-reference.com/" + game)
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        if ("(Women)" in soup.find(class_="box").h1.text):
            continue
        location = soup.find(class_="scorebox_meta").find_all("div")[1].get_text()
        home = soup.find(id="div_four-factors").find("tbody").find_all("th")[1].a.text
        away = soup.find(id="div_four-factors").find("tbody").find_all("th")[0].a.text
        if (home not in home_court_map):
            home_court_map[home] = {}
        if (location not in home_court_map[home]):
            home_court_map[home][location] = 1
        else:
            home_court_map[home][location] += 1
        dict["Date"].append(game.split("boxscores/")[1][0:10])
        dict["Home"].append(home)
        dict["Away"].append(away)
        total_g = 0
        for key in home_court_map[home].keys():
            total_g += home_court_map[home][key]
        if (home_court_map[home][location] > total_g / 4 and total_g > 15):
            dict["Neutral"].append("F")
        elif (home_court_map[home][location] < total_g / 4 and total_g > 15):
            dict["Neutral"].append("T")
        else:
            dict["Neutral"].append("?")
        dict["Home Rtg"].append(float(soup.find(id="div_four-factors").find("tbody").find_all("tr")[1].find_all("td")[5].text))
        dict["Away Rtg"].append(float(soup.find(id="div_four-factors").find("tbody").find_all("tr")[0].find_all("td")[5].text))
        dict["Poss"].append(float(soup.find(id="div_four-factors").find("tbody").find_all("tr")[1].find_all("td")[0].text))
        dict["URL"].append(game)
        dfFinal = pd.DataFrame.from_dict(dict)
        dfFinal = dfFinal.drop_duplicates()
        dfFinal.to_csv('./efficiency_stats.csv', index = False)


get_sports_reference_stats()