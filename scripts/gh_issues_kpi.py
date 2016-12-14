from datetime import datetime
from github3 import login
import getpass

user = raw_input("GitHub User: ")
password = getpass.getpass()

gh = login(user, password)

def get_defect_no(to_date):
    query = "is:issue user:indigo-dc label:bug created:<%s" % to_date
    return len([issue for issue in gh.search_issues(query)])

def get_defect_closed_no(to_date):
    query = "is:issue user:indigo-dc label:bug created:<%s is:closed" % to_date
    return len([issue for issue in gh.search_issues(query)])

def get_defect_rejected_no(to_date):
    query = ("is:issue user:indigo-dc label:bug created:<%s "
             "label:invalid") % to_date
    return len([issue for issue in gh.search_issues(query)])

def get_defect_removal_efficiency(to_date):
    return (float(get_defect_closed_no(to_date))/get_defect_no(to_date))*100

def get_defect_removal_resolution_time(to_date):
    query = "is:issue user:indigo-dc label:bug created:<%s is:closed" % to_date
    l = []
    for issue in gh.search_issues(query):
        l.append((issue.issue.closed_at - issue.issue.created_at).days)
    return sum(l)/float(len(l))

print("## 1st release ##")
to_date = "2016-11-01"
print("* Number of defects: %s" % get_defect_no(to_date))
print("* Number of defects rejected: %s" % get_defect_rejected_no(to_date))
print("* KPI Defect Removal Efficiency: %s" % get_defect_removal_efficiency(to_date))
print("* KPI Defect Removal Resolution Time: %s"
      % get_defect_removal_resolution_time(to_date))
print("* KPI Rejected Defect Ratio: %s:%s"
      % (get_defect_rejected_no(to_date), get_defect_no(to_date)))
