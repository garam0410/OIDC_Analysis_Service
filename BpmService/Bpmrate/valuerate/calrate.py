#Ranking rate
from scipy.sparse import data
from valuerate.models import *
from django.db.models import Max, Min
import pandas as pd
import seaborn as sb
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import preprocessing
from sqlalchemy import create_engine
import schedule
import time
import threading
import random
import datetime as dt


# 평균 계산
def calaver():

    print("---------------")
    print("cal")
    re = "calaver success"
    
    try:
        
        #mid 전체 호출
        midMx = Movieinfo.objects.values('mid')
        
        for i in range(0 , len(midMx)):
            
            #nmid = 현재 영화의 mid와 mid = nmid 인 영화의 러닝타임
            nmid = midMx[i]['mid']
            runti = Movieinfo.objects.filter(mid = nmid).aggregate(runningtime = Max('runningtime'))

            #초기화
            avlist = [0 for row in range(runti['runningtime'])]
            result = []

            #Data 존재 Check
            datacheck = [0 for row in range(runti['runningtime'])]
            datacheck = Bpmdata.objects.filter(mid = nmid).values_list('bpm', flat=True)

            #최소 10명이 시청 했을 시 분석 시작
            if(len(datacheck) > 10):
                
                #mid = i 인 전체 데이터 호출
                result = Bpmdata.objects.filter(mid = nmid).values('bpm')
                pnumb = len(result)
                
                #slist라는 2차원 배열 선언 (행은 측정자 수, 열은 영화 상영시간)
                slist = [[0 for col in range(runti['runningtime'])] for row in range(pnumb)]
                
                #slist라는 2차원 배열에 mid = i인 영화의 개인의 bpm 저장
                for j in range(0, pnumb):

                    slist.insert(j , result[j]['bpm'].split(','))
                
                #sumval 변수에 각 초당 심박수 저장 후 avlist 평균으로 저장하여 db에 insert
                for k in range(0, runti['runningtime']):

                    sumval = 0
                    
                    for l in range(0, pnumb):

                        sumval += int(slist[l][k])
                        
                    avlist[k] = sumval / pnumb
                
                
                #평균 수치 전부 삭제 후 새로이 저장
                m = []
                m = Moviegraph.objects.filter(mid=nmid).all()
                m.delete()
                
                for j in range(0, len(avlist)):

                    mi = Moviegraph(mid = Movieinfo.objects.get(mid=nmid), bpm = avlist[j])
                    mi.save()

    except Exception as e:

        print(e)
        print("calaver failed")
        print("----------------")

    print(dt.datetime.now())
    print(re)
    print("----------------")

    return
# BPM 최댓값, 최솟값
def Mdata():

    print("----------------")
    print('mda')
    re = "Mdata Success"

    try:

        #mid
        midMx = Movieinfo.objects.values('mid')
        
        for i in range(0, len(midMx)):
            
            #nmid = 현재 영화의 mid와 mid = nmid 인 영화의 러닝타임
            nmid = midMx[i]['mid']
            runti = Movieinfo.objects.filter(mid = nmid).aggregate(runningtime = Max('runningtime'))

            datacheck = Bpmdata.objects.filter(mid = nmid).values_list('bpm', flat=True)

            #datacheck 의 길이를 통해 DB에 bpm 데이터가 존재할 경우 실행.
            if(len(datacheck) > 0):
                
                #mid = nmid 인 영화의 bpm 데이터
                rdata = Bpmdata.objects.filter(mid = nmid).values('bpm')
                pnumb = len(rdata)

                # 행 = 측정자 수, 열 = 상영시간 을 가지는 2차원 배열 초기화
                flist = [[0 for col in range(runti['runningtime'])] for row in range(pnumb)]

                # 값 저장용 1차원 배열
                singdlist = []

                # 2차원 배열에 bpm 정보를 전부 split해서 저장
                for j in range(0, pnumb):
            
                    flist.insert(j , rdata[j]['bpm'].split(','))

                # 생성된 2차원 배열 값을 1차원 배열에 전부 저장
                for k in range(0, pnumb):
                    for l in range(0, runti['runningtime']):
                        singdlist.append(int(flist[k][l]))
                
                # max, min method 통해 1차원 배열에서 최댓값, 최솟값 산출
                MaxVal = max(singdlist)
                MinVal = min(singdlist)
                
                # Model orm을 통해 db에 최댓값, 최솟값 저장
                mi = Movieinfo.objects.get(mid = nmid)
                mi.bmax = MaxVal
                mi.bmin = MinVal
                mi.save()

    except Exception as e:

        print(e)
        print("Mdata failed")
        print("----------------")

    print(dt.datetime.now())
    print(re)
    print("----------------")

    return 
    
