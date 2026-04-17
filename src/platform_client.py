from __future__ import annotations

from dataclasses import dataclass

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@dataclass
class PlatformSession:
    session: requests.Session
    base_url: str

    def login(self, username: str, password: str) -> None:
        # Login to the platform using the given credentials
        login_url = f"{self.base_url}/login"
        payload = {"username": username, "password": password}
        # POST credentials and persist session cookies
        response = self.session.post(login_url, data=payload, timeout=10)

        # Raise an error on unsuccessful login
        response.raise_for_status()

    def fetch_account_html(self) -> str:
        # Request the account page using the authenticated session
        account_url = f"{self.base_url}/account"
        response = self.session.get(account_url, timeout=10)

        # Ensure request was successful before returning HTML
        response.raise_for_status()
        return response.text

    def open_account_in_browser(self) -> None:
        """Optional helper to inspect the page manually with Selenium.

        This is not required to solve the assignment, but it reflects the kind of
        tooling the team uses in production.
        """
        options = Options()
        options.add_argument("-no-sandbox")
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(f"{self.base_url}/account")
            print(driver.title)
        finally:
            driver.quit()


def build_session(base_url: str) -> PlatformSession:
    return PlatformSession(session=requests.Session(), base_url=base_url.rstrip("/"))
