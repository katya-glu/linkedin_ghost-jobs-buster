from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

class Crawler:

    # consts
    driver_path = 'chromedriver.exe'
    website = 'https://www.linkedin.com/'
    jobs_path = "jobs/"
    user_email = 'your_email'
    user_password = 'your_password'
    job_description = "software developer"
    address = "Tel Aviv District"

    def __init__(self):
        self.service = Service(self.driver_path)
        self.user_name = ""
        self.password = ""
        self.login_button = ""
        self.security_check_on_login = False
        self.jobs_with_description = []
        self.open_browser()


    def open_browser(self):
        chr_options = Options()
        chr_options.add_experimental_option("detach", True)
        chr_options.add_argument("--start-maximized")
        self.browser = webdriver.Chrome(service=self.service, options=chr_options)
        self.browser.get(self.website)


    def login(self):
        self.user_name = self.browser.find_element('id', 'session_key')
        self.user_name.clear()
        self.user_name.send_keys(self.user_email)
        self.password = self.browser.find_element('id', 'session_password')
        self.password.clear()
        self.password.send_keys(self.user_password)
        self.password.send_keys(Keys.RETURN)


    def job_search(self):
        # go to the Jobs section
        job_link = self.browser.find_element(By.LINK_TEXT, "Jobs")
        job_link.click()
        time.sleep(3)

        # introduce keyword and location and hit enter
        search_keyword = self.browser.find_element(By.CLASS_NAME, 'jobs-search-box__keyboard-text-input')
        search_keyword.clear()
        search_keyword.send_keys(self.job_description)
        time.sleep(1)
        search_location = self.browser.find_element(By.CSS_SELECTOR, "[aria-label='City, state, or zip code']")
        search_location.clear()
        search_location.send_keys(self.address)
        time.sleep(1)
        search_location.send_keys(Keys.RETURN)


    def filter(self):
        # select all filters, click on entry level button
        all_filters_button = self.browser.find_element(By.CLASS_NAME, "search-reusables__all-filters-pill-button")
        all_filters_button.click()
        time.sleep(1)
        WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-experience-2']"))).click()
        time.sleep(1)
        show_results_button = self.browser.find_element(By.CLASS_NAME, "search-reusables__secondary-filters-show-results-button")
        show_results_button.click()


    def find_offers(self):
        #find the total amount of results (if > 24)
        total_results = self.browser.find_element(By.CLASS_NAME, "display-flex.t-12.t-black--light.t-normal.jobs-search-results-list__text")
        total_results_int = int(total_results.text.split(" ", 1)[0].replace(",", ""))
        print("Total jobs num is:", total_results_int)

        time.sleep(4)

        # get results for the first page and append to jobs_with_description list
        curr_page = self.browser.current_url
        results = self.browser.find_elements(By.CLASS_NAME, 'ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item')
        #print("Jobs num on first page is: ", len(results))
        for index, job in enumerate(results):
            hover = ActionChains(self.browser).move_to_element(job)
            hover.perform()
            title = job.find_element(By.CLASS_NAME, 'disabled.ember-view.job-card-container__link.job-card-list__title')
            title.click()
            time.sleep(1)
            description = self.browser.find_element(By.CLASS_NAME, 'jobs-description-content__text')
            details = self.browser.find_element(By.CLASS_NAME, 'mt5.mb2')
            #print(f'{index}, {job.text},{description.text} \n \n \n')
            job_with_description = [job.text, details.text, description.text]
            self.jobs_with_description.append(job_with_description)

        test_job = self.jobs_with_description[0]
        details = test_job[1]
        print("Job details: ", details)

        # if there is more than one page - find page and get all jobs from that page
        """if total_results_int > 24:
            time.sleep(2)

            # find the last page and construct url based on total pages amount
            find_pages = self.browser.find_elements(By.CLASS_NAME, 'artdeco-pagination__indicator.artdeco-pagination__indicator--number.ember-view')
            total_pages = find_pages[-1].text
            total_pages_int = int(total_pages)
            get_last_page = self.browser.find_element(By.XPATH, "//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.browser.current_url
            total_jobs = int(last_page.split('start=', 1)[1])

            # go through all pages and job offers and append to jobs_with_description list
            for page_number in range(25, total_jobs+25, 25):
                self.browser.get(curr_page+"&start="+str(page_number))
                time.sleep(2)
                results_ext = self.browser.find_elements(By.CLASS_NAME, 'ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item')
                for index, result_ext in enumerate(results_ext):
                    hover = ActionChains(self.browser).move_to_element(result_ext)
                    hover.perform()
                    title = result_ext.find_element(By.CLASS_NAME,
                                             'disabled.ember-view.job-card-container__link.job-card-list__title')
                    title.click()
                    time.sleep(1)
                    description = self.browser.find_element(By.CLASS_NAME, 'jobs-description-content__text')
                    details = self.browser.find_element(By.CLASS_NAME, 'mt5.mb2')
                    #print(f'{index}, {result_ext.text},{description.text} \n \n \n')
                    job_with_description = [job.text, details.text, description.text]
                    self.jobs_with_description.append(job_with_description)"""

        print("Jobs num in list:", len(self.jobs_with_description))


    def get_jobs_count(self, jobs):
        return jobs.__len__()


    def is_security_check(self):
        curr_url = self.browser.current_url
        print("security_check_on_login", self.security_check_on_login)
        if "checkpoint/challenge/" in curr_url:
            self.security_check_on_login = True
            print("security_check_on_login", self.security_check_on_login)

    def pass_security_check(self):
        linkedin_logo = self.browser.find_element(By.ID, "linkedin-logo")

        """action = webdriver.common.action_chains.ActionChains(self.browser)
        for y_offset in range(50, 1000, 20):
            for x_offset in range(0, 800, 20):
                action.move_to_element_with_offset(linkedin_logo, x_offset, y_offset)
                action.click()
                action.perform()"""
        #verify_button.click()
        #WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='button']"))).click()


if __name__ == "__main__":
    new_crawler = Crawler()
    new_crawler.login()
    new_crawler.is_security_check()
    if not new_crawler.security_check_on_login:
        new_crawler.job_search()
        time.sleep(2)
        new_crawler.filter()
        time.sleep(2)
        new_crawler.find_offers()
    else:
        print("Security check active..")
        time.sleep(10)
        new_crawler.pass_security_check()