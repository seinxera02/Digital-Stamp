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

# Templates as strings
templates = {
    'base.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Digital Stamp System - {{ company }}{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .glass-effect { backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); }
        .stamp-shadow { filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3)); }
    </style>
</head>
<body class="gradient-bg min-h-screen">
    <nav class="glass-effect border-b border-white/20 p-4">
        <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <i class="fas fa-stamp text-white text-2xl"></i>
                <h1 class="text-xl font-bold text-white">{{ company }}</h1>
            </div>
            <div class="flex items-center space-x-4 text-white">
                {% if session.username %}
                    <span class="flex items-center space-x-2">
                        <i class="fas fa-user"></i>
                        <span>{{ session.username }}</span>
                    </span>
                    {% if session.is_admin %}
                        <a href="/admin" class="flex items-center space-x-1 hover:text-yellow-300 transition-colors">
                            <i class="fas fa-cog"></i>
                            <span>Admin</span>
                        </a>
                    {% endif %}
                    <a href="/logout" class="flex items-center space-x-1 hover:text-red-300 transition-colors">
                        <i class="fas fa-sign-out-alt"></i>
                        <span>Logout</span>
                    </a>
                {% else %}
                    <a href="/" class="flex items-center space-x-1 hover:text-blue-300 transition-colors">
                        <i class="fas fa-sign-in-alt"></i>
                        <span>Login</span>
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <main class="container mx-auto p-6">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="mb-6 space-y-2">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} glass-effect text-white p-4 rounded-lg border border-white/20">
                            <i class="fas fa-{{ 'exclamation-triangle' if category == 'error' else 'check-circle' }} mr-2"></i>
                            {{ message }}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
</body>
</html>
    ''',
    
    'login.html': '''
{% extends "base.html" %}

