import time, re

import pyautogui
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium import common
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())


class TwitterClient():
    # driver = None
    def __init__(self, session_path=None):
        options = webdriver.ChromeOptions()
        if session_path is not None:
            options.add_argument('--user-data-dir=' + session_path)
        # options.add_argument('--headless')
        options.add_argument("--disable-notifications")
        options.add_argument('--window-size=1920,1080')
        chromedriver_path = ChromeDriverManager().install()
        self.driver = webdriver.Chrome(chromedriver_path, options=options)

    def login(self, username=None, password=None):
        try:
            self.driver.get('https://twitter.com/i/flow/login')
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//input[contains(@autocomplete, "username")]')))
            current_url = self.driver.current_url
            username_input = self.driver.find_element(By.XPATH, '//input[contains(@autocomplete, "username")]')
            username_input.send_keys(username)
            username_input.send_keys(Keys.ENTER)

            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//input[contains(@autocomplete, "current-password")]')))
            password_input = self.driver.find_element(By.XPATH, '//input[contains(@autocomplete, "current-password")]')
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 15).until(lambda driver: driver.current_url != current_url)
        except:
            print('[-] Error logging in')

    def logout(self):
        if not self.is_logged_in:
            return
        try:
            self.driver.get('https://twitter.com/home')
            time.sleep(4)
            self.driver.find_element(By.XPATH, "//div[@data-testid='SideNav_AccountSwitcher_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            self.driver.find_element(By.XPATH, "//div[@data-testid='SideNav_AccountSwitcher_Button']").click()
        time.sleep(1)
        try:
            self.driver.find_element(By.XPATH, "//a[@data-testid='AccountSwitcher_Logout_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//a[@data-testid='AccountSwitcher_Logout_Button']").click()
        time.sleep(3)
        try:
            self.driver.find_element(By.XPATH, "//div[@data-testid='confirmationSheetConfirm']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            self.driver.find_element(By.XPATH, "//div[@data-testid='confirmationSheetConfirm']").click()
        time.sleep(3)
        self.is_logged_in = False

    def is_logged_in(self):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')

        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                (By.XPATH, '//div[contains(@data-testid, "SideNav_AccountSwitcher_Button")]')))
            menu_item = self.driver.find_element(By.XPATH,
                                                 '//div[contains(@data-testid, "SideNav_AccountSwitcher_Button")]')
            if menu_item:
                return True
            else:
                return False
        except Exception as e:
            return False

    def get_trends(self):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')
            time.sleep(3)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[contains(@data-testid,"trend")]')))
        trends = []
        try:
            trends_sections = self.driver.find_elements(By.XPATH, '//div[contains(@data-testid,"trend")]')
            for trend in trends_sections:
                trend_span = trend.find_elements_by_xpath('.//span')
                if trend_span and len(trend_span) > 2:
                    trends.append({
                        'element': trend,
                        'text': trend_span[1].text
                    })
            return trends
        except Exception as e:
            return trends

    def walk_home(self, tweets_count=10):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')
            time.sleep(3)
        if "Home" not in self.driver.title:
            home_link = self.driver.find_element(By.XPATH, '//a[contains(@data-testid, "AppTabBar_Home_Link")]')
            home_link.click()
        actions = ActionChains(self.driver)
        tweets = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//article[contains(@data-testid, "tweet")]')))
            while (len(tweets) < tweets_count):
                print('tweet lenght', len(tweets))
                tweets_list = self.driver.find_elements(By.XPATH, '//article[contains(@data-testid, "tweet")]')
                offset = len(tweets) % 13
                for tweet in tweets_list[offset:]:
                    position = tweet.location
                    size = tweet.size
                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'],
                                               position['y'])

                    links = tweet.find_elements_by_xpath('.//a[contains(@role, "link")]')
                    username_link = links[1]
                    post_link = None
                    for link in links:
                        if "/status/" in link.get_attribute('href'):
                            post_link = link
                            break
                    tweets.append({
                        'elements': {
                            'tweet': tweet,
                            'post_link': post_link,
                            'username': username_link
                        },
                        'username': username_link.get_attribute('href').split('twitter.com/')[1],
                        'post_id': post_link.get_attribute('href').split('/')[-1],
                        'location': position,
                        'size': size,
                    })

                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'],
                                               position['y'] + size['height'])
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(3)
            return tweets
        except Exception as e:
            print(e)
            return tweets

    def get_more_tweets(self, previously_scrapped=0, tweets_count=10, last_element=None):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')
            time.sleep(3)
        if "Home" not in self.driver.title:
            home_link = self.driver.find_element_by_xpath('//a[contains(@data-testid, "AppTabBar_Home_Link")]')
            home_link.click()
        actions = ActionChains(self.driver)
        tweets = []
        try:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            if last_element:
                self.driver.execute_script('window.scroll(arguments[0], arguments[1])', last_element['location']['x'],
                                           last_element['location']['y'] + last_element['size']['height'])
                time.sleep(3)
            print('[+] start loading more')
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//article[contains(@data-testid, "tweet")]')))
            while (len(tweets) < tweets_count):
                tweets_list = self.driver.find_elements(By.XPATH, '//article[contains(@data-testid, "tweet")]')
                offset = (len(tweets) + previously_scrapped) % 13
                print('total tweets found: ', len(tweets))
                for tweet in tweets_list[offset:]:
                    position = tweet.location
                    size = tweet.size
                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'],
                                               position['y'])
                    links = tweet.find_elements_by_xpath('.//a[contains(@role, "link")]')
                    username_link = links[1]
                    post_link = None
                    for link in links:
                        if "/status/" in link.get_attribute('href'):
                            post_link = link
                            break
                    tweets.append({
                        'elements': {
                            'tweet': post_link,
                            'username': username_link
                        },
                        'username': username_link.get_attribute('href').split('twitter.com/')[1],
                        'post_id': post_link.get_attribute('href').split('/')[-1],
                        'location': position,
                        'size': size,
                    })

                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'],
                                               position['y'] + size['height'])
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(3)
            return tweets
        except Exception as e:
            print('Exception', e)
            return tweets

    def like_tweets(self, cycles=10):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        for i in range(cycles):
            try:
                self.driver.find_element(By.XPATH, "//div[@data-testid='like']").click()
            except Exception as e:
                print(e)

            time.sleep(1)
            self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight/1.5)')
            time.sleep(5)

    def subscribe(self, user):
        try:
            self.driver.get(f'https://twitter.com/{user}')
            time.sleep(10)

            # data-testid="40255499-follow"
            # follow user
            self.driver.find_element(By.XPATH, "//div[@data-testid='40255499-follow']").click()

        except Exception as e:
            print(e)

    def Unfollow(self, user):
        try:
            self.driver.get(f'https://twitter.com/{user}')
            time.sleep(10)

            # data-testid="40255499-follow"
            # follow user
            self.driver.find_element(By.XPATH, "//div[@data-testid='40255499-unfollow']").click()
            self.driver.find_element(By.XPATH, "//div[@data-testid='confirmationSheetConfirm']").click()

        except Exception as e:
            print(e)

    # Search By keyword and like the 10 latest postes
    def search_tweet(self, hashtag, cycles=10):
        no_of_pagedowns = 10
        # here we can search a url and determind what changes per search and replicate it with an f string, and passing the value/s that change
        self.driver.get('https://twitter.com/search?q=' + hashtag + '&src=typd')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        self.driver.find_element(By.XPATH,
                                 "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[1]/div[2]/nav/div/div[2]/div/div[2]").click()
        elem = self.driver.find_element(By.TAG_NAME, "body")
        time.sleep(3)

        for i in range(cycles):
            self.driver.find_element(By.XPATH, "//div[@data-testid='like']").click()

        while no_of_pagedowns:
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(1.5)
            no_of_pagedowns -= 1

    # Search by keyword
    def search_hashtag(self, hashtag):

        if not self.is_logged_in:
            raise Exception("You must log in first!")

        try:

            self.driver.get(f'https://twitter.com/search?q={hashtag}&src=typd')

            time.sleep(3)

            for i in range(1, 3):
                self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')

                time.sleep(3)

        except Exception as e:

            print(e)

    def like_post(self, user_id=None, post_id=None):
        if not self.is_logged_in:
            raise Exception("You must log in first!")
        try:
            self.driver.get('https://twitter.com/' + user_id + '/status/' + post_id)
            time.sleep(3)
            btn_react = self.driver.find_element(By.XPATH, "//div[@data-testid='like']")
            btn_react.click()
            time.sleep(1)
            return True
        except Exception as e:
            print(e)
            print('Cannot like this post')

    def retweet_post(self, user_id=None, post_id=None):
        if not self.is_logged_in:
            raise Exception("You must log in first!")
        try:
            self.driver.get('https://twitter.com/' + user_id + '/status/' + post_id)
            time.sleep(3)
            self.driver.find_element(By.XPATH, "//div[@data-testid='retweet']").click()
            self.driver.find_element(By.XPATH, "//div[@data-testid='retweetConfirm']").click()
            time.sleep(1)
            return True
        except Exception as e:
            print(e)
            print('Cannot retweet this post')

    def comment(self, user_id, post_id, comment):
        try:
            self.driver.get('https://twitter.com/' + user_id + '/status/' + post_id)
            time.sleep(3)
            self.driver.find_element(By.XPATH, "//div[@data-testid='reply']").click()
            time.sleep(5)

            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@data-testid="tweetTextarea_0"]')))

            comment_section = self.driver.find_element(By.XPATH, '//div[@data-testid="tweetTextarea_0"]')
            time.sleep(5)
            comment_section.send_keys(comment)
            time.sleep(5)
            comment_section.send_keys(Keys.ENTER)

            reply_button = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@data-testid='tweetButton']")))
            reply_button.click()
            #Comment with hashtag

            time.sleep(5)

        except:
            print('[-] Cannot Comment ')

    def close(self):
        self.driver.close()
