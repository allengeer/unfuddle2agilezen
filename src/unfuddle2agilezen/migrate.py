import json

__author__ = 'ageer'


import getpass
import simplejson
import sys
import urllib2
import requests
import re
import ConfigParser

from datetime import datetime, date

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print "skip: %s" % option
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

Config = ConfigParser.ConfigParser()
Config.read("settings.txt")

ACCOUNT_DETAILS = {
    'account': ConfigSectionMap("Unfuddle")['site'],
    'username': ConfigSectionMap("Unfuddle")['user'],
    'password': ConfigSectionMap("Unfuddle")['pass'],
}
SEND_MAIL = False



class Unfuddle(object):
    def __init__(self):
        self.base_url = 'https://%s.unfuddle.com' % (ACCOUNT_DETAILS['account'])
        self.api_base_path = '/api/v1/'

    def get_data(self, api_end_point):
        # url = 'https://subdomain.unfuddle.com/api/v1/projects'
        url = self.base_url + self.api_base_path + api_end_point

        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Unfuddle API',
                                  uri=url,
                                  user=ACCOUNT_DETAILS['username'],
                                  passwd=ACCOUNT_DETAILS['password'])

        opener = urllib2.build_opener(auth_handler)
        opener.addheaders = [('Content-Type', 'application/xml'), ('Accept', 'application/json')]

        # print '', url, ''
        try:
            response = opener.open(url).read().strip()
            # print 'response:', response
            return simplejson.loads(response)
        except IOError, e:
            print IOError, e

    def get_projects(self):
        return self.get_data('projects')

    def select_project(self):
        projects = self.get_projects()
        if len(projects) == 1:
            print 'There is only one project "%s"' % (projects[0]['title'])
            return projects[0]
        for index, project in enumerate(projects):
            print '%s. %s' % (index+1, project['title'])
        project_index = int(raw_input('Enter the project number: ')) - 1
        return projects[project_index]

    def get_tickets(self, project=None):
        if not project:
            project = self.select_project()
        api_end_point = 'projects/%s/tickets' % (project['id'])
        tickets = self.get_data(api_end_point)
        return project, tickets

    def dynamic_report(self, project=None, query_string=None):
        if project:
            api_end_point = 'projects/%s/ticket_reports/dynamic' % (project['id'])
        else:
            api_end_point = 'ticket_reports/dynamic'
        if query_string:
            api_end_point += '?%s' % (query_string)
        dynamic_report = self.get_data(api_end_point)
        return dynamic_report



def migrateActiveMilestoneTicketsToStory(projectid, milestoneid, agileprojectid, storyname, size=None, priority=None, owner=None, tags=None):
    """
    Migrates a milestone to a new story in AgileZen. All active tickets are created as tasks.
    projectid - unfuddle project id
    milestoneid - unfuddle milestone id to get active tix from
    agileprojectid - agile project id to use
    storyname - title of the story to create
    size - time commitment of story
    priority - self explanatory
    owner - the owner id or username of this story
    tags - array of tags for this story
    """
    u = Unfuddle()

    tix = u.get_data("projects/%s/milestones/%s/active_tickets?limit=1000" %(projectid, milestoneid) )

    tasks = []
    for ticket in tix:
        if ticket.get("summary", None) is not None:
            tasks.append({"text": ticket.get("summary", None)[:255] })

    payload = { "text": storyname,
         "size": size,
         "priority": priority,
         "owner":owner,
         "tags": tags,
         "tasks": tasks
    }


    url = 'https://agilezen.com/api/v1/projects/%s/stories' % agileprojectid
    headers = {"X-Zen-ApiKey":ConfigSectionMap("Agilezen")['apikey']}
    r = requests.post(url, data=simplejson.dumps(payload), headers=headers)
    return r

migrateActiveMilestoneTicketsToStory(21,1597,63611,"1.3.27 Release", "40 h", "Normal", 84699, ['Siteblox', 'Core', 'Deployment Required'])