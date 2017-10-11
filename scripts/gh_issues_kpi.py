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

## 1st release
print("## 1st release ##")
INDIGO1_major_release = "2016-08-08"
INDIGO1_first_update = "2016-09-19"
INDIGO1_second_update = "2016-10-11"
INDIGO1_third_update = "2016-10-28"
INDIGO1_four_update = "2016-11-16"
INDIGO1_five_update = "2016-12-05"
INDIGO1_six_update = "2016-12-30"
INDIGO1_seven_update = "2017-02-03"
INDIGO1_eight_update = "2017-03-01"
INDIGO1_nine_update = "2017-03-24"
## 2nd release
print("## 2nd release ##")
INDIGO2_major_release = "2017-03-31"
INDIGO2_first_update = "2017-06-01"
INDIGO2_second_update = "2017-07-07"
INDIGO2_third_update = "2017-08-05"
INDIGO2_four_update = "2017-09-01"
INDIGO2_five_update = "2017-09-30"
reporting_period = "2017-10-01"

for d in [
        ("INDIGO1_four_update", INDIGO1_four_update, INDIGO1_third_update),
        ("INDIGO1_five_update", INDIGO1_five_update, INDIGO1_four_update),
        ("INDIGO1_six_update", INDIGO1_six_update, INDIGO1_five_update),
        ("INDIGO1_seven_update", INDIGO1_seven_update, INDIGO1_five_update),
        ("INDIGO1_eight_update", INDIGO1_eight_update, INDIGO1_six_update),
        ("INDIGO1_nine_update", INDIGO1_nine_update, INDIGO1_eight_update),
        ("INDIGO2_major_release", INDIGO2_major_release, INDIGO1_nine_update),
        ("INDIGO2_first_update", INDIGO2_first_update, INDIGO2_major_release),
        ("INDIGO2_major_update", INDIGO2_second_update, INDIGO2_first_update),
        ("INDIGO2_major_update", INDIGO2_third_update, INDIGO2_second_update),
        ("INDIGO2_major_update", INDIGO2_four_update, INDIGO2_third_update),
        ("INDIGO2_major_update", INDIGO2_five_update, INDIGO2_four_update),
    ]:
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