# 클러스터링
def cluster():

    print("----------------")
    print('clu')
    re = "cluster Success"
    
    try:
        
        
        engine = create_engine('mysql+pymysql://root:bpmservice@118.67.132.152/bpm', convert_unicode = True)
        conn = engine.connect()
        

        #mid 
        midMx = Movieinfo.objects.values('mid')
        

        for i in range(0, len(midMx)):
            
            
            #nmid = 현재 영화의 mid와 mid = nmid 인 영화의 러닝타임
            nmid = midMx[i]['mid']
            runti = Movieinfo.objects.filter(mid = nmid).aggregate(runningtime = Max('runningtime'))

            #점수 계산용 변수
            score = 0

            #mid = nmid 인 영화의 사람 수
            pcount = Bpmtest.objects.filter(mid = nmid).values_list('tid')
            pnumb = len(pcount)

            #BPMDATA 테이블 전체 호출
            fdata = pd.read_sql_table('BPMDATA', conn)

            #MID = nmid인 조건부 데이터 전처리
            mdata = fdata[(fdata['MID'] == nmid)]
            bpmsplit = mdata["BPM"].str.split(',')
            
            print("split")
        
            InsBpmList = [[0 for col in range(runti['runningtime'])] for row in range(pnumb)]
            AvList = [0 for row in range(pnumb)]
            

            for t in range(0, pnumb):
                sumvar = 0
                for y in range(0, runti['runningtime']):
                    
                    InsBpmList[t][y] = int(bpmsplit[t][y])

                    sumvar += InsBpmList[t][y]

                AvList[t] = sumvar / pnumb

            
            fixdata = pd.DataFrame(AvList, columns=['bpm'])
            
            print(fixdata.head)
            points = fixdata.values
            kmeans= KMeans(n_clusters=3)
            kmeans.fit(points)
            kmeans.cluster_centers_
            kmeans.labels_
            fixdata['cluster'] = kmeans.labels_
            
            print(kmeans.cluster_centers_)
            CentA = int(kmeans.cluster_centers_[0])
            CentB = int(kmeans.cluster_centers_[1])
            CentC = int(kmeans.cluster_centers_[2])

            for p in range(0, pnumb):

                dA = int(bpmsplit[p][0]) - CentA
                dB = int(bpmsplit[p][0]) - CentB
                dC = int(bpmsplit[p][0]) - CentC

                disList = [ dA, dB, dC]
                NearData = min(disList)

                if NearData == dA:

                    for a in range(0, runti['runningtime']):
                        if int(bpmsplit[p][a]) > 1.2 * CentA:
                            score += 1
                elif NearData == dB:

                    for a in range(0, runti['runningtime']):
                        if int(bpmsplit[p][a]) > 1.2 * CentB:
                            score += 1
                elif NearData == dC:

                    for a in range(0, runti['runningtime']):
                        if int(bpmsplit[p][a]) > 1.2 * CentC:
                            score += 1

            rpoint = score / pnumb
            
            mi = Scoring.objects.get(mid = nmid)
            mi.score = rpoint
            mi.save()

            
    except Exception as e:

        print(e)
        print("cluster failed")
        print("----------------")
    
    print(dt.datetime.now())
    print(re)
    print("----------------")

    return 

# Score에 따른 랭킹 지정
def rating():

    print("----------------")
    print('rat')
    re = "rating Success"

    try:
        
        # Scoring에 존재하는 데이터만 랭킹 지정
        ScoreList = Scoring.objects.order_by('mid').all().values_list('score', flat=True)
        MidList = Scoring.objects.order_by('mid').all().values_list('mid', flat=True)
        DataList = [[0 for col in range(2)] for row in range(len(MidList))] 

        
        # mid에 해당하는 score를 가진 DataList 생성
        for p in range(0, len(ScoreList)):
            DataList[p] = [int(MidList[p]), int(ScoreList[p])]
        
        # score를 기준으로 정렬
        DataList = sorted(DataList, key = lambda x: -x[1])

        # 기존의 랭킹 데이터 삭제
        m = Movierank.objects.all()
        m.delete()

        # 순위에 맞게 db 삽입
        for i in range(0, len(MidList)):

            mi = Movierank(mid = Movieinfo.objects.get(mid = DataList[i][0]) , rank = i+1)
            mi.save()
        
        
    except Exception as e:

        print(e)
        print("rating failed")
        print("----------------")
    
    print(dt.datetime.now())
    print(re)
    print("----------------")

    return 

