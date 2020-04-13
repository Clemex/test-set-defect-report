# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:01:09 2020

@author: Roch Tourigny
Company: Clemex Technologies inc.

@Contributors:

an attempt to create a custom report for defects encountered during a testset execution.

from the exported xml files, 
fill a data frame with pertinent info:
 suite, plan, test, testcase, status, Jira Issue link
use jinja and an html template to generate an html report
it is possible to use pdfkit to generate a pdf from the html
open the html and copy paste the content to a Confluence report page, perhaps in an Expand macro.

to do:
 implement a search tool for the notes in case of a manual test.
"""

import sys
import xml.etree.ElementTree as ET
from atlassian import Jira

#Globals
defectnumber = 0    # will serve as index to retreive data from dictionary in same order as inserted.
df = {}
JiraProject = 'Your Jira Project Name Goes Here'
JiraUrl = 'Your Jira Url goes Here'

jira = Jira(
url=JiraUrl,
username='YourUserName',
password='YourToken')

def details(LevelX, testinfo):
	"""
		this function retreives the error information from the XML files
		then gets known Jira issues keys and summary
		then updates the data frame
		
		INPUT
		LevelX is the current test node of the XML file
		testinfo is a list of strings, et this stage, the testset name, suite name and plan name are known
		
		OUTPUT
		df is a python dictionary of defect information
	"""
    JQL = ''
    global defectnumber
    global df
    global jira
	global JiraProject
    # Get the errors from the Xml file
    try:
        detailsNode = LevelX.find('OutputDir')
        detailsDir = detailsNode.text
        detailsTree = ET.parse(sys.argv[1] + "/" + detailsDir + "/" + 'Output.xml')
        detailsRoot = detailsTree.getroot()
        
        # append details to return list
		# manual test will require a search for note
        for textline in detailsRoot.findall('Line'):
            if textline.attrib['Type'] == 'Error':
                testinfo[4] += textline.text + '<br />'
            elif textline.attrib['Type'] == 'Verify':
                try:
                    if textline.attrib['Error'] == 'true':
                        testinfo[4] += textline.text + '<br />'
                except:
                    print ('Verify action passed')
    except:
        print('detail :', testinfo)
# get Jira info
    try:
        detailsNode = LevelX.find('OutputDir')
        detailsDir = detailsNode.text
        JiradetailsTree = ET.parse(sys.argv[1] + "/" + detailsDir + "/" + 'Test.xml')
        JiradetailsRoot = JiradetailsTree.getroot() 

        for Jiratextline in JiradetailsRoot.iter('Node'):
            TestIdToLookFor = Jiratextline.attrib['GUID']
            #build the query
            JQL = 'project = ' + JiraProject + ' AND ("Test Identifiers" ~ "'+TestIdToLookFor+'")AND (status!=Resolved) ORDER BY issuekey'
            
            data = jira.jql(JQL)
            #print(data)
            Bugs = data.get('total')
            if Bugs > 1:
                print ('There are multiple issues with this test')
            JiraIssue = ''
            issues = data.get('issues')
            for issue in range (Bugs):
                # use tags to make an hyperlink to the issues
                JiraIssue += '<a href = "' + JiraUrl + issues[issue].get('key') + '">'
                JiraIssue += issues[issue].get('key')
                JiraIssue += ' | ' + issues[issue].get('fields').get('status').get('name')
                JiraIssue += ' | ' + issues[issue].get('fields').get('summary')+'</a><br />'
			# append Jira issue hyperlink to the list of strings
            testinfo[5] += JiraIssue
#            print ('Jira issues =', JiraIssue)
    except:
        print ('Error getting Jira issues', JQL)
    # save to dictionary
    df.update({defectnumber: testinfo})
    defectnumber+=1

def TestNode(LevelX, suiteplan):
	"""
		this function verifies if a test failed, if so it call details to complement information 
		
		INPUT
		LevelX is the current test node of the XML file
		suiteplan is a list of strings, et this stage, the testset name, suite name and plan name are known
		
		OUTPUT
		none
	"""
    testlist = ['', '', '', '']
    # In a test node, there can be multiple test cases
    multiple = LevelX.findall('Entity')
    if len(multiple) > 1:
        # iterate all test cases
        print('multiple')
        for testcase in LevelX.findall('Entity'):
            for Status in testcase.iter('TestStatus'):
                if ET.iselement(Status):
                    teststatus = Status.text
                    if teststatus == 'Failed':
                        testlist[0] = LevelX.attrib['Name']
                        testlist[1] = testcase.attrib['Name']
                        details(testcase,suiteplan + testlist)
                else:
                    print('Status not found ', LevelX.attrib['Name'])
    else:
        print('single')
        single = LevelX.find('Test')
        Status = single.find('TestStatus')
        if ET.iselement(Status):
            teststatus = Status.text
            if teststatus ==  'Failed':
                testlist[0] = LevelX.attrib['Name']
                testlist[1] = ''
                details(LevelX, suiteplan + testlist)
        else:
            print('Status not found ', LevelX.attrib['Name'])
         
            
def main(argv):
    global df
    # Some var
    TestSetName = ''
    BuildVersion = ''
    Header = ['Suite', 'Plan', 'Test', 'Test Case', 'Status', 'Jira Issue Summary']
    # we receive input path if used from within AT using generate custom report
    # if used from a bath file, first call atexport to obtain the xml files for the testset
    # then call this script supplying both path and a file name
    try:
        reportName = '/' + str(sys.argv[3])
    except:
        reportName = "/TestSetDefects.html"
    inputpath = sys.argv[1] + "/TestSet.xml"
    outputpath = sys.argv[2]  + reportName
#    print('input =', inputpath)
#    print('output = ', outputpath)
    

    tree = ET.parse(inputpath) # open the testset report
    root = tree.getroot() #start at the root of the xml document.

    # get the name of the test set and the build version
    try:
        TestSetName = root.find('Name').text
    except:
        print('unable to locate test set name')
    try:
        BuildVersion = root.find('BuildNumber').text
    except:
        print('unable to locate Build Version')
        

    # support only 4 levels of xml, usually ok for suite->plans->tests->test case
    # the test node function will support test cases for a single test
    for Level1 in root.findall('Entity'):
        print('level 1')
        if Level1.attrib['Kind'] == 'Node':
            TestNode(Level1, ['', ''])
        else:
            for Level2 in Level1:
                print('level 2')
                if Level2.attrib['Kind'] == 'Node':
                    TestNode(Level2, ['', Level1.attrib['Name']])
                else:
                    for Level3 in Level2:
                        print('level 3')
                        if Level3.attrib['Kind'] == 'Node':
                            TestNode(Level3, [Level1.attrib['Name'], Level2.attrib['Name']])
                        else:
                            for Level4 in Level3:
                                print('level 4')
                                if Level4.attrib['Kind'] == 'Node':
                                    TestNode(Level4, [Level1.attrib['Name'], Level2.attrib['Name']])
                                else:
                                    print('not enough levels')

	# at this stage, we shall have the necessary data into df
	# so we can proceed to fill in the template and render it.
    import jinja2
    templateLoader = jinja2.FileSystemLoader(searchpath="C:/Users/roch/Documents/Zeenyx/CustomReport") #C:\Users\roch\Documents\Zeenyx\CustomReport ./
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "Defect_report_Template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    
    outputText = template.render(df=df, Build_Version=BuildVersion, Test_Set=TestSetName, Header=Header)
    html_file = open(outputpath, 'w')
    html_file.write(outputText)
    html_file.close()
    # you can use pdfkit to convert the just created html report to pdf.
	#import pdfkit
	#pdfkit.from_file(outputpath , outputpath + '.pdf')
	
if __name__ == "__main__":
    main(sys.argv[1:])
