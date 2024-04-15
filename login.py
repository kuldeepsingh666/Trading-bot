from fyers_apiv3 import fyersModel
import credentials as cred
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pyotp as tp


def login():
    client_id = cred.client_id
    secret_key = cred.secret_key
    redirect_uri = cred.redirect_url
    totp_key = cred.totp_key

    response_type = "code"
    grant_type = "authorization_code"


    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type=response_type,
        grant_type=grant_type
    )
    # Generate the auth code using the session model
    response = session.generate_authcode()

    # Print the auth code received in the response
    print(response)


    link = response

    driver = webdriver.Chrome()
    # Set Chrome options for headless mode
    # options = Options()
    # options.add_argument('--headless=new')

    # Initialize Chrome webdriver
    # driver = webdriver.Chrome(options=options)

    driver.get(link)

    time.sleep(1)
    login_with_client_id_x_path = '//*[@id="login_client_id"]'
    elem = driver.find_element(By.XPATH, login_with_client_id_x_path)
    elem.click()
    time.sleep(1)
    client_id_input_x_path = '//*[@id="fy_client_id"]'
    elem1 = driver.find_element(By.XPATH, client_id_input_x_path)
    elem1.send_keys(cred.user)
    elem1.send_keys(Keys.RETURN)

    time.sleep(1)

    t = tp.TOTP(totp_key).now()

    driver.find_element(By.XPATH, '//*[@id="first"]').send_keys(t[0])
    driver.find_element(By.XPATH, '//*[@id="second"]').send_keys(t[1])
    driver.find_element(By.XPATH, '//*[@id="third"]').send_keys(t[2])
    driver.find_element(By.XPATH, '//*[@id="fourth"]').send_keys(t[3])
    driver.find_element(By.XPATH, '//*[@id="fifth"]').send_keys(t[4])
    driver.find_element(By.XPATH, '//*[@id="sixth"]').send_keys(t[5])

    driver.find_element(By.XPATH, '//*[@id="confirmOtpSubmit"]').click()
    time.sleep(1)

    driver.find_element(By.ID, "verifyPinForm").find_element(By.ID, "first").send_keys(cred.pin1)
    driver.find_element(By.ID, "verifyPinForm").find_element(By.ID, "second").send_keys(cred.pin2)
    driver.find_element(By.ID, "verifyPinForm").find_element(By.ID, "third").send_keys(cred.pin3)
    driver.find_element(By.ID, "verifyPinForm").find_element(By.ID, "fourth").send_keys(cred.pin4)

    driver.find_element(By.XPATH, '//*[@id="verifyPinSubmit"] ').click()

    time.sleep(2)
    new_url = driver.current_url  # Get the current URL before closing the driver
    print(new_url)
    driver.close()  # Now you can close the driver
    auth_code = new_url[new_url.index('auth_code=')+10: new_url.index('&state')]
    print(auth_code)

    # Create a session object to handle the Fyers API authentication and token generation
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type=response_type,
        grant_type=grant_type
    )

    # Set the authorization code in the session object
    session.set_token(auth_code)

    # Generate the access token using the authorization code
    response = session.generate_token()

    # Print the response, which should contain the access token and other details
    print(response)

    access_token=response['access_token']
    with open('access.txt','w') as k:
        k.write(access_token)