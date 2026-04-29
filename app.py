from flask import Flask, request, jsonify, render_template_string
from counter_service import CounterService
from storage import FileStorage
import uuid

app = Flask(__name__)

counter_service = CounterService(FileStorage('counter_data.json'))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Visit Counter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .stat-box {
            background: #f0f0f0;
            padding: 20px;
            margin: 10px 0;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            margin: 5px;
            cursor: pointer;
        }
        .reset-btn {
            background: #ff4444;
            color: white;
            border: none;
        }
    </style>
</head>
<body>
    <h1>Visit Counter</h1>

    <div class="stat-box">
        <h2>All Time Statistics</h2>
        <p><strong>Total Visits:</strong> {{ stats_all.total_visits }}</p>
        <p><strong>Unique Visitors:</strong> {{ stats_all.unique_visitors }}</p>
    </div>

    <div class="stat-box">
        <h2>Today's Statistics</h2>
        <p><strong>Total Visits:</strong> {{ stats_today.total_visits }}</p>
        <p><strong>Unique Visitors:</strong> {{ stats_today.unique_visitors }}</p>
    </div>

    <div>
        <button onclick="location.href='/stats'">Get JSON Stats</button>
        <form action="/reset" method="POST" style="display:inline;">
            <button type="submit" class="reset-btn" onclick="return confirm('Reset all statistics?')">
                Reset Statistics
            </button>
        </form>
    </div>
</body>
</html>
'''


@app.route('/')
def index():
    ip = request.remote_addr
    cookie = request.cookies.get('visitor_id')
    counter_service.add_visit(ip, cookie)

    stats_all = counter_service.get_stats('all')
    stats_today = counter_service.get_stats('today')

    response = app.make_response(
        render_template_string(
            HTML_TEMPLATE,
            stats_all=stats_all,
            stats_today=stats_today
        )
    )

    if not cookie:
        response.set_cookie('visitor_id', str(uuid.uuid4()), max_age=31536000)

    return response


@app.route('/stats')
def get_stats():
    ip = request.remote_addr
    cookie = request.cookies.get('visitor_id')
    counter_service.add_visit(ip, cookie)

    period = request.args.get('period', 'all')
    stats = counter_service.get_stats(period)

    return jsonify(stats)


@app.route('/reset', methods=['POST'])
def reset_stats():
    counter_service.reset()
    return jsonify({'status': 'success', 'message': 'Statistics reset'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)