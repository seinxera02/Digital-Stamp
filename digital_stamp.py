from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, Blueprint
from datetime import datetime
import os, sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller temp folder
else:
    base_path = os.path.abspath(".")

template_folder = os.path.join(base_path, "templates")
static_folder = os.path.join(base_path, "static")  # if you have static files

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = 'seiko_electric_demo_secret_key'

# Create a Blueprint instance
# The blueprint name is 'digital_stamp_bp'
# The __name__ argument helps locate templates and static files relative to this blueprint
digital_stamp_bp = Blueprint('digital_stamp_bp', __name__,
                             template_folder='templates',
                             static_folder='static')

# Company data based on Seiko Electric Co. Ltd.
COMPANY_NAME = "SEIKO ELECTRIC CO. LTD."
COMPANY_WEBSITE = "https://www.seiko-denki.co.jp/en/"
COMPANY_DESCRIPTION = "Ecologically friendly and safety contributing to infrastructure building"

# Departments based on Seiko Electric's business areas
DEPARTMENTS = [
    "Power Systems", 
    "Control Technology", 
    "Green Engineering", 
    "Renewable Energy", 
    "System Components",
    "Engineering Service"
]

# Enhanced user data with more realistic structure
USERS = {
    'tanaka': {'department': 'Power Systems', 'full_name': 'Hiroshi Tanaka', 'position': 'Senior Engineer'},
    'suzuki': {'department': 'Control Technology', 'full_name': 'Akiko Suzuki', 'position': 'Project Manager'},
    'yamamoto': {'department': 'Green Engineering', 'full_name': 'Kenji Yamamoto', 'position': 'Chief Engineer'},
    'sato': {'department': 'Renewable Energy', 'full_name': 'Yuki Sato', 'position': 'Technical Lead'},
    'watanabe': {'department': 'System Components', 'full_name': 'Michiko Watanabe', 'position': 'Quality Manager'},
    'admin': {'department': 'Engineering Service', 'full_name': 'System Administrator', 'position': 'Admin'}
}

@digital_stamp_bp.route('/')
def index():
    return render_template('login.html', company=COMPANY_NAME)

@digital_stamp_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip().lower()
    
    if username in USERS:
        session['username'] = username
        session['user_data'] = USERS[username]
        session['is_admin'] = (username == 'admin')
        return redirect(url_for('digital_stamp_bp.stamp'))
    else:
        flash('User not found. Please contact administrator or use valid credentials.', 'error')
        return render_template('login.html', company=COMPANY_NAME, available_users=USERS)

@digital_stamp_bp.route('/stamp')
def stamp():
    if 'username' not in session:
        return redirect(url_for('digital_stamp_bp.index'))

    user_data = session.get('user_data', {})
    return render_template('stamp.html', 
                         company=COMPANY_NAME,
                         department=user_data.get('department', ''),
                         username=session['username'],
                         full_name=user_data.get('full_name', ''),
                         position=user_data.get('position', ''),
                         current_date=datetime.now().strftime('%Y-%m-%d'),
                         website=COMPANY_WEBSITE)

@digital_stamp_bp.route('/admin')
def admin():
    if not session.get('is_admin', False):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('digital_stamp_bp.index'))

    return render_template('admin.html', 
                         company=COMPANY_NAME,
                         users=USERS,
                         departments=DEPARTMENTS)

@digital_stamp_bp.route('/admin/add_user', methods=['POST'])
def add_user():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Access denied'}), 403
    
    username = request.form.get('username', '').strip().lower()
    full_name = request.form.get('full_name', '').strip()
    department = request.form.get('department', '').strip()
    position = request.form.get('position', '').strip()
    
    if username in USERS:
        flash('Username already exists!', 'error')
    elif username and full_name and department:
        USERS[username] = {
            'full_name': full_name,
            'department': department,
            'position': position
        }
        flash(f'User {username} added successfully!', 'success')
    else:
        flash('All fields are required!', 'error')

    return redirect(url_for('digital_stamp_bp.admin'))

@digital_stamp_bp.route('/admin/edit_user', methods=['POST'])
def edit_user():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Access denied'}), 403
    
    username = request.form.get('username')
    full_name = request.form.get('full_name', '').strip()
    department = request.form.get('department', '').strip()
    position = request.form.get('position', '').strip()
    
    if username in USERS and full_name and department:
        USERS[username].update({
            'full_name': full_name,
            'department': department,
            'position': position
        })
        flash(f'User {username} updated successfully!', 'success')
    else:
        flash('User not found or invalid data!', 'error')

    return redirect(url_for('digital_stamp_bp.admin'))

@digital_stamp_bp.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Access denied'}), 403
    
    username = request.form.get('username')
    
    if username == 'admin':
        flash('Cannot delete admin user!', 'error')
    elif username in USERS:
        del USERS[username]
        flash(f'User {username} deleted successfully!', 'success')
    else:
        flash('User not found!', 'error')

    return redirect(url_for('digital_stamp_bp.admin'))

@digital_stamp_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('digital_stamp_bp.index'))


if __name__ == '__main__':
    app.run(debug=True)