{% block content %}
<div class="max-w-md mx-auto">
    <div class="glass-effect rounded-lg shadow-2xl p-8 border border-white/20">
        <div class="text-center mb-8">
            <i class="fas fa-stamp text-6xl text-white mb-4"></i>
            <h2 class="text-3xl font-bold text-white mb-2">Digital Stamp System</h2>
            <p class="text-white/80">{{ company }}</p>
        </div>
        
        <form method="POST" action="/login" class="space-y-6">
            <div>
                <label for="username" class="block text-sm font-medium text-white mb-2">
                    <i class="fas fa-user mr-2"></i>Username
                </label>
                <input type="text" id="username" name="username" required 
                       class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white placeholder-white/60"
                       placeholder="Enter your username">
            </div>
            
            <button type="submit" class="w-full bg-white/20 hover:bg-white/30 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-300 border border-white/20">
                <i class="fas fa-sign-in-alt mr-2"></i>Login
            </button>
        </form>
        
        {% if available_users %}
        <div class="mt-8 p-4 bg-white/10 rounded-lg border border-white/20">
            <p class="text-white font-semibold mb-3">
                <i class="fas fa-info-circle mr-2"></i>Available Users:
            </p>
            <div class="grid grid-cols-1 gap-2 text-sm">
                {% for username, data in available_users.items() %}
                <div class="flex justify-between items-center text-white/90 bg-white/10 rounded px-3 py-2">
                    <span class="font-mono">{{ username }}</span>
                    <span class="text-xs">{{ data.department }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
    ''',
    
    'stamp.html': '''
{% extends "base.html" %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Stamp Display -->
        <div class="glass-effect rounded-lg shadow-2xl p-8 border border-white/20">
            <h2 class="text-2xl font-bold text-white mb-6 text-center">
                <i class="fas fa-stamp mr-2"></i>Digital Corporate Stamp
            </h2>
            
            <div class="flex justify-center mb-6">
                <div id="stamp-container" class="relative">
                    <svg id="corporate-stamp" width="280" height="280" viewBox="0 0 280 280" class="stamp-shadow">
                        <!-- Transparent background -->
                        <defs>
                            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                                <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
                            </filter>
                        </defs>
                        
                        <!-- Outer decorative border -->
                        <circle cx="140" cy="140" r="135" fill="none" stroke="#1e40af" stroke-width="3" opacity="0.8"/>
                        <circle cx="140" cy="140" r="130" fill="none" stroke="#1e40af" stroke-width="1" opacity="0.6"/>
                        
                        <!-- Chain pattern border -->
                        <circle cx="140" cy="140" r="125" fill="none" stroke="#374151" stroke-width="2" stroke-dasharray="6 3" opacity="0.7"/>
                        
                        <!-- Inner circles -->
                        <circle cx="140" cy="140" r="120" fill="none" stroke="#1e40af" stroke-width="2" opacity="0.8"/>
                        <circle cx="140" cy="140" r="100" fill="none" stroke="#6b7280" stroke-width="1" stroke-dasharray="2 3" opacity="0.5"/>
                        
                        <!-- Top curved text path -->
                        <path id="top-curve" d="M 30 140 A 110 110 0 0 1 250 140" fill="none"/>
                        
                        <!-- Bottom curved text path -->
                        <path id="bottom-curve" d="M 250 140 A 110 110 0 0 1 30 140" fill="none"/>
                        
                        <!-- Top curved company name -->
                        <text font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e40af" opacity="0.9">
                            <textPath href="#top-curve" startOffset="50%" text-anchor="middle">
                                <tspan id="stamp-company-top">SEIKO ELECTRIC CO. LTD.</tspan>
                            </textPath>
                        </text>
                        
                        <!-- Bottom curved department -->
                        <text font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#374151" opacity="0.8">
                            <textPath href="#bottom-curve" startOffset="50%" text-anchor="middle">
                                <tspan id="stamp-department-bottom">{{ department.upper() }} DIVISION</tspan>
                            </textPath>
                        </text>
                        
                        <!-- Center content -->
                        <text x="140" y="125" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#1e40af" opacity="0.8">
                            <tspan>CORPORATE SEAL</tspan>
                        </text>
                        
                        <!-- Decorative line -->
                        <line x1="110" y1="135" x2="170" y2="135" stroke="#6b7280" stroke-width="1" opacity="0.6"/>
                        
                        <!-- Position -->
                        <text x="140" y="150" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" font-weight="semibold" fill="#374151" opacity="0.7">
                            <tspan id="stamp-position">{{ position.upper() }}</tspan>
                        </text>
                        
                        <!-- User name -->
                        <text x="140" y="165" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#1e40af" opacity="0.9">
                            <tspan id="stamp-username">{{ full_name.upper() }}</tspan>
                        </text>
                        
                        <!-- Date -->
                        <text x="140" y="185" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#6b7280" opacity="0.8">
                            <tspan id="stamp-date">{{ current_date }}</tspan>
                        </text>
                        
                        <!-- Decorative elements -->
                        <text x="70" y="190" text-anchor="middle" font-size="16" fill="#1e40af" opacity="0.7">★</text>
                        <text x="210" y="190" text-anchor="middle" font-size="16" fill="#1e40af" opacity="0.7">★</text>
                        
                        <!-- Website reference (small) -->
                        <text x="140" y="200" text-anchor="middle" font-family="Arial, sans-serif" font-size="7" fill="#6b7280" opacity="0.5">
                            <tspan>www.seiko-denki.co.jp</tspan>
                        </text>
                    </svg>
                </div>
            </div>
            
            <div class="flex justify-center space-x-4">
                <button onclick="copyStampImage()" 
                        class="flex items-center space-x-2 bg-green-500/80 hover:bg-green-600/80 text-white py-2 px-4 rounded-lg transition-all duration-300">
                    <i class="fas fa-copy"></i>
                    <span>Copy Stamp</span>
                </button>
                
                <button onclick="downloadStamp()" 
                        class="flex items-center space-x-2 bg-purple-500/80 hover:bg-purple-600/80 text-white py-2 px-4 rounded-lg transition-all duration-300">
                    <i class="fas fa-download"></i>
                    <span>Download PNG</span>
                </button>
            </div>
        </div>
        
        <!-- Controls -->
        <div class="glass-effect rounded-lg shadow-2xl p-8 border border-white/20">
            <h3 class="text-xl font-bold text-white mb-6">
                <i class="fas fa-edit mr-2"></i>Stamp Configuration
            </h3>
            
            <div class="space-y-6">
                <div class="bg-white/10 rounded-lg p-4 border border-white/20">
                    <h4 class="text-white font-semibold mb-3">Company Information</h4>
                    <div class="space-y-2 text-white/80 text-sm">
                        <p><strong>Company:</strong> {{ company }}</p>
                        <p><strong>Department:</strong> {{ department }}</p>
                        <p><strong>Website:</strong> <a href="{{ website }}" target="_blank" class="text-blue-300 hover:underline">{{ website }}</a></p>
                    </div>
                </div>
                
                <div>
                    <label for="edit-full-name" class="block text-sm font-medium text-white mb-2">
                        <i class="fas fa-user mr-2"></i>Full Name
                    </label>
                    <input type="text" id="edit-full-name" value="{{ full_name }}" 
                           class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white placeholder-white/60"
                           onkeyup="updateStamp()">
                </div>
                
                <div>
                    <label for="edit-position" class="block text-sm font-medium text-white mb-2">
                        <i class="fas fa-id-badge mr-2"></i>Position
                    </label>
                    <input type="text" id="edit-position" value="{{ position }}" 
                           class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white placeholder-white/60"
                           onkeyup="updateStamp()">
                </div>
                
                <div>
                    <label for="edit-date" class="block text-sm font-medium text-white mb-2">
                        <i class="fas fa-calendar mr-2"></i>Date
                    </label>
                    <input type="date" id="edit-date" value="{{ current_date }}" 
                           class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white"
                           onchange="updateStamp()">
                </div>
            </div>
            
            <div id="copy-message" class="hidden mt-4 p-3 bg-green-500/20 border border-green-500/30 rounded-lg text-green-300 text-center">
                <i class="fas fa-check-circle mr-2"></i>
                <span id="message-text">Stamp copied successfully!</span>
            </div>
        </div>
    </div>
</div>

<script>
function updateStamp() {
    const fullName = document.getElementById('edit-full-name').value;
    const position = document.getElementById('edit-position').value;
    const date = document.getElementById('edit-date').value;
    
    document.getElementById('stamp-username').textContent = fullName.toUpperCase();
    document.getElementById('stamp-position').textContent = position.toUpperCase();
    document.getElementById('stamp-date').textContent = date;
}

async function copyStampImage() {
    try {
        const svg = document.getElementById('corporate-stamp');
        const svgData = new XMLSerializer().serializeToString(svg);
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        canvas.width = 280;
        canvas.height = 280;
        
        img.onload = async function() {
            // Keep transparent background
            ctx.drawImage(img, 0, 0);
            
            try {
                canvas.toBlob(async function(blob) {
                    try {
                        await navigator.clipboard.write([
                            new ClipboardItem({
                                'image/png': blob
                            })
                        ]);
                        showMessage('Transparent stamp image copied to clipboard!');
                    } catch (err) {
                        showMessage('Stamp copied (transparency may vary by application)');
                    }
                });
            } catch (err) {
                showMessage('Image copy not supported in this browser');
            }
        };
        
        const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
        const url = URL.createObjectURL(svgBlob);
        img.src = url;
        
    } catch (err) {
        showMessage('Failed to copy. Please try download instead.', 'error');
    }
}

function downloadStamp() {
    const svg = document.getElementById('corporate-stamp');
    const svgData = new XMLSerializer().serializeToString(svg);
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    canvas.width = 280;
    canvas.height = 280;
    
    img.onload = function() {
        ctx.drawImage(img, 0, 0);
        
        const link = document.createElement('a');
        const timestamp = new Date().toISOString().slice(0, 10);
        link.download = `seiko-electric-stamp-${timestamp}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
        
        showMessage('Stamp downloaded successfully!');
    };
    
    const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
    const url = URL.createObjectURL(svgBlob);
    img.src = url;
}

function showMessage(text, type = 'success') {
    const message = document.getElementById('copy-message');
    const messageText = document.getElementById('message-text');
    
    messageText.textContent = text;
    message.className = `mt-4 p-3 border rounded-lg text-center ${
        type === 'error' ? 'bg-red-500/20 border-red-500/30 text-red-300' : 'bg-green-500/20 border-green-500/30 text-green-300'
    }`;
    message.classList.remove('hidden');
    
    setTimeout(() => {
        message.classList.add('hidden');
    }, 4000);
}
</script>
{% endblock %}
    ''',
    
    'admin.html': '''
{% extends "base.html" %}

{% block title %}Admin Panel - {{ company }}{% endblock %}

{% block content %}
<div class="max-w-6xl mx-auto space-y-8">
    <!-- Header -->
    <div class="glass-effect rounded-lg shadow-2xl p-6 border border-white/20">
        <div class="flex items-center justify-between">
            <h2 class="text-3xl font-bold text-white">
                <i class="fas fa-cog mr-3"></i>Administration Panel
            </h2>
            <div class="text-white/80">
                <p class="text-sm">Total Users: {{ users|length }}</p>
                <p class="text-xs">{{ company }}</p>
            </div>
        </div>
    </div>
    
    <!-- Add User Form -->
    <div class="glass-effect rounded-lg shadow-2xl p-6 border border-white/20">
        <h3 class="text-xl font-bold text-white mb-4">
            <i class="fas fa-user-plus mr-2"></i>Add New User
        </h3>
        
        <form method="POST" action="/admin/add_user" class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
                <label class="block text-sm font-medium text-white mb-2">Username</label>
                <input type="text" name="username" required 
                       class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white placeholder-white/60"
                       placeholder="e.g., yoshida">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-white mb-2">Full Name</label>
                <input type="text" name="full_name" required 
                       class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white placeholder-white/60"
                       placeholder="e.g., Takeshi Yoshida">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-white mb-2">Department</label>
                <select name="department" required 
                        class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white">
                    <option value="">Select Department</option>
                    {% for dept in departments %}
                        <option value="{{ dept }}" class="text-gray-800">{{ dept }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-white mb-2">Position</label>
                <input type="text" name="position" required 
                       class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white placeholder-white/60"
                       placeholder="e.g., Senior Engineer">
            </div>
            
            <div class="md:col-span-4">
                <button type="submit" class="bg-green-500/80 hover:bg-green-600/80 text-white px-6 py-2 rounded-lg transition-all duration-300">
                    <i class="fas fa-plus mr-2"></i>Add User
                </button>
            </div>
        </form>
    </div>
    
    <!-- Users List -->
    <div class="glass-effect rounded-lg shadow-2xl p-6 border border-white/20">
        <h3 class="text-xl font-bold text-white mb-4">
            <i class="fas fa-users mr-2"></i>User Management
        </h3>
        
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="border-b border-white/20">
                        <th class="text-left text-white font-semibold py-3 px-4">Username</th>
                        <th class="text-left text-white font-semibold py-3 px-4">Full Name</th>
                        <th class="text-left text-white font-semibold py-3 px-4">Department</th>
                        <th class="text-left text-white font-semibold py-3 px-4">Position</th>
                        <th class="text-left text-white font-semibold py-3 px-4">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for username, data in users.items() %}
                    <tr class="border-b border-white/10 hover:bg-white/5 transition-colors" id="user-{{ username }}">
                        <td class="py-3 px-4 text-white/80" id="pos-{{ username }}">{{ data.position }}</td>
                        <td class="py-3 px-4 space-x-2">
                            <button onclick="editUser('{{ username }}')" 
                                    class="bg-blue-500/80 hover:bg-blue-600/80 text-white px-3 py-1 rounded text-sm transition-colors">
                                <i class="fas fa-edit"></i>
                            </button>
                            {% if username != 'admin' %}
                            <button onclick="deleteUser('{{ username }}')" 
                                    class="bg-red-500/80 hover:bg-red-600/80 text-white px-3 py-1 rounded text-sm transition-colors">
                                <i class="fas fa-trash"></i>
                            </button>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Edit User Modal -->
<div id="editModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm hidden items-center justify-center z-50">
    <div class="glass-effect rounded-lg shadow-2xl p-6 border border-white/20 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-white mb-4">
            <i class="fas fa-edit mr-2"></i>Edit User
        </h3>
        
        <form id="editForm" method="POST" action="/admin/edit_user" class="space-y-4">
            <input type="hidden" id="edit-username" name="username">
            
            <div>
                <label class="block text-sm font-medium text-white mb-2">Full Name</label>
                <input type="text" id="edit-full-name" name="full_name" required 
                       class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-white mb-2">Department</label>
                <select id="edit-department" name="department" required 
                        class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white">
                    {% for dept in departments %}
                        <option value="{{ dept }}" class="text-gray-800">{{ dept }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-white mb-2">Position</label>
                <input type="text" id="edit-position" name="position" required 
                       class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/50 text-white">
            </div>
            
            <div class="flex space-x-4">
                <button type="submit" class="flex-1 bg-green-500/80 hover:bg-green-600/80 text-white py-2 rounded-lg transition-colors">
                    <i class="fas fa-save mr-2"></i>Save Changes
                </button>
                <button type="button" onclick="closeEditModal()" class="flex-1 bg-gray-500/80 hover:bg-gray-600/80 text-white py-2 rounded-lg transition-colors">
                    <i class="fas fa-times mr-2"></i>Cancel
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Delete Confirmation Modal -->
<div id="deleteModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm hidden items-center justify-center z-50">
    <div class="glass-effect rounded-lg shadow-2xl p-6 border border-white/20 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-white mb-4">
            <i class="fas fa-exclamation-triangle mr-2 text-red-400"></i>Confirm Delete
        </h3>
        
        <p class="text-white/90 mb-6">Are you sure you want to delete user <span id="delete-username-display" class="font-mono text-yellow-300"></span>?</p>
        
        <form id="deleteForm" method="POST" action="/admin/delete_user">
            <input type="hidden" id="delete-username" name="username">
            
            <div class="flex space-x-4">
                <button type="submit" class="flex-1 bg-red-500/80 hover:bg-red-600/80 text-white py-2 rounded-lg transition-colors">
                    <i class="fas fa-trash mr-2"></i>Delete User
                </button>
                <button type="button" onclick="closeDeleteModal()" class="flex-1 bg-gray-500/80 hover:bg-gray-600/80 text-white py-2 rounded-lg transition-colors">
                    <i class="fas fa-times mr-2"></i>Cancel
                </button>
            </div>
        </form>
    </div>
</div>

<script>
const users = {{ users|tojson }};

function editUser(username) {
    const user = users[username];
    
    document.getElementById('edit-username').value = username;
    document.getElementById('edit-full-name').value = user.full_name;
    document.getElementById('edit-department').value = user.department;
    document.getElementById('edit-position').value = user.position;
    
    document.getElementById('editModal').classList.remove('hidden');
    document.getElementById('editModal').classList.add('flex');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
    document.getElementById('editModal').classList.remove('flex');
}

function deleteUser(username) {
    document.getElementById('delete-username').value = username;
    document.getElementById('delete-username-display').textContent = username;
    
    document.getElementById('deleteModal').classList.remove('hidden');
    document.getElementById('deleteModal').classList.add('flex');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    document.getElementById('deleteModal').classList.remove('flex');
}

// Close modals when clicking outside
document.getElementById('editModal').addEventListener('click', function(e) {
    if (e.target === this) closeEditModal();
});

document.getElementById('deleteModal').addEventListener('click', function(e) {
    if (e.target === this) closeDeleteModal();
});
</script>
{% endblock %}
    '''
}

# In digital_stamp.py

# ... other code ...

# Create templates directory and write template files
def setup_templates(base_path):  # Add `base_path` as an argument
    template_dir = os.path.join(base_path, 'templates')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    for filename, content in templates.items():
        with open(os.path.join(template_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    setup_templates()
    app.run(debug=True)