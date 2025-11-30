*** Settings ***
Library    Browser    jsextension=${EXECDIR}/browserstackExecutor.js
Library    OperatingSystem
Library    Collections
Library    ../custom_libs/browserstack_connection_helper.py
Resource   variables.robot

*** Keywords ***
Open Test Browser
    [Arguments]    ${execution_env}=local
    IF    '${execution_env}' == 'local'
        New Browser    browser=${BROWSER}    headless=${HEADLESS}
        New Context    viewport={'width': ${VIEWPORT_WIDTH}, 'height': ${VIEWPORT_HEIGHT}}
    ELSE IF    '${execution_env}' == 'remote'
        startLocalTunnel
        ${cdpURL}=    createCdpUrl    ${BROWSER}
        ${platfromDetails}=    getPlatformDetails
        Log    Connecting to remote browser at ${CDP_URL}
        Connect To Browser    ${CDP_URL}
    END

Close Test Browser
    Close Context
    Close Browser
    stopLocalTunnel
