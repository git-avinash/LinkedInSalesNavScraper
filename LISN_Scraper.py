from helpers import get_inputs, make_browser, print_app_end, quit_browser, get_defaults, get_links, get_data, make_json_to_csv, make_json, get_inputs, print_app_info, get_filters

import time


class App:
    def __init__(self) -> None:
        print_app_info()

        self.browser: object = make_browser(headless=False)

        self.browser.get(get_defaults("url", "login"))

        self.scrape_data_amount: int = get_inputs(self.browser)

        self.filters: dict = get_filters(self.browser)

        self.result_links: list = get_links(
            self.browser, self.scrape_data_amount)

        self.scraped_details: dict = get_data(
            self.browser, self.result_links, self.scrape_data_amount)

        self.scraped_details["filters"] = self.filters

        quit_browser(self.browser)

        file_name = "./ScrapedData/ScrapedData_{}".format(
            time.strftime("%d_%b_%Y_%H_%M", time.localtime()))

        make_json(self.scraped_details, f"{file_name}.json")

        make_json_to_csv(
            f"{file_name}.json",
            f"{file_name}.csv"
        )

        print_app_end()


App()
