*** Settings ***
Documentation       End-to-end test scenarios for the LambdaTest E-Commerce Playground.
...                 Uses the Robot Framework Browser library (Playwright).

Library             Browser
Library             OperatingSystem
Library             pabot.PabotLib
Library             ../custom_libs/compare_images.py
Resource            ../resources/common.robot
Resource            ../resources/pages/home_page.robot
Resource            ../resources/pages/search_page.robot
Resource            ../resources/pages/product_page.robot
Resource            ../resources/pages/cart_page.robot

Suite Setup         Run Setup Only Once    Open Test Browser    execution_env=${EXECUTION_ENV}
Suite Teardown      Run Teardown Only Once    Close Test Browser


*** Test Cases ***

Verify Homepage Loads Successfully
   [Documentation]    Checks if the homepage loads and critical elements are visible.
   Load Homepage
   Verify Homepage Elements

Search For An Existing Product
   [Documentation]    Verifies that searching for "iPhone" returns relevant results.
   Load Homepage
   Search For Product    iPhone
   Verify Search Results    iPhone

Add First Available Product To Cart
    [Documentation]    Navigates to the homepage, adds the first featured product to the cart, and verifies the success message.
    Load Homepage
    Add First Product To Cart
    Verify Product Added To Cart

Verify Top Categories Are Visible
    [Documentation]    Checks if the top categories are displayed on the homepage.
    Load Homepage
    Navigate To Top Category    Shop by Category
    
    ${PROJECT_ROOT}=    Evaluate    os.path.abspath(os.path.join(r"${CURDIR}", os.pardir))    modules=os
    ${FILENAME}=       Evaluate    os.path.join(r"${PROJECT_ROOT}", "top_categories_actual.png")    modules=os
    Take Screenshot    selector=xpath=//h5[text()='Top categories ']/parent::div    filename=${FILENAME}
    
    # Optionally, you can add image comparison logic here if needed.
    # Note: compare_images is now in custom_libs
    ${res}=    compare_images   ${FILENAME}    ${PROJECT_ROOT}/top_categories_expected.png
    IF    ${res["ssim_score"]} < 1.0
        IF   ${res["ocr_result"]} == False
            Fail    Images differ significantly and OCR detected differences. See logfile for details.
        END    
    ELSE
        Pass Execution    Images match within acceptable limits.
    END