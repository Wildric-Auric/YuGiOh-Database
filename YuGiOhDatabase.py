import sqlite3 as sql
import requests
from threading import Thread
from html import unescape
from shutil import copyfileobj

namesPage = 'https://www.yugioh.com/cards?page='
pageNum = 145
fandomIds = 'https://yugioh.fandom.com/wiki/Special:SearchByProperty?property=Database+ID&value='
start = 4007



def setDatabaseNames(pageNum, namesPage):
    COUNT = 0
    with sql.connect("sql.db") as connexion:
        cursor = connexion.cursor()
        for i in range(1, pageNum+1):
            pageRes = requests.get(namesPage + str(i)).text
            while 1: 
                findKey = pageRes.find("<strong>")
                if findKey == -1:
                    break
                lastIndex = pageRes.find("<", findKey+8)
                cardName = pageRes[findKey+8:lastIndex]
                pageRes = pageRes[lastIndex::]
                sqlReq = 'INSERT INTO YuGiOhDB(CardName) VALUES("{}");'.format(cardName);
                cursor.execute(sqlReq)
                COUNT +=1
                print(COUNT)
       #response = cursor.fetchall()
    connexion.close()
    

def setDataBaseNamesFromFandom(page):
    COUNT = 0
    i = 4007
    with sql.connect("sql.db") as connexion:
        cursor = connexion.cursor()
        while 1:
                previous = i
                pageRes = requests.get(page + str(i)).text
                start = pageRes.find("List of results")
                if start == -1:
                    break
                end = pageRes.find("</div>", start + 14)
                pageRes = (pageRes[start+14:end])
                start = ""
                if len(str(i)) == 4: end = pageRes.find(str(i)[0]+","+str(i)[1::]) 
                else: end = pageRes.find(str(i)[0:2]+","+str(i)[2::])  
                pageRes = pageRes[end::]
                while 1:
                    start = pageRes.find("title=")
                    if start == -1:
                        start = pageRes.find("(")
                        end = pageRes.find(")", start)
                        try:
                            i = int((pageRes[start+1: end]).replace(",", ""))
                        except: print(pageRes)
                        break
                    
                    end = pageRes.find(">", start +6)
                    cardName = pageRes[start+6:end]
                    pageRes = pageRes[end+1::]
                    
                    if "l:B" not in cardName: 
                        sqlReq = 'INSERT INTO YuGiOhDB(CardName) VALUES({});'.format(cardName);
                        cursor.execute(sqlReq)
                        COUNT +=1
                        print(COUNT)

                if i == previous: break

    
    connexion.close()
    
def addItem(id = False):
        COUNT = 0
        cardLinkPrefix = "https://yugioh.fandom.com/wiki/"
        with sql.connect("sql.db") as connexion:
            cursor = connexion.cursor()
            sqlReq = "SELECT CardName FROM YuGiOhDB"
            cursor.execute(sqlReq)
            lis = cursor.fetchall()
            L,lis1,lis2,lis3,lis4 = [],[],[],[],[]
            
            def iterationThread(start,end,l):
                COUNT =0
                for j in range(start, end):
                    i = lis[j]
                    cardName = "_".join((unescape(i[0])).split())
                    pageRes = requests.get(cardLinkPrefix + cardName).text
                    key = pageRes.find("Passcode/")
                    if key ==-1:
                        print("Can't find id for " +str(cardName))
                        l.append(0)
                        continue
                    key+=9
                    try:
                        idCode = int(pageRes[key:pageRes.find('"', key)])
                    except Exception as ex:
                        l.append(0)
                        continue
                    l.append(idCode)
                    COUNT +=1
                    print(COUNT)
            t1 = Thread(target=iterationThread, args=(0,3000,lis1))
            t2 = Thread(target=iterationThread, args=(3000,6000,lis2))
            t3 = Thread(target=iterationThread, args=(6000,9000,lis3))
            t4 = Thread(target=iterationThread, args=(9000,len(lis),lis4))
            t1.start()
            t2.start()
            t3.start()
            t4.start()
            t1.join()
            t2.join()
            t3.join()
            t4.join()
            L = lis1 + lis2 + lis3 + lis4
            for j in range(len(lis)):
                 i = lis[j]
                 idCode = L[j]
                 sqlReq = ' UPDATE YuGiOhDB  SET id = {}    WHERE CardName = "{}"'.format(idCode,i[0])
                 cursor.execute(sqlReq)
     
def donwloadImages():     
    with sql.connect("sql.db") as connexion:
        cursor = connexion.cursor()
        sqlReq = "SELECT id FROM YuGiOhDB"
        cursor.execute(sqlReq)
        lis = cursor.fetchall()
        print(len(lis))
    def iterationThread(start, end):
        for i in range(start, end):
            cardId = (lis[i])[0]
            try:
                if cardId != 0:
                    response = requests.get("https://ygoprodeck.com/pics/{}.jpg".format(cardId), stream=True)
                    with open('Card Images/{}.png'.format(cardId), 'wb') as out_file:
                        copyfileobj(response.raw, out_file)
                    del response
            except Exception as ex:
                print(ex)
                continue
    # t1 = Thread(target=iterationThread, args=(0,3000))
    # t2 = Thread(target=iterationThread, args=(3000,6000))
    # t3 = Thread(target=iterationThread, args=(6000,9000))
    # t4 = Thread(target=iterationThread, args=(9000,len(lis)))
    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()
    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()
    
    
donwloadImages()
#addItem()
#setDatabaseNames(pageNum, namesPage)
#setDataBaseNamesFromFandom(fandomIds)