import os
import time
from DrissionPage import ChromiumPage, ChromiumOptions, SessionPage
from bs4 import BeautifulSoup

def readData(fileName):
    f = open(fileName, 'r', encoding='utf-8')
    f.flush()
    data = []
    for i, line in enumerate(f):
        try:
            line = repr(line)
            line = line[1:len(line) - 3]
            data.append(line)
        except:
            print("err")
    f.close()
    return data

def append_to_file(file_name, content):
    """Append content to a file."""
    with open(file_name, 'a') as file:
        file.write(content + os.linesep)
def createChromeDriver():
    try:
        #os.system('rm -rf /tmp/DrissionPage/userData_9222/Default')
        options = ChromiumOptions()
        options.set_paths('/usr/bin/google-chrome')

        arguments = [
            "-no-first-run",
            "-force-color-profile=srgb",
            "-metrics-recording-only",
            "-password-store=basic",
            "-use-mock-keychain",
            "-export-tagged-pdf",
            "-no-default-browser-check",
            "-disable-background-mode",
            "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
            "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
            "-deny-permission-prompts",
            "-disable-gpu",

        ]

        for argument in arguments:
            options.set_argument(argument)

        driver = ChromiumPage(options)

        return driver
    except Exception as e:
        print(f'setup_chromium exception: {str(e)}')

def loginShoppe(driver, userName, passWord):
    try:
        driver.get('https://shopee.vn')
        time.sleep(3)
        eleSearch = driver.eles('.shopee-searchbar-input__input')
        if len(eleSearch) > 0:
            return True

        driver.ele('@name=loginKey').input(userName)
        time.sleep(1)
        driver.ele('@name=password').input(passWord)
        time.sleep(1)
        driver.ele('xpath://button[contains(text(), "Đăng nhập")]').click()

        return True
    except Exception as e:
        print('Login err' + str(e))
        return False

def searchKeyWord(driver, keyWord):
    try:
        driver.get('https://shopee.vn/search?keyword=' + keyWord)
        time.sleep(1)
        return True
    except Exception as e:
        print('Search err' + str(e))
        return False

def scroll_and_wait(driver):
    """Scrolls down the page smoothly and waits for data to load."""
    scroll_script = """
        var scroll = document.body.scrollHeight / 10;
        var i = 0;
        function scrollit(i) {
            window.scrollBy({top: scroll, left: 0, behavior: 'smooth'});
            i++;
            if (i < 5) {
                setTimeout(scrollit, 500, i);
            }
        }
        scrollit(i);
    """
    driver.run_js(scroll_script)

def fetch_page_data(driver):
    """Fetch HTML of the page."""
    try:
        return driver.ele('.WaPg2j').html
    except Exception as e:
        print(f'Error fetching page data: {str(e)}')
        return None

def extract_product_details(item):
    """Extract details of a single product."""
    name = item.find('img', alt=True)['alt'] if item.find('img', alt=True) else None
    image_link = item.find('img', src=True)['src'] if item.find('img', src=True) else None
    price_details = item.select_one('div.flex-shrink div.truncate.flex.items-baseline')
    price = price_details.get_text(strip=True).replace("₫", "").strip() if price_details else None
    numberOfSold = item.select_one('div.truncate.text-shopee-black87.text-xs.min-h-4.flex-shrink-1').get_text(strip=True) if item.select_one('div.truncate.text-shopee-black87.text-xs.min-h-4.flex-shrink-1') else None
    linkProduct = item.find('a', class_='contents')['href'] if item.find('a', class_='contents') and 'href' in item.find('a', class_='contents').attrs else None

    return [name, price, linkProduct, image_link, numberOfSold] if all([name, image_link, price, numberOfSold, linkProduct]) else None


def click_next_page(driver):
    """Navigate to the next page of search results if available."""
    try:
        driver.run_js('document.querySelector(".shopee-icon-button--right").click()')
        time.sleep(1)
    except Exception as e:
        print(f'Error clicking next page: {str(e)}')

def is_end_of_page(data):
    """Check if the end of the page is reached."""
    return 'shopee-icon-button shopee-icon-button--right shopee-icon-button--disabled' in data

def process_search_results(driver):
    """Extract and save product details from search results."""
    while True:
        scroll_and_wait(driver)  # Simulate user scroll
        data = fetch_page_data(driver)
        if not data or is_end_of_page(data):
            break

        parse_and_save_products(data)
        click_next_page(driver)

def parse_and_save_products(data):
    """Parse product details from HTML and save to file."""
    soup = BeautifulSoup(data, 'html.parser')
    items = soup.find_all('li', class_='shopee-search-item-result__item')
    for item in items:
        try:
            product_details = extract_product_details(item)
            if product_details:
                append_to_file('products.csv', ','.join(f'"{detail}"' for detail in product_details))
        except Exception as e:
            print(f'Error parsing product: {str(e)}')

userName = 'login'
passWord = 'password'

driver = createChromeDriver()
loginShoppe(driver, userName, passWord)

print('Please login success before run this code')
print('Please login success before run this code')
print('Please login success before run this code')
print('Please login success before run this code')
print('Please login success before run this code')
time.sleep(120)

keywords = readData('keyword_search.csv')
for keyword in keywords:
    searchKeyWord(driver, keyword)
    process_search_results(driver)
