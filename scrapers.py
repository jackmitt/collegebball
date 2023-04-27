from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import time
import datetime
from os.path import exists

class Database:
    def __init__(self, keys = []):
        self.df = pd.DataFrame()
        self.dict = {}
        for key in keys:
            self.dict[key] = []
        self.tempRow = []

    def getKeys(self):
        return (list(self.dict.keys()))

    def getCol(self, colName):
        return (self.dict[colName])

    def getLength(self):
        return (len(list(self.dict.keys())[0]))

    def getDict(self):
        return (self.dict)

    def getDataFrame(self):
        self.df = pd.DataFrame.from_dict(self.dict)
        return(self.df)

    def getCell(self, col, index):
        return (self.dict[col][index])

    def initDictFromCsv(self, path):
        self.dict = pd.read_csv(path, encoding = "ISO-8859-1").to_dict(orient="list")

    def addColumn(self, colName):
        self.dict[colName] = []

    def addCellToRow(self, datum):
        if (len(self.tempRow) + 1 > len(self.dict)):
            raise ValueError("The row is already full")
        else:
            self.tempRow.append(datum)

    def appendRow(self):
        if (len(self.tempRow) != len(self.dict)):
            raise ValueError("The row is not fully populated")
        else:
            for i in range(len(self.dict.keys())):
                self.dict[list(self.dict.keys())[i]].append(self.tempRow[i])
            self.tempRow = []

    def trashRow(self):
        self.tempRow = []

    def dictToCsv(self, pathName):
        self.df = pd.DataFrame.from_dict(self.dict)
        self.df = self.df.drop_duplicates()
        self.df.to_csv(pathName, index = False)

    def printRow(self):
        print(self.tempRow)

    def printDict(self):
        print(self.dict)

    def reset(self):
        self.tempRow = []
        self.dict = {}
        for key in list(self.dict.keys()):
            self.dict[key] = []

    def merge(self, B):
        for key in B.getKeys():
            if (key not in list(self.dict.keys())):
                self.dict[key] = B.getCol(key)

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

