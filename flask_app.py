import json
import requests

from config import config
from flask import Flask, render_template, request, redirect
from wtforms import Form, IntegerField, validators


app = Flask(__name__)
app.config.from_object(config['default'])

# Base addreses
base_api_url = 'https://api.stackexchange.com'
base_oauth_url = 'https://stackexchange.com/oauth'
base_oauth_token_url = base_oauth_url + '/access_token'

# Additional urls
get_users_info_url = '/2.2/users/{}?site=stackoverflow'
get_users_posts_url = '/2.2/users/{}/posts?site=stackoverflow'
get_personal_users_posts_url = '/2.2/me/posts?site=stackoverflow'

# List of Stackexchange application credentials
client_id = '11193'
redirect_uri = "http://localhost:5000"
client_secret = '35qF*sMB36Ju1JfNiL9VLw(('
key = 'vX7iutxvD0eY94F2ufmTMw(('


# Form for entering user id
class SearchPostsForm(Form):
    user_id = IntegerField(
        'User ID',
        [validators.NumberRange(min=1, max=10000000)]
    )


@app.route('/', methods=['GET', 'POST'])
def index():
    """
        View that contains search posts form and form that redirect user to
        "get_personal_posts" view.
        Search Posts Form:
            requires: user_id,
            returns: list of user's posts

        If Application Login Page on stackexchage returns code parameter
        that this view will get list of logged user.
    """
    form = SearchPostsForm(request.form)
    posts = None

    if request.method == 'GET':
        code = request.args.get('code')
        # If code parameter exists than application
        # can get access token to get personal user's posts
        if code:
            # Get access_token
            access_token = requests.post(
                base_oauth_token_url,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                }
            ).content.decode('utf-8')

            # Get personal posts
            posts = requests.get(
                ''.join([
                    base_api_url,
                    get_personal_users_posts_url,
                    "&{}".format(access_token),
                    "&key={}".format(key),
                ])
            ).content

    if request.method == 'POST' and form.validate():

            # Get posts by user_id
            posts = requests.get(
                ''.join([
                    base_api_url,
                    get_users_posts_url.format(form.user_id.data)
                ])
            ).content

    if posts:
        posts = json.loads(posts.decode('utf8'))['items']

    return render_template('index.html', form=form, posts=posts)


@app.route('/get-personal-posts/', methods=['POST'])
def get_personal_posts():
    """
        View that used for redirecting user to Application Login page
        on stackexchange
    """
    return redirect(
        ''.join([
                    base_oauth_url,
                    "?",
                    "client_id={}".format(client_id),
                    "&scope=no_expiry",
                    "&redirect_uri={}".format(redirect_uri),
                ])
        )


if __name__ == '__main__':
    app.run()
