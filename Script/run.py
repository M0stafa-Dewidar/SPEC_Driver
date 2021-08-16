#   File: sandbox.py
#   Author: Mostafa Dewidar
#   DATE: 08/13/2021
#   Description: This scrript runs SPECviewPerf2020 on the sw viewset for 3 iterations, 
#   records processor and Memory Utilization during said iterations using perfmon,
#   and generates a pdf report will all collected data
# 

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from multiprocessing import Process
from reportlab.pdfgen.canvas import Canvas
import xml.etree.ElementTree as ET
import re


#constants used as parameters to the program
num_iterations = 3
installation_dir = 'C:\\SPEC\\SPECgpc\\SPECviewperf2020v2'
perfmon_data_dir = "E:\\Mostafa\\SPECviewPerfmonData"
spec_data_dir = "E:\\Mostafa\\specdata"
final_scores = ["13.97","14.33","14.02"]

# Uses logman in a shell to create a perfmon counter to collect memory and processor 
# utilization data and starts collecting the data
def run_perfmon():
    create_counter_command = ' logman create counter SPECviewPerf -f bin  -b 01/01/2009 00:00:05  -E 01/01/2009 23:59:00 -si 05 -v mmddhhmm -O E:\Mostafa\SPECviewPerfmonData\data -cf E:\Mostafa\Sandbox\SPECviewPerfCounters.config'
    os.system(create_counter_command)
    os.system("logman start SPECviewPerf")

#Stops collecting performance data
def stop_perfmon():
    os.system("logman stop SPECviewPerf")

#Runs SPECviewPerf on the sw viewset and saves the results to an xml file
def run_SPECviewPerf():
    os.chdir(installation_dir)
    command = '\\SPEC\\SPECgpc\\SPECviewperf2020v2\\viewperf\\bin\\viewperf.exe \\SPEC\\SPECgpc\\SPECviewperf2020v2\\viewsets\\sw\\config\\sw.xml -results "E:\\Mostafa\\specdata" -window 10 20 1900 1060 \\SPEC\\SPECgpc\\SPECviewperf2020v2'
    os.system(command)

#runs SPECviewPerf for 3 iterations and records memory and processor utilization data simultaneoulsy
#using perfmon
def run_processes():
    perfmon = Process(target=run_perfmon)
    perfmon.start()
    for i in range(num_iterations):
        SPECview = Process(target=run_SPECviewPerf)
        SPECview.start()
        SPECview.join()
        final_scores.append(get_xml_data())
    stop_perfmon()

#Collects Final score data from the SPECviePerf run
def get_xml_data():
    os.chdir(spec_data_dir)
    #get latest modified directory (this is a hack to get around unpredictable naming conventions of SPECviewPerf result folders)
    all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    path = latest_subdir + '\\results.xml'
    tree = ET.parse(path)
    root = tree.getroot()
    for child in root:
        if child.tag == 'Composite':
            return child.attrib['Score']

# Converts data collected by perfmon from .blg to .csv to faciliate data representation
# And manipulation using pandas and matplotlip.
def relog_perfmon_data():
    os.chdir(perfmon_data_dir)
    os.system('cd')
    all_files = [d for d in os.listdir('.') if os.path.isfile(d)]
    latest_file = max(all_files, key=os.path.getmtime)

    # This is a similar hack to the one used in get_xml_data()
    command = 'relog .\{}  /f csv /o E:\Mostafa\data.csv -y'.format(latest_file)
    print(command)
    os.system(command)

# #replaces all empty cells with 0s
def clean_data(df):
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df.fillna(0, inplace=True)
    df.to_csv("E:\\Mostafa\\clean_data.csv")


#Loads, cleans, and converts perfmon data into graphs.
def process_perfmon_data():
    relog_perfmon_data()
    csv_dir = 'E:\\Mostafa\\data.csv' 
    df = pd.read_csv(csv_dir, index_col=0)
    clean_data(df)
    df = pd.read_csv("E:\\Mostafa\\clean_data.csv",index_col=0)
    os.chdir("E:\\Mostafa\\graphs")
    for i in range(0,len(df.columns)):
        plt.clf()
        plt.close("all")
        plt.figure()
        df.plot(y=df.columns[i],figsize=(20,12),title=df.columns[i])
        plt.savefig("{}.jpeg".format(i))

#Creates a pdf report using the reportlab canvas
def create_report():
    os.chdir("E:\\Mostafa")
    canvas = Canvas("report.pdf")
    return canvas

#adds the graphs to the created pdf canvas
def add_graph(canvas,page_number,x,y):
    canvas.drawInlineImage('E:\\Mostafa\\graphs\\{}.jpeg'.format(page_number),x,y,width=500,height=340)



#creates pages with one graph each
def create_page(canvas, page_number):
    #add numbering
    canvas.drawString(50,800,str(page_number+1))

    #add title
    canvas.drawString(350,800,"SPECviewPerf/Perfmon Report - sw")

    #add line for header
    canvas.line(30,790,560,790)
    add_graph(canvas,page_number, 50,400)
    add_graph(canvas,page_number+1, 50,50)
    canvas.showPage()


def add_cover(canvas,final_scores):
    #add numbering
    canvas.drawString(50,800,str(1))
    canvas.setFont("Helvetica", 24)
    canvas.drawString(100,700,"SPECviewPerf & Perfmon Report")
    canvas.setFont("Helvetica", 11)
    canvas.drawString(100,650,"This report contains results for running the sw viewset for 3 iterations,")
    canvas.drawString(100,620, "as well as memory and processor utilization data obtained during the test using perfmon")
    canvas.setFont("Helvetica", 16)
    canvas.drawString(100,580,"SPECviewPerf Results:")
    canvas.setFont("Helvetica", 12)
    for i in range(len(final_scores)):
        canvas.drawString(100,530 - (i*50),"Final Composite Score from iteration {}: ".format(i+1)  + final_scores[i] + " FPS")
    final_scores = [float(i) for i in final_scores]
    canvas.drawString(100,380,"Final Average Composite Score: " + str(sum(final_scores)/len(final_scores)) + "FPS")
    canvas.setFont("Helvetica", 16)
    canvas.drawString(100,330,"Perfmon Data Follows in the coming pages...")
    canvas.showPage()

#generates pdf report
def generate_report():
    canvas = create_report()
    add_cover(canvas,final_scores)
    for i in range(1,16,2):
        create_page(canvas,i)
    canvas.save()


#Script driver, runs the program
def main():
    run_processes()
    process_perfmon_data()
    generate_report()

if __name__ == "__main__":
    main()