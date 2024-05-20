from flask import Flask, render_template, Response, request, send_file, jsonify
from flask_cors import CORS
import requests
import freedns
import random
import string


## CONFIG ##

ip = ""  # the default ip for the site. can be overrided by request headers
length = 16 # the length of the usernames,firstnames,passwords,lastnames and the subdomain length. the longer the better, less duplicates

## END OF CONFIG ##



client = freedns.Client()
app = Flask('__dnsing__')
CORS(app)

def randomString(N):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(N))

def getEmailInbox(email):
    url = f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Application-Name": "web",
        "Application-Version": "2.4.1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }

    params = {
        "referrer": "https://temp-mail.io/",
        "method": "GET",
        "mode": "cors"
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()


def generateRandomEmail(): 
    url = "https://api.internal.temp-mail.io/api/v3/email/new"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json;charset=utf-8",
        "Referer": "https://temp-mail.io/",
        "Application-Name": "web",
        "Application-Version": "2.4.1",
        "Origin": "https://temp-mail.io",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive",
        "Cookie": "_ga=GA1.2.707509929.1715546874; _gid=GA1.2.1539898098.1715546874; _gat=1; _ga_3DVKZSPS3D=GS1.2.1715546874.1.1.1715546898.36.0.0; __gads=ID=040f9f87d10f93bd:T=1715546877:RT=1715546877:S=ALNI_MZtJcGiGQbRA472JwPAk4rU3ZikLQ; __gpi=UID=00000e05e83f565d:T=1715546877:RT=1715546877:S=ALNI_Mb4oE6o8E1hEFIZcKvN5godRU9utA; __eoi=ID=be4fae4976dc5020:T=1715546877:RT=1715546877:S=AA-AfjYU9yeVGK8BMR796WPCkxLo",
        "TE": "trailers"
    }
    data = {
        "min_name_length": 10,
        "max_name_length": 10
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

@app.route('/api/v1/get/captcha')
def captcha_Get():
    captcha = client.get_captcha()

    with open('capthca.png', 'wb') as f:
        f.write(captcha)
    return send_file('capthca.png')
    
@app.route('/api/v1/get/email')
def email_get():
    return generateRandomEmail()

@app.route('/api/v1/post/createAccount')
def create_account_post():
    print("GOT AC REQUEST")
    email = request.headers.get('email-code')
    captcha = request.headers.get('capthca-code')

    username = randomString(16)
    lastname = randomString(16)
    firstname = randomString(16) 
    password = randomString(16)


    client.create_account(captcha, firstname, lastname, username, password, email)
    data = {
        "username": username,
        "lastname": lastname,
        "firstname": firstname,
        "password": password
    }
    return jsonify(data)

@app.route('/api/v1/get/inbox')
def get_inbox():
    return getEmailInbox(request.headers.get('in-box'))

@app.route('/api/v1/post/activateAccount')
def post_activateAccount():
    client.activate_account(request.headers.get('activation-code'))
    return 'activated account i hope'

@app.route('/api/v1/post/createSubdomain')
def post_createSubdomain():
    username = request.headers.get('user-name')
    password = request.headers.get('pass-word')
    subdomainName = randomString(16)
    domain_id = request.headers.get('domain-id')
    destination = "38.175.196.242"
    captcha_code = request.headers.get('captcha-code')
    record_type = "A"

    data = {
        "subdomain": subdomainName,
        "destination": destination
    }

    client.login(username, password)
    client.create_subdomain(captcha_code, record_type, subdomainName, domain_id, destination)
    return jsonify(data)

@app.route('/api/v1/get/registry')
def get_reg():
    query = request.headers.get('query-code')
    return client.get_registry(page=1, query=query, sort=1)

app.run(debug=True)
