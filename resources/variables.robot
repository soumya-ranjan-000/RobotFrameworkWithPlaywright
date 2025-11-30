*** Variables ***
${URL}              https://ecommerce-playground.lambdatest.io/
${BROWSER}          chromium
${HEADLESS}         ${False}
${VIEWPORT_WIDTH}   1920
${VIEWPORT_HEIGHT}  1080
${EXECUTION_ENV}    remote

# Cloud Provider Credentials (Dummy by default)
${LT_USERNAME}      rakiraja7751841655
${LT_ACCESS_KEY}    qiVXAvskeaUSiPueoIrTygPUvhl65iLge56FN0zs9T9fQ6VArS
${REMOTE_URL}       https://${LT_USERNAME}:${LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub
