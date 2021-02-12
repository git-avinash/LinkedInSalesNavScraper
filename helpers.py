from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import time
import json
import random
import pandas as pd


# Scraping Helpers
def print_app_info() -> None:
    print("""
########################################

  + LISN Scraper  
  + App Version: 1.0
  + contact: mail.avinashsah@gmail.com   

########################################
>> APP LOGS:
    """)


def print_app_end() -> None:
    print("""
########################################

  -  Successfully Scraped All Data  -  

########################################
    """)


def get_inputs(browser: object) -> int:
    is_scrapable_url: bool = False
    is_valid_input: bool = False
    scrape_data_amount: int = None

    print(">> Please Login and search for results")
    input(">> Hit Enter once satisfied with results after applying filters")

    while not is_valid_input:
        scrape_data_amount: int = input(
            ">> Number of account you want to scrape: ")

        try:
            scrape_data_amount = int(scrape_data_amount)
            is_valid_input: bool = True
        except ValueError:
            print(">> Not a valid input!")

    while not is_scrapable_url:
        scrapable_url: str = "https://www.linkedin.com/sales/search/people"
        current_url: str = browser.current_url

        if current_url.startswith(scrapable_url):
            is_scrapable_url: bool = True

        else:
            print(">> This is not a valid page...")
            input(">> PLEASE HIT ENTER AFTER VISITING A VALID PAGE")

    return scrape_data_amount


def sleep_random() -> None:
    sleep_time: int = random.randrange(3, 6)
    time.sleep(sleep_time)


def get_defaults(type_name: str, name: str) -> str:
    xpath: dict = {}

    xpath["url"] = {
        "login": "https://www.linkedin.com/sales/login",
        "home": "https://www.linkedin.com/sales/homepage",
    }

    xpath["results"] = {
        "total_results": "//button[@id='search-spotlight-tab-ALL']/span[1]",
        "result_links": "//*[@class='result-lockup__name']/a"
    }

    xpath["pages"] = {
        "home_identifier": "//a[@data-control-name='view_home_from_app_header']",
        "current_page": "//li[starts-with(@class,'selected')]",
        # Inject Value
        "jump_to_page": "//button[@aria-label='Navigate to page {}']",
    }

    xpath["profile"] = {
        "unlock_profile": "//button[@data-control-name='unlock']",
        "full_name": "//span[starts-with(@class,'profile-topcard-person')]",
        "photo": "//div[@class='presence-entity--size-6 relative']/img",
        "country": "//div[starts-with(@class,'profile-topcard__location-data')]",
        "show_contacts": "//div[starts-with(@class,'profile-topcard__contact-info')]//button",
        "close_contacts": "//button[@aria-label='Dismiss']",
        "phone_number": "//div[starts-with(@class,'contact-info-form__phone-read')]/a",
        "email": "//div[starts-with(@class,'contact-info-form__email-read')]/a",
    }

    xpath["experience"] = {
        "show_more_position": "//div[@id='profile-experience']/button",
        "len_experience": "//div[@id='profile-experience']//li[starts-with(@class,'profile-position')]",
        "position": "[{}]//dt",  # len + Inject Value
        "company": "[{}]//span//a",  # len + Inject Value
        "company_link": "[{}]/a",  # len + Inject Value
        "experience": "[{}]//p[2]",  # len + Inject Value
    }

    xpath["education"] = {
        "show_more_education": "//div[@id='profile-education']/button",
        "len_education": "//li[starts-with(@class,'profile-education')]",
        # len + Inject Value
        "school_name": "[{}]//dt[starts-with(@class,'profile-education')]/a",
        # len + Inject Value
        "field_of_study": "[{}]//span[@data-test-education='field']",
        # len + Inject Value
        "degree_name": "[{}]//span[@data-test-education='degree']",
    }

    xpath["company"] = {
        "see_all": "//h2[@class='subtitle']//button[contains(text(), 'See all')]",
        "about_no_see_all": "//h2[@class='subtitle']/div",
        "about_see_all": "//div[starts-with(@class,'topcard-extended')]/p",
        "company_head_count": "//a[@data-control-name='topcard_employees']",
        "website": "//div[starts-with(@class,'meta-links')]//a[@data-control-name='topcard_website']",
        "headquarters": "//div[starts-with(@class,'meta-links')]//a[@data-control-name='topcard_headquarters']",
    }

    xpath["filters"] = {
        "filters": "//div[starts-with(@class,'relative search-filter')]",
        "institute": "Education",
        "source": "Linked In",
    }

    return xpath[type_name][name]


