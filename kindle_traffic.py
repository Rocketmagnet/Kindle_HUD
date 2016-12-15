# 
import os

def CheckPollenCache():
    print "Checking pollen cache"
    if os.path.exists("pollen_cache.json"):
        print "Pollen cache exists"
        with open("pollen_cache.json", "r") as f:
            pollenCache = json.loads(f.read())
            pollenCache[0] = datetime.datetime.strptime(pollenCache[0],'%Y%m%d')
            if pollenCache[0].date() < today:
                print "Pollen cache is old"
                return ""
            else:
                print "Pollen cache is current:", pollenCache[1]
                return pollenCache[1]
    else:
        print "Pollen cache doesn't exist"
        return ""

def WritePollenCache(pollenLevel):
    pollenCache = [datetime.date.today().strftime('%Y%m%d'), pollenLevel]
    print "Writing pollen cache:", pollenLevel
    with open("pollen_cache.json", 'w') as f:
        f.write(json.dumps(pollenCache))
    
            pollenInfo = CheckPollenCache()
            if pollenInfo == "":
                    WritePollenCache(pollenInfo)