# UID의 연령대에 따른 랜덤추천
def reccomand(x):

    print("----------------")
    print('rec')
    re = "reccomand Success"

    # uid parameter를 받아와 int로 초기화
    intx = int(x)

    # 받아온 uid의 나이 인 uage 호출
    uinfo = Userinfo.objects.filter(uid = intx).values('uage')

    # 호출한 uage를 int로 초기화 해준 변수 age
    age = int(uinfo[0]['uage'])

    # 데이터 처리용 list, dict
    rlist = []
    mlist = []
    recmid = []
    rslist = []
    firecmid = []
    firectit = {}
    result = []


    try:

        # 연령대 별로 구분 해놓은 alevel 값
        alevel = 0

        if(10 < age < 20):

            alevel = 1

        elif(20 < age < 30):

            alevel = 2

        elif(30 < age < 40):

            alevel = 3

        elif(40 < age < 50):

            alevel = 4

        elif(50 < age < 60):

            alevel = 5

        elif(60 < age < 70):

            alevel = 6

        
        # 구분해놓은 alevel 즉 연령대에 해당하는 다른 유저 10명의 시청목록 호출
        if(alevel == 1):

            recuid = Userinfo.objects.filter(uage__range=(10, 20)).values('uid')
            
            
            for a in range(0, len(recuid)):
                rslist.append(recuid[a]['uid'])

            rlist = random.sample(rslist, 10)
            
            
            for i in range(0, 10):

                mlist = Bpmtest.objects.filter(uid = rlist[i]).values('mid')
                
                for j in range(0, len(mlist)):
                    recmid.append(mlist[j]['mid'])
        
        elif(alevel == 2):
    
            recuid = Userinfo.objects.filter(uage__range=(20, 30)).values('uid')
            
            
            for a in range(0, len(recuid)):
                rslist.append(recuid[a]['uid'])

            
            rlist = random.sample(rslist, 10)
            
            
            for i in range(0, 10):

                mlist = Bpmtest.objects.filter(uid = rlist[i]).values('mid')
                
                for j in range(0, len(mlist)):
                    recmid.append(mlist[j]['mid'])
        
        elif(alevel == 3):
    
            recuid = Userinfo.objects.filter(uage__range=(30, 40)).values('uid')
            
            
            for a in range(0, len(recuid)):
                rslist.append(recuid[a]['uid'])

            rlist = random.sample(rslist, 10)
            
            
            for i in range(0, 10):

                mlist = Bpmtest.objects.filter(uid = rlist[i]).values('mid')
                
                for j in range(0, len(mlist)):
                    recmid.append(mlist[j]['mid'])

        elif(alevel == 4):
    
            recuid = Userinfo.objects.filter(uage__range=(40, 50)).values('uid')
            
            
            for a in range(0, len(recuid)):
                rslist.append(recuid[a]['uid'])

            rlist = random.sample(rslist, 10)
            
            
            for i in range(0, 10):

                mlist = Bpmtest.objects.filter(uid = rlist[i]).values('mid')
                
                for j in range(0, len(mlist)):
                    recmid.append(mlist[j]['mid'])

        elif(alevel == 5):
    
            recuid = Userinfo.objects.filter(uage__range=(50, 60)).values('uid')
            
            
            for a in range(0, len(recuid)):
                rslist.append(recuid[a]['uid'])

            rlist = random.sample(rslist, 10)
            
            
            for i in range(0, 10):

                mlist = Bpmtest.objects.filter(uid = rlist[i]).values('mid')
                
                for j in range(0, len(mlist)):
                    recmid.append(mlist[j]['mid'])

        elif(alevel == 6):
    
            recuid = Userinfo.objects.filter(uage__range=(60, 70)).values('uid')
            
            
            for a in range(0, len(recuid)):
                rslist.append(recuid[a]['uid'])

            rlist = random.sample(rslist, 10)
            
            
            for i in range(0, 10):

                mlist = Bpmtest.objects.filter(uid = rlist[i]).values('mid')
                
                for j in range(0, len(mlist)):
                    recmid.append(mlist[j]['mid'])

        # 호출한 10명의 시청목록을 중복 제거 후 랜덤으로 5개 산출
        myset = set(recmid)
        recmid = list(myset)
        firecmid = random.sample(recmid, 5)
        
        # 웹페이지 전달을 위한 JSON 형태의 배열 생성
        for p in range(0, 5):
            
            ti = Movieinfo.objects.filter(mid = firecmid[p]).values("title")
            firectit = {"title" : ti[0]["title"]}
            result.append(firectit)
            
    except Exception as e:

        print(e)
        print("rating failed")
        print("----------------")

    print(dt.datetime.now())
    print(re)
    print("----------------")

    return result




# schedule.every().day.at("00:00").do(Mdata)
# schedule.every().day.at("01:00").do(calaver)
# schedule.every().day.at("02:00").do(cluster)
# schedule.every().day.at("09:00").do(rating)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

