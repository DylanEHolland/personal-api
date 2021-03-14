LINKEDIN_API_ENDPOINT="https://api.linkedin.com/v2"
from linkedin import linkedin
import os
from flask import request

def get_user_details(client):
    url = '%s/emailAddress?q=members&projection=(elements*(handle~))' % LINKEDIN_API_ENDPOINT
    response = client.make_request('GET', url)
    output = None
    response = response.json()
    email_address = response['elements'][0]['handle~']['emailAddress']
    url = "%s/me?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))" % LINKEDIN_API_ENDPOINT
    response = client.make_request('GET', url)
    response = response.json()

    if response and "firstName" in response and "lastName" in response:
        first_name = response['firstName']['localized']['en_US']
        last_name = response['lastName']['localized']['en_US']

    return first_name, last_name, email_address


def linkedin_client():
    print(request.base_url)
    return linkedin.LinkedInAuthentication(
        os.environ.get("LINKEDIN_KEY"),
        os.environ.get("LINKEDIN_SECRET"),
        request.base_url + "/auth/linkedin-callback",
        ['r_liteprofile', 'r_emailaddress']
    )