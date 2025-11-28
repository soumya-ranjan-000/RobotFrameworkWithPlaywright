Robot Framework + Playwright E-Commerce Tests

This project contains test scenarios for the LambdaTest E-Commerce Playground using Robot Framework and the Browser library (powered by Playwright).

Prerequisites

Python: Ensure Python 3.8+ is installed.

Node.js: Required by the Browser library (Playwright).

Installation

Install Python Dependencies:

pip install -r requirements.txt


Initialize Playwright:
The Browser library requires a separate initialization step to download the browser binaries.

rfbrowser init


Running the Tests

To run the tests, execute the following command in your terminal:

robot ecommerce_tests.robot


Configuration Options

You can override the browser type or headless mode from the command line:

Run in Headless Mode (no visible UI):

robot --variable HEADLESS:True ecommerce_tests.robot


Run on Firefox:

robot --variable BROWSER:firefox ecommerce_tests.robot


Scenarios Covered

Verify Homepage Loads: Checks page title and visibility of the "Shop by Category" menu.

Search For An Existing Product: Searches for "iPhone" and verifies the search result header and product grid.

Add First Available Product To Cart: Adds the first item from the featured list to the cart and validates the success toast notification.