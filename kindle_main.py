import time
from   datetime import date
import datetime
from   xml.dom import minidom
import kindle_graphics
import kindle_dates   
import kindle_weather
import kindle_traffic
import png
import os
import email_update

emailMessage = "Nothing"

print " "
print "----------------------"
print "     Kindle Main"
print "----------------------"
try:
    
    eventsList = kindle_dates.GetEvents()

    ###########################
    # EDIT your location here #
    ###########################    
    [hour, day1Date, forecast] = kindle_weather.FetchWeatherForecast("httpRequest", "UK/London.json")
    
    
    day2Date = day1Date+datetime.timedelta(1)
    day3Date = day1Date+datetime.timedelta(2)

    print(day1Date)
    print(day2Date)
    print(day3Date)

    if kindle_dates.IsWorkingDay(eventsList):
        day1     = 'day1'
        day1Dawn = 'day1Dawn'
        day1Morn = 'day1Morn'
        day1Even = 'day1Even'
        day1Nigh = 'day1Nigh'
        
    #else:

    day1Low      = forecast['day1'].minTemp                     # Working days need to know the weather during travel to and from work only
    day1High     = forecast['day1'].maxTemp                     # so the weather report has gaps in it for when you're at work
    nightLow     = forecast['day1Nigh'].minTemp
    nightHigh    = forecast['day1Nigh'].maxTemp
    day2Low      = forecast['day2'].minTemp
    day2High     = forecast['day2'].maxTemp
    day3Low      = forecast['day3'].minTemp
    day3High     = forecast['day3'].maxTemp

    #hour = forecast['day1'].hour
    print "hour =", hour

    day1Name = day1Date.strftime("%a")
    day2Name = day2Date.strftime("%A")
    day3Name = day3Date.strftime("%A")

    print("day1Name", day1Name)
    print("day2Name", day2Name)
    print("day3Name", day3Name)

    def TemperatureToString(temperature):
        if (temperature != -99) & (temperature != 99):
            return str(temperature)  + '*'
        else:
            return " "

    # Morning: time from 05:00 to 11:00 - show  M&E
    # Evening: time from 12:00 to 20:00 - show  E&N
    # Night:   time from 21:00 to 04:00 - show  N&M

    if (hour>=5) & (hour <=10):
        # Morning display    
        print("Morning display")    
        day1LeftLabel  = "Morning"
        day1RightLabel = "Evening"
        day2Label      = day2Name
        day3Label      = day3Name
        
        day1MornIcon = forecast['day1Morn'].worstCondition
        day1EvenIcon = forecast['day1Even'].worstCondition
        day1NighIcon = forecast['day1Nigh'].worstCondition
        day2MornIcon = forecast['day2Morn'].worstCondition
        day2EvenIcon = forecast['day2Even'].worstCondition
        day3MornIcon = forecast['day3Morn'].worstCondition
        day3EvenIcon = forecast['day3Even'].worstCondition

        day1LeftTemp  = TemperatureToString(day1Low)
        day1RightTemp = TemperatureToString(day1High)
        day2LeftTemp  = TemperatureToString(day2Low)
        day2RightTemp = TemperatureToString(day2High)
        day3LeftTemp  = TemperatureToString(day3Low)
        day3RightTemp = TemperatureToString(day3High)
        
        if (day1Low  !=  99):
            day1LeftTemp  = str(day1Low)  + '*'
        if (day1High != -99):
            day1RightTemp = str(day1High) + '*'

        windchill = str(forecast['day1'].feelsLike)
        windSpeed = str(forecast['day1'].windSpeed)
        uvi       = str(forecast['day1'].uvi)
        humidity  = str(forecast['day1'].humidity)

            
    if (hour>=11) & (hour <=20):
        # Evening display    
        print("Evening display")
        day1LeftLabel = "Evening"
        day1RightLabel = "Tonight"
        day2Label     = day2Name
        day3Label     = day3Name

        day1MornIcon = forecast['day1Even'].worstCondition
        day1EvenIcon = forecast['day1Nigh'].worstCondition
        if day1EvenIcon <=6:
            day1EvenIcon += 25
            
        day2MornIcon = forecast['day2Morn'].worstCondition
        day2EvenIcon = forecast['day2Even'].worstCondition
        day3MornIcon = forecast['day3Morn'].worstCondition
        day3EvenIcon = forecast['day3Even'].worstCondition

        day1LeftTemp  = TemperatureToString(day1Low)
        day1RightTemp = TemperatureToString(day1High)
        day2LeftTemp  = TemperatureToString(day2Low)
        day2RightTemp = TemperatureToString(day2High)
        day3LeftTemp  = TemperatureToString(day3Low)
        day3RightTemp = TemperatureToString(day3High)

        windchill = str(forecast['day1'].feelsLike)
        windSpeed = str(forecast['day1'].windSpeed)
        uvi       = str(forecast['day1'].uvi)
        humidity  = str(forecast['day1'].humidity)

        
    if (hour>=21):
        # Night display    
        print("Night display (before midnight)")
        day1LeftLabel  = "Tonight"
        day1RightLabel = "Morning"
        day2Label      = day2Name
        day3Label      = day3Name

        d1 = forecast['day1Nigh'].worstCondition
        if d1 <= 5:
            d1 += 25
        day1MornIcon = d1
        day1EvenIcon = forecast['day2Morn'].worstCondition
        day2MornIcon = forecast['day2Morn'].worstCondition
        day2EvenIcon = forecast['day2Even'].worstCondition
        day3MornIcon = forecast['day3Morn'].worstCondition
        day3EvenIcon = forecast['day3Even'].worstCondition

        day1LeftTemp  = TemperatureToString(nightLow)
        day1RightTemp = TemperatureToString(nightHigh)
        day2LeftTemp  = TemperatureToString(day2Low)
        day2RightTemp = TemperatureToString(day2High)
        day3LeftTemp  = TemperatureToString(day3Low)
        day3RightTemp = TemperatureToString(day3High)

        windchill = str(forecast['day1Nigh'].feelsLike)
        windSpeed = str(forecast['day1Nigh'].windSpeed)
        uvi       = str(forecast['day1Nigh'].uvi)
        humidity  = str(forecast['day1Nigh'].humidity)
        print "Done"
        
    if (hour <=4):
        # Night display    
        print("Night display (after midnight)")
        
        day1LeftLabel  = "Tonight"
        day1MornIcon = forecast['day1Dawn'].worstCondition
        if day1MornIcon <=6:
            day1MornIcon += 25
        
        
        
        day1RightLabel = "Morning"
        day1EvenIcon = forecast['day1Morn'].worstCondition
        
        day3Date = day2Date
        day2Date = day1Date
        day1Date = day1Date - datetime.timedelta(1)
        
        day1Name = day1Date.strftime("%a")
        day2Name = day2Date.strftime("%A")
        day3Name = day3Date.strftime("%A")

        print "New dates:", day1Date, day2Date, day3Date
        print "New names:", day1Name, day2Name, day3Name

        day2Label      = day2Name
        day3Label      = day3Name
        
        day2MornIcon = forecast['day1Morn'].worstCondition
        day2EvenIcon = forecast['day1Even'].worstCondition
        day3MornIcon = forecast['day2Morn'].worstCondition
        day3EvenIcon = forecast['day2Even'].worstCondition

        day1LeftTemp  = TemperatureToString(nightLow)
        day1RightTemp = TemperatureToString(nightHigh)
        day2LeftTemp  = TemperatureToString(day1Low)
        day2RightTemp = TemperatureToString(day1High)
        day3LeftTemp  = TemperatureToString(day2Low)
        day3RightTemp = TemperatureToString(day2High)

        windchill = str(forecast['day1Dawn'].feelsLike)
        windSpeed = str(forecast['day1Dawn'].windSpeed)
        uvi       = str(forecast['day1Dawn'].uvi)
        humidity  = str(forecast['day1Dawn'].humidity)    

        
    def RenderWeatherDay1():
    	print "Icons: ", day1MornIcon, day1EvenIcon
        try:
            kindle_graphics.weatherooLarge.DrawCentred(day1MornIcon-1, 100,  60)
            kindle_graphics.weatherooLarge.DrawCentred(day1EvenIcon-1, 290,  60)
            
            kindle_graphics.trebuchet_37px.PrintCentred("Low",      75, 340)
            kindle_graphics.trebuchet_37px.PrintCentred("High",    315, 340)
            
            # Morning, Evening
            kindle_graphics.trebuchet_37px.PrintCentred(day1LeftLabel,  100, 230)
            kindle_graphics.trebuchet_37px.PrintCentred(day1RightLabel, 290, 230)

            # Temperature big numbers
            kindle_graphics.trebuchet_37px.PrintCentred( day1LeftTemp,   75, 300)   
            kindle_graphics.trebuchet_37px.PrintCentred( day1RightTemp, 315, 300)
            kindle_graphics.numbers_103px.PrintCentred( windchill+'*',  195, 290)   
            
            # Main date string, Low High words
            #kindle_graphics.trebuchet_37px.PrintCentred(kindle_dates.GetTodaysDateString(), 210, 20)    # Fixme: use day1date
            kindle_graphics.trebuchet_37px.PrintCentred(kindle_dates.MakeDateString(day1Date), 210, 20)    # Fixme: use day1date
            
        except:
            print "Exception in RenderWeatherDay1()"
        
    def RenderExtrasDay1():
        try:
            kindle_graphics.trebuchet_28px.Print("WindChill: ", 25, 470)
            kindle_graphics.trebuchet_28px.Print("WindSpeed: " ,25, 500)
            kindle_graphics.trebuchet_28px.Print("UV Index:  ", 25, 530)
            kindle_graphics.trebuchet_28px.Print("Humidity: " , 25, 560)

            kindle_graphics.trebuchet_28px.PrintRightJus(windchill, 200, 470)
            kindle_graphics.trebuchet_28px.PrintRightJus(windSpeed, 200, 500)
            kindle_graphics.trebuchet_28px.PrintRightJus(uvi,       200, 530)
            kindle_graphics.trebuchet_28px.PrintRightJus(humidity,  200, 560)

            kindle_graphics.trebuchet_28px.Print("*",   202, 470)
            kindle_graphics.trebuchet_17px.Print("kph", 203, 508)
            kindle_graphics.trebuchet_28px.Print("%",   202, 560)

            windSpeedValue = int(windSpeed)
            if windSpeedValue >= 43:
                windsockIcon = 0
            elif windSpeedValue >= 25:
                windsockIcon = 1
            elif windSpeedValue >= 10:
                windsockIcon = 2
            else:
                windsockIcon = 3

        except:
            print "Exception in RenderExtrasDay1()"

    def RenderExtrasDay1_v2(pollenLevel):
        print "RenderExtrasDay1_v2(", pollenLevel, ")"
        try:
            uvi = str(forecast['next4hours'].uvi)
            pop = str(forecast['next4hours'].pop)
            hum = str(forecast['next4hours'].humidity)
            sky = str(forecast['next4hours'].sky)
            
            pol = pollenLevel
            #if pollenLevel == "None":
            #    pol = '-'
            #if pollenLevel == "Low":
            #    pol = 'L'
            #if pollenLevel == "Moderate":
            #    pol = 'M'
            #if pollenLevel == "High":
            #    pol = 'H'
            #if pollenLevel == "Very High":
            #    pol = 'VH'
            
            print "Pollen level: ", pollenLevel, "--", pol
            
            extrasList = []
            extrasList.append([0, uvi, ' '])
            extrasList.append([1, hum, '%'])
            extrasList.append([3, sky, '%'])
            extrasList.append([2, pop, '%'])
            extrasList.append([4, pol, ' '])
            
            y = 410
            for extra in extrasList:
                icon   = extra[0]
                number = extra[1]
                units  = extra[2]
                
                kindle_graphics.extrasIcons.Draw(              icon,  35, y)
                kindle_graphics.trebuchet_37px.PrintRightJus(number, 135, y)
                kindle_graphics.trebuchet_37px.Print(         units, 138, y)
                
                y += 37
                
            windSpeedValue = int(windSpeed)
            if windSpeedValue >= 43:
                windsockIcon = 0
            elif windSpeedValue >= 25:
                windsockIcon = 1
            elif windSpeedValue >= 10:
                windsockIcon = 2
            else:
                windsockIcon = 3

            print "    done RenderExtrasDay1_v2"

        except:
            print "Exception in RenderExtrasDay1_v2()"


    def RenderWeatherDay2():
        try:
            kindle_graphics.trebuchet_37px.PrintCentred(day2Label,     505,  20)
            # Temperature numbers
            kindle_graphics.trebuchet_37px.Print(day2LeftTemp,  460, 150)
            kindle_graphics.trebuchet_37px.Print(day2RightTemp, 530, 150)

            kindle_graphics.weatherooSmall.DrawCentred(day2MornIcon-1, 460,  60)
            kindle_graphics.weatherooSmall.DrawCentred(day2EvenIcon-1, 550,  60)
        except:
            print "Exception in RenderWeatherDay2()"

            
    def RenderWeatherDay3():
        try:
            kindle_graphics.trebuchet_37px.PrintCentred(day3Label,     695,  20)

            # Temperature numbers
            kindle_graphics.trebuchet_37px.Print(day3LeftTemp,  650, 150)
            kindle_graphics.trebuchet_37px.Print(day3RightTemp, 720, 150) 

            kindle_graphics.weatherooSmall.DrawCentred(day3MornIcon-1, 650, 60)
            kindle_graphics.weatherooSmall.DrawCentred(day3EvenIcon-1, 740, 60)
        except:
            print "Exception in RenderWeatherDay3()"

            
    def RenderTrafficInfo(startY, trafficInfo):
        print "RenderTrafficInfo()"
        try:
            y = startY + 20
            
            for traffic in trafficInfo:
                oldY = y;
                print traffic
                icon      = traffic[0]
                location  = traffic[1]
                condition = traffic[2]
                if icon == 'Closures':
                    kindle_graphics.trafficIcons.Draw(0, 400, y)
                if icon == 'Roadworks':
                    kindle_graphics.trafficIcons.Draw(1, 400, y)
                if icon == 'Incidents':
                    kindle_graphics.trafficIcons.Draw(2, 400, y)
                if icon == 'Delays':
                    kindle_graphics.trafficIcons.Draw(3, 400, y)
                if icon == 'NoProblems':
                    kindle_graphics.trafficIcons.Draw(4, 400, y)
                    
                y = kindle_graphics.trebuchet_17px_Bold.PrintBlock(location,  470, y, 325)
                y = kindle_graphics.trebuchet_17px.PrintBlock(condition,      470, y, 325)
                y += 20
                if y-oldY < 60:
                    y += 60-(y-oldY)

                if y >= 540:
                    break
                    
            print trafficInfo
            return y
            
        except:
            print "Exception in RenderTrafficInfo()"

            
    def RenderTrainInfo(startY, trainInfo):
        print "RenderTrainInfo()"
        try:
            y = startY+20
            #kindle_graphics.trebuchet_37px.Print("Rail",  400, y)
            #y += 50
            print "------"
            print trainInfo
            print "------"
            #trainInfo = kindle_traffic.GetTrainEmail()
            #trainInfo = [ ["Delays", "Stratford Station Closed", "Station closed today for some reason"] ]
            #trainInfo = [ ["NoProblems", "Trains good", "There is no disruption reported at this time affecting services between Stratford and Ingatestone."] ]
            
            for train in trainInfo:
                oldY = y;
                icon      = train[0]
                location  = train[1]
                condition = train[2]
                
                print icon
                print location
                print condition
                
                if icon == 'Cancelled':
                    kindle_graphics.trafficIcons.Draw(6, 400, y)
                if icon == 'CancelledOrDelayed':
                    kindle_graphics.trafficIcons.Draw(6, 400, y)
                if icon == 'Delayed':
                    kindle_graphics.trafficIcons.Draw(5, 400, y)
                if icon == 'NoProblems':
                    kindle_graphics.trafficIcons.Draw(4, 400, y)

                y = kindle_graphics.trebuchet_17px_Bold.PrintBlock(location,  470, y, 325)
                y = kindle_graphics.trebuchet_17px.PrintBlock(condition,      470, y, 325)
                y += 20
                if y-oldY < 60:
                    y += 60-(y-oldY)

            return y
            
        except:
            print "Exception in RenderTrafficInfo()"
            return y

        
    def RenderEvents(startY, whichDays):
        print "RenderEvents(startY, whichDays)"
        print eventsList
        numLines = 0
        
        try:
            y = startY
            for event in eventsList:
            
                if whichDays == "today":
                    if event.find(whichDays) == -1:
                        #print "Not Today"
                        return y
                        
                    if numLines >= 3:
                        #print "numLines >= 3"
                        return y
                        
                #print numLines, y, event
                kindle_graphics.trebuchet_17px.Print(event[0].upper() + event[1:],  410, y)
                numLines += 1
                y        += 22
                
                if numLines >= 5:
                    #print "numLines >= 5"
                    return y
                        
        except:
            print "Exception in RenderEvents()"
        return y
            
    def RenderWeekdayMorning():
        try:
            print "RenderWeekdayMorning()"
            RenderWeatherDay1()
            
            trafficInfo = kindle_traffic.GetEmails("Traffic Trains Pollen")
            print "\n---------"
            print trafficInfo
            print "---------\n"

            y = RenderEvents(4, "today")
            
            y = RenderTrainInfo(y, trafficInfo[1])
            RenderTrafficInfo(y, trafficInfo[0])
            RenderExtrasDay1_v2(trafficInfo[2])
            kindle_graphics.DrawWindCompass(290, 485, forecast['next4hours'].windInfo)
        except:
            print "Exception in RenderWeekdayMorning()"

    def RenderWeekdayOther():
        #try:
            print "RenderWeekdayOther()"
            RenderWeatherDay1()
            print "RenderWeatherDay2()"
            RenderWeatherDay2()
            print "RenderWeatherDay3()"
            RenderWeatherDay3()
            print 'trafficInfo = kindle_traffic.GetEmails("Pollen")'
            try:
                trafficInfo = kindle_traffic.GetEmails("Pollen")
            except:
                print "Exception trapped"
                
            print "RenderExtrasDay1_v2(trafficInfo[2])"
            RenderExtrasDay1_v2(trafficInfo[2])
            print "kindle_graphics.ReadRainRadar()"
            kindle_graphics.ReadRainRadar()
            print "kindle_graphics.DrawWindCompass(300, 500, forecast['next4hours'].windInfo)"
            kindle_graphics.DrawWindCompass(290,485, forecast['next4hours'].windInfo)
            print "RenderEvents()"
            RenderEvents(196, "")
        #except:
        #    print "Exception in RenderWeekdayOther()"
        
    def RenderWeekend():
        print "RenderWeekend()"
        pass

    #RenderWeekdayMorning()
    if ((hour == 8) | (hour == 9) | (hour == 10)) & kindle_dates.IsWorkingDay(eventsList):
        RenderWeekdayMorning()
    else:
        RenderWeekdayOther()
    
    updateMessage = str(datetime.datetime.today())[0:16]
except:
    updateMessage = "Update Failed " + str(datetime.datetime.today())[11:16] + " - "

# kindle_graphics.weatherooSmall.DrawCentred(0, 10, 10)
    
kindle_graphics.trebuchet_11px.Print(updateMessage, 1,1)
kindle_graphics.RenderBatteryLife(0,0,0)
kindle_graphics.WriteImageToKindleScreen("weather.png")
#email_update.UpdateFromEmail()


#kindle_email.send_email_attachment("weather.png", emailMessage)

# /etc/init.d/framework stop 
# gasgauge-info -m
