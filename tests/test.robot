*** Settings ***
Library   Browser

Suite Setup    New Browser    chromium    headless=False
Suite Teardown    Close Browser

*** Test Cases ***
Example Test
    New Page    https://playwright.dev
    Get Text    h1    contains    Playwright