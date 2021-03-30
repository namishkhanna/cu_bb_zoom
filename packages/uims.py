import re, time, csv, os
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as chromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from .miscellaneous import is_connected, connectionCheck, logger, GetUserDetails, fiveFailedAttempts, threeFailedInputs



class UimsManagement():
    """
    This cell handels all the UIMS related data.
    1. Login into UIMS
    2. Download Time Table from UIMS
    3. Checking if internet connection is avaliable.
    4. Loading data from the stored files.

    Attributes:
        fileName: Name of the file in which you want to store the Time Table.
        userName: UID of the student.
        password: password of the student
        chromePath: path to default google chrome profile
    """



    def __init__(self, fileName, userName, password, chromePath, browserName):
        self.fileName = fileName
        self.userName = userName
        self.password = password
        self.chromePath = chromePath
        self.browserName = browserName



    # getting time table from CUIMS
    def getDetailsFromUIMS(self):

        if self.browserName == "Google Chrome":
            # declaring webdriver
            try:
                chrome_options = chromeOptions()
                chrome_options.add_argument("--use-fake-ui-for-media-stream")
                chrome_options.add_argument('log-level=3')
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument('--headless')
                prefs = {"download.default_directory" : str(os.getcwd())}
                chrome_options.add_experimental_option("prefs",prefs)
                driver = webdriver.Chrome(options=chrome_options)
            except:
                logger.error("Check if chromedrivers are in the path")
                input()
                exit()
            

        elif self.browserName == "Brave":
            BraveFlag=False

            try:
                brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
                brave_options = chromeOptions()
                brave_options.add_argument("--use-fake-ui-for-media-stream")
                brave_options.add_argument('log-level=3')
                brave_options.add_argument("--start-maximized")
                brave_options.add_argument('--headless')
                prefs = {"download.default_directory" : str(os.getcwd())}
                brave_options.add_experimental_option("prefs",prefs)
                brave_options.binary_location = brave_path
                driver = webdriver.Chrome(chrome_options=brave_options)
                BraveFlag=True
            except:
                logger.error("Check if chromedrivers are in the path")
            

            if not BraveFlag:
                try:
                    brave_path = "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
                    brave_options = chromeOptions()
                    brave_options.add_argument("--use-fake-ui-for-media-stream")
                    brave_options.add_argument('log-level=3')
                    brave_options.add_argument("--start-maximized")
                    brave_options.add_argument('--headless')
                    prefs = {"download.default_directory" : str(os.getcwd())}
                    brave_options.add_experimental_option("prefs",prefs)
                    brave_options.binary_location = brave_path
                    driver = webdriver.Chrome(chrome_options=brave_options)
                except:
                    logger.error("Check if chromedrivers are in the path")
                    logger.warning("Exiting ..... ")
                    input()
                    exit()
            

        elif self.browserName == "Mozilla Firefox":
            try:
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--use-fake-ui-for-media-stream")
                firefox_options.add_argument('log-level=3')
                firefox_options.add_argument("--start-maximized")
                firefox_options.add_argument('--headless')
                profile = webdriver.FirefoxProfile()
                profile.set_preference("browser.download.folderList", 2)
                profile.set_preference("browser.download.manager.showWhenStarting", False)
                profile.set_preference("browser.download.dir", str(os.getcwd()))
                profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
                driver = webdriver.Firefox(options=firefox_options,firefox_profile=profile)
            except:
                logger.error("Check if geeckodriver are in the path")
                input()
                exit()


        networkAvaliable = connectionCheck()
        if not networkAvaliable:
            is_connected()
        

        logger.info("Logging into UIMS")
        counter = 0


        # entering username and password in CUIMS
        while(networkAvaliable):
            try:
                driver.get('https://uims.cuchd.in/uims/')
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='txtUserId']"))).send_keys(self.userName)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='btnNext']"))).click()
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='txtLoginPassword']"))).send_keys(self.password)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='btnLogin']"))).click()
            except:
                logger.error("Problem Logging in UIMS")
                is_connected()


            # Checking if username and password are correct
            driver.get('https://uims.cuchd.in/UIMS/StudentHome.aspx')
            currentURL = str(driver.current_url) 
            if currentURL!="https://uims.cuchd.in/UIMS/StudentHome.aspx":
                counter+=1
                logger.error("Username or Password is incorrect")
                getDetailsOBJ = GetUserDetails("userData.txt")
                newDetails = getDetailsOBJ.getCorrectDetails()
                self.userName = newDetails['username']
                self.password = newDetails['password']

                # User unable to give valid input
                if newDetails['failInput']:
                    driver.close()
                    input()
                    exit()

                logger.info(f"Username: {self.userName}  Password: {self.password}")
            else:
                logger.info("Logged is successfully to UIMS")
                break
            

            # valid input but not valid cridentials for UIMS
            if counter==3:
                threeFailedInputs()


        # going to time table page
        logger.info("Getting your Time Table")
        counter=0


        while(networkAvaliable):
            counter+=1
            try:
                driver.get('https://uims.cuchd.in/UIMS/frmMyTimeTable.aspx')
                # checking if time table page is opned
                WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='My Time Table']"))).click()
                break
            except:
                logger.error("Problem fetching Time Table")
                is_connected()

            if counter==5:
                fiveFailedAttempts()


        html = driver.page_source
        soup = BeautifulSoup(html,"lxml")
        ControlID = str(soup(text=re.compile('ControlID')))[1722:1754]


        # downloading time table csv file
        while(networkAvaliable):
            url = f'https://uims.cuchd.in/UIMS/Reserved.ReportViewerWebControl.axd?ReportSession=ycmrf5jtz5d1gjjcfk4bleib&Culture=1033&CultureOverrides=True&UICulture=1033&UICultureOverrides=True&ReportStack=1&ControlID={ControlID}&OpType=Export&FileName=rptStudentTimeTable&ContentDisposition=OnlyHtmlInline&Format=CSV'
            try:
                if self.browserName == "Mozilla Firefox":
                    driver.set_page_load_timeout(5)
                driver.get(url)
                time.sleep(2)
                break
            except TimeoutException:
                break
            except:
                logger.error("Problem downloading Time Table")
                is_connected()

        driver.quit()



    # filtering data and extracting necessary details
    def loadDetailsFromFIle(self):
        logger.info("Loading your details ..... ")
        file_path = self.fileName
        Empty = ""
        now = datetime.now()
        day = str(now.strftime("%A"))[:3]
        join = []
        to_join = []
        all_course_name = []
        unique_course_name = []
        zoom_input_course_code = []
        zoom_to_join = []
        row_with_link = []
        row_without_link = []
        is_none = False


        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == "None":
                    is_none = True
                else:
                    is_none = False
                break
        

        if not is_none:
            
            # finding all course code and course name for old csv
            try:
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if(len(row)==2):
                            if(row[1]!='Title'):
                                all_course_name.append(row)
            except:
                logger.error(f"Unable to read file: {file_path}")
                logger.info("Exiting the program .....")
                input()
                exit()
            

            # finding unique course code and course name for old csv
            for x in all_course_name: 
                if x not in unique_course_name: 
                    unique_course_name.append(x) 

            row_number = 0
            try:
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        row_number += 1
                        if(len(row)==3):
                            if(row[2]!='CourseCode'):
                                if(row[2]!=Empty):
                                    if(row[2].split(':')[1]!='L'):
                                        zoom_input_course_code.append([row_number,row[0],row[1],row[2].split(':')[0]])
                                        row_with_link.append(row_number)
                                    else:
                                        row_without_link.append(row_number)
                    file.close()
            except:
                logger.error(f"Unable to read file: {file_path}")
                logger.info("Exiting the program .....")
                input()
                exit()


            # joining time, day and course name
            for i in zoom_input_course_code:
                for j in unique_course_name:
                    if(i[3]==j[0]):
                        zoom_to_join.append([i[0],i[2],i[1],j[1].lstrip()])
        

            # displaying all practical lectures
            print()
            print("Total Practical Lectures: ")
            for i in range(len(zoom_to_join)):
                print(str(i+1) + ": " + zoom_to_join[i][1] + "->" + " " + zoom_to_join[i][2] + "->" + " " + zoom_to_join[i][3])
            print()


            print("Enter Zoom Links for all Practical Lectures...")
            for i in range(len(zoom_to_join)):
                print(str(i+1) + ": " + zoom_to_join[i][1] + "->" + " " + zoom_to_join[i][2] + "->" + " " + zoom_to_join[i][3])
                print("Enter Zoom Link: ")
                link_input = input()
                zoom_to_join[i].append(link_input)
                print()

            # creating new csv with zoom links
            new_csv = []
            row_len = 0
            try:
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        row_len += 1
                        if row_len in row_with_link:
                            for j in zoom_to_join:
                                if row_len == j[0]:
                                    row.insert(0, j[4])
                        else:
                            row.insert(0,"None")
                        new_csv.append(row)
                os.remove(file_path)
                file = open(file_path, 'w+', newline ='')
                with file:    
                    write = csv.writer(file)
                    write.writerows(new_csv)
            except:
                logger.error(f"Unable to read file: {file_path}")
                logger.info("Exiting the program .....")
                input()
                exit()


        ############################ DISPLAYING ###################################
        # finding all course code and course name for new csv
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if(len(row)==3):
                        if(row[2]!='Title'):
                            all_course_name.append([row[1], row[2]])
        except:
            logger.error(f"Unable to read file: {file_path}")
            logger.info("Exiting the program .....")
            input()
            exit()
        

        # finding unique course code and course name for new csv
        for x in all_course_name: 
            if x not in unique_course_name: 
                unique_course_name.append(x) 


        # finding time and course code for particular day
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if(len(row)==4):
                        if(row[3]!='CourseCode'):
                            if(row[3]!=Empty):
                                if(row[2]==day):
                                    to_join.append([row[1].split(" ")[0] + " " + row[1].split(" ")[3], row[3].split(':')[0], row[0]])
        except:
            logger.error(f"Unable to read file: {file_path}")
            logger.info("Exiting the program .....")
            input()
            exit()


        # joining time and course name for particular day
        for i in to_join:
            for j in unique_course_name:
                if(i[1]==j[0]):
                    join.append([i[0], j[1].lstrip(), i[2]])
                    

        # displaying all lectures for particular day
        print()
        print("Total Lectures Today: ")
        for i in range(len(join)):
            print(str(i+1) + ": " + join[i][0] + " " + join[i][1])
        print()

        return join
