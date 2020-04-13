Test Set defect custom report

Intended purpose:
	This custom report is focusing on tests that failed during test set execution.
	If there are any known Jira issues, a summary and link is provided as to help determine
	if the fault is already known.
	
Requirements:
	Python 3.x (I use an Anaconda distribution as it includes a lot of libraries)
	Jinja
	Atalassian-python-api
	
Installation:
	Get an install Python from your prefered source.
	
	open a command line with administrator privileges and issue the following.
	pip install atlassian-python-api
	
	once done, follow with:
	pip install Jinja2
	
	copy the python script and the HTML template to a folder where the person logged in at test execution has read acces permission.
	C:\users\testeremeritus\documents\zeenyx\customreports
	
	copy or create a batch file in Ascential test folder for this user.
	Foler: 
		C:\Users\testeremeritus\AppData\Local\Zeenyx\AscentialTest\Reports
	File:
		TestSetDefect.cmd
		contains a single line.
		python C:\Users\testeremeritus\Documents\Zeenyx\CustomReport\TestsetDefectCR.py %1 %2
	

Usage:
	You must edit the python script to include your Jira URL and credentials in order to provide acces to Atlassian Jira.
	You must also provide a project name.
	Since this is based on REST-api, you will need a token from Atlassian.
	If Ascential Test is already set for defect tracking with Jira, you can use the same token.
	To obtain a new token, visit your Jira account settings page, then the security page from which you can have acces to the 'Create and manage API token' page.
	
	Please read Ascential Test help document to familiarize yourself with the processes involving a custom report
	and obtain further details.
	
	On each computer used to generate the custom report, the test set has to be exported at least once.
	
	If you run your test set from the command line, a third argument can be suppplied to specify a file name
	ex:
	python C:\Users\testeremeritus\Documents\zeenyx\CustomReport\TestsetDefectCR.py "C:\Temp\UA" "C:\users\testeremeritus\desktop" "UA_W10_64_DefectSummary.html"
	
	The resulting report is a HTML document that can be opened with your favorite browser and the content can be copied to a Confluence page or the like.
	You cal also use the package pdfkit to convert this document to pdf.
	
Credits:
	Creator: Roch Tourigny
	Contributors:
	
	Clemex Tecnologies inc. management to allow and encourage community sharing.
	