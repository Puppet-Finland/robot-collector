#!/usr/bin/env python
#
import getopt
import sys
import xml.etree.ElementTree as ET

class PrometheusCollector():

    def __init__(self, outputxml, metricsfile, testsuite):
        """Initialize new instance of Robot Collector"""
        self.outputxml = outputxml
        self.metricsfile = metricsfile
        self.testsuite = testsuite

    def write_metric(self, name: str, desc: str, val: int, labels: str = '', type: str = 'gauge'):
        with open(self.metricsfile, 'a') as f:
            f.write(f"# HELP {name} {desc}\n")
            f.write(f"# TYPE {name} {type}\n")
            f.write(f"{name}{labels} {val}\n")
    
    
    def clear_metrics(self):
        with open(self.metricsfile, 'w') as f:
            pass
    
    
    def run(self):
        self.clear_metrics()
    
        tree  = ET.parse(self.outputxml)
        root  = tree.getroot()
    
        test_count = 0
    
        for stat in root.find('statistics').find('suite').findall('stat'):
            stat_id     = stat.get('id')
            stat_name   = stat.get('name')
            test_count += 1
    
            failed  = stat.get('fail')
            skipped = stat.get('skip')
            passed  = stat.get('pass')
    
            labels=f'{{suite="{self.testsuite}", suite_id="{stat_id}", suite_name="{stat_name}"}}'
    
            self.write_metric('robot_passed_total', 'Total number of passed tests.', passed, labels)
            self.write_metric('robot_skipped_total', 'Total number of skipped tests.', skipped, labels)
            self.write_metric('robot_failed_total', 'Total number of failed tests.', failed, labels)
    
    
        self.write_metric('robot_tests_total', 'Total number of all tests.', test_count, f'{{suite="{self.testsuite}"}}')

def usage():
    print("Usage: robot_collector [-h|--help] -o|--outputxml <path to output.xml> -m|--metricsfile <metrics file for textfile collector> -t|--testsuite <test suite name>")
    print()
    print("Options:")
    print("  -h, --help:        print this help message")
    print("  -o, --outputxml:   path to Robot Framework-generated output.xml with the test results")
    print("  -m, --metricsfile: where to save the metrics - should be insider the Prometheus Textfile Collector directory")
    print("  -t, --testsuite:   name of the test suite. Used as a label in the produced metrics to distinguish between test suites")
    print()
    sys.exit(2)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:m:t:", ["help", "outputxml=", "metricsfile=", "testsuite="])
    except getopt.GetoptError as err:
        print(err)
        usage()

    outputxml = None
    metricsfile = None
    testsuite = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--outputxml"):
            outputxml = a
        elif o in ("-m", "--metricsfile"):
            metricsfile = a
        elif o in ("-t", "--testsuite"):
            testsuite = a
        else:
            assert False, "unhandled option"

    if outputxml == None or metricsfile == None or testsuite == None:
        usage()

    collector = PrometheusCollector(outputxml, metricsfile, testsuite)
    collector.run()

if __name__ == '__main__':
    main()
