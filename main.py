import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time



url = 'https://www.tokopedia.com/p/handphone-tablet/handphone'
driver = webdriver.Chrome('/Users/agungwicaksono/Downloads/chromedriver')
driver.get(url=url)
pagination_class = 'css-txlndr-unf-pagination'
product_class = 'css-bk6tzz'
next_and_prev_class = 'css-ad7yub-unf-pagination-item'
delay = 3
product_list = []
num_of_product = 3

def create_dict():
    name_class = 'css-t9du53'
    more_detail_button = 'css-1n6vhqs'
    description_class = 'css-1k1relq'
    image_class = 'css-1c345mg'
    price_class = 'css-aqsd8m'
    rating_class = 'icon-star'
    seller_class = 'css-12gb68h'

    # check if element more detail button exist
    try:
        more_detail_button = driver.find_element_by_class_name(
            more_detail_button)
        more_detail_button.click()
    except:
        description_class = 'css-17zm3l'

    try:
        name = driver.find_element_by_class_name(name_class).text
        description = driver.find_element_by_class_name(description_class).text
        image = driver.find_elements_by_class_name(image_class)
        image_list = []
        for i in image:
            image_list.append(i.get_attribute('src'))
        price = driver.find_element_by_class_name(price_class).find_element_by_class_name('price').text
        rating = driver.find_element_by_xpath(
            f'//img[@class="{rating_class}"]/following-sibling::span[@class="main"]').text
        seller = driver.find_element_by_class_name(
            seller_class).find_element_by_tag_name('h2').text

        product_dict = {
            'name': name,
            'description': description,
            'image': image_list,
            'price': price,
            'rating': rating,
            'seller': seller
        }
    except Exception as e:
        print('Error: '+e.__str__())
        return None
    return product_dict


index = 0
while len(product_list) < num_of_product:
    # scroll to bottom to trigger load all product
    driver.execute_script("window.scrollTo(0, 1080)")

    try:
        pagination_element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, pagination_class)))
        
        # get all product
        product_element_list = driver.find_elements_by_class_name(product_class)
        
        # open product in new tab
        element_clicked = product_element_list[index]

        # don't click if css-nysll7 is exist
        # css-nysll7 is indicator for ads
        is_ads = True
        try:
            element_clicked.find_element_by_xpath('.//div[@class="css-nysll7"]')
        except Exception:
            is_ads = False

        if not is_ads:
            ActionChains(driver).key_down(
                Keys.COMMAND).click(element_clicked).perform()
        
            # switch to new tab
            driver.switch_to.window(driver.window_handles[-1])
            # wait until loading finish
            time.sleep(delay)
            
            # get all data from product
            product_dict = create_dict()
            if product_dict is not None:
                product_list.append(product_dict)

            driver.close()

            # switch back to main tab
            driver.switch_to.window(driver.window_handles[0])


        
        if index == len(product_element_list) - 1:
            # go to next page
            # get next and prev button
            next_and_prev_button = driver.find_elements_by_class_name(next_and_prev_class)
            # click next button
            next_and_prev_button[1].click()
            # reset index
            index = 0
        
        index += 1

    except TimeoutException:
        print("Loading took too much time!")
    
driver.close()

# Save to csv
df = pd.DataFrame(product_list)
df.to_csv('product_list.csv', index=False)
