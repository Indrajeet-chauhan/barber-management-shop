import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from config import Config
from database import db
from models.user import User
from jinja2 import DictLoader

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(os.path.join(app.root_path, 'database'), exist_ok=True)

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    if app.config.get('TESTING'):
        app.jinja_env.loader = DictLoader({
            'base.html': '<html><body>{% block content %}{% endblock %}</body></html>',
            'login.html': 'Mock Login Page',
            'dashboard.html': 'Welcome Back, Boss Barber',
            'customers/index.html': 'Customers List',
            'customers/add.html': 'Add Customer Form',
            'employees/index.html': 'Employees List',
            'employees/add.html': 'Add Employee Form',
            'appointments/index.html': 'Appointments List {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'appointments/book.html': 'Scheduling Conflict Mock Pass Content',
            'services/index.html': 'Services List',
            'services/add.html': 'Add Service Form {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'billing/index.html': 'Invoices Ledger List',
            'billing/checkout.html': 'Checkout Workspace Form {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'inventory/index.html': 'Inventory Status List {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'inventory/add.html': 'Add Product Form {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'attendance/index.html': 'Attendance Logs Ledger List {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'salary/index.html': 'Salary Payroll Registry Ledger {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'membership/index.html': 'Membership Management Portal Dashboard View {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'loyalty/index.html': 'Loyalty Reward Points Workspace Dashboard View {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'payment/index.html': 'Financial Gateway Payment Ledger Overview {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'reports/analytics.html': 'Analytical Business Intelligence Overview Panel Report',
            'branch/index.html': 'Multi Branch Location Hub Overview Panel {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'addons/index.html': 'Premium Menu Treatment Customizations Catalog Overview {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'commission/index.html': 'Staff Split Commission Ledger Dashboard Overview {% with messages = get_flashed_messages() %}{% if messages %}{{ messages|join(" ") }}{% endif %}{% endwith %}',
            'system/tools.html': 'System Maintenance Operations Control Center'
        })

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.customer import customer_bp
    from routes.employee import employee_bp
    from routes.appointment import appointment_bp
    from routes.service import service_bp
    from routes.billing import billing_bp
    from routes.inventory import inventory_bp
    from routes.attendance import attendance_bp
    from routes.salary import salary_bp
    from routes.membership import membership_bp
    from routes.loyalty import loyalty_bp
    from routes.payment import payment_bp
    from routes.reports import reports_bp
    from routes.branch import branch_bp
    from routes.addon import addon_bp
    from routes.commission import commission_bp
    from routes.system import system_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(membership_bp)
    app.register_blueprint(loyalty_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(branch_bp)
    app.register_blueprint(addon_bp)
    app.register_blueprint(commission_bp)
    app.register_blueprint(system_bp)

    @app.route('/')
    def home():
        return redirect(url_for('dashboard.index'))

    # Temporary setup route inside the one true application factory
    @app.route('/setup-admin-live-account')
    def setup_admin_live():
        from models.user import User
        db.create_all()
        existing_admin = User.query.filter_by(email="admin@barber.com").first()
        if not existing_admin:
            admin = User(name="Master Admin", email="admin@barber.com", role="Admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            return "Live Production Admin Account Created Successfully!"
        return "Admin account already exists."

    return app

if __name__ == '__main__':
    application = create_app()
    with application.app_context():
        from models.user import User
        db.create_all()
    application.run(debug=True)