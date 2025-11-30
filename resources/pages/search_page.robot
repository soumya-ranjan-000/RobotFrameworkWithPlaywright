*** Settings ***
Library    Browser
Resource   ../variables.robot

*** Keywords ***
Search For Product
    [Arguments]    ${product_name}
    Type Text    ${SEARCH_INPUT}    ${product_name}
    Click        ${SEARCH_BUTTON}

Verify Search Results
    [Arguments]    ${product_name}
    Wait For Elements State    h1 >> text="Search - ${product_name}"    visible
    ${count}=    Get Element Count    ${PRODUCT_CARD}
    Should Be True    ${count} > 0

*** Variables ***
${SEARCH_INPUT}     div#search input[name="search"][data-autocomplete_route]
${SEARCH_BUTTON}    //div[@class="search-button"]/button[not(@class="type-icon")]
${PRODUCT_CARD}     //div[@class="image"]