def realgm(year, month, day):
    A = Database(["Date","Home","Away","Neutral","Game_Type","Poss","h_ORtg","a_ORtg","h_eFG%","a_eFG%","h_TO%","a_TO%","h_OR%","a_OR%","h_FTR","a_FTR","h_FIC","a_FIC","url"])
    for a in ["h_","a_"]:
        for b in ["s_","r1_","r2_","r3_","r4_","l1_","l2_","l3_"]:
            for c in ["pg_","sg_","sf_","pf_","c_"]:
                for d in ["name","seconds","FGM-A","3PM-A","FTM-A","FIC","OReb","DReb","Ast","PF","STL","TO","BLK","PTS"]:
                    A.addColumn(a + b + c + d)
    driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path=driver_path, options = chrome_options)
    browser.maximize_window()
    urlRoot = "https://basketball.realgm.com/ncaa/scores/"
    if (not exists("./realgm_gameUrls.csv")):
        curDate = datetime.date(year, month, day)
        gameUrls = []
        while (curDate < datetime.date(2023, 4, 10)):
            browser.get(curDate.strftime(urlRoot + "%Y-%m-%d/All"))
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            all = soup.find(class_="large-column-left scoreboard")
            for t in all.find_all("table"):
                for h in t.find_all('a'):
                    #print (t.find_all("tr")[3].find("th").find("a")['href'])
                    if (h.has_attr("href") and "boxscore" in h['href']):
                        if (h['href'] not in gameUrls):
                            gameUrls.append(h['href'])
            curDate = curDate + datetime.timedelta(days=1)
            if (curDate.month == 5):
                curDate = datetime.date(curDate.year, 11, 1)
        save = {}
        save["urls"] = gameUrls
        dfFinal = pd.DataFrame.from_dict(save)
        dfFinal = dfFinal.drop_duplicates()
        dfFinal.to_csv("./realgm_gameUrls.csv", index = False)
    else:
        gameUrls = pd.read_csv("./realgm_gameUrls.csv", encoding = "ISO-8859-1")["urls"].tolist()

    counter = 0
    if (exists("./gameStatsNew.csv")):
        A.initDictFromCsv("./gameStatsNew.csv")
        scrapedGames = pd.read_csv('./gameStatsNew.csv', encoding = "ISO-8859-1")["url"].tolist()
        for game in scrapedGames:
            gameUrls.remove(game)
   # try:
    for game in gameUrls:
        time.sleep(5)
        browser.get("https://basketball.realgm.com" + game)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        A.addCellToRow(game.split("boxscore/")[1].split("/")[0])
        A.addCellToRow(soup.find_all(class_="boxscore-gamedetails")[0].find_all("a")[1].text)
        A.addCellToRow(soup.find_all(class_="boxscore-gamedetails")[0].find_all("a")[0].text)
        if ("Neutral Site" in soup.find_all(class_="boxscore-gamedetails")[0].get_text()):
            A.addCellToRow("True")
        else:
            A.addCellToRow("False")
        A.addCellToRow(soup.find_all(class_="boxscore-gamedetails")[0].find_all("strong")[1].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[1].find("tbody").find_all("tr")[0].find_all("td")[1].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[1].find("tbody").find_all("tr")[1].find_all("td")[2].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[1].find("tbody").find_all("tr")[0].find_all("td")[2].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[1].find_all("td")[1].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[0].find_all("td")[1].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[1].find_all("td")[2].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[0].find_all("td")[2].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[1].find_all("td")[3].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[0].find_all("td")[3].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[1].find_all("td")[4].text)
        A.addCellToRow(soup.find_all(class_="basketball force-table")[2].find("tbody").find_all("tr")[0].find_all("td")[4].text)
        A.addCellToRow(soup.find_all(class_="tablesaw compact tablesaw-swipe tablesaw-sortable")[1].find("tfoot").find_all("tr")[1].find_all("td")[8].text)
        A.addCellToRow(soup.find_all(class_="tablesaw compact tablesaw-swipe tablesaw-sortable")[0].find("tfoot").find_all("tr")[1].find_all("td")[8].text)
        A.addCellToRow(game)

        for z in ["h", "a"]:
            if (z == "h"):
                hdc = soup.find(class_="large-column-left").find_all("table")[1].find("tbody")
                hbs = soup.find_all(class_="tablesaw compact tablesaw-swipe tablesaw-sortable")[1].find("tbody")
            else:
                hdc = soup.find(class_="large-column-left").find_all("table")[0].find("tbody")
                hbs = soup.find_all(class_="tablesaw compact tablesaw-swipe tablesaw-sortable")[0].find("tbody")
            roles = ["s","r","r","r","r","l","l","l"]
            for tr in hdc.find_all("tr"):
                while (tr.find("strong").text == "Lim PT" and roles[0] == "r"):
                    for i in range(14*5):
                        A.addCellToRow(np.nan)
                    del roles[0]
                for td in tr.find_all("td"):
                    if (td["data-th"] != "Role"):
                        try:
                            curDude = td.find("a").text
                        except:
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            A.addCellToRow(np.nan)
                            continue
                        A.addCellToRow(curDude)
                        for p in hbs.find_all("tr"):
                            if (p.find("a").text == curDude):
                                A.addCellToRow(int(p.find_all("td")[4].text.split(":")[0]) * 60 + int(p.find_all("td")[4].text.split(":")[1]))
                                A.addCellToRow(p.find_all("td")[5].text)
                                A.addCellToRow(p.find_all("td")[6].text)
                                A.addCellToRow(p.find_all("td")[7].text)
                                A.addCellToRow(p.find_all("td")[8].text)
                                A.addCellToRow(p.find_all("td")[9].text)
                                A.addCellToRow(p.find_all("td")[10].text)
                                A.addCellToRow(p.find_all("td")[12].text)
                                A.addCellToRow(p.find_all("td")[13].text)
                                A.addCellToRow(p.find_all("td")[14].text)
                                A.addCellToRow(p.find_all("td")[15].text)
                                A.addCellToRow(p.find_all("td")[16].text)
                                A.addCellToRow(p.find_all("td")[17].text)
                                break
                del roles[0]
            for i in range(len(roles)*5*14):
                try:
                    A.addCellToRow(np.nan)
                except:
                    break


        A.appendRow()
        counter += 1
        if (counter % 10 == 1):
            A.dictToCsv("./gameStatsNew.csv")
    #except:
        #time.sleep(3)
        #browser.close()
        #realgm(2003, 11, 3)
    A.dictToCsv("./gameStatsNew.csv")
    browser.close()


realgm(2003, 11, 3)