def get_links(browser: object, amount: int) -> list:
    print(">> Scraping links...")

    links: list = []
    active_page = get_active_page(browser)

    while len(links) < amount:
        scroll_page_to_bottom(browser)

        result_link_elements: list = browser.find_elements_by_xpath(
            get_defaults("results", "result_links"))

        for link in result_link_elements:
            links.append(link.get_attribute("href"))  # +"\n")

        active_page += 1
        browser.find_element_by_xpath(get_defaults(
            "pages", "jump_to_page").format(active_page)).click()

        sleep_random()

    return links


def get_active_page(browser: object) -> int:
    active_page: int = int(browser.find_element_by_xpath(get_defaults(
        "pages", "current_page")).get_attribute("aria-label").split(" ")[-1].replace(")", "").strip())

    return active_page


def unlock_if_available(browser: object) -> None:
    unlock_profile_path: str = get_defaults("profile", "unlock_profile")
    is_locked: bool = is_available(browser, unlock_profile_path, delay=2)
    if is_locked:
        browser.find_element_by_xpath(unlock_profile_path).click()
        sleep_random()


def see_all_about(browser: object) -> bool:
    see_all_about_path: str = get_defaults("company", "see_all")

    if is_available(browser, see_all_about_path):
        browser.find_element_by_xpath(see_all_about_path).click()

        sleep_random()

        return True

    return False


def show_all_contacts(browser: object) -> bool:
    show_all_contacts_path: str = get_defaults("profile", "show_contacts")

    if is_available(browser, show_all_contacts_path):
        browser.find_element_by_xpath(show_all_contacts_path).click()

        sleep_random()

        return True

    return False


def close_all_contacts(browser: object) -> None:
    close_all_contacts_path: str = get_defaults("profile", "close_contacts")

    if is_available(browser, close_all_contacts_path):
        browser.find_element_by_xpath(close_all_contacts_path).click()

        sleep_random()


def get_profile_details(browser: object) -> dict:
    full_name_path: str = get_defaults("profile", "full_name")
    photo_path: str = get_defaults("profile", "photo")
    country_path: str = get_defaults("profile", "country")
    phone_number_path: str = get_defaults("profile", "phone_number")
    email_path: str = get_defaults("profile", "email")

    if is_available(browser, full_name_path):
        full_name: list = browser.find_element_by_xpath(
            full_name_path).text.split(",")[0].split(" ")

        if len(full_name) == 2:
            first_name: str = full_name[0]
            middle_name: str = "-"
            last_name: str = full_name[1]
        elif len(full_name) == 3:
            first_name: str = full_name[0]
            middle_name: str = full_name[1]
            last_name: str = full_name[2]
        else:
            first_name: str = "-"
            middle_name: str = "-"
            last_name: str = "-"
    else:
        first_name: str = "-"
        middle_name: str = "-"
        last_name: str = "-"

    if is_available(browser, photo_path):
        photo_link: str = browser.find_element_by_xpath(
            photo_path).get_attribute("src")
        if photo_link.startswith("data:image"):
            photo: str = "-"
        else:
            photo: str = photo_link
    else:
        photo: str = "-"

    if is_available(browser, country_path):
        country: str = browser.find_element_by_xpath(country_path).text
    else:
        country: str = "-"

    if show_all_contacts(browser):
        if is_available(browser, phone_number_path):
            phone_number: str = browser.find_element_by_xpath(
                phone_number_path).text
        else:
            phone_number: str = "-"

        if is_available(browser, email_path):
            email: str = browser.find_element_by_xpath(email_path).text
        else:
            email: str = "-"

    else:
        phone_number: str = "-"
        email: str = "-"

    close_all_contacts(browser)

    profile: dict = {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "photo": photo,
        "country": country,
        "phone_number": phone_number,
        "email": email,
    }

    return profile


