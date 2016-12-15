# The Kindle HUD brings up a list of important dates over the next 6 days, including:
# - People's birthdays
# - Significant dates, e.g. national holidays
# - Events from your Google Calendar
# 
# 
# Events are cached locally:
# - Birthdays are stored permanently in a local file
# - Significant dates are downloaded once a year.
# - Google Calendar is downloaded once a day, in the morning.
# 
# Google Calendar events can be short events, or cover a whole week or more,
# and the event is written to the screen in a human friendly way, E.G.
# 
# Single event example:
#   Work Christmas Dinner at 6:30 tomorrow
# 
# Multi-day event example:
#   Weekend Party from Friday to Sunday
# 
# Week long event example:
#   Half term all next week
# 
# Very long event example:
#   Summer holidays starts on thursday
# 
# 
# The Kindle HUD can handle multiple Google Calendars, and each
# one has its own list of Included and Excluded words kept in a
# local file. The Include/Exclude file lets you filter events
# based on keywords in the title or description of the events.
# For example, a school calenday might list events for all classes
# in the school, but you might only be interested in those for your
# child. 
# 
# 
# We also have the concept of a 'Working Day'. The Kindle HUD can render
# its screen differently depending on the day of the week. On a work day
# morning, for example, we might want to render the train and traffic
# information. But there's no point doing that at the weekend.
# 

import os
import time
from datetime import tzinfo, timedelta, datetime, date

import datetime
import json
import urllib
from xml.dom import minidom
import re
import sys
import imaplib
import getpass
import email
from HTMLParser import HTMLParser
import xml.etree.ElementTree as ET
import copy
from dateutil import *
from dateutil.rrule import *
from dateutil.parser import *
import kindle_ical

BST_begins = datetime.date.fromordinal(1)
BST_ends   = datetime.date.fromordinal(100)

ZeroTime = datetime.datetime.strptime('000000','%H%M%S')      
FREQ_Convert = {"YEARLY": YEARLY, "MONTHLY": MONTHLY, "WEEKLY": WEEKLY, "DAILY": DAILY, "HOURLY": HOURLY}


christianHolidays = ["http://www.webcal.fi/cal.php?id=424&format=json&start_year=current_year&end_year=current_year&tz=Europe%2FLondon"]
christianHolidays.append(["Valentine's Day", "Shrove Tuesday", "St. Patrick's Day", "Good Friday", "Thanksgiving", "Halloween"])

goodToKnow = ["http://www.webcal.fi/cal.php?id=219&format=json&start_year=current_year&end_year=current_year&tz=Europe%2FLondon"]
goodToKnow.append(["March equinox", "Daylight Saving Time begins", "Midsummer's Eve", "Father's Day", "Summer solstice", "September equinox", "Daylight Saving Time ends", "Guy Fawkes Day", "Remembrance Sunday", "Black Friday", "Winter solstice", "Chinese New Year"])

holidays = ["http://www.webcal.fi/cal.php?id=83&format=json&start_year=current_year&end_year=current_year&tz=Europe%2FLondon"]
holidayNames = ["New Year's Day", "Good Friday", "Easter", "Easter Monday", "Early May Bank Holiday", "Spring Bank Holiday", "Summer Bank Holiday", "Christmas Day", "Boxing Day", "Boxing Day Bank Holiday"]
holidays.append(holidayNames)
# holidayDates = []

paganHolidays = ["http://www.webcal.fi/cal.php?id=342&format=json&start_year=current_year&end_year=current_year&tz=Europe%2FLondon"]
paganHolidays.append(["Yule"])

dateSources = [christianHolidays, goodToKnow, holidays, paganHolidays] 


################################
# EDIT the calendar names here #
################################

# Google Calendars:
school_calendar_URL    = ""
personal_calendar_URL  = ""
work_calendar_URL      = ""

