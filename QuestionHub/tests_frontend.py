import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re

class TestFrontend(unittest.TestCase):
    def setUp(self):
        options = webdriver.EdgeOptions()
        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/')
        time.sleep(5) 

    def tearDown(self):
        self.driver.quit()
            
    def login(self):
        login_page_element = "body > nav > div.user-menu > ul > li:nth-child(1) > a"
        username_element = "#id_username"
        password_element = "#id_password"
        username = "testuser"
        password = "Password123!"
        login_button_element = "body > div.Page-login > form > input.submit-button"
        try:
            login_page_button = self.driver.find_element(By.CSS_SELECTOR, login_page_element)
            login_page_button.click()

            username_field = self.driver.find_element(By.CSS_SELECTOR, username_element)
            password_field = self.driver.find_element(By.CSS_SELECTOR, password_element)
            username_field.send_keys(username)
            password_field.send_keys(password)

            login_button = self.driver.find_element(By.CSS_SELECTOR, login_button_element)
            login_button.click()

            time.sleep(5)

        except Exception as e:
            print(f"Login failed: {e}")
            raise

    def test_loggingIn(self):
            username = "testuser"
            username_button_element = "body > nav > div.user-menu > ul > li > button"
            try:
                self.login()
                username_button = self.driver.find_element(By.CSS_SELECTOR, username_button_element)
                actual_username = username_button.text
                self.assertEqual(actual_username, username, f"Expected Username: {username}, Actual Username: {actual_username}")

                print("Test passed: Login functionality tested successfully.")

            except AssertionError as e:
                print(f"Test failed: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")          
                
    def test_login_page(self):
        login_element = "body > nav > div.user-menu > ul > li:nth-child(1) > a"

        try:
            login_button = self.driver.find_element(By.CSS_SELECTOR, login_element)
            ActionChains(self.driver).click(login_button).perform()
            time.sleep(5) 

            current_url = self.driver.current_url
            expected_url = 'http://127.0.0.1:8000/login/' 
            self.assertEqual(current_url, expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Login button functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
            
    def test_register_page(self):
        register_element = "body > nav > div.user-menu > ul > li:nth-child(2) > a"

        try:
            register_button = self.driver.find_element(By.CSS_SELECTOR, register_element)
            ActionChains(self.driver).click(register_button).perform()
            time.sleep(5)  

            current_url = self.driver.current_url
            expected_url = 'http://127.0.0.1:8000/register' 
            self.assertEqual(current_url, expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Register button functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
            
    def test_create_post(self):
        
        create_post_element = "body > span > a > i.fa-solid.fa-plus.fa-bounce"
        expected_url = 'http://127.0.0.1:8000/ask/'
        try:
            self.login()
            create_post_button = self.driver.find_element(By.CSS_SELECTOR, create_post_element)
            ActionChains(self.driver).click(create_post_button).perform()
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertEqual(current_url, expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Create post functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")     
                
    def test_create_topic(self):
        
        create_topic_element = "body > nav > div.main-menu > ul > li:nth-child(6) > a"
        expected_url = 'http://127.0.0.1:8000/topic/'
        try:
            self.login()
            create_topic_button = self.driver.find_element(By.CSS_SELECTOR, create_topic_element)
            ActionChains(self.driver).click(create_topic_button).perform()
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertEqual(current_url, expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Create topic functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")     

    def test_logout(self):
        user_menu_element = "body > nav > div.user-menu > ul > li > button"
        logout_element = "body > nav > div.user-menu > ul > li > ul > li:nth-child(2) > a"
        expected_url = 'http://127.0.0.1:8000/login/'
        try:
            self.login()
            user_menu_button = self.driver.find_element(By.CSS_SELECTOR, user_menu_element)
            ActionChains(self.driver).click(user_menu_button).perform()
            time.sleep(2)  
            logout_button = self.driver.find_element(By.CSS_SELECTOR, logout_element)
            ActionChains(self.driver).click(logout_button).perform()
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertEqual(current_url, expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Logout functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  

    def test_ordering_button(self):      
        ordering_element = "#orderingOptions > form > select"
        expected_url = 'http://127.0.0.1:8000/?ordering=num_views'
        try:
            self.login()
            ordering_button = self.driver.find_element(By.CSS_SELECTOR, ordering_element)
            ActionChains(self.driver).click(ordering_button).perform()  
            time.sleep(2)  
            ordering_button.send_keys(Keys.DOWN)
            ordering_button.send_keys(Keys.ENTER)
            time.sleep(2)
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertEqual(current_url, expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Ordering functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  

    def test_friend_sidebar(self):     
        friend_sidebar_element = "body > div.user-sidebar > ul > li > a"
        expected_url = r'http:\/\/127.0.0.1:8000\/chat\/friend\/\d+'
        try:
            self.login()
            friend_sidebar = self.driver.find_element(By.CSS_SELECTOR, friend_sidebar_element)
            ActionChains(self.driver).click(friend_sidebar).perform()  
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertIsNotNone(re.search(expected_url, current_url), f"Expected URL pattern: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Friend sidebar functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  

    def test_topic_sidebar(self):   
        trending_topics_element = "body > div.sidebar > ul > li:nth-child(1) > a"
        expected_url = r'http:\/\/127.0.0.1:8000\/topic\/\d+\/'
        try:
            self.login()
            topic_sidebar = self.driver.find_element(By.CSS_SELECTOR, trending_topics_element)
            ActionChains(self.driver).click(topic_sidebar).perform() 
            time.sleep(2)   
            current_url = self.driver.current_url
            self.assertIsNotNone(re.search(expected_url, current_url), f"Expected URL pattern: {expected_url}, Actual URL: {current_url}")


            print("Test passed: Topic sidebar functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  

    def test_topic_search(self):   
        topic_search_element = "body > nav > div.main-menu > ul > li:nth-child(2) > div > button"
        topic_element = "#myDropdown > a:nth-child(3)"
        expected_url = r'http:\/\/127.0.0.1:8000\/topic\/\d+\/'
        try:
            self.login()
            topic_search_menu = self.driver.find_element(By.CSS_SELECTOR, topic_search_element)
            ActionChains(self.driver).click(topic_search_menu).perform()
            time.sleep(2)  
            first_topic = self.driver.find_element(By.CSS_SELECTOR, topic_element)
            ActionChains(self.driver).click(first_topic).perform()
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertIsNotNone(re.search(expected_url, current_url), f"Expected URL pattern: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Topic search functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  
    

    def test_post_search(self): 
        post_search_element = "body > nav > div.main-menu > ul > li:nth-child(3) > div > button"
        post_element = "#myDropdown-post > a:nth-child(2)"
        expected_url = r'http:\/\/127.0.0.1:8000\/post\/\d+\/'
        try:
            self.login()
            post_search_menu = self.driver.find_element(By.CSS_SELECTOR, post_search_element)
            ActionChains(self.driver).click(post_search_menu).perform()
            time.sleep(2)  
            first_post = self.driver.find_element(By.CSS_SELECTOR, post_element)
            ActionChains(self.driver).click(first_post).perform()
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertIsNotNone(re.search(expected_url, current_url), f"Expected URL pattern: {expected_url}, Actual URL: {current_url}")

            print("Test passed: Post search functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  
    
    
    def test_user_search(self):
        user_search_element = "body > nav > div.main-menu > ul > li:nth-child(4) > div > button"
        user_element = "#myDropdown-user > a:nth-child(2)"
        expected_url = r'http:\/\/127.0.0.1:8000\/profile\/\d+\/'
        try:
            self.login()
            user_search_menu = self.driver.find_element(By.CSS_SELECTOR, user_search_element)
            ActionChains(self.driver).click(user_search_menu).perform()
            time.sleep(2)  
            first_user = self.driver.find_element(By.CSS_SELECTOR, user_element)
            ActionChains(self.driver).click(first_user).perform()
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertIsNotNone(re.search(expected_url, current_url), f"Expected URL pattern: {expected_url}, Actual URL: {current_url}")

            print("Test passed: User search functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  
 
    def test_myprofile(self):
        user_menu_element = "body > nav > div.user-menu > ul > li > button"
        myprofile_element = "body > nav > div.user-menu > ul > li > ul > li:nth-child(1) > a"
        expected_url = 'http://127.0.0.1:8000/profile/'
        try:
            self.login()
            user_menu_button = self.driver.find_element(By.CSS_SELECTOR, user_menu_element)
            ActionChains(self.driver).click(user_menu_button).perform()
            time.sleep(2)  
            myprofile_button = self.driver.find_element(By.CSS_SELECTOR, myprofile_element)
            ActionChains(self.driver).click(myprofile_button).perform()
            time.sleep(2)  
            current_url = self.driver.current_url
            self.assertEqual(current_url, expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}")

            print("Test passed: My profile functionality tested successfully.")

        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  
             
if __name__ == '__main__':
    unittest.main()