def get_company_details(browser: object, links: str) -> list:
    company_details: list = []

    about_no_see_all_path: str = get_defaults("company", "about_no_see_all")
    about_see_all_path: str = get_defaults("company", "about_see_all")
    company_head_count_path: str = get_defaults(
        "company", "company_head_count")
    website_path: str = get_defaults("company", "website")
    headquarters_path: str = get_defaults("company", "headquarters")

    if links:
        for link in links:
            if link == "-":
                company_details_obj: dict = {
                    "head_count": "-",
                    "website": "-",
                    "headquarters": "-",
                    "about": "-"
                }

                company_details.append(company_details_obj)
            else:
                browser.get(link)

                sleep_random()

                if is_available(browser, company_head_count_path):
                    head_count: str = browser.find_element_by_xpath(
                        company_head_count_path).text.split(" ")[0]
                else:
                    head_count: str = "-"

                if is_available(browser, website_path):
                    website: str = browser.find_element_by_xpath(
                        website_path).get_attribute("href")
                else:
                    website: str = "-"

                if is_available(browser, headquarters_path):
                    headquarters: str = browser.find_element_by_xpath(
                        headquarters_path).get_attribute("href").replace("https://www.google.com/maps/place/", "").replace("+", " ")
                else:
                    headquarters: str = "-"

                if see_all_about(browser):
                    about: str = browser.find_element_by_xpath(
                        about_see_all_path).text
                elif is_available(browser, about_no_see_all_path):
                    about: str = browser.find_element_by_xpath(
                        about_no_see_all_path).text.split("\n")[0]
                else:
                    about: str = "-"

                company_details_obj: dict = {
                    "head_count": head_count,
                    "website": website,
                    "headquarters": headquarters,
                    "about": about.strip()
                }

                company_details.append(company_details_obj)

                sleep_random()

    else:
        company_details_obj: dict = {
            "head_count": "-",
            "website": "-",
            "headquarters": "-",
            "about": "-"
        }

        company_details.append(company_details_obj)

    return company_details


def get_filters(browser: object) -> dict:
    filter_raw: list = []
    filters: dict = {}

    filters_path: str = get_defaults("filters", "filters")
    institute_path: str = get_defaults("filters", "institute")
    source_path: str = get_defaults("filters", "source")

    filter_chaos: list = [
        x.text for x in browser.find_elements_by_xpath(filters_path)]

    for chaos in filter_chaos:
        if chaos.startswith("Industry"):
            filter_raw.append(chaos)

        elif chaos.startswith("Seniority level"):
            filter_raw.append(chaos)

        elif chaos.startswith("Function"):
            filter_raw.append(chaos)

        elif chaos.startswith("Title"):
            filter_raw.append(chaos)
        else:
            continue

    for raw in filter_raw:
        filter_data = raw.split("\n")
        len_obj = len(filter_data)

        if filter_data[0] == "Industry":
            if len_obj > 1:
                filters["industries"] = filter_data[2:]
            else:
                filters["industries"] = ["-"]

        if filter_data[0] == "Seniority level":
            if len_obj > 1:
                filters["seniority_level"] = filter_data[2:]
            else:
                filters["seniority_level"] = ["-"]

        if filter_data[0] == "Function":
            if len_obj > 1:
                filters["function"] = filter_data[2:]
            else:
                filters["function"] = ["-"]

        if filter_data[0] == "Title":
            if len_obj > 1:
                filters["title"] = filter_data[2:-2]

            else:
                filters["title"] = ["-"]

    filters["institute"] = institute_path
    filters["source"] = source_path

    return filters


