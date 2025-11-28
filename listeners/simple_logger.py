import os
import re

from robot.libraries.BuiltIn import BuiltIn


class SimpleLogger:
    ROBOT_LISTENER_API_VERSION = 3
    SCREENSHOT_DIR = "screenshots"

    def __init__(self):
        # Ensure the screenshot directory exists
        os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)

    def start_test(self, name, attributes):
        """Called when a test case starts."""
        print(f"--- STARTING TEST: {name} ---")

    def end_test(self, name, result):
        """Called when a test case ends. In V3, the second argument is the result object."""
        # Access the status using dot notation (result.status).
        status = result.status
        print(f"--- ENDED TEST: {name} with status {status} ---")

        # Logic to listen specifically for failure and take screenshots
        if status == 'FAIL':
            try:
                # 1. Get the instance of the Browser library
                browser_library = BuiltIn().get_library_instance('Browser')

                # 2. Call the instance's method to get the active Playwright page object
                # page = browser_library.playwright.current_page

                safe_name = re.sub(r'[^\w\-_\.]', '_', name)

                full_page_path = os.path.join(self.SCREENSHOT_DIR, f"{safe_name}_full_page_failure.png")
                # page.screenshot(path=full_page_path, full_page=True)
                BuiltIn().run_keyword('Take Screenshot')
                print(f"!!! Full webpage screenshot saved to: {full_page_path} !!!")

                # # 2. Attempt to parse the failing selector and take an element screenshot
                # selector_match = re.search(r"locator\('(.+?)'\)", result.message)
                #
                # if selector_match:
                #     failing_selector = selector_match.group(1)
                #     element_path = os.path.join(self.SCREENSHOT_DIR, f"{safe_name}_element_failure.png")
                #
                #     # Use the page.locator method to find the element
                #     locator = page.locator(failing_selector).first
                #
                #     # Ensure the element is visible before trying to screenshot it
                #     if locator.is_visible():
                #         locator.screenshot(path=element_path)
                #         print(f"!!! Element screenshot for '{failing_selector}' saved to: {element_path} !!!")
                #     else:
                #         print("Element identified in error message was not visible for element screenshot.")
                # else:
                #     print("Could not parse failing selector from error message for element screenshot.")

            except Exception as e:
                # Catch exceptions during the screenshot process itself
                print(f"WARNING: Failed to take screenshot in listener: {e}")

            # Print original failure message
            print(f"!!! TEST FAILURE DETECTED: {name} failed with message: {result.message} !!!")

    def end_suite(self, name, attributes):
        """Called when a test suite ends."""
        print(f"\n--- SUITE '{name}' FINISHED ---")