# The names of the calendars in quotes are used to find the Include/Exclude file for
# each calendar, and for the filename of its cache.
calendars_list = [ [school_calendar_URL, "school"], [personal_calendar_URL, "personal"], [work_calendar_URL, "work"] ]


###########################
# EDIT the work days here #
###########################
def IsWorkingDay(eventList):
    workingDay = True
    day = datetime.date.today().weekday()
    if (day == 0) | (day == 5) | (day == 6):                # Is it Monday, Saturday or Sunday today ?
        workingDay = False

    for holiday in holidayNames:                            # Does the event list say there is a holiday 'today' ?
        holidayString = holiday + " today"
        if any([holidayString in e for e in eventList]):
            workingDay = False
                
    return workingDay


def AdjustTimeForBST(t, d):

    d2 = datetime.date(2000, d.month, d.day)

    hour = t.hour
    min  = t.minute

    if (d2 >= BST_begins) & (d2 < BST_ends):
        hour += 1
        
    return datetime.time(hour, min)

    
def CalcDaysUntil(date):
    '''Calculates the age and days until next birthday
      from the given birth date to display in the results'''
    returnDays = 0
    try:
        #for i in './- ':
        #    if (date.find(i) != -1):
        #        date = date.split(i)
        #        break;
        #birthdate = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        birthdate = date
        today = datetime.date.today()
        
        #print birthdate, today, birthdate-today
        if (today.month > birthdate.month):
            nextYear = datetime.date(today.year + 1, birthdate.month, birthdate.day)
        elif (today.month < birthdate.month):
            nextYear = datetime.date(today.year, today.month + (birthdate.month - today.month), birthdate.day)
        elif (today.month == birthdate.month):
            if (today.day > birthdate.day):
                nextYear = datetime.date(today.year + 1, birthdate.month, birthdate.day)
            elif (today.day < birthdate.day):
                nextYear = datetime.date(today.year, birthdate.month, today.day + (birthdate.day - today.day))
            elif (today.day == birthdate.day):
                nextYear = 0
 
        age = today.year - birthdate.year
 
        if nextYear == 0: #if today is the birthday
            returnDays = datetime.timedelta(0)
        else:
            daysLeft = nextYear - today
            returnDays = daysLeft
    except:
        returnDays = datetime.timedelta(0)
    return returnDays

    
def RemoveDups(inputfile):
    lines     = open(inputfile, 'r').readlines()
    lines_set = set(lines)
    out       = open(inputfile, 'w')
    for line in lines_set:
        out.write(line)
        
def GetKey(item):
    d = item[1]    
    return d[4:]

    

    
def ReadCalendarCache(cache_file_name):
    if not os.path.exists(cache_file_name):
        return "Need to refresh"
        
    with open(cache_file_name) as f:
        calendar_cache = json.load(f)
        
    cache_date = datetime.datetime.strptime(calendar_cache[0],'%Y%m%d')
    
    if cache_date.date() < datetime.date.today():
        return "Need to refresh"
        
    return calendar_cache[1]

    
    
def WriteCalendarCache(calendar_cache, cache_file_name):
    calendar_cache_file_data = [datetime.date.today().strftime('%Y%m%d'), calendar_cache]
    file = open(cache_file_name, 'w')
    file.write(json.dumps(calendar_cache_file_data))

    
    
def FetchCalendarDates(calendar_URL, calendar_name):
    calendar_cache_file_name = calendar_name+'_calendar_cache.json'
    calendar_cache = ReadCalendarCache(calendar_cache_file_name)
    
    if calendar_cache == "Need to refresh":
        print 'Downloading '+calendar_name+' calendar'
        response  = urllib.urlopen(calendar_URL)
        downloaded_calendar_iCal = response.read()
        open("basic.ics", "w").write(downloaded_calendar_iCal)        
        calendar = kindle_ical.ParseIcal("basic.ics", calendar_name)
        WriteCalendarCache(calendar, calendar_cache_file_name)
        return calendar
    else:
        print 'Using '+calendar_name+' calendar cache'
        return calendar_cache
    

    
