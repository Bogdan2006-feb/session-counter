import os
from flask import Flask, request, jsonify, render_template_string, abort
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
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f4f4f4; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        h2 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f9f9f9; }
        .admin-link { display: inline-block; margin-top: 20px; color: #666; text-decoration: none; }
        .admin-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>📊 Visit Counter</h1>

    <div class="card">
        <h2>General Stats</h2>
        <p><strong>Total Visits:</strong> {{ stats.total_visits }}</p>
        <p><strong>Unique Visitors:</strong> {{ stats.unique_visitors }}</p>
    </div>

    <div class="stats-grid">
        <div class="card">
            <h2>📅 By Day</h2>
            <table>
                {% for day, count in stats.visits_by_day.items() %}
                <tr><td>{{ day }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>

        <div class="card">
            <h2>📅 By Week</h2>
            <table>
                {% for week, count in stats.visits_by_week.items() %}
                <tr><td>{{ week }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <div class="stats-grid">
        <div class="card">
            <h2>📅 By Month</h2>
            <table>
                {% for month, count in stats.visits_by_month.items() %}
                <tr><td>{{ month }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>

        <div class="card">
            <h2>📱 Devices / Browsers</h2>
            <table>
                {% for device, count in stats.devices.items() %}
                <tr><td>{{ device }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <a href="/admin" class="admin-link">🔐 Admin Panel →</a>
</body>
</html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body { font-family: sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #fff8f8; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #cc0000; }
        h2 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f9f9f9; }
        .btn-reset { background: #ff4444; color: white; border: none; padding: 15px 30px; cursor: pointer; border-radius: 4px; font-size: 16px; }
        .btn-reset:hover { background: #ff0000; }
        .warning { background: #fff3cd; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #ffc107; }
        .back-link { display: inline-block; margin-top: 20px; color: #666; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>🔐 Admin Panel</h1>

    <div class="warning">
        <strong>Warning:</strong> This page is only accessible from localhost. 
        Resetting will permanently delete all statistics.
    </div>

    <div class="card">
        <h2>⚠️ Reset All Data</h2>
        <form action="/admin/reset" method="POST">
            <button type="submit" class="btn-reset" onclick="return confirm('Are you sure? This cannot be undone!')">
                ⚠️ RESET ALL STATISTICS
            </button>
        </form>
    </div>

    <div class="card">
        <h2>General Stats</h2>
        <p><strong>Total Visits:</strong> {{ stats.total_visits }}</p>
        <p><strong>Unique Visitors:</strong> {{ stats.unique_visitors }}</p>
    </div>

    <div class="stats-grid">
        <div class="card">
            <h2>📅 By Day</h2>
            <table>
                {% for day, count in stats.visits_by_day.items() %}
                <tr><td>{{ day }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>

        <div class="card">
            <h2>📅 By Week</h2>
            <table>
                {% for week, count in stats.visits_by_week.items() %}
                <tr><td>{{ week }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <div class="stats-grid">
        <div class="card">
            <h2>📅 By Month</h2>
            <table>
                {% for month, count in stats.visits_by_month.items() %}
                <tr><td>{{ month }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>

        <div class="card">
            <h2>📱 Devices / Browsers</h2>
            <table>
                {% for device, count in stats.devices.items() %}
                <tr><td>{{ device }}</td><td>{{ count }}</td></tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <a href="/" class="back-link">← Back to public page</a>
</body>
</html>
'''


def is_local_request():
    ip = request.remote_addr
    return ip in ['127.0.0.1', 'localhost', '::1'] or ip.startswith('192.168.') or ip.startswith('10.')


@app.route('/')
def index():
    ip = request.remote_addr
    cookie = request.cookies.get('visitor_id')
    user_agent = request.headers.get('User-Agent', 'Unknown')

    counter_service.add_visit(ip, user_agent, cookie)

    stats = counter_service.get_stats('all')

    response = app.make_response(
        render_template_string(HTML_TEMPLATE, stats=stats)
    )

    if not cookie:
        response.set_cookie('visitor_id', str(uuid.uuid4()), max_age=31536000)

    return response


@app.route('/admin')
def admin():
    if not is_local_request():
        abort(403)

    stats = counter_service.get_stats('all')
    return render_template_string(ADMIN_TEMPLATE, stats=stats)


@app.route('/admin/reset', methods=['POST'])
def admin_reset():
    if not is_local_request():
        abort(403)

    counter_service.reset()
    return jsonify({'status': 'success', 'message': 'Statistics reset'})


@app.route('/reset', methods=['POST'])
def reset_stats():
    abort(404)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)