def get_experience_details(browser: object) -> tuple:
    experience: list = []
    company_links: list = []

    show_more_experience_path: str = get_defaults(
        "experience", "show_more_position")

    if is_available(browser, show_more_experience_path):
        browser.find_element_by_xpath(
            show_more_experience_path).click()
        sleep_random()

    experience_path: str = get_defaults("experience", "len_experience")
    if is_available(browser, experience_path):
        len_experience: int = len(
            browser.find_elements_by_xpath(experience_path))

    else:
        len_experience: int = 0

    if len_experience > 0:
        incrementer: int = 1

        while incrementer <= len_experience:
            experience_obj = {}

            position_path: str = experience_path + \
                get_defaults("experience", "position").format(
                    incrementer)
            company_path: str = experience_path + \
                get_defaults("experience", "company").format(
                    incrementer)
            true_experience_path: str = experience_path + \
                get_defaults("experience", "experience").format(
                    incrementer)
            company_link_path: str = experience_path + \
                get_defaults("experience", "company_link"). format(incrementer)

            if is_available(browser, position_path):
                experience_obj["position"] = browser.find_element_by_xpath(
                    position_path).text
            else:
                experience_obj["position"] = "-"

            if is_available(browser, company_path):
                experience_obj["company"] = browser.find_element_by_xpath(
                    company_path).text
            else:
                experience_obj["company"] = "-"

            if is_available(browser, true_experience_path):
                experience_obj["experience"] = browser.find_element_by_xpath(
                    true_experience_path).text.split("\n")[1]
            else:
                experience_obj["experience"] = "-"

            if is_available(browser, company_link_path):
                company_links.append(browser.find_element_by_xpath(
                    company_link_path).get_attribute("href"))
            else:
                company_links.append("-")

            experience.append(experience_obj)

            incrementer += 1

    else:
        experience.append({
            "position": "-",
            "company": "-",
            "experience": "-",
        })

    return experience, company_links


def get_education_details(browser: object) -> list:
    education: list = []
    show_more_education_path: str = get_defaults(
        "education", "show_more_education")
    if is_available(browser, show_more_education_path):
        browser.find_element_by_xpath(show_more_education_path).click()
        sleep_random()

    education_path: str = get_defaults("education", "len_education")
    if is_available(browser, education_path):
        len_education: int = len(
            browser.find_elements_by_xpath(education_path))
    else:
        len_education: int = 0

    if len_education > 0:
        incrementer: int = 1

        while incrementer <= len_education:
            education_obj = {}

            school_name_path: str = education_path + \
                get_defaults("education", "school_name").format(
                    incrementer)
            field_path: str = education_path + \
                get_defaults("education", "field_of_study").format(
                    incrementer)
            degree_name_path: str = education_path + \
                get_defaults("education", "degree_name").format(
                    incrementer)

            if is_available(browser, school_name_path):
                education_obj["school_name"] = browser.find_element_by_xpath(
                    school_name_path).text
            else:
                education_obj["school_name"] = "-"

            if is_available(browser, field_path):
                education_obj["field_of_study"] = browser.find_element_by_xpath(
                    field_path).text
            else:
                education_obj["field_of_study"] = "-"

            if is_available(browser, degree_name_path):
                education_obj["degree_name"] = browser.find_element_by_xpath(
                    degree_name_path).text
            else:
                education_obj["degree_name"] = "-"

            education.append(education_obj)

            incrementer += 1

    else:
        education.append({
            "school_name": "-",
            "field_of_study": "-",
            "degree_name": "-",
        })

    return education


