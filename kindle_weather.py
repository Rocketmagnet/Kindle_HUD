# This file deals with downloading and interpreting JSON weather data from Wunderground.
# 
# 
# 
# 
# 
# 
# 
# 



import json
import time
from datetime import date
from datetime import time
import datetime
import urllib
import png

"""
 0   0
 1   1
 3   2
 5   3
 7   3-4
10   4
12   5
15   5-6
19   6-7
23   7
27   
31   


"""


conditionsNiceness=[0] * 25
conditionsNiceness[ 9] =  0	# Blowing Snow	
conditionsNiceness[22] =  1	# Chance of Ice Pellets	
conditionsNiceness[23] =  2	# Ice Pellets	
conditionsNiceness[24] =  3	# Blizzard
conditionsNiceness[16] =  4	# Flurries	
conditionsNiceness[19] =  5	# Snow Showers	
conditionsNiceness[21] =  6	# Snow	
conditionsNiceness[20] =  7	# Chance of Snow	
conditionsNiceness[18] =  8	# Chance of Snow Showers	
conditionsNiceness[15] =  9	# Thunderstorm	
conditionsNiceness[ 8] = 10 # Very Cold	
conditionsNiceness[14] = 11	# Chance of a Thunderstorm	
conditionsNiceness[13] = 12	# Rain	
conditionsNiceness[11] = 13	# Showers	
conditionsNiceness[12] = 14	# Chance of Rain	
conditionsNiceness[10] = 15	# Chance of Showers	
conditionsNiceness[ 6] = 16	# Foggy
conditionsNiceness[ 4] = 17	# Cloudy	
conditionsNiceness[ 3] = 18	# Mostly Cloudy	
conditionsNiceness[ 2] = 19	# Partly Cloudy	
conditionsNiceness[ 5] = 20	# Hazy	
conditionsNiceness[ 7] = 21	# Very Hot	
conditionsNiceness[ 1] = 22	# Clear

windDirections = {'N':0, 'NNW':1, 'NW':2, 'WNW':3, 'W':4, 'WSW':5, 'SW':6, 'SSW':7, 'S':8, 'SSE':9, 'SE':10, 'ESE':11, 'E':12, 'ENE':13, 'NE':14, 'NNE':15}

def max(a, b):
    if (b>a):
        return b
    else:
        return a

def min(a, b):
    if (b<a):
        return b
    else:
        return a
        
def DateLessOrEqual(dateAndTime1, dateAndTime2):
    if (dateAndTime1[0] >  dateAndTime2[0]):
        return 0
    if (dateAndTime1[0] <  dateAndTime2[0]):
        return 1
    if (dateAndTime1[1] <= dateAndTime2[1]):
        return 1
    
    return 0
    
        
