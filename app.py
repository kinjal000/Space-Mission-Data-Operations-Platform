import os
import sqlite3
import json
import socket
import logging
import time
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
try:
    import hvac
    HAS_VAULT = True
except ImportError:
    HAS_VAULT = False
    print("Warning: 'hvac' module not found. Vault features will be bypassed.")

try:
    from prometheus_flask_exporter import PrometheusMetrics
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    print("Warning: 'prometheus-flask-exporter' module not found. Metrics will be bypassed.")

app = Flask(__name__)

# Setup Logger
logger = logging.getLogger('polaris')
logger.setLevel(logging.INFO)

# Console logger
stdout_handler = logging.StreamHandler()
stdout_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(stdout_formatter)
logger.addHandler(stdout_handler)

# Custom Logstash UDP Logger
class LogstashUDPHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def emit(self, record):
        try:
            log_entry = {
                "timestamp": self.formatter.formatTime(record, "%Y-%m-%dT%H:%M:%S") + ".000Z",
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
                "file": record.filename,
                "line": record.lineno
            }
            if hasattr(record, 'extra_fields'):
                log_entry.update(record.extra_fields)
            payload = (json.dumps(log_entry) + "\n").encode('utf-8')
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, (self.host, self.port))
            sock.close()
        except Exception:
            pass

logstash_host = os.getenv('LOGSTASH_HOST', 'logstash')
logstash_port = int(os.getenv('LOGSTASH_PORT', '5000'))
logstash_handler = LogstashUDPHandler(logstash_host, logstash_port)
logstash_handler.setFormatter(stdout_formatter)
logger.addHandler(logstash_handler)

def log_event(message, level='info', extra=None):
    if extra is None:
        extra = {}
    extra_fields = {
        'username': session.get('username', 'anonymous'),
        'ip_address': request.remote_addr if request else '127.0.0.1',
        'url': request.path if request else 'startup'
    }
    extra_fields.update(extra)
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra={'extra_fields': extra_fields})

# Initialize Prometheus Metrics if available
if HAS_PROMETHEUS:
    try:
        metrics = PrometheusMetrics(app)
        metrics.info('app_info', 'Application info', version='1.0.0')
    except Exception as e:
        print(f"Failed to initialize Prometheus metrics: {e}")

# Initialize Vault and Retrieve Secrets
def init_vault():
    if not HAS_VAULT:
        return
    vault_addr = os.getenv('VAULT_ADDR', 'http://vault:8200')
    vault_token = os.getenv('VAULT_TOKEN', 'polaris-root-token')
    client = hvac.Client(url=vault_addr, token=vault_token)
    for i in range(15):
        try:
            if client.is_authenticated():
                # Ensure the polaris secret is created
                try:
                    client.secrets.kv.v2.read_secret_version(path='polaris', mount_point='secret')
                except Exception:
                    client.secrets.kv.v2.create_or_update_secret(
                        path='polaris',
                        secret={
                            'secret_key': 'polaris_vault_secret_key',
                            'db_path': 'database/polaris.db'
                        },
                        mount_point='secret'
                    )
                break
        except Exception as e:
            print(f"Waiting for Vault: {e}")
            time.sleep(2)

if HAS_VAULT:
    try:
        init_vault()
    except Exception as e:
        print(f"Vault initialization bypassed: {e}")

vault_secrets = {}
if HAS_VAULT:
    try:
        vault_addr = os.getenv('VAULT_ADDR', 'http://vault:8200')
        vault_token = os.getenv('VAULT_TOKEN', 'polaris-root-token')
        client = hvac.Client(url=vault_addr, token=vault_token)
        if client.is_authenticated():
            read_response = client.secrets.kv.v2.read_secret_version(path='polaris', mount_point='secret')
            vault_secrets = read_response['data']['data']
    except Exception as e:
        print(f"Failed to read from Vault: {e}")

