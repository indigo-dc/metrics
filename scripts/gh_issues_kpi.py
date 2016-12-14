from datetime import datetime
from github3 import login
import getpass

user = raw_input("GitHub User: ")
password = getpass.getpass()

gh = login(user, password)


def period(f):
    def _period(*args):
        to_date = args[0]
        try:
            from_date = args[1]
            query = "created:%s..%s" % (from_date, to_date)
        except IndexError:
            query = "created:<%s" % to_date
            pass
        return f(query)
    return _period


@period
def get_defect_no(query_period):
    query = ' '.join([
        "is:issue user:indigo-dc label:bug",
        query_period])
    return len([issue for issue in gh.search_issues(query)])

@period
def get_defect_closed_no(query_period):
    query = ' '.join([
        "is:issue user:indigo-dc label:bug is:closed",
        query_period])
    return len([issue for issue in gh.search_issues(query)])

@period
def get_defect_rejected_no(query_period):
    query = ' '.join([
        "is:issue user:indigo-dc label:bug label:invalid",
        query_period])
    return len([issue for issue in gh.search_issues(query)])

def get_defect_removal_efficiency(to_date, *args):
    defect_no = get_defect_no(to_date, *args)
    defect_closed_no = get_defect_closed_no(to_date, *args)
    return (defect_closed_no/float(defect_no))*100

def get_defect_removal_resolution_time(to_date):
    query = "is:issue user:indigo-dc label:bug created:<%s is:closed" % to_date
    l = []
    for issue in gh.search_issues(query):
        l.append((issue.issue.closed_at - issue.issue.created_at).days)
    return sum(l)/float(len(l))

print("## 1st release ##")
major_release = "2016-08-08"
first_update = "2016-09-19"
second_update = "2016-10-11"
third_update = "2016-10-28"
reporting_period = "2016-11-01"

for d in [("major release", major_release),
          ("first update", first_update, major_release),
          ("second update", second_update, first_update),
          ("third update", third_update, second_update)]:
    print("- %s -" % d[0])
    print("* Number of defects: %s"
          % get_defect_no(*d[1:]))
    print("* Number of defects rejected: %s"
          % get_defect_rejected_no(*d[1:]))
    print("* KPI Defect Removal Efficiency: %s"
          % get_defect_removal_efficiency(*d[1:]))
    print("* KPI Rejected Defect Ratio: %s:%s"
          % (get_defect_rejected_no(*d[1:]), get_defect_no(*d[1:])))


print("* KPI Defect Removal Resolution Time: %s"
      % get_defect_removal_resolution_time(reporting_period))
