from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class Crawler:

    # consts
    driver_path = 'chromedriver.exe'
    website = 'https://www.linkedin.com/'
    user_email = 'your_email'
    user_password = 'your_password'

    def __init__(self):
        self.service = Service(self.driver_path)
        self.user_name = ""
        self.password = ""
        self.login_button = ""
        self.open_browser()


    def open_browser(self):
        chr_options = Options()
        chr_options.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(service=self.service, options=chr_options)
        self.browser.get(self.website)


    def login(self):
        self.user_name = self.browser.find_element('id', 'session_key')
        self.user_name.send_keys(self.user_email)
        self.password = self.browser.find_element('id', 'session_password')
        self.password.send_keys(self.user_password)
        self.login_button = self.browser.find_element(By.CLASS_NAME, 'sign-in-form__submit-button')
        self.login_button.click()


new_crawler = Crawler()
new_crawler.login()
