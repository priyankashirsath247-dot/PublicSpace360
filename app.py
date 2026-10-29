import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
import db

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config.get('UPLOAD_SPACES_FOLDER', os.path.join(Config.BASE_DIR, 'uploads', 'spaces')), exist_ok=True)

# Initialize database on startup
with app.app_context():
    db.init_db()

# -----------------------------------------------------------------------------
# Authentication & Authorization Helpers
# -----------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'admin_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin authentication required.', 'danger')
            return redirect(url_for('admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Context processor for templates
@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'user_name': session.get('user_name'),
        'user_role': session.get('role'),
        'is_admin': 'admin_id' in session,
        'is_logged_in': 'user_id' in session or 'admin_id' in session,
        'google_maps_api_key': app.config.get('GOOGLE_MAPS_API_KEY', '')
    }

# Serve uploaded report photos
@app.route('/uploads/reports/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Serve uploaded public space photos
@app.route('/uploads/spaces/<filename>')
def uploaded_space_file(filename):
    return send_from_directory(app.config.get('UPLOAD_SPACES_FOLDER', os.path.join(Config.BASE_DIR, 'uploads', 'spaces')), filename)

# -----------------------------------------------------------------------------
# Frontend Page Routes
# -----------------------------------------------------------------------------

@app.route('/')
def home():
    featured_spaces = db.query_db("SELECT * FROM public_spaces ORDER BY average_visitors DESC LIMIT 6")
    return render_template('index.html', featured_spaces=featured_spaces)

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    return render_template('login.html')

@app.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def user_dashboard():
    user_id = session.get('user_id')
    user = db.query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    surveys_completed = db.query_db("""
        SELECT s.*, p.name as space_name, p.type as space_type 
        FROM surveys s 
        JOIN public_spaces p ON s.space_id = p.id 
        WHERE s.user_id = %s 
        ORDER BY s.created_at DESC
    """, (user_id,))
    reports_submitted = db.query_db("""
        SELECT r.*, p.name as space_name 
        FROM reports r 
        JOIN public_spaces p ON r.space_id = p.id 
        WHERE r.user_id = %s 
        ORDER BY r.created_at DESC
    """, (user_id,))
    return render_template('dashboard.html', 
                           user=user, 
                           surveys=surveys_completed, 
                           reports=reports_submitted)

@app.route('/map')
@app.route('/explore-map')
def map_page():
    areas = db.query_db("SELECT * FROM areas ORDER BY name ASC")
    return render_template('map.html', areas=areas, google_maps_api_key=app.config.get('GOOGLE_MAPS_API_KEY', ''))

@app.route('/spaces')
def spaces_page():
    space_type = request.args.get('type', '')
    query = request.args.get('q', '')
    area = request.args.get('area', '')
    areas = db.query_db("SELECT * FROM areas ORDER BY name ASC")
    return render_template('spaces.html', active_type=space_type, search_query=query, active_area=area, areas=areas)

app.add_url_rule('/spaces', endpoint='public_spaces_page', view_func=spaces_page)

@app.route('/public-space/<int:space_id>')
@app.route('/spaces/<int:space_id>')
def space_details_page(space_id):
    space = db.query_db("SELECT * FROM public_spaces WHERE id = %s", (space_id,), one=True)
    if not space:
        flash("Public space not found.", "warning")
        return redirect(url_for('spaces_page'))
    
    # Fetch multi-image gallery from public_space_images (Requirement 4 & 16)
    gallery_images = db.query_db("""
        SELECT * FROM public_space_images 
        WHERE public_space_id = %s 
        ORDER BY is_primary DESC, id ASC
    """, (space_id,))

    # If no separate gallery records yet, fallback to primary image
    if not gallery_images and space.get('primary_image'):
        gallery_images = [{
            'id': 0,
            'public_space_id': space['id'],
            'image_path': space['primary_image'],
            'image_source': space.get('image_source', 'Field Survey'),
            'image_credit': space.get('image_credit', 'Academic Survey Team'),
            'is_primary': 1
        }]

    # Calculate survey statistics (Requirement 11)
    avg_ratings = db.query_db("""
        SELECT 
            ROUND(AVG(safety_rating), 1) as avg_safety,
            ROUND(AVG(cleanliness_rating), 1) as avg_cleanliness,
            ROUND(AVG(lighting_rating), 1) as avg_lighting,
            ROUND(AVG(seating_rating), 1) as avg_seating,
            ROUND(AVG(water_rating), 1) as avg_water,
            ROUND(AVG(accessibility_rating), 1) as avg_accessibility,
            COUNT(*) as survey_count
        FROM surveys 
        WHERE space_id = %s
    """, (space_id,), one=True)

    survey_count = avg_ratings.get('survey_count', 0) if avg_ratings else 0
    clean_score = float(avg_ratings.get('avg_cleanliness') or 4.0) if avg_ratings else 4.0
    safe_score = float(avg_ratings.get('avg_safety') or 4.2) if avg_ratings else 4.2
    maint_score = round((float(avg_ratings.get('avg_lighting') or 4.0) + float(avg_ratings.get('avg_seating') or 4.0) + float(avg_ratings.get('avg_water') or 3.8)) / 3.0, 1) if avg_ratings else 3.9
    fac_score = round((float(avg_ratings.get('avg_seating') or 4.0) + float(avg_ratings.get('avg_accessibility') or 4.2)) / 2.0, 1) if avg_ratings else 4.1

    overall_avg = 4.2
    if avg_ratings and survey_count > 0:
        sub_ratings = [
            float(avg_ratings.get('avg_safety') or 4),
            float(avg_ratings.get('avg_cleanliness') or 4),
            float(avg_ratings.get('avg_lighting') or 4),
            float(avg_ratings.get('avg_seating') or 4),
            float(avg_ratings.get('avg_water') or 4),
            float(avg_ratings.get('avg_accessibility') or 4)
        ]
        overall_avg = round(sum(sub_ratings) / len(sub_ratings), 1)

    # Top improvement requested (Requirement 11)
    top_improvement = db.query_db("""
        SELECT improvement, COUNT(*) as cnt 
        FROM surveys 
        WHERE space_id = %s AND improvement IS NOT NULL AND improvement != '' 
        GROUP BY improvement 
        ORDER BY cnt DESC LIMIT 1
    """, (space_id,), one=True)
    most_requested_improvement = top_improvement['improvement'] if top_improvement else "Better children's play equipment"

    # User reviews & comments (Requirement 10)
    feedback_list = db.query_db("""
        SELECT f.*, COALESCE(f.user_name, u.name, 'Community Visitor') as display_name 
        FROM feedback f 
        LEFT JOIN users u ON f.user_id = u.id 
        WHERE f.space_id = %s AND (f.status = 'Approved' OR f.status IS NULL)
        ORDER BY f.created_at DESC LIMIT 15
    """, (space_id,))

    recent_reports = db.query_db("""
        SELECT issue_type, priority, status, created_at 
        FROM reports 
        WHERE space_id = %s 
        ORDER BY created_at DESC LIMIT 5
    """, (space_id,))

    return render_template('space-details.html', 
                           space=space, 
                           gallery_images=gallery_images,
                           avg_ratings=avg_ratings, 
                           survey_count=survey_count,
                           clean_score=clean_score,
                           safe_score=safe_score,
                           maint_score=maint_score,
                           fac_score=fac_score,
                           overall_avg=overall_avg,
                           most_requested_improvement=most_requested_improvement,
                           feedback=feedback_list,
                           reports=recent_reports)

@app.route('/survey')
def survey_page():
    preselect_space_id = request.args.get('space_id', type=int)
    spaces = db.query_db("SELECT id, name, area, type FROM public_spaces ORDER BY name ASC, area ASC")
    return render_template('survey.html', spaces=spaces, preselect_id=preselect_space_id)

@app.route('/results')
def results_page():
    return render_template('results.html')

@app.route('/report')
def report_page():
    preselect_space_id = request.args.get('space_id', type=int)
    spaces = db.query_db("SELECT id, name, area, type FROM public_spaces ORDER BY name ASC, area ASC")
    recent_issues = db.query_db("""
        SELECT r.*, p.name as space_name, p.area 
        FROM reports r 
        JOIN public_spaces p ON r.space_id = p.id 
        ORDER BY r.created_at DESC LIMIT 8
    """)
    return render_template('report.html', spaces=spaces, preselect_id=preselect_space_id, recent_issues=recent_issues)

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/admin/login')
def admin_login_page():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin-login.html')

@app.route('/admin')
@app.route('/admin/dashboard')
@app.route('/admin/spaces')
@app.route('/admin/surveys')
@app.route('/admin/reports')
@app.route('/admin/users')
@app.route('/admin/analytics')
@app.route('/admin/images')
@app.route('/admin/feedback')
@admin_required
def admin_dashboard():
    path = request.path
    active_tab = 'overview'
    if '/admin/spaces' in path:
        active_tab = 'spaces'
    elif '/admin/surveys' in path:
        active_tab = 'surveys'
    elif '/admin/reports' in path:
        active_tab = 'reports'
    elif '/admin/users' in path:
        active_tab = 'users'
    elif '/admin/analytics' in path:
        active_tab = 'analytics'
    elif '/admin/images' in path:
        active_tab = 'images'
    elif '/admin/feedback' in path:
        active_tab = 'feedback'

    spaces = db.query_db("SELECT * FROM public_spaces ORDER BY id DESC")
    areas = db.query_db("SELECT * FROM areas ORDER BY name ASC")
    surveys = db.query_db("""
        SELECT s.*, p.name as space_name, COALESCE(u.name, 'Community Respondent') as user_name, COALESCE(u.email, 'Anonymous') as user_email
        FROM surveys s
        JOIN public_spaces p ON s.space_id = p.id
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC
    """)
    reports = db.query_db("""
        SELECT r.*, p.name as space_name, COALESCE(u.name, 'Anonymous Citizen') as user_name 
        FROM reports r
        JOIN public_spaces p ON r.space_id = p.id
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY r.created_at DESC
    """)
    users = db.query_db("SELECT id, name, email, mobile, age_group, gender, role, created_at FROM users ORDER BY created_at DESC")
    feedback_items = db.query_db("""
        SELECT f.*, p.name as space_name, p.area 
        FROM feedback f 
        JOIN public_spaces p ON f.space_id = p.id 
        ORDER BY f.created_at DESC
    """)
    images_list = db.query_db("""
        SELECT psi.*, p.name as space_name, p.area 
        FROM public_space_images psi 
        JOIN public_spaces p ON psi.public_space_id = p.id 
        ORDER BY psi.uploaded_at DESC
    """)

    return render_template('admin-dashboard.html', 
                           spaces=spaces, 
                           areas=areas,
                           surveys=surveys, 
                           reports=reports, 
                           users=users,
                           feedbacks=feedback_items,
                           images=images_list,
                           active_tab=active_tab)

@app.route('/spaces/add', methods=['POST'])
@admin_required
def add_public_space():
    name = request.form.get('name')
    space_type = request.form.get('type')
    area = request.form.get('area') or 'New Panvel'
    address = request.form.get('address')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    description = request.form.get('description', '')
    facilities = request.form.get('facilities', '')
    opening_time = request.form.get('opening_time', '05:30 AM')
    closing_time = request.form.get('closing_time', '09:30 PM')
    average_visitors = request.form.get('average_visitors', 500)
    condition = request.form.get('condition', 'Good')
    image_source = request.form.get('image_source', 'Field Survey')
    image_credit = request.form.get('image_credit', 'Academic Survey Team')
    image = request.form.get('image') or 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800'
    google_maps_url = request.form.get('google_maps_url') or f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

    if name and space_type and address and latitude and longitude:
        space_id = db.execute_db("""
            INSERT INTO public_spaces 
            (name, type, area, address, latitude, longitude, description, facilities, opening_time, closing_time, average_visitors, condition, primary_image, image_source, image_credit, google_maps_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, space_type, area, address, float(latitude), float(longitude), description, facilities, opening_time, closing_time, int(average_visitors), condition, image, image_source, image_credit, google_maps_url))
        
        # Also record in public_space_images
        db.execute_db("""
            INSERT INTO public_space_images (public_space_id, image_path, image_source, image_credit, is_primary)
            VALUES (%s, %s, %s, %s, 1)
        """, (space_id, image, image_source, image_credit))

        flash('Public space added successfully!', 'success')
    else:
        flash('Please fill in all required fields.', 'danger')
    return redirect(url_for('spaces_page'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    mobile = data.get('mobile', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    age_group = data.get('age_group', '').strip()
    gender = data.get('gender', '').strip()

    # Validation
    if not all([name, email, mobile, password, age_group, gender]):
        return jsonify({'success': False, 'error': 'All fields are required.'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'error': 'Please provide a valid email address.'}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters.'}), 400

    # Duplicate check
    existing = db.query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
    if existing:
        return jsonify({'success': False, 'error': 'An account with this email already exists.'}), 409

    # Hash password securely
    hashed_pwd = generate_password_hash(password)

    user_id = db.execute_db("""
        INSERT INTO users (name, email, mobile, password, age_group, gender, role)
        VALUES (%s, %s, %s, %s, %s, %s, 'user')
    """, (name, email, mobile, hashed_pwd, age_group, gender))

    # Set session
    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    session['role'] = 'user'

    return jsonify({
        'success': True,
        'message': 'Registration Successful! Welcome to PublicSpace360.',
        'redirect': '/dashboard'
    }), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Please enter both email and password.'}), 400

    user = db.query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['role'] = user.get('role', 'user')

    return jsonify({
        'success': True,
        'message': f"Welcome back, {user['name']}!",
        'redirect': '/dashboard'
    })

@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Admin email and password are required.'}), 400

    admin = db.query_db("SELECT * FROM admins WHERE email = %s", (email,), one=True)
    if not admin or not check_password_hash(admin['password'], password):
        return jsonify({'success': False, 'error': 'Invalid administrator credentials.'}), 401

    session['admin_id'] = admin['id']
    session['admin_name'] = admin['name']
    session['admin_email'] = admin['email']
    session['role'] = 'admin'

    return jsonify({
        'success': True,
        'message': 'Admin authenticated successfully.',
        'redirect': '/admin/dashboard'
    })

@app.route('/api/statistics', methods=['GET'])
@app.route('/api/stats', methods=['GET'])
def api_stats():
    total_spaces = db.query_db("SELECT COUNT(*) as count FROM public_spaces", one=True)['count']
    total_surveys = db.query_db("SELECT COUNT(*) as count FROM surveys", one=True)['count']
    parks_count = db.query_db("SELECT COUNT(*) as count FROM public_spaces WHERE type = 'Parks'", one=True)['count']
    playgrounds_count = db.query_db("SELECT COUNT(*) as count FROM public_spaces WHERE type = 'Playgrounds'", one=True)['count']
    promenades_count = db.query_db("SELECT COUNT(*) as count FROM public_spaces WHERE type = 'Promenades'", one=True)['count']
    gardens_count = db.query_db("SELECT COUNT(*) as count FROM public_spaces WHERE type = 'Gardens'", one=True)['count']
    gyms_count = db.query_db("SELECT COUNT(*) as count FROM public_spaces WHERE type = 'Open Gyms'", one=True)['count']
    total_reports = db.query_db("SELECT COUNT(*) as count FROM reports", one=True)['count']
    resolved_reports = db.query_db("SELECT COUNT(*) as count FROM reports WHERE status = 'Resolved'", one=True)['count']
    total_users = db.query_db("SELECT COUNT(*) as count FROM users", one=True)['count']

    return jsonify({
        # Exact keys matching prompt specification
        'spaces': total_spaces,
        'responses': total_surveys,
        'parks': parks_count,
        'playgrounds': playgrounds_count,
        'promenades': promenades_count,
        'gardens': gardens_count,
        'gyms': gyms_count,
        # Extended metrics for dashboard & analytics
        'total_spaces': total_spaces,
        'total_surveys': total_surveys,
        'parks_count': parks_count,
        'playgrounds_count': playgrounds_count,
        'promenades_count': promenades_count,
        'gardens_count': gardens_count,
        'gyms_count': gyms_count,
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'total_users': total_users
    })

@app.route('/api/spaces', methods=['GET'])
def api_get_spaces():
    category = request.args.get('type')
    area = request.args.get('area')
    facility = request.args.get('facility')
    search = request.args.get('q')

    sql = """
        SELECT p.*, 
            ROUND(COALESCE(AVG(s.safety_rating + s.cleanliness_rating + s.lighting_rating + s.seating_rating + s.water_rating + s.accessibility_rating) / 6.0, 4.3), 1) as rating,
            COUNT(DISTINCT s.id) as survey_count,
            COUNT(DISTINCT f.id) as review_count
        FROM public_spaces p
        LEFT JOIN surveys s ON p.id = s.space_id
        LEFT JOIN feedback f ON p.id = f.space_id AND (f.status = 'Approved' OR f.status IS NULL)
    """
    conditions = []
    params = []

    if category and category.lower() != 'all':
        conditions.append("LOWER(p.type) = LOWER(%s)")
        params.append(category)

    if area and area.lower() != 'all':
        conditions.append("LOWER(p.area) = LOWER(%s)")
        params.append(area)

    if facility and facility.lower() != 'all':
        conditions.append("LOWER(p.facilities) LIKE LOWER(%s)")
        params.append(f"%{facility}%")

    if search:
        conditions.append("(LOWER(p.name) LIKE LOWER(%s) OR LOWER(p.area) LIKE LOWER(%s) OR LOWER(p.address) LIKE LOWER(%s) OR LOWER(p.facilities) LIKE LOWER(%s))")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " GROUP BY p.id ORDER BY p.name ASC"
    spaces = db.query_db(sql, tuple(params))
    return jsonify(spaces)

@app.route('/api/spaces/<int:space_id>', methods=['GET'])
def api_get_space(space_id):
    space = db.query_db("SELECT * FROM public_spaces WHERE id = %s", (space_id,), one=True)
    if not space:
        return jsonify({'error': 'Space not found'}), 404
    
    gallery = db.query_db("""
        SELECT * FROM public_space_images 
        WHERE public_space_id = %s 
        ORDER BY is_primary DESC, id ASC
    """, (space_id,))
    space['images'] = gallery
    space['gallery_images'] = gallery

    ratings = db.query_db("""
        SELECT 
            ROUND(AVG(safety_rating), 1) as avg_safety,
            ROUND(AVG(cleanliness_rating), 1) as avg_cleanliness,
            ROUND(AVG(lighting_rating), 1) as avg_lighting,
            ROUND(AVG(seating_rating), 1) as avg_seating,
            ROUND(AVG(water_rating), 1) as avg_water,
            ROUND(AVG(accessibility_rating), 1) as avg_accessibility,
            COUNT(*) as survey_count
        FROM surveys WHERE space_id = %s
    """, (space_id,), one=True)
    space['ratings'] = ratings
    space['survey_stats'] = {
        'safety': ratings['avg_safety'] if ratings and ratings['avg_safety'] else 4.2,
        'cleanliness': ratings['avg_cleanliness'] if ratings and ratings['avg_cleanliness'] else 4.0,
        'lighting': ratings['avg_lighting'] if ratings and ratings['avg_lighting'] else 4.1,
        'seating': ratings['avg_seating'] if ratings and ratings['avg_seating'] else 4.3,
        'water': ratings['avg_water'] if ratings and ratings['avg_water'] else 3.8,
        'accessibility': ratings['avg_accessibility'] if ratings and ratings['avg_accessibility'] else 4.4,
        'overall': 4.1,
        'survey_count': ratings['survey_count'] if ratings and ratings['survey_count'] else 0
    }
    return jsonify(space)

@app.route('/api/areas', methods=['GET'])
def api_get_areas():
    areas = db.query_db("SELECT * FROM areas ORDER BY name ASC")
    return jsonify(areas)

@app.route('/api/spaces', methods=['POST'])
@admin_required
def api_add_space():
    data = request.get_json() or {}
    name = data.get('name')
    type_val = data.get('type')
    area = data.get('area', 'New Panvel')
    address = data.get('address')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    description = data.get('description', '')
    facilities = data.get('facilities', '')
    opening_time = data.get('opening_time', '05:30 AM')
    closing_time = data.get('closing_time', '09:30 PM')
    average_visitors = data.get('average_visitors', 500)
    condition = data.get('condition', 'Good')
    image = data.get('image') or 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800'
    image_source = data.get('image_source', 'Field Survey')
    image_credit = data.get('image_credit', 'Academic Survey Team')
    google_maps_url = data.get('google_maps_url') or f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

    if not all([name, type_val, address, latitude, longitude]):
        return jsonify({'success': False, 'error': 'Name, type, address, latitude, and longitude are required.'}), 400

    new_id = db.execute_db("""
        INSERT INTO public_spaces 
        (name, type, area, address, latitude, longitude, description, facilities, opening_time, closing_time, average_visitors, condition, primary_image, image_source, image_credit, google_maps_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, type_val, area, address, float(latitude), float(longitude), description, facilities, opening_time, closing_time, int(average_visitors), condition, image, image_source, image_credit, google_maps_url))

    db.execute_db("""
        INSERT INTO public_space_images (public_space_id, image_path, image_source, image_credit, is_primary)
        VALUES (%s, %s, %s, %s, 1)
    """, (new_id, image, image_source, image_credit))

    return jsonify({'success': True, 'id': new_id, 'message': 'Public space created successfully.'}), 201

@app.route('/api/spaces/<int:space_id>', methods=['PUT'])
@admin_required
def api_update_space(space_id):
    data = request.get_json() or {}
    fields = ['name', 'type', 'area', 'address', 'latitude', 'longitude', 'description', 'facilities', 'opening_time', 'closing_time', 'average_visitors', 'condition', 'image']
    updates = []
    params = []
    
    for f in fields:
        if f in data:
            updates.append(f"{f} = %s")
            val = data[f]
            if f in ['latitude', 'longitude']:
                val = float(val)
            elif f == 'average_visitors':
                val = int(val)
            params.append(val)

    if not updates:
        return jsonify({'success': False, 'error': 'No fields provided for update.'}), 400

    params.append(space_id)
    sql = f"UPDATE public_spaces SET {', '.join(updates)} WHERE id = %s"
    db.execute_db(sql, tuple(params))
    return jsonify({'success': True, 'message': 'Public space updated successfully.'})

@app.route('/api/spaces/<int:space_id>', methods=['DELETE'])
@admin_required
def api_delete_space(space_id):
    db.execute_db("DELETE FROM public_spaces WHERE id = %s", (space_id,))
    return jsonify({'success': True, 'message': 'Public space deleted successfully.'})

@app.route('/api/surveys', methods=['GET'])
def api_get_surveys():
    space_id = request.args.get('space_id')
    sql = """
        SELECT s.*, p.name as space_name, p.type as space_type,
               COALESCE(u.name, 'Community Respondent') as user_name
        FROM surveys s
        JOIN public_spaces p ON s.space_id = p.id
        LEFT JOIN users u ON s.user_id = u.id
    """
    params = []
    if space_id:
        sql += " WHERE s.space_id = %s"
        params.append(space_id)

    sql += " ORDER BY s.created_at DESC"
    surveys = db.query_db(sql, tuple(params))
    return jsonify(surveys)

@app.route('/api/surveys', methods=['POST'])
def api_submit_survey():
    data = request.get_json() or {}
    space_id = data.get('space_id')
    visit_frequency = data.get('visit_frequency')
    purpose = data.get('purpose')
    age_group = data.get('age_group')
    safety = data.get('safety_rating')
    cleanliness = data.get('cleanliness_rating')
    lighting = data.get('lighting_rating')
    seating = data.get('seating_rating')
    water = data.get('water_rating')
    accessibility = data.get('accessibility_rating')
    improvement = data.get('improvement', '')
    suggestion = data.get('suggestion', '')

    if not all([space_id, visit_frequency, purpose, age_group, safety, cleanliness, lighting, seating, water, accessibility]):
        return jsonify({'success': False, 'error': 'Please answer all required rating questions.'}), 400

    user_id = session.get('user_id')

    survey_id = db.execute_db("""
        INSERT INTO surveys 
        (user_id, space_id, visit_frequency, purpose, age_group, safety_rating, cleanliness_rating, lighting_rating, seating_rating, water_rating, accessibility_rating, improvement, suggestion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, int(space_id), visit_frequency, purpose, age_group, int(safety), int(cleanliness), int(lighting), int(seating), int(water), int(accessibility), improvement, suggestion))

    return jsonify({
        'success': True,
        'id': survey_id,
        'message': 'Survey submitted successfully! Thank you for contributing to our community project.'
    }), 201

@app.route('/api/surveys/<int:survey_id>', methods=['DELETE'])
@admin_required
def api_delete_survey(survey_id):
    db.execute_db("DELETE FROM surveys WHERE id = %s", (survey_id,))
    return jsonify({'success': True, 'message': 'Survey response deleted.'})

@app.route('/api/reports', methods=['GET'])
def api_get_reports():
    reports = db.query_db("""
        SELECT r.*, p.name as space_name, COALESCE(u.name, 'Anonymous Citizen') as user_name
        FROM reports r
        JOIN public_spaces p ON r.space_id = p.id
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY r.created_at DESC
    """)
    return jsonify(reports)

@app.route('/api/reports', methods=['POST'])
def api_submit_report():
    # Handle either JSON or multipart form data
    if request.is_json:
        data = request.get_json()
        photo_filename = None
    else:
        data = request.form
        photo_file = request.files.get('photo')
        photo_filename = None
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            filename = secure_filename(f"{int(datetime.now().timestamp())}_{photo_file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(filepath)
            photo_filename = filename

    space_id = data.get('space_id')
    issue_type = data.get('issue_type')
    description = data.get('description', '').strip()
    location = data.get('location', '').strip()
    priority = data.get('priority', 'Medium')

    if not all([space_id, issue_type, description]):
        return jsonify({'success': False, 'error': 'Public space, issue type, and description are required.'}), 400

    user_id = session.get('user_id')

    report_id = db.execute_db("""
        INSERT INTO reports (user_id, space_id, issue_type, description, photo, location, priority, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Reported')
    """, (user_id, int(space_id), issue_type, description, photo_filename, location, priority))

    return jsonify({
        'success': True,
        'id': report_id,
        'message': 'Issue reported successfully. Our Smart City maintenance team will review it shortly.'
    }), 201

@app.route('/api/reports/<int:report_id>', methods=['PUT'])
@admin_required
def api_update_report(report_id):
    data = request.get_json() or {}
    status = data.get('status')
    priority = data.get('priority')
    
    updates = []
    params = []
    if status:
        updates.append("status = %s")
        params.append(status)
    if priority:
        updates.append("priority = %s")
        params.append(priority)

    if not updates:
        return jsonify({'success': False, 'error': 'No fields to update.'}), 400

    params.append(report_id)
    sql = f"UPDATE reports SET {', '.join(updates)} WHERE id = %s"
    db.execute_db(sql, tuple(params))

    return jsonify({'success': True, 'message': 'Report updated successfully.'})

@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
@admin_required
def api_delete_report(report_id):
    db.execute_db("DELETE FROM reports WHERE id = %s", (report_id,))
    return jsonify({'success': True, 'message': 'Report deleted successfully.'})

@app.route('/api/feedback', methods=['POST'])
def api_submit_feedback():
    data = request.get_json() or {}
    space_id = data.get('space_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    user_name = data.get('user_name', '').strip() or session.get('user_name') or 'Community Citizen'
    user_email = data.get('user_email', '').strip() or session.get('user_email') or 'citizen@panvel.community'

    if not space_id or not rating or not comment:
        return jsonify({'success': False, 'error': 'Rating and comment are required.'}), 400

    user_id = session.get('user_id')
    fid = db.execute_db("""
        INSERT INTO feedback (user_id, space_id, user_name, user_email, rating, comment, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'Approved')
    """, (user_id, int(space_id), user_name, user_email, int(rating), comment))

    return jsonify({'success': True, 'id': fid, 'message': 'Comment submitted successfully! Thank you for your feedback.'}), 201

@app.route('/api/feedback/<int:space_id>', methods=['GET'])
def api_get_feedback(space_id):
    feedbacks = db.query_db("""
        SELECT f.*, COALESCE(f.user_name, u.name, 'Community Visitor') as user_name
        FROM feedback f
        LEFT JOIN users u ON f.user_id = u.id
        WHERE f.space_id = %s AND (f.status = 'Approved' OR f.status IS NULL)
        ORDER BY f.created_at DESC
    """, (space_id,))
    return jsonify(feedbacks)

# Admin Image Management APIs (Requirement 18)
@app.route('/api/spaces/<int:space_id>/images', methods=['POST'])
@admin_required
def api_add_space_image(space_id):
    image_source = (request.form.get('image_source') if not request.is_json else request.get_json().get('image_source')) or 'Field Survey Photograph'
    image_credit = (request.form.get('image_credit') if not request.is_json else request.get_json().get('image_credit')) or 'Academic Research Team'
    is_primary = 1 if (request.form.get('is_primary') in ['1', 'true', 'True', True] or (request.is_json and request.get_json().get('is_primary') in ['1', 'true', 'True', True, 1])) else 0
    
    image_path = None
    if 'photo' in request.files:
        photo_file = request.files['photo']
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            filename = secure_filename(f"space_{space_id}_{int(datetime.now().timestamp())}_{photo_file.filename}")
            filepath = os.path.join(app.config['UPLOAD_SPACES_FOLDER'], filename)
            photo_file.save(filepath)
            image_path = f"/uploads/spaces/{filename}"
    elif request.form.get('image_url'):
        image_path = request.form.get('image_url').strip()
    elif request.is_json and request.get_json().get('image_url'):
        image_path = request.get_json().get('image_url').strip()

    if not image_path:
        return jsonify({'success': False, 'error': 'Please provide an image file or URL.'}), 400

    if is_primary:
        db.execute_db("UPDATE public_space_images SET is_primary = 0 WHERE public_space_id = %s", (space_id,))
        db.execute_db("UPDATE public_spaces SET primary_image = %s, image_source = %s, image_credit = %s WHERE id = %s", (image_path, image_source, image_credit, space_id))

    img_id = db.execute_db("""
        INSERT INTO public_space_images (public_space_id, image_path, image_source, image_credit, is_primary)
        VALUES (%s, %s, %s, %s, %s)
    """, (space_id, image_path, image_source, image_credit, is_primary))

    return jsonify({
        'success': True,
        'id': img_id,
        'image_path': image_path,
        'message': 'Photograph added to public space gallery successfully with copyright attribution.'
    }), 201

@app.route('/api/spaces/images/<int:image_id>', methods=['DELETE'])
@admin_required
def api_delete_space_image(image_id):
    img = db.query_db("SELECT * FROM public_space_images WHERE id = %s", (image_id,), one=True)
    if not img:
        return jsonify({'success': False, 'error': 'Image not found.'}), 404
        
    db.execute_db("DELETE FROM public_space_images WHERE id = %s", (image_id,))
    return jsonify({'success': True, 'message': 'Image removed successfully.'})

@app.route('/api/spaces/images/<int:image_id>/primary', methods=['PUT'])
@admin_required
def api_set_primary_image(image_id):
    img = db.query_db("SELECT * FROM public_space_images WHERE id = %s", (image_id,), one=True)
    if not img:
        return jsonify({'success': False, 'error': 'Image not found.'}), 404

    space_id = img['public_space_id']
    db.execute_db("UPDATE public_space_images SET is_primary = 0 WHERE public_space_id = %s", (space_id,))
    db.execute_db("UPDATE public_space_images SET is_primary = 1 WHERE id = %s", (image_id,))
    db.execute_db("UPDATE public_spaces SET primary_image = %s, image_source = %s, image_credit = %s WHERE id = %s", (img['image_path'], img['image_source'], img['image_credit'], space_id))
    return jsonify({'success': True, 'message': 'Primary image updated successfully.'})

# Admin Comment Moderation APIs (Requirement 10)
@app.route('/api/feedback/<int:feedback_id>/status', methods=['PUT'])
@admin_required
def api_update_feedback_status(feedback_id):
    data = request.get_json() or {}
    status = data.get('status', 'Approved')
    db.execute_db("UPDATE feedback SET status = %s WHERE id = %s", (status, feedback_id))
    return jsonify({'success': True, 'message': f'Comment marked as {status}.'})

@app.route('/api/feedback/<int:feedback_id>', methods=['DELETE'])
@admin_required
def api_delete_feedback(feedback_id):
    db.execute_db("DELETE FROM feedback WHERE id = %s", (feedback_id,))
    return jsonify({'success': True, 'message': 'Comment deleted successfully.'})

@app.route('/api/users', methods=['GET'])
@admin_required
def api_get_users():
    users = db.query_db("SELECT id, name, email, mobile, age_group, gender, role, created_at FROM users ORDER BY created_at DESC")
    return jsonify(users)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    db.execute_db("DELETE FROM users WHERE id = %s", (user_id,))
    return jsonify({'success': True, 'message': 'User deleted successfully.'})

@app.route('/api/logout', methods=['POST', 'GET'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@app.route('/api/admin/logout', methods=['POST', 'GET'])
def api_admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    if session.get('role') == 'admin':
        session.pop('role', None)
    return jsonify({'success': True, 'message': 'Admin logged out successfully.'})

@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not all([name, email, subject, message]):
        return jsonify({'success': False, 'error': 'All fields are required.'}), 400

    cid = db.execute_db("""
        INSERT INTO contact_messages (name, email, subject, message)
        VALUES (%s, %s, %s, %s)
    """, (name, email, subject, message))

    return jsonify({'success': True, 'id': cid, 'message': 'Your message has been sent successfully!'})

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    """Aggregated statistics for dynamic Chart.js visualizations."""
    total_surveys_row = db.query_db("SELECT COUNT(*) as count FROM surveys", one=True)
    total_responses = total_surveys_row['count'] if total_surveys_row else 0

    # 1. Public Space Usage by Type
    usage_by_type = db.query_db("""
        SELECT p.type, COUNT(s.id) as count 
        FROM public_spaces p
        LEFT JOIN surveys s ON p.id = s.space_id
        GROUP BY p.type
    """)
    type_labels = [row['type'] for row in usage_by_type]
    type_counts = [row['count'] for row in usage_by_type]
    total_usage = sum(type_counts) or 1
    type_percentages = [round((c / total_usage) * 100, 1) for c in type_counts]

    # 2. Main Activities
    activities = db.query_db("""
        SELECT purpose, COUNT(*) as count 
        FROM surveys 
        GROUP BY purpose 
        ORDER BY count DESC
    """)
    activity_labels = [row['purpose'] for row in activities]
    activity_counts = [row['count'] for row in activities]

    # 3. Age Groups
    age_groups = db.query_db("""
        SELECT age_group, COUNT(*) as count 
        FROM surveys 
        GROUP BY age_group 
        ORDER BY count DESC
    """)
    age_labels = [row['age_group'] for row in age_groups]
    age_counts = [row['count'] for row in age_groups]

    # 4. Facility Average Ratings
    facility_avgs = db.query_db("""
        SELECT 
            ROUND(AVG(safety_rating), 2) as safety,
            ROUND(AVG(cleanliness_rating), 2) as cleanliness,
            ROUND(AVG(lighting_rating), 2) as lighting,
            ROUND(AVG(seating_rating), 2) as seating,
            ROUND(AVG(water_rating), 2) as water,
            ROUND(AVG(accessibility_rating), 2) as accessibility
        FROM surveys
    """, one=True)

    facility_labels = ['Safety', 'Cleanliness', 'Lighting', 'Seating', 'Drinking Water', 'Accessibility']
    facility_scores = [
        float(facility_avgs.get('safety') or 4.2),
        float(facility_avgs.get('cleanliness') or 4.1),
        float(facility_avgs.get('lighting') or 4.0),
        float(facility_avgs.get('seating') or 3.9),
        float(facility_avgs.get('water') or 3.5),
        float(facility_avgs.get('accessibility') or 4.3)
    ]

    # 5. Visit Frequency Breakdown
    frequencies = db.query_db("""
        SELECT visit_frequency, COUNT(*) as count 
        FROM surveys 
        GROUP BY visit_frequency 
        ORDER BY count DESC
    """)
    freq_labels = [row['visit_frequency'] for row in frequencies]
    freq_counts = [row['count'] for row in frequencies]

    # 6. Priority Improvement Needs
    improvements = db.query_db("""
        SELECT improvement, COUNT(*) as count 
        FROM surveys 
        WHERE improvement IS NOT NULL AND improvement != ''
        GROUP BY improvement 
        ORDER BY count DESC LIMIT 6
    """)
    imp_labels = [row['improvement'] for row in improvements]
    imp_counts = [row['count'] for row in improvements]

    # Most used space
    top_space = db.query_db("""
        SELECT p.name, COUNT(s.id) as count 
        FROM public_spaces p 
        JOIN surveys s ON p.id = s.space_id 
        GROUP BY p.id 
        ORDER BY count DESC LIMIT 1
    """, one=True)

    return jsonify({
        'total_responses': total_responses,
        'most_used_space': top_space['name'] if top_space else 'Central Heritage Botanical Park',
        'usage_by_type': {
            'labels': type_labels,
            'counts': type_counts,
            'percentages': type_percentages
        },
        'activities': {
            'labels': activity_labels,
            'counts': activity_counts
        },
        'age_groups': {
            'labels': age_labels,
            'counts': age_counts
        },
        'facility_ratings': {
            'labels': facility_labels,
            'scores': facility_scores
        },
        'visit_frequencies': {
            'labels': freq_labels,
            'counts': freq_counts
        },
        'improvement_needs': {
            'labels': imp_labels,
            'counts': imp_counts
        }
    })

if __name__ == '__main__':
    print("[PublicSpace360] Server starting on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
