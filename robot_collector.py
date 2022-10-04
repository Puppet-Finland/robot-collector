#!/usr/bin/env python
#
import getopt
import xml.etree.ElementTree as ET

_RESULTS_FILE = '/home/robot/output.xml'
_METRICS_FILE = '/var/lib/node_exporter/textfile_collector/robot_result.prom'
_TEST_APP     = 'myapp'

class PrometheusCollector():

    def __init__(self):
        """TODO"""

    def write_metric(self, name: str, desc: str, val: int, labels: str = '', type: str = 'gauge'):
        with open(_METRICS_FILE, 'a') as f:
            f.write(f"# HELP {name} {desc}\n")
            f.write(f"# TYPE {name} {type}\n")
            f.write(f"{name}{labels} {val}\n")
    
    
    def clear_metrics(self):
        with open(_METRICS_FILE, 'w') as f:
            pass
    
    
    def run(self):
        self.clear_metrics()
    
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
    
            self.write_metric('robot_passed_total', 'Total number of passed tests.', passed, labels)
            self.write_metric('robot_skipped_total', 'Total number of skipped tests.', skipped, labels)
            self.write_metric('robot_failed_total', 'Total number of failed tests.', failed, labels)
    
    
        self.write_metric('robot_tests_total', 'Total number of all tests.', test_count, f'{{test_app="{_TEST_APP}"}}')

if __name__ == '__main__':
    collector = PrometheusCollector()
    collector.run()
