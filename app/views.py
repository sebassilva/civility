import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8001"

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]

    user = request.form["user"]
    person = request.form["person"]
    grade = request.form["grade"]
    comment = request.form["comment"]
    signature = request.form["signature"]




    post_object = {
        'content': post_content,
        'user': user,
        'person': person,
        'grade': grade,
        'comment': comment,
        'signature': signature,
    }

    # TODO: Validate data

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')



@app.route('/submit_new_user', methods=['POST'])
def register_new_user():
    """
    Endpoint to create a new peer
    This just passes the information to the node server it is connected to :)
    """

    user = request.form["user"]
    password = request.form["password"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    curp = request.form["curp"]
    node_address = request.form["node_address"]


    post_object = {
        'user': user,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'curp': curp,
        'node_address': node_address,
    }
    print('POST OBJETC', post_object)

    # TODO: Validate data

    # Submit a transaction
    new_tx_address = "{}/register_node".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    print(new_tx_address)

    return redirect('/')





def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
