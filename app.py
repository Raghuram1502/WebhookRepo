from flask import Flask,request,render_template,jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["github_events"]
collection = db["events"]

def timestamp_format(dt):
    return dt.strftime('%d %B %Y - %I:%M %p UTC')

def process_event(event_type,data):
    timestamp = datetime.utcnow()
    formatted_time = timestamp_format(timestamp)
    message = ""

    if event_type == "push":
        author = data['pusher']['name']
        branch = data['ref'].split('/')[-1]
        message = f'"{author}" pushed to "{branch}" on {formatted_time}'  

    elif event_type == 'pull_request':
        author = data['sender']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']

        if data['action'] == 'closed' and data['pull_request'].get('merged'):
            message = f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {formatted_time}'
        else:
            message = f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {formatted_time}'

    return {
        'message': message,
        'timestamp': timestamp
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    data = request.json
    parsed = process_event(event_type, data)
    if parsed['message']:
        collection.insert_one(parsed)
    return jsonify({'status': 'received'}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = collection.find().sort('timestamp', -1).limit(10)
    return jsonify([e['message'] for e in events])

if __name__ == "__main__":
    app.run(debug=True)