def FetchImportantDaysForTheYear():
    try:
        birthdaysFile = open('birthdays.txt', 'r')
        allEventsFile = open('allEvents.txt', 'w')
        
        eventList = []
        for dateSource in dateSources:
            response  = urllib.urlopen(dateSource[0])
            datesJSON = response.read()
            datesInfo = json.loads(datesJSON.decode('ASCII'))
            
            for day in datesInfo:
                name = day['name']
                #print name
                for nameCheck in dateSource[1]:
                    if name.startswith(nameCheck):
                        #print(name, day['date'])
                        #eventLine = name.replace(" ", "_") + " " + day['date'] + "\n"
                        #allEventsFile.write(eventLine)
                        eventList.append([name.replace(" ", "_"), day['date']])
                        
        for line in birthdaysFile:
            l = line.split()
            eventList.append(l)

        eventList = sorted(eventList, key=GetKey)

        prevEventName = ""
        for e in eventList:                     # Write events to the file, removing duplicates
            if prevEventName != e[0]:
                eventLine = e[0] + " " + e[1] + "\n"
                allEventsFile.write(eventLine)
                #print eventLine
                prevEventName = e[0]

        birthdaysFile.close()
        allEventsFile.close()

        return 1
    except:
        return 0
                
 

def GetEvents():
    global BST_begins
    global BST_ends
        
    try:    
        if (os.path.exists('currentYear.txt') != True):
            currentYear = open('currentYear.txt', 'w')
            currentYear.write("2000")
            currentYear.close()
            
        currentYear = open('currentYear.txt', 'r').readlines()
        print "currentYear:", currentYear
        year = datetime.date.today().year
        if (year != int(currentYear[0])):
            print "Need to refresh"
            if (FetchImportantDaysForTheYear()):
                print "Refresh Successful"
                f = open('currentYear.txt', 'w')
                f.write(str(year))
            else:
                print "Refresh Failed"
        print "using allevents.txt"

        eventList = []
        
        eventString = ""
        f = open('allEvents.txt', 'r')
        
        for line in f:
            bday = line.split()
            if len(bday) == 2:
                name = bday[0]
                when = datetime.datetime.strptime(bday[1],'%Y-%m-%d')      
                days = CalcDaysUntil(when)
                numDays = days.days

                #print name, when
                
                if name == "Daylight_Saving_Time_begins":
                    BST_begins = datetime.date(2000, when.month, when.day)
                    print "BST_begins =", BST_begins
                    
                if name == "Daylight_Saving_Time_ends":
                    BST_ends = datetime.date(2000, when.month, when.day)
                    print "BST_ends   =", BST_ends
                    
                if (numDays==0):
                    eventString = name + " today\n"
                
                if (numDays==1):
                    eventString = name + " tomorrow\n"
                  
                if ((numDays>1) & (numDays<=6)):    
                    dayOfWeek = date.today() + days
                    eventString = name+ " on " + dayOfWeek.strftime("%A\n")
                    #print eventString
                    
                if eventString != "":
                    eventList.append( (eventString.replace("_", " "), numDays) )
                    #print eventList
                    eventString = ""
                
    except:
        print "EXCEPTION IN GetEvents()"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print exc_type
        print exc_value
        print exc_traceback
        eventList = []
    
    #print eventList
    #school_events = FetchCalendarDates()
    #print "school_events =", school_events
    kindle_ical.SetBST(BST_begins, BST_ends)

    for calendar in calendars_list:
        #print calendar
        events = FetchCalendarDates(calendar[0], calendar[1])
        #print events
        print "done"
        if events != None:
            eventList = eventList + events
    
    sortedEventList = sorted(eventList, key=lambda numDays: numDays[1])
    #print "sortedEventList=", sortedEventList
    
    finalEventsList = []
    for eventTuple in sortedEventList:
        finalEventsList.append(eventTuple[0])
        
    return finalEventsList
 