def get_data(browser: object, links: list, amount: int) -> dict:
    account_details: list = []
    links_scraped: int = 1

    for link in links:
        if links_scraped <= amount:
            print(f">> Scraping Link number {links_scraped}/{amount}")
            browser.get(link)
            sleep_random()

            unlock_if_available(browser)

            print(">> Scraping Profile Details")
            profile: dict = get_profile_details(browser)

            print(
                ">> Scraping Experience Details")
            experience, company_links = get_experience_details(browser)

            print(
                ">> Scraping Education Details")
            education: list = get_education_details(browser)

            print(">> Scraping Company Details")
            company: list = get_company_details(browser, company_links)

            "Final Details"
            details: dict = {}
            details["name"] = profile
            details["experience"] = experience
            details["education"] = education
            details["company"] = company
            account_details.append(details)

            links_scraped += 1

        else:
            break

    scraped_details: dict = {
        "account_details": account_details
    }

    return scraped_details


def make_json(details: dict, filename: str) -> None:
    print(">> Saving data into JSON file")

    with open(filename, "w") as result_file:
        result_file.writelines(json.dumps(details))


def make_json_to_csv(json_file_name: str, export_file_name: str) -> None:
    print(">> Saving data into CSV file")

    rows: list = []

    with open(json_file_name, "r") as data_file:
        data: dict = json.loads(data_file.read())

    account_details: list = data["account_details"]
    filter_details: dict = data["filters"]

    industry: str = " ".join(
        [x + "\n" for x in filter_details["industries"]])
    seniority_level: str = " ".join(
        [x + "\n" for x in filter_details["seniority_level"]])
    function: str = " ".join(
        [x + "\n" for x in filter_details["function"]])
    title: str = " ".join([x + "\n" for x in filter_details["title"]])

    institute: str = filter_details["institute"]
    source: str = filter_details["source"]

    for index, detail in enumerate(account_details):
        NO_VAL: str = ""
        first_name: str = detail["name"]["first_name"]
        middle_name: str = detail["name"]["middle_name"]
        last_name: str = detail["name"]["last_name"]
        photo: str = detail["name"]["photo"]
        country: str = detail["name"]["country"]
        phone_number: str = detail["name"]["phone_number"]
        email: str = detail["name"]["email"]

        experience: list = detail["experience"]
        company: list = detail["company"]
        education: list = detail["education"]

        len_experience: int = len(detail["experience"])
        len_education: int = len(detail["education"])

        if len_experience > len_education:
            for index, _ in enumerate(range(len_experience)):
                if index == 0:
                    rows.append((
                        email, first_name, middle_name, last_name, phone_number, country,
                        experience[index]["company"], company[index]["head_count"],
                        industry, institute, source,
                        experience[index]["position"], experience[index]["company"], experience[index]["experience"],
                        education[index]["school_name"], education[index]["field_of_study"], education[index]["degree_name"],
                        seniority_level, function, title, photo,
                        company[index]["website"], company[index]["about"], company[index]["headquarters"],
                    ))

                elif index > 0 and index < len_education:
                    rows.append((
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["company"], company[index]["head_count"],
                        NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["position"], experience[index]["company"], experience[index]["experience"],
                        education[index]["school_name"], education[index]["field_of_study"], education[index]["degree_name"],
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        company[index]["website"], company[index]["about"], company[index]["headquarters"],
                    ))

                else:
                    rows.append((
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["company"], company[index]["head_count"],
                        NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["position"], experience[index]["company"], experience[index]["experience"],
                        NO_VAL, NO_VAL, NO_VAL,
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        company[index]["website"], company[index]["about"], company[index]["headquarters"],
                    ))

        elif len_experience < len_education:
            for index, _ in enumerate(range(len_education)):
                if index == 0:
                    rows.append((
                        email, first_name, middle_name, last_name, phone_number, country,
                        experience[index]["company"], company[index]["head_count"],
                        industry, institute, source,
                        experience[index]["position"], experience[index]["company"], experience[index]["experience"],
                        education[index]["school_name"], education[index]["field_of_study"], education[index]["degree_name"],
                        seniority_level, function, title, photo,
                        company[index]["website"], company[index]["about"], company[index]["headquarters"],
                    ))

                elif index > 0 and index < len_experience:
                    rows.append((
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["company"], company[index]["head_count"],
                        NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["position"], experience[index]["company"], experience[index]["experience"],
                        education[index]["school_name"], education[index]["field_of_study"], education[index]["degree_name"],
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        company[index]["website"], company[index]["about"], company[index]["headquarters"],
                    ))

                else:
                    rows.append((
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        NO_VAL, NO_VAL,
                        NO_VAL, NO_VAL, NO_VAL,
                        NO_VAL, NO_VAL, NO_VAL,
                        education[index]["school_name"], education[index]["field_of_study"], education[index]["degree_name"],
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        NO_VAL, NO_VAL, NO_VAL,
                    ))
        else:
            for index, _ in enumerate(range(len_education)):
                if index == 0:
                    rows.append((
                        email, first_name, middle_name, last_name, phone_number, country,
                        experience[index]["company"], company[index]["head_count"],
                        industry, institute, source,
                        experience[index]["position"], experience[index]["company"], experience[index]["experience"],
                        education[index]["school_name"], education[index]["field_of_study"], education[index]["degree_name"],
                        seniority_level, function, title, photo,
                        company[index]["website"], company[index]["about"], company[index]["headquarters"],
                    ))

                else:
                    rows.append((
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["company"], company[index]["head_count"],
                        NO_VAL, NO_VAL, NO_VAL,
                        experience[index]["position"], experience[index]["company"], experience[index]["experience"],
                        education[index]["school_name"], education[index]["field_of_study"], education[index]["degree_name"],
                        NO_VAL, NO_VAL, NO_VAL, NO_VAL,
                        company[index]["website"], company[index]["about"], company[index]["headquarters"],
                    ))

        rows.append((
            NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL, NO_VAL,
            NO_VAL, NO_VAL,
            NO_VAL, NO_VAL, NO_VAL,
            NO_VAL, NO_VAL, NO_VAL,
            NO_VAL, NO_VAL, NO_VAL,
            NO_VAL, NO_VAL, NO_VAL, NO_VAL,
            NO_VAL, NO_VAL, NO_VAL,
        ))

    df = pd.DataFrame(
        data=rows,
        columns=[
            "Email", "First Name", "Middle Name", "Last Name", "Phone Number", "Country",
            "Company Name", "Company HeadCount",
            "Indusrty", "Institute", "Source",
            "Position", "Company", "Experience",
            "School Name", "Field of Study", "Degree Name",
            "Senority Level", "Funtion", "Title", "Photograph",
            "Company Website", "About Company", "Headquaters",
        ]
    )

    df.to_csv(export_file_name, index=False)


