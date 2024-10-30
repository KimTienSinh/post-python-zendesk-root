import json
import urllib.parse
import arrow
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_hc_settings():
    # Split the credentials into a tuple for basic authentication
    email = os.environ.get('ZENDESK_EMAIL')
    token = os.environ.get('ZENDESK_TOKEN')
    credentials = (f"{email}/token", token)  # This will be used for basic auth with requests

    return {
        'base_url': os.environ.get('ZENDESK_URL'),
        'credentials': credentials,
        'agent_id': os.environ.get('ZENDESK_AGENT_ID')
    }

def get_new_posts(topic_id, start_time):
    if start_time:
        start_time = arrow.get(start_time)
    else:
        start_time = arrow.utcnow().shift(hours=-1)

    hc = get_hc_settings()
    url = f'{hc["base_url"]}/api/v2/community/topics/{topic_id}/posts.json'
    headers = {'Content-Type': 'application/json'}

    # get new posts
    new_posts = []
    while url:
        response = requests.get(url, auth=hc['credentials'], headers=headers)
        if response.status_code != 200:
            error =  {'status_code': response.status_code, 'text': response.text}
            return {'error': error}
        data = response.json()
        url = data['next_page']
        for post in data['posts']:
            created_at_time = arrow.get(post['created_at'])
            if created_at_time > start_time:
                new_posts.append(post)
            else:                   # no more new posts
                url = None          # stop paginating
                break               # stop 'for' loop

    # reformat data for response
    external_resources = []
    for post in new_posts:
        external_id = str(post['author_id'])
        author = {'external_id': external_id, 'name': 'community user'}
        resource = {
            'external_id': str(post['id']),
            'message': post['title'],
            'html_message': post['details'],
            'created_at': post['created_at'],
            'author': author
        }
        external_resources.append(resource)

    # get next start time
    if external_resources:
        created_at_times = []
        for resource in external_resources:
            created_at_times.append(arrow.get(resource['created_at']))
        start_time = max(created_at_times)   # get most recent datetime in list

    # add start_time to state
    state = {'start_time': start_time.isoformat()}

    # convert state dict to JSON object, then URL encode
    state = urllib.parse.quote(json.dumps(state))

    return {
        'external_resources': external_resources,
        'state': state
    }


def create_post_comment(post_id, comment):
    hc = get_hc_settings()
    url = f'{hc["base_url"]}/api/v2/community/posts/{post_id}/comments.json'
    data = {'comment': {'body': comment, 'author_id': hc['agent_id']}}
    auth = hc['credentials']
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    response = requests.post(url, json=data, auth=auth, headers=headers)
    if response.status_code != 201:
        error = f'{response.status_code}: {response.text}'
        print(f'Failed to create post comment with error {error}')
        return {'error': response.status_code}

    comment = response.json()['comment']
    return {'external_id': str(comment['id']), 'allow_channelback': False}