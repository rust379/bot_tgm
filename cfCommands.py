import codeforces as cf_api
import time
import random
import hashlib
import urllib.request
import urllib.parse
import requests
import json
import tokens

def makeRequest(req):
    """Запрос на кф"""
    try:
        url = 'http://codeforces.com/api/' + req
        req = requests.get(url).json()    
        return req

    except Exception as e:
        return str(e)


def userRating(handle):
    """изменение рейтинга пользователя"""
    t = int(time.time())
    rand = str(random.randint(100000, 999999))
    cf_hash = rand + '/user.rating?handle=' + handle + '&time=' + str(t) 
    cf_hash = hashlib.sha512(cf_hash.encode('utf-8')).hexdigest()
    req = 'user.rating?handle=' + handle + '&time=' + str(t) + '&apiSig=' + rand + cf_hash     
    ret = makeRequest(req)
    ans = ""
    for i in ret['result']:
        ans += str(i['contestName']) + " " + str(i['oldRating']) + " -> " + str(i['newRating']) + " rank - " + str(i['rank']) + "\n"
    return ans

def curUserRating(*handles):
    """Текущий рейтинг пользователя"""
    t = int(time.time())
    rand = str(random.randint(100000, 999999))
    l = []
    for i in handles:
        l.append(i)
    l.sort()
    handle = 'handles='
    for i in l:
        handle += i + ';'
    cf_hash = rand + '/user.info?' + handle + '&time=' + str(t) 
    cf_hash = hashlib.sha512(cf_hash.encode('utf-8')).hexdigest()
    req = 'user.info?' + handle + '&time=' + str(t) + '&apiSig=' + rand + cf_hash     
    ret = makeRequest(req)
    ans = ""
    for i in ret['result']:
        ans += str(i['handle']) + "\n"
        ans += "rating:" + str(i['rating']) + "\n\n"
    return ans

def userInfo(*handles):
    """ Информация о польователях"""    
    t = int(time.time())
    rand = str(random.randint(100000, 999999))
    l = []
    for i in handles:
        l.append(i)
    l.sort()
    handle = 'handles='
    for i in l:
        handle += i + ';'
    cf_hash = rand + '/user.info?' + handle + '&time=' + str(t) 
    cf_hash = hashlib.sha512(cf_hash.encode('utf-8')).hexdigest()
    req = 'user.info?' + handle + '&time=' + str(t) + '&apiSig=' + rand + cf_hash     
    ret = makeRequest(req)
    ans = ""
    for i in ret['result']:
        ans += str(i['handle']) + "\n"
        ans += "name: " + str(i['firstName']) + " " +str(i['lastName']) + "\n"
        ans += "email: " + str(i['email']) + "\n"
        ans += "vk: " + str(i['vkId']) + "\n"
        ans += str(i['country']) + " " + str(i['city']) + "\n"
        ans += "organization: " + str(i['organization']) + "\n"
        ans += "contribution: " + str(i['contribution']) + "\n"
        ans += "rank:" + str(i['rank']) + " max rank: " + str(i['maxRank']) + "\n"
        ans += "rating:" + str(i['rating']) + " max rating: " + str(i['maxRating']) + "\n\n"
    return ans
    
def problemsetProblems(*tags):
    """ Получение задач по тегам"""    
    t = int(time.time())
    rand = str(random.randint(100000, 999999))
    l = []
    for i in tags:
        l.append(i)
    l.sort()
    tag = 'tags='
    for i in l:
        tag += i + ';'
    cf_hash = rand + '/problemset.problems?' + tag + '&time=' + str(t) 
    cf_hash = hashlib.sha512(cf_hash.encode('utf-8')).hexdigest()
    req = 'problemset.problems?' + tag + '&time=' + str(t) + '&apiSig=' + rand + cf_hash     
    ret = makeRequest(req)
    ans = ""
    for i in ret['result']['problems']:
        ans += str(i['contestId']) + " "
        ans += "name: " + str(i['name']) + " "
        ans += "index: " + str(i['index']) + " "
        ans += "type: " + str(i['type']) + " "  
        try:
            ans += "points: " + str(i['points']) + " "
        except Exception as e:
            pass
        ans += "tags: " + str(i['tags']) + "\n"
     #   ans += "Solved count: " + str(i['solvedCount']) + "\n"
    return ans

def contestListPublic(gym = 'false'):
    """Информация о доступных соревнованиях"""
    t = int(time.time())
    rand = str(random.randint(100000, 999999))
    cf_hash = rand + '/contest.list?gyme=' + gym + '&time=' + str(t) 
    cf_hash = hashlib.sha512(cf_hash.encode('utf-8')).hexdigest()
    req = 'contest.list?gym=' + gym + '&time=' + str(t) + '&apiSig=' + rand + cf_hash
    ret = makeRequest(req)
    ans = ""
    for i in ret['result']:
        ans += str(i['contestId']) + " "
        ans += "name: " + str(i['name']) + " "
        ans += "type: " + str(i['type']) + " "
        ans += "phase: " + str(i['phase']) + " "  
        ans += "durationSeconds: " + str(i['durationSeconds']) + " "
        #ans += "tags: " + str(i['tags']) + "\n"
     #   ans += "Solved count: " + str(i['solvedCount']) + "\n"
    return ans

def contestListPrivate(gym = 'false'):
    """Информация о доступных соревнованиях для пользователя"""
    t = int(time.time())
    rand = str(random.randint(100000, 999999))
    cf_hash = rand + '/contest.list?' + 'apiKey=' + tokens.api_key + '&gym=' + gym + '&time=' + str(t) + '#' + tokens.api_sec
    cf_hash = hashlib.sha512(cf_hash.encode('utf-8')).hexdigest()
    req = 'contest.list?gym=' + gym + '&apiKey=' + tokens.api_key + '&time=' + str(t) + '&apiSig=' + rand + cf_hash
    ret = makeRequest(req)
    ans = ""
    for i in ret['result']:
        ans += str(i['contestId']) + " "
        ans += "name: " + str(i['name']) + " "
        ans += "type: " + str(i['type']) + " "
        ans += "phase: " + str(i['phase']) + " "  
        ans += "durationSeconds: " + str(i['durationSeconds']) + " "
        #ans += "tags: " + str(i['tags']) + "\n"
        #ans += "Solved count: " + str(i['solvedCount']) + "\n"
    return ans
        
