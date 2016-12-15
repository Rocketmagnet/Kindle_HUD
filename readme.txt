Kindle Heads-Up Display and Weather

1)
Edit kindle_main.py
Find the line that calls kindle_weather.FetchWeatherForecast (about line 25).
Edit the string "UK/London.json" to suit your location


2)
If you want your Google calendar events to show on the HUD:
Go to the settings page for your Google Calendar
Copy the private ICAL URL for the calendar
Paste it into one of the calendar_urls
Edit the relevant ??_words.txt file to filter the events

3)
Find the IsWorkingDay() function, and edit it to suit your work week