def ordinal(n):
    th = ["st","nd","rd","th","th","th","th","th","th","th","th","th","th","th","th","th","th","th","th","th","st","nd","rd","th","th","th","th","th","th","th","st","nd"]
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
    
def dtStylish(dt,f):
    return dt.strftime(f).replace("{th}", ordinal(dt.day))
    
def GetTodaysDateString():
    return dtStylish(date.today(), "%a {th} %b\n")

def MakeDateString(d):
    return dtStylish(d, "%a {th} %b\n")
    
def before(str, ch):
    pos_a = str.find(ch)
    if pos_a == -1: return ""
    return str[0:pos_a]

def after(str, ch):
    # Find and validate first part.
    pos_a = str.rfind(ch)
    if pos_a == -1: return ""
    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(ch)
    if adjusted_pos_a >= len(str): return ""
    return str[adjusted_pos_a:]

def ParseFREQ(value):
    return ["FREQ", value]
    
def ParseINTERVAL(value):
    return ["interval", int(value)]
    
def ParseBYDAY(value):
    if (value[0].isdigit()):
        return ["byweekday", value[1:3]+"(+"+value[0]+")"]
    else:
        return ["byweekday", value[0:2]]
    
parseFunctions = {'FREQ':ParseFREQ, 'INTERVAL':ParseINTERVAL, 'BYDAY':ParseBYDAY}

def ParseRrule(rruleString):
    params = rruleString.split(';')
    outputString = ""
    keywords = {"dtstart":"datetime.datetime.today().date()"}
    
    for param in params:
        name  = before(param, '=')
        value = after(param, '=')
        
        if name == "FREQ":
            freq = value
        elif name in parseFunctions:
            keys = parseFunctions[name](value)
            #print keys
            keywords[keys[0]] = keys[1]
      
    #outputString += "dtstart=datetime(" + str(datetime.datetime.today().date()) + ")"
    #outputString += "dtstart=datetime(2014,12,4)"
    #r = rrule(outputString)
    print freq, str(keywords)
    r = rrule(MONTHLY, *keywords)
    
    #print r.after(datetime.datetime.today().date())
        #print name, value
        #if name == "BYDAY":
        #    print ParseBYDAY(value)

class newTZinfo(tzinfo):
    
    """ Overrides abstract class tzinfo from datetime to provide mean for TZID support from ical
    """
    name = ""
    def setID(self,ID):
        self.name = ID
    def getID(self):
        return self.name

    def utcoffset(self, dt):
        return timedelta(hours=0) + self.dst(dt)
    def dst(self, dt):
        return timedelta(hours=0)

        
def _icalindex_to_pythonindex(self,indexes):
    #FIXME: change this to load_integerlist and add check that we have "," as list separator (and no other values)
    ret_val = []
    for index in indexes:
        index = int(index)
        if index>MaxInteger or index<-MaxInteger:
            self.Validator("3.3.8_1","Found: %i",index)
        ret_val.append(index)
    return ret_val

   