# The PeriodConditions class is used to filter the weather data for a particular time period.
# Typical time periods would be today morning, or the weekend.
# 
# The class extracts useful info for the time period, like:
# - Maximum UVI, humidity
# - Windspeed distribution
# - A suitable icon to represent this time period
#
class PeriodConditions:
    
    def __init__(self, startTime, endTime):
        self.worstCondition = 0
        self.niceness       = 0
        self.name           = ""
        self.startTime      = startTime
        self.endTime        = endTime
        self.windSpeed      = 0
        self.uvi            = 0
        self.humidity       = 0
        self.feelsLike      = 99
        self.pop            = 0
        self.sky            = 0
        self.qpf            = 0
        self.snow           = 0
        self.minTemp        = 99
        self.maxTemp        = -99
        self.dayName        = "unknown"
        self.hour           = -1
        self.windInfo       = [[999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0], [999,0]]
        
    def UpdateFromDictionary(self, i):
        year          = int(i['FCTTIME']['year'])
        month         = int(i['FCTTIME']['mon'])
        dayOfMonth    = int(i['FCTTIME']['mday_padded'])
        hour          = int(i['FCTTIME']['hour_padded'])
        condition     = int(i['fctcode'])
        temp          = eval(i['temp']['metric'])
        conditions    = i['wx']
        conditionName = i['condition']
        windSpeed     = eval(i['wspd']['metric'])
        windDir       = i['wdir']['dir']
        windDirNum    = windDirections[windDir]
        uvi           = eval(i['uvi'])
        humidity      = eval(i['humidity'])
        feelsLike     = eval(i['feelslike']['metric'])
        qpf           = eval(i['qpf']['metric'])
        snow          = eval(i['snow']['metric'])
        pop           = eval(i['pop'])
        sky           = eval(i['sky'])

        dayName = i['FCTTIME']['weekday_name_unlang']
        
        thisDateTime  = [date(year, month, dayOfMonth), time(hour,0,0)]
        niceness      = conditionsNiceness[condition]
        
        
        if (self.hour == -1):
            self.hour = datetime.datetime.today().hour + 1
        
        
        # Is the date between the start and end times?
        if (DateLessOrEqual(self.startTime, thisDateTime)) & (DateLessOrEqual(thisDateTime, self.endTime)):
            
            if (self.name == "") | (niceness < self.niceness):
                self.niceness       = niceness
                self.worstCondition = condition
                self.name           = conditionName
                
            self.windSpeed  = max(self.windSpeed, windSpeed)
            self.uvi        = max(self.uvi,       uvi)              # Ultraviolet light index
            self.humidity   = max(self.humidity,  humidity)
            self.feelsLike  = min(self.feelsLike, feelsLike)        # Temperature accounting for wind chill
            self.pop        = max(self.pop,       pop)              # Probability of Precipitation (rain or snow)
            self.sky        = max(self.sky,       sky)              # Cloud cover
            self.qpf       += qpf
            self.snow      += snow
            self.maxTemp    = max(self.maxTemp, temp)
            self.minTemp    = min(self.minTemp, temp)
            self.dayName    = dayName
            self.windInfo[windDirNum][0] = min(self.windInfo[windDirNum][0], windSpeed)
            self.windInfo[windDirNum][1] = max(self.windInfo[windDirNum][1], windSpeed)
            
    def Print(self):
        print("worstCondition:", self.worstCondition)
        print("niceness      :", self.niceness      )
        print("name          :", self.name          )
        print("startTime     :", self.startTime     )
        print("endTime       :", self.endTime       )
        print("windSpeed     :", self.windSpeed     )
        print("uvi           :", self.uvi           )
        print("humidity      :", self.humidity      )
        print("feelsLike     :", self.feelsLike     )
        print("pop           :", self.pop           )
        print("qpf           :", self.qpf           )
        print("snow          :", self.snow          )
        print("minTemp       :", self.minTemp       )
        print("maxTemp       :", self.maxTemp       )
        print(" ")
    
    
            