# Browser Navigation Helpers
def wait_for(browser: object, element_xpath: str, delay: int = 60) -> bool:
    try:
        WebDriverWait(browser, delay).until(
            ec.presence_of_element_located((By.XPATH, element_xpath)))
        return True
    except TimeoutException:
        return False


def make_browser(headless: bool = False) -> object:
    driver_path: str = "./browser_assets/webdriver/geckodriver.exe"
    browser_path: str = "./browser_assets/browser/firefox.exe"

    arguments: list = [
        "--disable-dev-shm-usage",
        "--no-sandbox",
    ]

    if headless:
        arguments.append("--headless")

    browser_options: object = Options()

    for argument in arguments:
        browser_options.add_argument(argument)

    browser: object = webdriver.Firefox(
        executable_path=driver_path,
        options=browser_options,
        firefox_binary=browser_path
    )

    return browser


def is_available(browser: object, element_xpath: str, delay: int = 1) -> bool:
    try:
        WebDriverWait(browser, delay).until(
            ec.presence_of_element_located((By.XPATH, element_xpath)))
        return True
    except TimeoutException:
        return False


def scroll_page_to_bottom(browser: object) -> None:
    with open("./js/scroll.js") as scroll_script:
        browser.execute_script(scroll_script.read())
    time.sleep(15)


def quit_browser(browser: object) -> None:
    browser.close()
    browser.quit()
    browser.service.stop()
