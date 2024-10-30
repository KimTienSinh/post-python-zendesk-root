import community
import random
import os
import json
import urllib.parse
from bottle import route, run, request, response, template
from pathlib import Path

@route('/')
def show_home():
    return '<p>Integration service for a Zendesk Support community channel</p>'

@route('/channels/community/pull', method='POST')
def pull_new_posts():
    metadata = request.forms.get('metadata')
    if metadata:
        metadata = urllib.parse.unquote(metadata)
        metadata = json.loads(metadata)
        topic_id = metadata.get('topic_id', '')

        start_time = ''
        if request.forms.get('state'):
            state = urllib.parse.unquote(request.forms['state'])
            state = json.loads(state)
            start_time = state.get('start_time', '')

        new_posts = community.get_new_posts(topic_id, start_time)
        if 'error' in new_posts:
            print(new_posts['error']['text'])
        else:
            response.status = 201
            response.headers['Content-Type'] = 'application/json'
            return json.dumps(new_posts)
    response.status = 400
    return "Bad Request: Missing 'metadata'"

@route('/channels/community/channelback', method='POST')
def channelback_ticket_comment():
    post_id = request.forms.get('parent_id')
    comment = request.forms.get('message')
    if post_id and comment:
        external_id = community.create_post_comment(post_id, comment)
        if 'error' in external_id:
            response.status = 500
            return
        response.status = 200
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(external_id)
    response.status = 400
    return "Bad Request: Missing 'parent_id' or 'message'"


@route('/channels/community/admin_ui', method='POST')
def show_admin_ui():
    return_url = request.forms['return_url']
    name = request.forms['name'] or 'Help Center community channel'
    
    topic_id = ''
    if 'metadata' in request.forms and request.forms['metadata']:
        metadata = request.forms['metadata']
        metadata = urllib.parse.unquote(metadata)
        metadata = json.loads(metadata)
        topic_id = metadata['topic_id']
    
    data = {
        'name': name,
        'topic_id': topic_id,
        'return_url': return_url
    }
    return template('admin', data=data)

@route('/channels/community/settings', method='POST')
def process_admin_settings():
    topic_id = request.forms['topic_id']
    if not topic_id or not topic_id.isdigit():
        return template('admin', data={'topic_id': 'invalid'})

    # set metadata
    metadata = {'topic_id': topic_id}
    metadata = urllib.parse.quote(json.dumps(metadata))

    data = {
        'return_url': request.forms['return_url'],
        'name': request.forms['name'],
        'metadata': metadata
    }
    return template('admin_callback', data=data)


@route('/channels/community/manifest')
def serve_manifest():
    file = Path('integration_manifest.json')
    with file.open(mode='r') as f:
        manifest = json.load(f)
    response.headers['Content-Type'] = 'application/json'
    return manifest


@route('/random_numbers', method='GET')
def get_random_numbers():
    random_numbers = [round(random.uniform(0, 1), 2) for _ in range(10)]

    response.content_type = 'application/json'
    return json.dumps({"random_numbers": random_numbers})

if __name__ == "__main__":
    if os.environ.get('ENVIRONMENT') == 'production':
        run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    else:
        run(host="localhost", port=8080, debug=True)