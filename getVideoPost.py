#!/usr/bin/env python
# coding: utf-8

# In[3]:


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import random
import mysql.connector
from mysql.connector import errorcode
import re
import requests
import os,sys


# In[4]:


options = webdriver.ChromeOptions()

#options.add_argument('headless')


# In[64]:


class page_video_retrieve():
    
    def __init__ (self, conn, driver_path):
        self.conn = conn
        self.cursor=self.conn.cursor()
        self.driver = webdriver.Chrome(driver_path,chrome_options=options)
    
    def logIn(self,name,password):
        self.name=name
        self.password=password
        driver = self.driver
        driver.get('https://www.facebook.com/')
        username = driver.find_element_by_id("email")
        passw = driver.find_element_by_name("pass")
        username.send_keys(name)
        time.sleep(random.randint(1,3))
        passw.send_keys(password)
        time.sleep(random.randint(1,3))
        driver.find_element_by_id("loginbutton").click()
        time.sleep(random.randint(1,3))
        
    def getVideoFromPage (self,page, videoDir, imageDir, vids): 
        
        def parStrNum(str):
            if str.endswith('K'):
                return int(float(str[:-1])*1000)
            elif str.endswith('M'):
                return int(float(str[:-1])*1000000)
            elif (',' in str) == True:
                return int(str.replace(',',''))
            else:
                return int(float(str))
            
        conn = self.conn
        cursor = self.cursor
        driver=self.driver
        self.page = page
        driver.get('https://www.facebook.com/'+page)
        driver.find_element_by_tag_name('body').click()
        driver.maximize_window()
        action = ActionChains(driver)
        video_page=driver.find_element_by_xpath("//div[@data-key='tab_videos']//a")
        action.move_to_element(video_page).click().perform()
        try:
            action.move_to_element(video_page).click().perform()
        except:
            pass
        
        driver.implicitly_wait(30)
        try:
            driver.find_element_by_xpath("//div[@class='_69ae']").click()
        except:
            pass
        
        
        time.sleep(3)
        show_more=True
        while True:
            try:
    
                action = ActionChains(driver)
                more_videos = driver.find_element_by_xpath("//div[@class='clearfix uiMorePager stat_elem _52jv']//a")
                action.move_to_element(more_videos).click().perform()
                time.sleep(random.randint(1,3))
                
            except NoSuchElementException:
                show_more = False
                break
                
              
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;") 
        match=False
        while(match==False):
            lastCount = lenOfPage
            time.sleep(3)
            lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount==lenOfPage:
                match=True
               
        videos_path="//div[@class='_u3y']"
        videos=driver.find_elements_by_xpath(videos_path)
        
        
        for i in range(len(videos)):
            
            try:
                link=driver.find_element_by_xpath("(//div[@class='_u3y'])[%d]//div[@class='_5asl']//a"%(i+1)).get_attribute('href')
            except:
                link=None
                
            try:
                videoId=link.split('/')[-2]
            except:  
                videoId=None
                continue
                
              
            if videoId in vids:
                print(videoId,' exists...')
                continue
            
            
            try:
                numOfViews = parStrNum(driver.find_element_by_xpath("(//div[@class='_u3y'])[%d]//span[@class='fcg']"%(i+1)).text.split(' ')[0])
            except:
                numOfViews=None
            try:
                title = driver.find_element_by_xpath("(//div[@class='_u3y'])[%d]//div[@class='_3v4h _48gm _50f3 _50f7']//a"%(i+1)).text
            except:
                title =None
            
            
            img = driver.find_element_by_xpath("(//div[@class='_u3y'])[%d]//img"%(i+1)).get_attribute('src')
            image=requests.get(img)
            with open(imgDir+videoId+'.jpg','wb') as imgs:
                imgs.write(image.content) 
            imgs.close()
            
            
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)
            time.sleep(random.randint(1,3))
            driver.find_element_by_tag_name("body").click()
            driver.implicitly_wait(30)

            try:

                action = ActionChains(driver)
                element = driver.find_element_by_xpath("(//video)[1]")
                action.move_to_element(element).click().perform()
                time.sleep(1)
            except:
                print (videoId, ' not found...')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            
            try:
                action = ActionChains(driver)
                element = driver.find_element_by_xpath("(//video)[1]")
                action.move_to_element(element).click().perform()    
            except:

                print (videoId, ' not found...')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            
            driver.implicitly_wait(20)
            
            try:
                post=driver.find_element_by_xpath("(//div[@class='_44bj'])[1]").text[:100]
            except NoSuchElementException:
                
                post=driver.find_element_by_xpath("//div[@class='_1rg-']").text[:100]
                
                
            except:
                post = None
            
            
            try:
                comments = driver.find_element_by_xpath("//a[@class='_ipm _-56']")
                numOfComments=parStrNum(comments.text.split(' ')[0])
            except Exception:
                numOfComments =0

            try:    
                shares = driver.find_element_by_xpath("//a[@class='_ipm _2x0m']")
                numOfShares=parStrNum(shares.text.split(' ')[0])

            except Exception:
                numOfShares =0



            try:
                driver.find_element_by_xpath("//div[@class='_ipp']//a[@class='_2x4v']").click()
                stats=driver.find_elements_by_xpath("//li[@class='_ds- _45hc']//span//span")

                numOfLike = 0
                numOfLove = 0
                numOfHaha = 0
                numOfWow = 0
                numOfSad = 0
                numOfAngry = 0

                for i in stats:
                    label=i.get_attribute('aria-label')
                    if label != None:
                        label=label.split(' ')
                        reaction = label[-1]
                        if reaction == 'Like':
                            numOfLike += parStrNum(label[0])
                        if reaction == 'Love':
                            numOfLove += parStrNum(label[0])
                        if reaction == 'Haha':
                            numOfHaha += parStrNum(label[0])
                        if reaction == 'Wow':
                            numOfWow += parStrNum(label[0])
                        if reaction == 'Sad':
                            numOfSad += parStrNum(label[0])
                        if reaction == 'Angry':
                            numOfAngry += parStrNum(label[0])



            except (ElementNotInteractableException, ElementClickInterceptedException):

                action = ActionChains(driver)
                element = driver.find_element_by_xpath("//div[@class='_ipp']//a[@class='_2x4v']")
                action.move_to_element(element).click().perform()

                stats=driver.find_elements_by_xpath("//li[@class='_ds- _45hc']//span//span")

                numOfLike = 0
                numOfLove = 0
                numOfHaha = 0
                numOfWow = 0
                numOfSad = 0
                numOfAngry = 0

                for i in stats:
                    label=i.get_attribute('aria-label')
                    if label != None:
                        label=label.split(' ')
                        reaction = label[-1]
                    if reaction == 'Like':
                        numOfLike += parStrNum(label[0])
                    if reaction == 'Love':
                        numOfLove += parStrNum(label[0])
                    if reaction == 'Haha':
                        numOfHaha += parStrNum(label[0])
                    if reaction == 'Wow':
                        numOfWow += parStrNum(label[0])
                    if reaction == 'Sad':
                        numOfSad += parStrNum(label[0])
                    if reaction == 'Angry':
                        numOfAngry += parStrNum(label[0])

            except Exception:

                numOfLike = None
                numOfLove = None
                numOfHaha = None
                numOfWow = None
                numOfSad = None
                numOfAngry = None

            time.sleep(2)
            
            new_link = re.sub(r'www[.]','mbasic.',link)
            driver.get(new_link)
            time.sleep(random.randint(2,5))
            
            try:
                action = ActionChains(driver)

                downloadableLink = driver.find_element_by_xpath("//div[@id='mobile_injected_video_feed_pagelet']//div[@class='widePic']")
                action.move_to_element(downloadableLink).click().perform()
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[2])
            
            
                url_link=driver.current_url
                r=requests.get(url_link)
                with open(videoDir+videoId+'.mp4','wb') as f:
                    f.write(r.content) 
                f.close()
                
                driver.close()
        
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(1)
                driver.close()

                
            except Exception:
                
                print (videoId + ' not downloadable...')
    
                driver.close()
        
                try:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    
                except:
                    pass
                time.sleep(1)
                
        

            driver.switch_to.window(driver.window_handles[0])
            sql = 'INSERT INTO videos (videoId,page,link,title,post,numOfViews,numOfLike, numOfLove, numOfHaha, numOfWow, numOfSad, numOfAngry, numOfComments, numOfShares) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql,(videoId,page,link,title,post,numOfViews,numOfLike, numOfLove, numOfHaha, numOfWow, numOfSad, numOfAngry,numOfComments, numOfShares))
            conn.commit()
                
        
        
    def driverQuit(self):
        
        self.driver.quit()


# In[61]:


name='evahou@umd.edu'
password ='rhsmithumd'
#conn = mysql.connector.connect(user='root', password='rootrhsmith', host='localhost',database='Facebook',charset = 'utf8mb4')
conn = mysql.connector.connect(user='root', password='Khj828828!', host='localhost',database='Facebook',charset = 'utf8mb4')
#driver_path = '/Users/kunpengzhang/Software/chromedriver'
driver_path = '/Users/wenqi/Desktop/Facebook/chromedriver'
cursor=conn.cursor()


# In[62]:


retrieve = page_video_retrieve(conn,driver_path)
retrieve.logIn(name,password)


# In[63]:


pages = ['174751071823','9018053518']
for page in pages:

    cursor.execute('select videoId from videos')
    rows = cursor.fetchall()
    vids = []
    for row in rows:
        vids.append(row[0])

    videoDir= 'videos/'+page+'/'
    if not os.path.exists(videoDir):
        os.mkdir(videoDir)
        
    imgDir= 'images/'+page+'/'
    if not os.path.exists(imgDir):
        os.mkdir(imgDir)
        

    retrieve.getVideoFromPage(page,videoDir,imgDir, vids)


# In[19]:


retrieve.driverQuit()


# In[ ]:




