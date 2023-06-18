import os.path, subprocess
from subprocess import STDOUT, PIPE
import glob
import re
import csv

sourcepath = r'/Users/p.golovnyak/IdeaProjects/otus-repo/gc-homework/src/main/java/ru/calculator/*.java'
outpath = '/Users/p.golovnyak/IdeaProjects/otus-repo/out'
main_class = 'ru.calculator.CalcDemo'


def compile_java(sourcepath: str, outpath: str):
    java_files = glob.glob(sourcepath)
    subprocess.check_call(
        ['javac', '-d', outpath] + java_files
    )


def __get_execution_time(stdout):
    pattern = r'spend msec:(\d+), sec:(\d+)'
    match = re.search(pattern, stdout)

    if match:
        msec = int(match.group(1))
        sec = int(match.group(2))
        return msec, sec
    else:
        raise ValueError('Bad java program was launched')


def execute_java(main_class, classpath, java_options):
    cmd = ['java', '-classpath', classpath] + java_options + [main_class]
    print('Running cmd ' + ' '.join(str(x) for x in cmd))
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    try:
        res = __get_execution_time(stdout)
        return res
    except ValueError:
        print(f'Some problems with java program: {stderr}')
        return 'err', 'err'


gc = '-XX:+UseG1GC'
rest_ops = '-XX:+HeapDumpOnOutOfMemoryError '

compile_java(sourcepath, outpath)
results = []

interesting_heap_sizes = [64, 128, 256, 512, 700, 900, 1024, 1500, 2048]
for heap_size in interesting_heap_sizes:
    java_options = [f'-Xms{heap_size}m', f'-Xmx{heap_size}m', gc]
    try:
        msec, sec = execute_java(main_class, outpath, java_options)
        print(f"Java program was running for sec: {sec}, msec: {msec}\n")
        results.append((f"{heap_size}M", msec))
    except ValueError:
        print("Some problems with java programm")


csv_filename = 'results_optimized.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['heap_size', 'msec'])
    writer.writerows(results)

print(f"Results written to {csv_filename} successfully.")
