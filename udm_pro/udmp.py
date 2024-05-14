#!/usr/bin/python3

import requests
import json
from datetime import date


class UDM_PRO_API:
    def __init__(self):
        self.TWO_HOURS = 7200
        self.ONE_DAY_IN_HOURS = 86400
        self.UDM_PRO_URL = "https://'<REDACTED>'"
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        self.data = {'username': '<REDACTED>', 'password': '<REDACTED>'}
        self.session = self.get_auth()

    def get_auth(self):
        self.session = requests.Session()
        self.session.post(f'{self.UDM_PRO_URL}/api/auth/login', headers=self.headers, json=self.data,
                          verify=False,
                          timeout=1)
        return self.session

    def get_site_details(self):
        url = f'{self.UDM_PRO_URL}/proxy/network/api/s/default/stat/sysinfo'
        response = self.session.get(url, headers=self.headers, verify=False, timeout=1).text
        site_details = json.loads(response)
        return site_details

    def get_site_health(self):
        url = f'{self.UDM_PRO_URL}/proxy/network/api/s/default/stat/health'
        response = self.session.get(url, headers=self.headers, verify=False, timeout=1).text
        health = json.loads(response)
        return health

    def get_routes(self):
        url = f'{self.UDM_PRO_URL}/proxy/network/api/s/default/rest/routing'
        response = self.session.get(url, headers=self.headers, verify=False, timeout=1).text
        routes = json.loads(response)
        return routes

    def get_events(self):
        url = f'{self.UDM_PRO_URL}/proxy/network/api/s/default/stat/event'
        response = self.session.get(url, headers=self.headers, verify=False, timeout=1).text
        events = json.loads(response)
        return events

    def get_recent_wan_events(self):
        wan_events = []
        events = self.get_events()
        for event in events['data']:
            event_date = event['datetime']
            today_date = str(date.today())
            year_month = today_date[0:7]
            day = int(today_date[8:10])
            if year_month in event_date:
                event_day = int(event_date[8:10])
                if event_day >= (day - 1):
                    if "WAN" in event['msg']:
                        wan_events.append(event)
                        print(f'WAN EVENT: {event} \n\n{event["msg"]} - {event_date}\n\n')

        return wan_events