import pickle
import datetime
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from Google import convert_to_RFC_datetime

class Calendar():
    def __init__(self, service):
        self.service = service
        
    def get_event(self, start, end, calendarid):
        events_result = self.service.events().list(calendarId=calendarid,
                                            timeMin=start,
                                            timeMax=end,
                                            singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def print_events(self, e):
        if not e:
            print('No upcoming events found.')
        for event in e:
            break
            try:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S')
                print(start, event['summary'])
            except KeyError:
                pass

    def check_duplicate(self, source, target, calendarid):
        s_target_time = target['start']['dateTime']
        e_target_time = target['end']['dateTime']
        for s in source:
            if target['summary'] in s.values():
                if (s_target_time in s['start'].values()) and (e_target_time in s['end'].values()):
                    return True
                else:
                    return False
            else:
                return False

    def delete_events(self, target, calendarID):
        for t in target:
            self.service.events().delete(calendarId=calendarID, eventId=t['id']).execute()

    def insert_events(self, target, calendarid):
        for t in target:
            year, month, day = map(int, t['start']['dateTime'].split('T')[0].split('-'))

            timefrom = convert_to_RFC_datetime(year=year, month=month, day=day, hour=0, minute=0)
            timeto = convert_to_RFC_datetime(year=year, month=month, day=day, hour=23, minute=59)

            source = self.get_event(timefrom, timeto, calendarid)
            if source:
                self.print_events(source)
                if self.check_duplicate(source, t, calendarid):
                    print('already exist')
                else:
                    self.service.events().insert(calendarId=calendarID, body=t).execute()
                    print(t)
            else:
                self.service.events().insert(calendarId=calendarID, body=t).execute()
                print(t)