*** Settings ***
Documentation       End-to-end test scenarios for the LambdaTest E-Commerce Playground.
...                 Uses the Robot Framework Browser library (Playwright).

Library             Browser
Library             OperatingSystem
Library             ../lib/ImageComparision.py
Suite Setup         New Browser    browser=${BROWSER}    headless=${HEADLESS}
Test Setup          New Context    viewport={'width': ${VIEWPORT_WIDTH}, 'height': ${VIEWPORT_HEIGHT}}
#Test Teardown       Capture Screenshot On Failure
Test Teardown       Close Context
Suite Teardown      Close Browser

*** Variables ***
${URL}              https://ecommerce-playground.lambdatest.io/
${BROWSER}          chromium
${HEADLESS}         ${False}
${VIEWPORT_WIDTH}   1920
${VIEWPORT_HEIGHT}  1080

# Selectors
${SEARCH_INPUT}     div#search input[name="search"][data-autocomplete_route]
${SEARCH_BUTTON}    //div[@class="search-button"]/button[not(@class="type-icon")]
${PRODUCT_CARD}     //div[@class="image"]
${ADD_TO_CART_BTN}  (//button[@title="Add to Car"])[1]
${SUCCESS_ALERT}    //div[@id='notification-box-top']//div[@class='toast-body']//p

*** Keywords ***
Capture Screenshot On Failure
    Run Keyword If    '${TEST STATUS}' == 'FAIL'    Take Screenshot

*** Test Cases ***

Verify Homepage Loads Successfully
   [Documentation]    Checks if the homepage loads and critical elements are visible.
   New Page    ${URL}
   Get Title   ==    Your Store
   Wait For Elements State    text="Shop by Category"    visible
   Wait For Elements State    ${SEARCH_INPUT}            visible

Search For An Existing Product
   [Documentation]    Verifies that searching for "iPhone" returns relevant results.
   New Page    ${URL}

   # Perform Search
   Type Text    ${SEARCH_INPUT}    iPhone
   Click        ${SEARCH_BUTTON}

   # Verify Results Page
   Wait For Elements State    h1 >> text="Search - iPhone"    visible

   # Verify at least one product is displayed
   ${count}=    Get Element Count    ${PRODUCT_CARD}
   Should Be True    ${count} > 0

Add First Available Product To Cart
    [Documentation]    Navigates to the homepage, adds the first featured product to the cart, and verifies the success message.
    New Page    ${URL}

    Sleep    4s    # Wait for products to load
    # Scroll to the first product to ensure visibility
    Scroll To Element    ${PRODUCT_CARD} >> nth=0

    Sleep     3s    # Wait for any animations
    # Hover over the first product to trigger overlay (if any)
    Hover    ${PRODUCT_CARD} >> nth=0

    # Click the "Add to Cart" button inside the first product card
    # We use '>>' to chain selectors: First product card -> Add to Cart button
    Click    ${PRODUCT_CARD} >> nth=0 >> ${ADD_TO_CART_BTN}
    Sleep    3s
    # Verify the success toast message appears
    Wait For Elements State    ${SUCCESS_ALERT}    visible    timeout=5s
    Get Text    ${SUCCESS_ALERT}    contains    Success: You have added


Verify Top Categories Are Visible
    [Documentation]    Checks if the top categories are displayed on the homepage.
    New Page    ${URL}
    Wait For Elements State    //a[text()=' Shop by Category']    visible    timeout=10s
    Click    //a[text()=' Shop by Category']
    ${PROJECT_ROOT}=    Evaluate    os.path.abspath(os.path.join(r"${CURDIR}", os.pardir))    modules=os
    ${FILENAME}=       Evaluate    os.path.join(r"${PROJECT_ROOT}", "top_categories_actual.png")    modules=os
    Take Screenshot    selector=xpath=//h5[text()='Top categories ']/parent::div    filename=${FILENAME}
    # Optionally, you can add image comparison logic here if needed.
    ${res}=    compare_images   ${FILENAME}    ${PROJECT_ROOT}/top_categories_expected.png    output_dir=${PROJECT_ROOT}/output    method=absdiff    align=False    min_area=1000
    IF    ${res.regions_count} > 0
        IF   ${res.ssim_score} < 0.99999999999
            Fail    Top categories visual regression detected. SSIM Score: ${res.ssim_score}, Changed Percent: ${res.changed_percent}, Regions Detected: ${res.regions_count}. See output images at: ${res.output_paths}
        END    
    ELSE
        Pass Execution    message
    END
    Log    SSIM Score: ${res.ssim_score}, Changed Percent: ${res.changed_percent}, Regions Detected: ${res.regions_count}, Output Paths: ${res.output_paths}