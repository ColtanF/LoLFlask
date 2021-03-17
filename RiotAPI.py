#! python3

import os
import requests
import json
import sys
import io

# For the print() statements. Default text wrapper is not UTF-8
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="UTF-8")

# constants
apiKey = "" # Will need to generate a new API key once a day from Riot's site
summName = "Coltan66"
domainUrl = "https://na1.api.riotgames.com"
summonerV4SummName = "/lol/summoner/v4/summoners/by-name/"
matchV4MatchList = "/lol/match/v4/matchlists/by-account/"
matchV4MatchId = "/lol/match/v4/matches/"
spectator_v4_bySumm = "/lol/spectator/v4/active-games/by-summoner/"
leagueEntries_bySumm = "/lol/league/v4/entries/by-summoner/"
champDict = {}
queueDict = {}
queueTypesMap = {
  420: "RANKED_SOLO_5x5",
  440: "RANKED_FLEX_SR"
}

class summInfo:
    def __init__(self, champ, summName, rankTier, rankDiv, spell1, spell2, profIcon):
        self.champ = champ
        self.summName = summName
        self.rankTier = rankTier
        self.rankDiv = rankDiv
        self.spell1 = spell1
        self.spell2 = spell2
        self.profIcon = str(profIcon)

    def setRankTier(self, rankTier):
        self.rankTier = rankTier

    def setRankDiv(self, rankDiv):
        self.rankDiv = rankDiv

    def toString(self):
        return "Name: " + self.summName + ", champ: " + self.champ + ""

class matchInfo:
    def __init__(self, summoners, gameMode, queueType):
        self.summoners = summoners
        self.gameMode = gameMode
        self.queueType = queueType


def readInChamps():
    with open(os.getcwd() + '\lolChamps.json', encoding="utf8") as f:
        leagueChamps = json.load(f)
    for champ in leagueChamps["data"]:
        champDict[leagueChamps["data"][champ]["key"]] = champ

def readInQueueTypes():
    with open(os.getcwd() + '\queues.json', encoding="utf8") as f:
        queueConsts = json.load(f)
    for qItem in queueConsts:
        queueDict[qItem["queueId"]] = qItem

def retrieveData(requestType,params):
    url = domainUrl + requestType + params[0] + "?api_key=" + apiKey
    response = requests.get(url)
    return json.loads(response.text)

def retrieveSummonerInfo(match):
    summs = []
    if ('status' in match and match['status']['status_code'] == 404):
        return summs

    gameMode = match["gameMode"]
    queueType = queueDict[match["gameQueueConfigId"]]["description"]

    for count, p in enumerate(match["participants"]):
        rankedData = retrieveData(leagueEntries_bySumm, [p["summonerId"]])
        print(rankedData)
        with open('rankInfo.json', 'w') as json_file:
            json.dump(rankedData, json_file)

        summ = summInfo(champDict[str(p["championId"])], p['summonerName'], "", "",
                p["spell1Id"], p["spell2Id"], p["profileIconId"])
        rankStr = "Unranked"
        if len(rankedData) > 0:
            for r in rankedData:
                if r['queueType'] == queueTypesMap[420]:
                    rankStr = r["tier"] + " " + r["rank"]
                    summ.setRankTier(r["tier"].title())
                    summ.setRankDiv(r["rank"])
        if summ.rankTier == "":
            summ.setRankTier("Unranked")
        summs.append(summ)
    return matchInfo(summs, gameMode, queueType)

def getSummMatchData(accountId):
    return retrieveData(matchV4MatchList, [accountId])

def getMatch(gameId):
    return retrieveData(matchV4MatchId, [gameId])

def search(name):
    readInChamps()
    readInQueueTypes()

    print("Searching for " + str(name))
    summ_json_data = retrieveData(summonerV4SummName,[name])
    print(summ_json_data)
    if "accountId" not in summ_json_data:
        return None
    encAccountId = summ_json_data["accountId"]
    summId = summ_json_data["id"]

    currMatch = retrieveData(spectator_v4_bySumm, [summId])
    print(currMatch)


    return retrieveSummonerInfo(currMatch)