def date_load(propval,params=[],LineNumber = 0):
    """ loads the date-time or date value + optional TZID into UTC date-time or date
    
    DTSTART, DTEND, DTSTAMP, UNTIL,..."""
    TZID="TZID not set - floatting"
    newdate = None
    
    for param in params:
        if param.find("TZID=")==0:
            TZID=param.split("=")[1]

    nTZinfo = newTZinfo()

    yeardate = int(propval[0:4])
    
    if propval.find("-")>=0:
        self.Validator("3.3.12_1",line_count = LineNumber,line = propval)
    
    if yeardate<1582: #retdate<datetime(year=1582,month=10,day=15):
        self.Validator("3.3.5_1", line_count = LineNumber,line = propval,alttxt = "dates prior to 1582/oct/15 might be in julian calendar, prior validation should be undertaken - date moved to 1900 for enumerator")
        propval = "1900"+propval[5:]
    elif yeardate<1875:
        self.Validator("3.3.5_1", line_count = LineNumber,line = propval)
    elif yeardate<1970:
        self.Validator("3.3.5_1", line_count = LineNumber,line = propval,alttxt="1970 however is often a computer epoch limit prior validation should be undertaken before keeping such a past date")
        
    if 'VALUE=DATE' in params:
        if len(propval)>8:
            self.Validator("3.3.4_1","expected date, found: %s"%(propval))
        else:
            newdate = datetime.strptime(propval,"%Y%m%d").date()
    else:
        if propval[len(propval)-1]=="Z":
            propval = propval[:-1]
            if not TZID=="TZID not set - floatting":
                self.Validator("3.3.5_3", LineNumber, propval)
            TZID = "UTC"
        if len(propval)==15:
            retdate = datetime.datetime.strptime(propval[0:15],"%Y%m%dT%H%M%S")
            if not TZID=="TZID not set - floatting":
                newdate = datetime.datetime(retdate.year,retdate.month,retdate.day,retdate.hour,retdate.minute,retdate.second,tzinfo=nTZinfo)
                newdate.tzinfo.setID(TZID)
            else:
                newdate = retdate
        elif len(propval)==8:
            #here is the case where we load UNTIL and it is a 'DATE' but we cannot check yet against the DTSTART value type
            newdate = datetime.strptime(propval[0:8],"%Y%m%d").date()
        else:
            self.Validator("3.3.5_2", LineNumber, line = propval)
    
    return newdate


def rrule_load(sRrule,param="",LineNumber = 0):
    """ load a string into a rrule object"""
    
    rules = {}
    rrule = sRrule.split(";")
    rule_count = 0
    for rule in rrule:
        rule_count +=1
        if len(rule)>0:
            #FIXME: this is to cater for line ending with ; which is probably not valid
            [param, value] = rule.split("=")
            #if param in rules:
                #self.Validator("3.3.10_1","%s rule part is defined twice in RRULE (Line: %i)"%(param,LineNumber))
                
            if (param == "FREQ"):
                rules[param] = FREQ_Convert[value]
                if rule_count >1:
                    #FREQ should be first rule part
                    print("3.3.10_2","see RRULE (Line: %i)"%(LineNumber))
                #if not value in RFC5545_FREQ :
                #    print("3.3.10_5","see RRULE (Line: %i)"%(LineNumber))
                    
            elif (param == "UNTIL"):
                #FIXME: see "3.3.10_6b"
                #rules["until"] = date_load(value)
                rules["until"] = datetime.datetime.strptime(value[0:8],'%Y%m%d')      
                #print "FIXME"
            elif (param == "COUNT"):
                try:
                    count_instances = int(value)
                except:
                    #print "Whoops"
                    print("3.3.10_6","see RRULE (Line: %i)"%(LineNumber))
                if count_instances <0:
                    #print "Whoops"
                    print("3.3.10_6","see RRULE (Line: %i)"%(LineNumber))
                else:
                    rules[param] = count_instances
            elif (param == "INTERVAL"):
                #( ";" "INTERVAL" "=" 1*DIGIT )          /
                rules["interval"] = int(value)
            elif (param == "BYSECOND"):
                #( ";" "BYSECOND" "=" byseclist )        /
                #byseclist  = seconds / ( seconds *("," seconds) )
                #seconds    = 1DIGIT / 2DIGIT       ;0 to 59
                byseclist = value.split(",")
                rules[param]=[]
                for seconds in byseclist:
                    if seconds>60:
                        print("3.3.10_7")
                    rules[param].append(int(seconds))
            elif (param == "BYMINUTE"):
                #if seconds>59:
                #    self.Validator("3.3.10_8")
                rules[param] = value
            elif (param == "BYHOUR"):
                rules[param] = value
            elif (param == "BYDAY"):
                #( ";" "BYDAY" "=" bywdaylist )          /
                #bywdaylist = weekdaynum / ( weekdaynum *("," weekdaynum) )
                #weekdaynum = [([plus] ordwk / minus ordwk)] weekday
                #plus       = "+"
                #  minus      = "-"
                #  ordwk      = 1DIGIT / 2DIGIT       ;1 to 53
                #  weekday    = "SU" / "MO" / "TU" / "WE" / "TH" / "FR" / "SA"
                #;Corresponding to SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY,
                #;FRIDAY, SATURDAY and SUNDAY days of the week.
                #bywdaylist = split(value,",")
                #for weekdaynum in bywdaylist:
                param = "byweekday"
                rules[param] = {}
                ldow = {}   #dictionnary with dow and list of index
                #{'MO': [0], 'TU': [1], 'WE': [-1]} means every monday, first tuesday
                # last wednesday, .. 
                bywdaylist = value.split(",")
                dow = ["MO","TU","WE","TH","FR","SA","SU"]
                dayStringtoweekdayClass = {"MO":MO, "TU":TU, "WE":WE, "TH":TH, "FR":FR, "SA":SA, "SU":SU}
                for weekdaynum in bywdaylist:
                    #get the position of the DOW
                    #weekdaynum of type: MO , 1MO, 2TU or -2WE
                    for d in dow:
                        print "-", d
                        if weekdaynum.find(d) >=0:
                            pos_dow = weekdaynum.find(d)
                            print "  ", pos_dow
                    #extract position of dow to split its index from it.
                    if pos_dow == 0:
                        index = 0
                    else:
                        index = int(weekdaynum[0:pos_dow])
                        print "index=", index
                    dayString = weekdaynum[pos_dow:]
                    dayClass = dayStringtoweekdayClass[dayString]
                    print "ddow class", dayClass(index)
                    
                    #p = dow.index(ddow)
                    
                    #print "p =", p
                    #ddow = dow2[p]
                    #print "ddow =",ddow
                    #print "ldow =",ldow
                    #if ddow in ldow:
                    #    ldow[ddow].append(index)
                    #    print "ldow! =",ldow
                    #else:
                    #    ldow[ddow] = [index]
                    #    print "ldow? =",ldow
                rules[param] = dayClass(index)
                #print "ddow =", ddow
                
