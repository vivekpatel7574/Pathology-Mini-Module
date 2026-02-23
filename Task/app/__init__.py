"""
Pathology Module - WSGI Flask Application
Server-rendered HTML with Jinja2 templating
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import os

from app.models import db, PathologyTest, LabTestOrder, LabTestResult, OrderStatusEnum, ResultStatusEnum
from app.controllers import PathologyTestController, LabTestOrderController, LabTestResultController


def create_app(config=None):
    """Application factory"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Configuration
    if config is None:
        config = {
            'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:@localhost:3306/pathology_db',  # MySQL from XAMPP
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'dev-secret-key-change-in-production',
            'JSON_SORT_KEYS': False,
        }
    
    app.config.update(config)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # ===== PATHOLOGY TEST ENDPOINTS =====
    
    @app.route('/')
    def index():
        """Dashboard/Home page"""
        test_count = PathologyTest.query.count()
        order_count = LabTestOrder.query.count()
        result_count = LabTestResult.query.count()
        today_orders = LabTestOrder.query.filter_by(order_date=date.today()).count()
        
        return render_template('index.html',
                             test_count=test_count,
                             order_count=order_count,
                             result_count=result_count,
                             today_orders=today_orders)
    
    @app.route('/tests', methods=['GET'])
    def list_tests():
        """List all tests with search"""
        search = request.args.get('search', '').strip()
        
        if search:
            tests = PathologyTestController.search_tests(search)
        else:
            tests = PathologyTestController.list_all_tests()
        
        return render_template('tests/list.html', tests=tests, search=search)
    
    @app.route('/tests/new', methods=['GET', 'POST'])
    def create_test():
        """Create a new test"""
        if request.method == 'POST':
            try:
                test = PathologyTestController.create_test(
                    test_name=request.form.get('test_name'),
                    test_code=request.form.get('test_code'),
                    sample_type=request.form.get('sample_type'),
                    normal_range=request.form.get('normal_range'),
                    price=request.form.get('price'),
                    is_active=request.form.get('is_active') == 'on'
                )
                flash(f'Test "{test.test_name}" created successfully (ID: {test.id})', 'success')
                return redirect(url_for('list_tests'))
            except ValueError as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('tests/form.html', test=None)
    
    @app.route('/tests/<int:test_id>/edit', methods=['GET', 'POST'])
    def edit_test(test_id):
        """Edit an existing test"""
        try:
            test = PathologyTestController.get_test_by_id(test_id)
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('list_tests'))
        
        if request.method == 'POST':
            try:
                updates = {
                    'test_name': request.form.get('test_name'),
                    'price': request.form.get('price'),
                    'normal_range': request.form.get('normal_range'),
                    'is_active': request.form.get('is_active') == 'on'
                }
                test = PathologyTestController.update_test(test_id, **updates)
                flash(f'Test "{test.test_name}" updated successfully', 'success')
                return redirect(url_for('list_tests'))
            except ValueError as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('tests/form.html', test=test)
    
    @app.route('/tests/<int:test_id>/view')
    def view_test(test_id):
        """View test details"""
        try:
            test = PathologyTestController.get_test_by_id(test_id)
            return render_template('tests/view.html', test=test)
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('list_tests'))
    
    # ===== LAB TEST ORDER ENDPOINTS =====
    
    @app.route('/orders', methods=['GET'])
    def list_orders():
        """List all orders"""
        filter_type = request.args.get('filter', 'all')
        search = request.args.get('search', '').strip()
        
        try:
            if search:
                orders = LabTestOrderController.search_orders(search)
            elif filter_type == 'today':
                orders = LabTestOrderController.list_today_orders()
            elif filter_type in ['Draft', 'Ordered', 'Completed', 'Cancelled']:
                orders = LabTestOrderController.list_orders_by_status(filter_type)
            else:
                orders = LabTestOrderController.list_all_orders()
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            orders = []
        
        return render_template('orders/list.html',
                             orders=orders,
                             filter_type=filter_type,
                             search=search,
                             statuses=[s.value for s in OrderStatusEnum])
    
    @app.route('/orders/new', methods=['GET', 'POST'])
    def create_order():
        """Create a new order"""
        active_tests = PathologyTestController.list_active_tests()
        
        if request.method == 'POST':
            try:
                order = LabTestOrderController.create_order(
                    patient_name=request.form.get('patient_name'),
                    patient_phone=request.form.get('patient_phone'),
                    test_id=int(request.form.get('test_id')),
                    order_date=request.form.get('order_date')
                )
                flash(f'Order "{order.order_id}" created successfully', 'success')
                return redirect(url_for('view_order', order_id=order.id))
            except (ValueError, TypeError) as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('orders/form.html', order=None, tests=active_tests)
    
    @app.route('/orders/<int:order_id>')
    def view_order(order_id):
        """View order details"""
        try:
            order = LabTestOrderController.get_order_by_id(order_id)
            result = LabTestResult.query.filter_by(order_id=order_id).first()
            
            # Determine available actions based on status
            actions = {
                'can_order': order.status == OrderStatusEnum.DRAFT.value,
                'can_create_result': order.status == OrderStatusEnum.ORDERED.value,
                'can_cancel': order.status in [OrderStatusEnum.DRAFT.value, OrderStatusEnum.ORDERED.value],
                'can_complete_result': result and result.status == ResultStatusEnum.DRAFT.value,
            }
            
            return render_template('orders/view.html', order=order, result=result, actions=actions)
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('list_orders'))
    
    @app.route('/orders/<int:order_id>/status', methods=['POST'])
    def update_order_status(order_id):
        """Update order status (AJAX or form)"""
        new_status = request.form.get('status')
        
        try:
            order = LabTestOrderController.transition_status(order_id, new_status)
            flash(f'Order status updated to "{new_status}"', 'success')
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
        
        return redirect(url_for('view_order', order_id=order_id))
    
    @app.route('/orders/<int:order_id>/cancel', methods=['POST'])
    def cancel_order(order_id):
        """Cancel an order"""
        try:
            order = LabTestOrderController.transition_status(order_id, OrderStatusEnum.CANCELLED.value)
            flash(f'Order "{order.order_id}" cancelled', 'success')
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
        
        return redirect(url_for('view_order', order_id=order_id))
    
    # ===== LAB TEST RESULT ENDPOINTS =====
    
    @app.route('/results', methods=['GET'])
    def list_results():
        """List all results"""
        filter_type = request.args.get('filter', 'all')
        
        try:
            if filter_type == 'completed':
                results = LabTestResultController.list_completed_results()
            else:
                results = LabTestResultController.list_all_results()
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            results = []
        
        return render_template('results/list.html', results=results, filter_type=filter_type)
    
    @app.route('/orders/<int:order_id>/result/new', methods=['GET', 'POST'])
    def create_result(order_id):
        """Create a result for an order"""
        try:
            order = LabTestOrderController.get_order_by_id(order_id)
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('list_orders'))
        
        # Check if order can have result created
        if not order.can_create_result():
            flash(f'Result can only be created for orders in "{OrderStatusEnum.ORDERED.value}" status', 'error')
            return redirect(url_for('view_order', order_id=order_id))
        
        if request.method == 'POST':
            try:
                result = LabTestResultController.create_result(
                    order_id=order_id,
                    result_value=request.form.get('result_value'),
                    technician_notes=request.form.get('technician_notes')
                )
                flash(f'Result created successfully', 'success')
                return redirect(url_for('view_result', result_id=result.id))
            except ValueError as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('results/form.html', order=order, result=None)
    
    @app.route('/results/<int:result_id>')
    def view_result(result_id):
        """View result details"""
        try:
            result = LabTestResultController.get_result_by_id(result_id)
            order = result.order
            test = order.test
            
            # Determine available actions
            actions = {
                'can_edit': result.status == ResultStatusEnum.DRAFT.value,
                'can_complete': result.can_complete(),
            }
            
            return render_template('results/view.html', result=result, order=order, test=test, actions=actions)
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('list_results'))
    
    @app.route('/results/<int:result_id>/edit', methods=['GET', 'POST'])
    def edit_result(result_id):
        """Edit a result (Draft only)"""
        try:
            result = LabTestResultController.get_result_by_id(result_id)
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('list_results'))
        
        order = result.order
        
        # Check if result can be edited
        if result.status != ResultStatusEnum.DRAFT.value:
            flash(f'Can only edit results in Draft status', 'error')
            return redirect(url_for('view_result', result_id=result_id))
        
        if request.method == 'POST':
            try:
                result = LabTestResultController.update_result(
                    result_id,
                    result_value=request.form.get('result_value'),
                    technician_notes=request.form.get('technician_notes')
                )
                flash(f'Result updated successfully', 'success')
                return redirect(url_for('view_result', result_id=result_id))
            except ValueError as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('results/form.html', order=order, result=result)
    
    @app.route('/results/<int:result_id>/complete', methods=['POST'])
    def complete_result(result_id):
        """Mark result as completed"""
        try:
            result = LabTestResultController.complete_result(result_id)
            flash(f'Result marked as completed. Related order also marked as completed.', 'success')
            return redirect(url_for('view_result', result_id=result_id))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('view_result', result_id=result_id))
    
    # ===== ERROR HANDLERS =====
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
