#!/usr/bin/env python
#
import getopt
import sys
import xml.etree.ElementTree as ET

class PrometheusCollector():

    def __init__(self, outputxml, metricsfile, id):
        """Initialize new instance of Robot Collector"""
        self.outputxml = outputxml
        self.metricsfile = metricsfile
        self.id = id

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
    
        suite_count = 0
    
        for stat in root.find('statistics').find('suite').findall('stat'):
            stat_id     = stat.get('id')
            stat_name   = stat.get('name')
            suite_count += 1
    
            failed  = stat.get('fail')
            skipped = stat.get('skip')
            passed  = stat.get('pass')
    
            labels=f'{{id="{self.id}", suite_id="{stat_id}", suite_name="{stat_name}"}}'
    
            self.write_metric('robot_passed_total', 'Total number of passed tests.', passed, labels)
            self.write_metric('robot_skipped_total', 'Total number of skipped tests.', skipped, labels)
            self.write_metric('robot_failed_total', 'Total number of failed tests.', failed, labels)
    
        self.write_metric('robot_testsuites_total', 'Total number of test suites.', suite_count, f'{{id="{self.id}"}}')

def usage():
    print("Usage: robot_collector [-h|--help] -o|--outputxml <path to output.xml> -m|--metricsfile <metrics file for textfile collector> -i|--id <prometheus identifier for the test results>")
    print()
    print("Options:")
    print("  -h, --help:        print this help message")
    print("  -o, --outputxml:   path to Robot Framework-generated output.xml with the test results")
    print("  -m, --metricsfile: where to save the metrics - should be insider the Prometheus Textfile Collector directory")
    print("  -i, --id:          prometheus identifier for the test results: not to be confused with test suite (output.xml may have several)")
    print()
    sys.exit(2)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:m:i:", ["help", "outputxml=", "metricsfile=", "id="])
    except getopt.GetoptError as err:
        print(err)
        usage()

    outputxml = None
    metricsfile = None
    id = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--outputxml"):
            outputxml = a
        elif o in ("-m", "--metricsfile"):
            metricsfile = a
        elif o in ("-i", "--id"):
            id = a
        else:
            assert False, "unhandled option"

    if outputxml == None or metricsfile == None or id == None:
        usage()

    collector = PrometheusCollector(outputxml, metricsfile, id)
    collector.run()

if __name__ == '__main__':
    main()
