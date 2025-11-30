*** Settings ***
Library    Browser
Resource   ../variables.robot

*** Keywords ***
Load Homepage
    New Page    ${URL}
    Get Title   ==    Your Store

Verify Homepage Elements
    Wait For Elements State    text="Shop by Category"    visible
    Wait For Elements State    ${SEARCH_INPUT}            visible

Navigate To Top Category
    [Arguments]    ${category_name}
    Wait For Elements State    //a[text()=' ${category_name}']    visible    timeout=10s
    Click    //a[text()=' ${category_name}']

*** Variables ***
${SEARCH_INPUT}     div#search input[name="search"][data-autocomplete_route]
