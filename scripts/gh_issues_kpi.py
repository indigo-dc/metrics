from datetime import datetime
from github3 import login
import getpass

user = raw_input("GitHub User: ")
password = getpass.getpass()

gh = login(user, password)
query = "is:issue user:indigo-dc is:closed label:bug closed:<2016-11-01"

def get_defect_removal_resolution_time():
    l = []
    for issue in gh.search_issues(query):
        l.append((issue.issue.closed_at - issue.issue.created_at).days)
    return sum(l)/float(len(l))
