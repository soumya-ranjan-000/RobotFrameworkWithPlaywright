*** Settings ***
Library    Browser
Resource   ../variables.robot

*** Keywords ***
Verify Product Added To Cart
    Wait For Elements State    ${SUCCESS_ALERT}    visible    timeout=5s
    Get Text    ${SUCCESS_ALERT}    contains    Success: You have added

*** Variables ***
${SUCCESS_ALERT}    //div[@id='notification-box-top']//div[@class='toast-body']//p