app.secret_key = vault_secrets.get('secret_key', 'polaris_secret_key')
db_relative_path = vault_secrets.get('db_path', 'database/polaris.db')
DATABASE = os.path.join(os.path.dirname(__file__), db_relative_path)


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    db_path = DATABASE
    if not os.path.exists(db_path):
        print("Initializing database polaris.db...")
        db = sqlite3.connect(db_path)
        
        schema_path = os.path.join(db_dir, 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                db.cursor().executescript(f.read())
                
        sample_path = os.path.join(db_dir, 'sample_data.sql')
        if os.path.exists(sample_path):
            with open(sample_path, 'r') as f:
                db.cursor().executescript(f.read())
                
        db.commit()
        db.close()
        print("Database initialized successfully!")

# Initialize database on app startup within context
with app.app_context():
    init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        db.close()
        
        if user:
            session['username'] = user['username']
            flash('Successfully logged in!', 'success')
            log_event(f"User '{username}' successfully logged in", 'info', {'event_type': 'login_success'})
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            log_event(f"Failed login attempt for user '{username}'", 'warning', {'event_type': 'login_failed'})
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    session.pop('username', None)
    flash('Successfully logged out.', 'info')
    if username:
        log_event(f"User '{username}' logged out", 'info', {'event_type': 'logout'})
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    log_event("Accessed dashboard", 'info', {'event_type': 'dashboard_access'})
    db = get_db()
    total_satellites = db.execute('SELECT COUNT(*) FROM satellites').fetchone()[0]
    active_missions = db.execute("SELECT COUNT(*) FROM missions WHERE status = 'Active'").fetchone()[0]
    total_telemetry = db.execute('SELECT COUNT(*) FROM telemetry').fetchone()[0]
    
    completed_missions = db.execute("SELECT COUNT(*) FROM missions WHERE status = 'Completed'").fetchone()[0]
    failed_missions = db.execute("SELECT COUNT(*) FROM missions WHERE status = 'Failed'").fetchone()[0]
    total_finished = completed_missions + failed_missions
    
    if total_finished > 0:
        success_rate = round((completed_missions / total_finished) * 100, 1)
    else:
        success_rate = 100.0
        
    recent_satellites = db.execute('SELECT name, launch_date FROM satellites ORDER BY id DESC LIMIT 2').fetchall()
    recent_missions = db.execute('SELECT name, start_date, status FROM missions ORDER BY id DESC LIMIT 2').fetchall()
    recent_telemetry = db.execute('''
        SELECT s.name as sat_name, t.temperature, t.battery_level, t.signal_strength, t.timestamp
        FROM telemetry t
        JOIN satellites s ON t.satellite_id = s.id
        ORDER BY t.id DESC LIMIT 4
    ''').fetchall()
    
    mission_status_counts = db.execute('SELECT status, COUNT(*) as count FROM missions GROUP BY status').fetchall()
    mission_status = {row['status']: row['count'] for row in mission_status_counts}
    for status in ['Planning', 'Active', 'Completed', 'Failed']:
        if status not in mission_status:
            mission_status[status] = 0
            
    db.close()
    
    return render_template('dashboard.html',
                           total_satellites=total_satellites,
                           active_missions=active_missions,
                           total_telemetry=total_telemetry,
                           success_rate=success_rate,
                           recent_satellites=recent_satellites,
                           recent_missions=recent_missions,
                           recent_telemetry=recent_telemetry,
                           mission_status=mission_status)

@app.route('/satellites', methods=['GET', 'POST'])
@login_required
def satellites():
    log_event("Accessed satellites list", 'info', {'event_type': 'satellites_access'})
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            launch_date = request.form.get('launch_date')
            orbit_type = request.form.get('orbit_type')
            status = request.form.get('status')
            
            db.execute('INSERT INTO satellites (name, launch_date, orbit_type, status) VALUES (?, ?, ?, ?)',
                       (name, launch_date, orbit_type, status))
            db.commit()
            flash(f'Satellite "{name}" added successfully.', 'success')
            log_event(f"Satellite '{name}' added successfully", 'info', {'event_type': 'satellite_add', 'satellite_name': name})
            
        elif action == 'edit':
            sat_id = request.form.get('id')
            name = request.form.get('name')
            launch_date = request.form.get('launch_date')
            orbit_type = request.form.get('orbit_type')
            status = request.form.get('status')
            
            db.execute('UPDATE satellites SET name = ?, launch_date = ?, orbit_type = ?, status = ? WHERE id = ?',
                       (name, launch_date, orbit_type, status, sat_id))
            db.commit()
            flash(f'Satellite "{name}" updated successfully.', 'success')
            log_event(f"Satellite '{name}' updated successfully", 'info', {'event_type': 'satellite_update', 'satellite_name': name})
            
        db.close()
        return redirect(url_for('satellites'))
        
    satellites_list = db.execute('SELECT * FROM satellites ORDER BY id DESC').fetchall()
    db.close()
    return render_template('satellites.html', satellites=satellites_list)

@app.route('/satellites/delete/<int:id>', methods=['POST'])
@login_required
def delete_satellite(id):
    db = get_db()
    sat = db.execute('SELECT name FROM satellites WHERE id = ?', (id,)).fetchone()
    if sat:
        db.execute('DELETE FROM satellites WHERE id = ?', (id,))
        db.commit()
        flash(f'Satellite "{sat["name"]}" deleted successfully.', 'success')
        log_event(f"Deleted satellite '{sat['name']}'", 'info', {'event_type': 'satellite_delete', 'satellite_name': sat['name']})
    db.close()
    return redirect(url_for('satellites'))

@app.route('/missions', methods=['GET', 'POST'])
@login_required
def missions():
    log_event("Accessed missions list", 'info', {'event_type': 'missions_access'})
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            target = request.form.get('target')
            start_date = request.form.get('start_date')
            status = request.form.get('status')
            
            db.execute('INSERT INTO missions (name, target, start_date, status) VALUES (?, ?, ?, ?)',
                       (name, target, start_date, status))
            db.commit()
            flash(f'Mission "{name}" created successfully.', 'success')
            log_event(f"Created mission '{name}'", 'info', {'event_type': 'mission_add', 'mission_name': name})
            
        elif action == 'edit':
            mission_id = request.form.get('id')
            name = request.form.get('name')
            target = request.form.get('target')
            start_date = request.form.get('start_date')
            status = request.form.get('status')
            
            db.execute('UPDATE missions SET name = ?, target = ?, start_date = ?, status = ? WHERE id = ?',
                       (name, target, start_date, status, mission_id))
            db.commit()
            flash(f'Mission "{name}" updated successfully.', 'success')
            log_event(f"Updated mission '{name}'", 'info', {'event_type': 'mission_update', 'mission_name': name})
            
        db.close()
        return redirect(url_for('missions'))
        
    missions_list = db.execute('SELECT * FROM missions ORDER BY id DESC').fetchall()
    db.close()
    return render_template('missions.html', missions=missions_list)

@app.route('/missions/delete/<int:id>', methods=['POST'])
@login_required
def delete_mission(id):
    db = get_db()
    mission = db.execute('SELECT name FROM missions WHERE id = ?', (id,)).fetchone()
    if mission:
        db.execute('DELETE FROM missions WHERE id = ?', (id,))
        db.commit()
        flash(f'Mission "{mission["name"]}" deleted successfully.', 'success')
        log_event(f"Deleted mission '{mission['name']}'", 'info', {'event_type': 'mission_delete', 'mission_name': mission['name']})
    db.close()
    return redirect(url_for('missions'))

@app.route('/telemetry', methods=['GET', 'POST'])
@login_required
def telemetry():
    log_event("Accessed telemetry records", 'info', {'event_type': 'telemetry_access'})
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            satellite_id = request.form.get('satellite_id')
            temperature = request.form.get('temperature')
            battery_level = request.form.get('battery_level')
            signal_strength = request.form.get('signal_strength')
            timestamp = request.form.get('timestamp')
            
            db.execute('INSERT INTO telemetry (satellite_id, temperature, battery_level, signal_strength, timestamp) VALUES (?, ?, ?, ?, ?)',
                       (satellite_id, temperature, battery_level, signal_strength, timestamp))
            db.commit()
            flash('Telemetry record logged successfully.', 'success')
            log_event(f"Logged telemetry record for satellite ID {satellite_id}", 'info', {'event_type': 'telemetry_add', 'satellite_id': satellite_id})
            
        elif action == 'edit':
            telemetry_id = request.form.get('id')
            satellite_id = request.form.get('satellite_id')
            temperature = request.form.get('temperature')
            battery_level = request.form.get('battery_level')
            signal_strength = request.form.get('signal_strength')
            timestamp = request.form.get('timestamp')
            
            db.execute('UPDATE telemetry SET satellite_id = ?, temperature = ?, battery_level = ?, signal_strength = ?, timestamp = ? WHERE id = ?',
                       (satellite_id, temperature, battery_level, signal_strength, timestamp, telemetry_id))
            db.commit()
            flash('Telemetry record updated successfully.', 'success')
            log_event(f"Updated telemetry record for satellite ID {satellite_id}", 'info', {'event_type': 'telemetry_update', 'satellite_id': satellite_id})
            
        db.close()
        return redirect(url_for('telemetry'))
        
    telemetry_list = db.execute('''
        SELECT t.id, t.satellite_id, s.name as satellite_name, t.temperature, t.battery_level, t.signal_strength, t.timestamp
        FROM telemetry t
        JOIN satellites s ON t.satellite_id = s.id
        ORDER BY t.timestamp DESC, t.id DESC
    ''').fetchall()
    
    satellites_list = db.execute('SELECT id, name FROM satellites ORDER BY name').fetchall()
    db.close()
    return render_template('telemetry.html', telemetry=telemetry_list, satellites=satellites_list)

@app.route('/telemetry/delete/<int:id>', methods=['POST'])
@login_required
def delete_telemetry(id):
    db = get_db()
    db.execute('DELETE FROM telemetry WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Telemetry record deleted successfully.', 'success')
    log_event(f"Deleted telemetry record ID {id}", 'info', {'event_type': 'telemetry_delete', 'record_id': id})
    return redirect(url_for('telemetry'))

@app.route('/analytics')
@login_required
def analytics():
    log_event("Accessed analytics dashboard", 'info', {'event_type': 'analytics_access'})
    db = get_db()
    
    total_satellites = db.execute('SELECT COUNT(*) FROM satellites').fetchone()[0]
    active_satellites = db.execute("SELECT COUNT(*) FROM satellites WHERE status = 'Active'").fetchone()[0]
    inactive_satellites = total_satellites - active_satellites
    
    active_missions = db.execute("SELECT COUNT(*) FROM missions WHERE status = 'Active'").fetchone()[0]
    total_telemetry = db.execute('SELECT COUNT(*) FROM telemetry').fetchone()[0]
    
    satellite_chart_data = {
        'labels': ['Active', 'Inactive'],
        'data': [active_satellites, inactive_satellites]
    }
    
    mission_counts = db.execute('SELECT status, COUNT(*) as count FROM missions GROUP BY status').fetchall()
    mission_map = {row['status']: row['count'] for row in mission_counts}
    mission_chart_data = {
        'labels': ['Planning', 'Active', 'Completed', 'Failed'],
        'data': [
            mission_map.get('Planning', 0),
            mission_map.get('Active', 0),
            mission_map.get('Completed', 0),
            mission_map.get('Failed', 0)
        ]
    }
    
    db.close()
    
    return render_template('analytics.html',
                           total_satellites=total_satellites,
                           active_satellites=active_satellites,
                           active_missions=active_missions,
                           total_telemetry=total_telemetry,
                           satellite_chart_data=satellite_chart_data,
                           mission_chart_data=mission_chart_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)
