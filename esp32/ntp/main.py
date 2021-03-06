from machine import RTC
import ntptime

rtc = RTC()
rtc.datetime() # get date and time

# synchronize with ntp
# need to be connected to wifi
ntptime.host = 'us.pool.ntp.org'
ntptime.settime() # set the rtc datetime from the remote server
rtc.datetime()    # get the date and time in UTC

utime.localtime()