# This function downloads the weather, then filters the data to extract 
# information about various useful time periods, like this morning, this evening, etc.
#         
# source can be either "httpRequest" to use urllib, or "wget" to use wget.
# location would be "UK/London.json" for london
# 
def FetchWeatherForecast(source, location):

    if (source == "httpRequest"):
        
        try:
            print "Trying to fetch weather online using urllib"
            response      = urllib.urlopen("http://api.wunderground.com/api/f912ab4e1aac3427/hourly10day/q/" + location)
            weatherJSON   = response.read()
            weatherData   = json.loads(weatherJSON.decode('utf8'))
            print "Success, caching"
            cache = open("forecast_cache.json", 'w')
            cache.write(weatherJSON)
            urlReadFailed = False
        except:
            print "Failed, loading from cache"
            response    = open("forecast_cache.json", 'r')
            print "reading"
            weatherJSON = response.read()
            print "Parsing"
            weatherData = json.loads(weatherJSON.decode('utf8'))
            print "OK"
            
            
    elif (source == "wget"):
        print "Trying to fetch weather online using wget"
        os.system("wget -O hourly_forecast.json http://api.wunderground.com/api/f912ab4e1aac3427/hourly/q/" + location)
        weatherFile = open("hourly_forecast3.json", 'r')        
        weatherJSON = weatherFile.read()
        weatherData = json.loads(weatherJSON)
    else:
        print "Loading weather from", source
        weatherFile = open(source, 'r')        
        weatherJSON = weatherFile.read()
        weatherData = json.loads(weatherJSON)

    year       = int(weatherData['hourly_forecast'][0]['FCTTIME']['year'])
    month      = int(weatherData['hourly_forecast'][0]['FCTTIME']['mon'])
    dayOfMonth = int(weatherData['hourly_forecast'][0]['FCTTIME']['mday_padded'])
    firstHour  = int(weatherData['hourly_forecast'][0]['FCTTIME']['hour_padded'])
    
    day1Date = date(year,month,dayOfMonth)
    day2Date = day1Date + datetime.timedelta(1)
    day3Date = day1Date + datetime.timedelta(2)
    
    print "Dates:"
    print(day1Date,day2Date,day3Date)
    print(day1Date.strftime("%A"),day2Date.strftime("%A"),day3Date.strftime("%A"))
    forecast = {}
    
    if (firstHour < 20):
        forecast['next4hours'] = PeriodConditions([day1Date, time(firstHour,0,0)], [day1Date, time(firstHour+4,0,0)])
    else:
        forecast['next4hours'] = PeriodConditions([day1Date, time(firstHour,0,0)], [day2Date, time(firstHour-20,0,0)])
    
    
    forecast['day1']       = PeriodConditions([day1Date, time( 7,0,0)], [day1Date, time(20,0,0)])
    forecast['day1Dawn']   = PeriodConditions([day1Date, time( 0,0,0)], [day1Date, time( 6,0,0)])
    forecast['day1Morn']   = PeriodConditions([day1Date, time( 7,0,0)], [day1Date, time(10,0,0)])
    forecast['day1Even']   = PeriodConditions([day1Date, time(17,0,0)], [day1Date, time(20,0,0)])
    forecast['day1Nigh']   = PeriodConditions([day1Date, time(21,0,0)], [day2Date, time( 6,0,0)])
    
    forecast['offDay']     = PeriodConditions([day1Date, time( 7,0,0)], [day1Date, time(23,0,0)])       # Used for weekends etc
    forecast['offDayDawn'] = PeriodConditions([day1Date, time( 0,0,0)], [day1Date, time( 6,0,0)])       # 
    forecast['offDayMorn'] = PeriodConditions([day1Date, time( 7,0,0)], [day1Date, time(13,0,0)])       # 
    forecast['offDayEven'] = PeriodConditions([day1Date, time(14,0,0)], [day1Date, time(20,0,0)])       # 
    forecast['offDayNigh'] = PeriodConditions([day1Date, time(21,0,0)], [day2Date, time( 6,0,0)])       # 
                                               
    forecast['day2']       = PeriodConditions([day2Date, time( 7,0,0)], [day2Date, time(20,0,0)])
    forecast['day2Morn']   = PeriodConditions([day2Date, time( 7,0,0)], [day2Date, time(10,0,0)])
    forecast['day2Even']   = PeriodConditions([day2Date, time(17,0,0)], [day2Date, time(20,0,0)])
                                               
    forecast['day3']       = PeriodConditions([day3Date, time( 7,0,0)], [day3Date, time(20,0,0)])
    forecast['day3Morn']   = PeriodConditions([day3Date, time( 7,0,0)], [day3Date, time(10,0,0)])
    forecast['day3Even']   = PeriodConditions([day3Date, time(17,0,0)], [day3Date, time(20,0,0)])
            
    for c in forecast:
        print c, forecast[c].startTime, forecast[c].endTime
        
        for i in weatherData['hourly_forecast']:
            forecast[c].UpdateFromDictionary(i)
                    
    return [firstHour, day1Date, forecast]
    
    
