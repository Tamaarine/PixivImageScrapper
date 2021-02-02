import requests
from tqdm import tqdm
import os
from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

# Chrome driver
chrome_options = Options()
chrome_options.add_argument("user-data-dir=selenium")
browser = webdriver.Chrome(chrome_options=chrome_options)

# Folder to store in
default_path = "D:\\Downloads"


def download_image(url):
    """

    This function will download the given url's image with proper filename labeling
    If a path is not provided the image will be downloaded to the Downloads folder
    """

    # Establish a Session with cookies
    s = requests.Session()

    # Fix for pixiv's request you have to add referer in order to download images
    response = s.get(url, headers={'User-Agent': 'Mozilla/5.0',
                                   'referer': 'https://www.pixiv.net/'}, stream=True)

    file_name = url.split("/")[-1]  # Retrieve the file name of the link
    together = os.path.join(default_path, file_name)  # Join together path with the file_name. Where to store the file
    file_size = int(response.headers["Content-Length"])  # Get the total byte size of the file
    chunk_size = 1024 # Consuming in 1024 byte per chunk

    # tqdm object that have total of file_size
    progress = tqdm(total=file_size, unit='B', unit_scale=True, desc="Downloading {file}".format(file = file_name))

    # Open the file destination and write in binary mode
    with open(together, "wb") as f:

        # Loop through each of the chunks in response in chunk_size and update the progres by calling update using
        # len(chunk) not chunk_size
        for chunk in response.iter_content(chunk_size):
            f.write(chunk)

            progress.update(len(chunk))

    """
    
    Don't do this, by passing the response.iter_content(chunk_size) directly into the tqdm.
    This will lead to progress bar not finishing problem.
    Let the progress only handle the file size, and use response.iter_content(chunk_size) for the for loop
    Then update the progress by adding the length of each chunk that is loaded.
    
    For some reason if you add it to tqdm it will not let the progress bar finish.
    
    progress = tqdm(response.iter_content(chunk_size),total=file_size, unit='B', unit_scale=True, desc="Downloading {file}".format(file = file_name))
    
    with open(together, "wb") as f:
        
        for chunk in progress:
            f.write(chunk)

            progress.update(len(chunk))

    """

    # Close the tqdm object and file object as good practice
    progress.close()
    f.close()


def open_all():
    """

    This function will try to click the See all button on pixiv website if there is none
    then it does nothing

    This function will try to click the See all button on pixiv if there isn't a See all
    button then it will return False, True otherwise and clicks it
    """
    try:
        browser.implicitly_wait(3)
        see_all = browser.find_element_by_xpath("//*[contains(text(), 'See all')]")

        # If there is see all then we click it
        see_all.click()

        time.sleep(3)
    except:

        pass


def get_all_image_links():
    """

    This function will return all of image URLs
    """

    # First we check if we can click the See all button
    open_all()

    urls = []

    # True that means there are multiple images
    image_container = browser.find_elements_by_css_selector("div[role='presentation']")[1]

    # We find all of the a tags first
    a_tags = image_container.find_elements_by_tag_name("a")

    # Then we use a for loop wrapped in a tqdm to represent progress
    for a in tqdm(a_tags, "Extracting Images"):
        # We go to that element so it will be loaded to add the urls
        ActionChains(browser).move_to_element(a).perform()
        img_tag = a.find_element_by_tag_name("img")

        # Adding the urls into the array
        urls.append(img_tag.get_attribute("src"))

    return urls


def main():
    """

    The main function that runs this program
    """

    # Ask the user for the link that they want to download
    url = input("Download Pixiv image: ")

    # Opens the urls link
    browser.get(url)

    # get_all_image_links return an array of image url links
    urls = get_all_image_links()

    # Loop through each link to download the image
    for link in urls:
        download_image(link)

    # Signal the program is completed
    print("Your file is available at " + default_path)


if __name__ == "__main__":
    """
    
    Runs the main
    """
    main()