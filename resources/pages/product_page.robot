*** Settings ***
Library    Browser
Resource   ../variables.robot

*** Keywords ***
Add First Product To Cart
    Scroll To Element    ${PRODUCT_CARD} >> nth=0
    Hover    ${PRODUCT_CARD} >> nth=0
    Click    ${PRODUCT_CARD} >> nth=0 >> ${ADD_TO_CART_BTN}

*** Variables ***
${PRODUCT_CARD}     //div[@class="image"]
${ADD_TO_CART_BTN}  (//button[@title="Add to Cart"])[1]
