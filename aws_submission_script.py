from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time


class AWSDeepRacerAutoSubmitter():
    """ automatically submit model to AWS DeepRacer community races """
    def __init__(self, model, races):
        self.model = model
        self.races = races

        self.driver = webdriver.Chrome( ChromeDriverManager().install() )

    def logIntoAWSConsole(self):
        """ gives you 60 seconds to login in with your user/passcode and RSA. After submitting RSA, the script will take care of the rest """
        url = 'http://bit.ly/2AxojxF'
        self.driver.get(url)

        self.wait = WebDriverWait(self.driver, 60)
        successfulLogin = self.wait.until( EC.presence_of_element_located((By.ID, "aws-services-container-search")) )

        return bool(successfulLogin)

    def submitToRaceRecursively(self):
        """ Until cancelled, continuously submit model to race """
        while True:
            self.wait.until( EC.presence_of_element_located((By.CLASS_NAME, "submitModelButton")) )
            time.sleep(1)

            if self.driver.find_element_by_class_name("submitModelButton").text not in ["Race again", "Enter race"]:
                print('not ready to submit.')
                time.sleep(15)
                continue
            
            raceAgain = self.driver.find_element_by_class_name("submitModelButton").find_element_by_css_selector("button[type='submit']")
            print(raceAgain.text)
            raceAgain.click()

            time.sleep(1)
            self.wait.until( EC.presence_of_element_located((By.CLASS_NAME, "awsui-select-keyboard-area")) )
            dropdown = self.driver.find_element_by_class_name( "awsui-select-keyboard-area").click()
            time.sleep(1)

            model = self.driver.find_element_by_css_selector("div[title='{}']".format(self.model)).click()
            time.sleep(1)

            submit = self.driver.find_element_by_class_name( "awsui-form-actions" ).find_elements_by_css_selector("button[type='submit']")[1]
            time.sleep(3)
            print(submit.text)
            submit.click()


    def connectToRaces(self):
        """ navigate to races """
        racesUrl = 'https://console.aws.amazon.com/deepracer/home?region=us-east-1#communityRaces'
        self.driver.get(racesUrl)

        self.wait.until( EC.presence_of_element_located((By.CLASS_NAME, "awsui-cards-container")) )
        listOfRaces = self.driver.find_elements(By.CLASS_NAME, "awsui-cards-card-container")
        time.sleep(1)
        for li in listOfRaces:
            # spin up a new driver/tab per race?
            if li.find_element_by_class_name("leaderboardCardTopSection__textContainer").find_element_by_class_name("awsui-tooltip-trigger").text in self.races:
                leaderboardButton = li.find_element_by_css_selector("button[type='submit']")
                leaderboardButton.click()

                self.submitToRaceRecursively()
            else: 
                print(li.find_element_by_class_name("leaderboardCardTopSection__textContainer").text)
        time.sleep(10)

    def main(self):
        successfulLogin = self.logIntoAWSConsole()

        if successfulLogin:
            self.connectToRaces()
        else:
            print('login unsuccessful.')

        
submitter = AWSDeepRacerAutoSubmitter(model='ri2018-ASmod28-1pt2-3',races=['htx-fake-race-1'])
submitter.main()
submitter.driver.quit()