#                    self._log("175",[rules[param],param])
            elif (param == "BYMONTHDAY"):
                # ( ";" "BYMONTHDAY" "=" bymodaylist )    /
                # bymodaylist = monthdaynum / ( monthdaynum *("," monthdaynum) )
                # monthdaynum = ([plus] ordmoday) / (minus ordmoday)
                # ordmoday   = 1DIGIT / 2DIGIT       ;1 to 31
                bymodaylist = value.split(",")
                rules[param] = icalindex_to_pythonindex(bymodaylist)
            elif (param == "BYYEARDAY"):
                byyeardaylist = value.split(",")
                rules[param] = icalindex_to_pythonindex(byyeardaylist)
            elif (param == "BYWEEKNO"):
                bywklist = value.split(",")
                rules[param] = icalindex_to_pythonindex(bywklist)
            elif (param == "BYMONTH"):
                #";" "BYMONTH" "=" bymolist )
                #bymolist   = monthnum / ( monthnum *("," monthnum) )
                #monthnum   = 1DIGIT / 2DIGIT       ;1 to 12
                bymolist = value.split(",")
                rules[param] = icalindex_to_pythonindex(bymolist)
            elif (param == "BYSETPOS"):
                #( ";" "BYSETPOS" "=" bysplist )         /
                # bysplist   = setposday / ( setposday *("," setposday) )
                # setposday  = yeardaynum
                bysplist = value.split(",")
                rules[param] = icalindex_to_pythonindex(bysplist)
            elif (param == "WKST"):
                rules[param] = value
            else:
                rules[param] = value
                
    if not "FREQ" in rules:
        print("3.3.10_3",LineNumber)
    if "UNTIL" in rules and "COUNT" in rules:
        print("3.3.10_4",LineNumber)
        
    return rules
        

        