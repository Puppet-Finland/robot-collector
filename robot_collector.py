#!/usr/bin/env python
#
import xml.etree.ElementTree as ET

_RESULTS_FILE = '/home/robot/output.xml'
_METRICS_FILE = '/var/lib/node_exporter/textfile_collector/robot_result.prom'
_TEST_APP     = 'myapp'

def write_metric(name: str, desc: str, val: int, labels: str = '', type: str = 'gauge'):
    with open(_METRICS_FILE, 'a') as f:
        f.write(f"# HELP {name} {desc}\n")
        f.write(f"# TYPE {name} {type}\n")
        f.write(f"{name}{labels} {val}\n")


def clear_metrics():
    with open(_METRICS_FILE, 'w') as f:
        pass


def run():
    clear_metrics()

    tree  = ET.parse(_RESULTS_FILE)
    root  = tree.getroot()

    test_count = 0

    for stat in root.find('statistics').find('suite').findall('stat'):
        stat_id     = stat.get('id')
        stat_name   = stat.get('name')
        test_count += 1

        failed  = stat.get('fail')
        skipped = stat.get('skip')
        passed  = stat.get('pass')

        labels=f'{{test_app="{_TEST_APP}", test_id="{stat_id}", test_name="{stat_name}"}}'

        write_metric('robot_passed_total', 'Total number of passed tests.', passed, labels)
        write_metric('robot_skipped_total', 'Total number of skipped tests.', skipped, labels)
        write_metric('robot_failed_total', 'Total number of failed tests.', failed, labels)


    write_metric('robot_tests_total', 'Total number of all tests.', test_count, f'{{test_app="{_TEST_APP}"}}')

if __name__ == '__main__':
    run()
