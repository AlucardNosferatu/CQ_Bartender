import os
import sqlite3
from sklearn.linear_model import LinearRegression
from sklearn import datasets
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

def db_querry():
    path = os.getcwd()
    path += "\\data\\app\\moe.min.qa\\qav2.db"
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    sql = """
    SELECT answer
    FROM qa
    WHERE priority=3
    ORDER BY answer
    """
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    return result

def ing_seg(result):
    menu_list = []
    for item in result:
        temp = item[0].split('\r\n')
        name = temp[0].split('是由')[0]
        content = temp[0].split('是由')[1].split('调制')[0].split('加冰')[0].split('经过陈化')[0]
        conList = content.split('和')[0].split('、')
        conList.append(content.split('和')[1])
        conDict = {}
        for ing in conList:
            conDict[ing.split('份')[1].replace('量的','')] = ing.split('份')[0].replace('任意','-1')
        conList = []
        for key in ['Adelhyde','Bronson萃取液','Powdered Delta','Flanergide','Karmotrine']:
            if key in conDict.keys():
                pass
            else:
                conDict[key]="0"
            conList.append(int(conDict[key]))
        temp = [word2vec(name),conList]
        menu_list.append(temp)
        if name == "Zen Star":
            break
    return menu_list
    
def word2vec(word):
    word = word.lower()
    word = word.zfill(20)
    ascii_list = []
    for alphabet in word:
        ascii_list.append(ord(alphabet))
    return ascii_list


def fitting(index):
    data = ing_seg(db_querry())
    X = []
    y = []
    for item in data:
        X.append(item[0])
        y.append(item[1][index])
    X = pd.DataFrame(X)
    y = pd.DataFrame(y)
    lr = LinearRegression()
    lr.fit(X, y)
    s=pickle.dumps(lr)
    f=open('mbn_'+str(index)+'.txt','wb')
    f.write(s)
    f.close()
    
for i in range(0,5):
    fitting(i)
        







