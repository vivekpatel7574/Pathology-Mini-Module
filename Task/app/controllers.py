"""
Business logic and controllers for Pathology module
Handles all server-side validations and state management
"""

from datetime import datetime, date
from app.models import (
    db, PathologyTest, LabTestOrder, LabTestResult,
    NamingSeries, OrderStatusEnum, ResultStatusEnum
)


class PathologyTestController:
    """Controller for Pathology Test operations"""

    @staticmethod
    def create_test(test_name, test_code, sample_type, normal_range, price, is_active=True):
        """
        Create a new pathology test
        Validations:
        - test_name and test_code must be unique
        - price must be positive
        """
        # Validate inputs
        if not test_name or not test_name.strip():
            raise ValueError("Test name is required")
        if not test_code or not test_code.strip():
            raise ValueError("Test code is required")
        if not sample_type or not sample_type.strip():
            raise ValueError("Sample type is required")
        if not normal_range or not normal_range.strip():
            raise ValueError("Normal range is required")
        
        try:
            price_float = float(price)
            if price_float <= 0:
                raise ValueError("Price must be greater than 0")
        except (ValueError, TypeError):
            raise ValueError("Invalid price format")

        # Check for duplicates
        existing = PathologyTest.query.filter_by(test_code=test_code).first()
        if existing:
            raise ValueError(f"Test code '{test_code}' already exists")

        existing_name = PathologyTest.query.filter_by(test_name=test_name).first()
        if existing_name:
            raise ValueError(f"Test name '{test_name}' already exists")

        test = PathologyTest(
            test_name=test_name,
            test_code=test_code,
            sample_type=sample_type,
            normal_range=normal_range,
            price=price_float,
            is_active=is_active
        )
        db.session.add(test)
        db.session.commit()
        return test

    @staticmethod
    def list_active_tests():
        """Get all active tests"""
        return PathologyTest.query.filter_by(is_active=True).all()

    @staticmethod
    def list_all_tests():
        """Get all tests (active and inactive)"""
        return PathologyTest.query.all()

    @staticmethod
    def search_tests(search_term):
        """Search tests by name or code"""
        if not search_term:
            return PathologyTest.query.all()
        
        search_pattern = f"%{search_term}%"
        return PathologyTest.query.filter(
            (PathologyTest.test_name.ilike(search_pattern)) |
            (PathologyTest.test_code.ilike(search_pattern))
        ).all()

    @staticmethod
    def get_test_by_id(test_id):
        """Get a single test by ID"""
        test = PathologyTest.query.get(test_id)
        if not test:
            raise ValueError(f"Test with ID {test_id} not found")
        return test

    @staticmethod
    def update_test(test_id, **kwargs):
        """
        Update test details
        Note: Cannot change test_code of active tests with orders
        """
        test = PathologyTestController.get_test_by_id(test_id)
        
        # Validate individual fields
        if 'test_name' in kwargs:
            if not kwargs['test_name'].strip():
                raise ValueError("Test name cannot be empty")
            # Check for duplicates
            existing = PathologyTest.query.filter(
                PathologyTest.test_name == kwargs['test_name'],
                PathologyTest.id != test_id
            ).first()
            if existing:
                raise ValueError(f"Test name '{kwargs['test_name']}' already exists")
            test.test_name = kwargs['test_name']

        if 'price' in kwargs:
            price_float = float(kwargs['price'])
            if price_float <= 0:
                raise ValueError("Price must be greater than 0")
            test.price = price_float

        if 'is_active' in kwargs:
            test.is_active = kwargs['is_active']

        if 'normal_range' in kwargs:
            if not kwargs['normal_range'].strip():
                raise ValueError("Normal range cannot be empty")
            test.normal_range = kwargs['normal_range']

        test.updated_at = datetime.utcnow()
        db.session.commit()
        return test


class LabTestOrderController:
    """Controller for Lab Test Order operations"""

    @staticmethod
    def _get_or_create_naming_series():
        """Get or create the naming series for orders"""
        series = NamingSeries.query.filter_by(series_name='LabTestOrder').first()
        if not series:
            series = NamingSeries(
                series_name='LabTestOrder',
                series_prefix='LTO-',
                current_number=1000
            )
            db.session.add(series)
            db.session.commit()
        return series

    @staticmethod
    def create_order(patient_name, patient_phone, test_id, order_date):
        """
        Create a new lab test order
        
        Business Rules:
        - Patient name and phone are required
        - Test must exist and be active
        - Order date cannot be in the past
        - Default status is Draft
        - Order ID is auto-generated using naming series
        """
        # Validate inputs
        if not patient_name or not patient_name.strip():
            raise ValueError("Patient name is required")
        if not patient_phone or not patient_phone.strip():
            raise ValueError("Patient phone is required")

        # Validate test exists and is active
        try:
            test = PathologyTestController.get_test_by_id(test_id)
        except ValueError as e:
            raise ValueError(f"Invalid test: {str(e)}")

        if not test.is_active:
            raise ValueError(f"Test '{test.test_name}' is not active and cannot be ordered")

        # Validate order date
        try:
            if isinstance(order_date, str):
                order_date_obj = datetime.strptime(order_date, '%Y-%m-%d').date()
            else:
                order_date_obj = order_date
        except (ValueError, TypeError):
            raise ValueError("Invalid order date format (use YYYY-MM-DD)")

        if order_date_obj < date.today():
            raise ValueError("Order date cannot be in the past")

        # Generate order ID
        series = LabTestOrderController._get_or_create_naming_series()
        order_id = series.get_next_name()

        # Create order with Draft status
        order = LabTestOrder(
            order_id=order_id,
            patient_name=patient_name,
            patient_phone=patient_phone,
            test_id=test_id,
            order_date=order_date_obj,
            status=OrderStatusEnum.DRAFT.value
        )
        db.session.add(order)
        db.session.commit()
        return order

    @staticmethod
    def list_all_orders():
        """Get all orders"""
        return LabTestOrder.query.order_by(LabTestOrder.created_at.desc()).all()

    @staticmethod
    def list_today_orders():
        """Get all orders scheduled for today"""
        today = date.today()
        return LabTestOrder.query.filter_by(order_date=today).order_by(
            LabTestOrder.created_at.desc()
        ).all()

    @staticmethod
    def list_orders_by_status(status):
        """Get all orders with specific status"""
        valid_statuses = [s.value for s in OrderStatusEnum]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        return LabTestOrder.query.filter_by(status=status).order_by(
            LabTestOrder.created_at.desc()
        ).all()

    @staticmethod
    def get_order_by_id(order_id):
        """Get a single order by ID"""
        order = LabTestOrder.query.get(order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        return order

    @staticmethod
    def get_order_by_order_id(order_id_str):
        """Get a single order by order_id string (e.g., LTO-1001)"""
        order = LabTestOrder.query.filter_by(order_id=order_id_str).first()
        if not order:
            raise ValueError(f"Order '{order_id_str}' not found")
        return order

    @staticmethod
    def transition_status(order_id, new_status):
        """
        Transition order status with validation
        
        Valid transitions:
        - Draft → Ordered, Cancelled
        - Ordered → Completed, Cancelled
        - Completed → (no transitions)
        - Cancelled → (no transitions)
        """
        order = LabTestOrderController.get_order_by_id(order_id)
        
        # Validate new status
        valid_statuses = [s.value for s in OrderStatusEnum]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")

        # Check if transition is allowed
        if not order.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from {order.status} to {new_status}. "
                f"Valid transitions from {order.status}: {order.can_transition_to.__doc__}"
            )

        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        return order

    @staticmethod
    def search_orders(search_term):
        """Search orders by order_id or patient name"""
        if not search_term:
            return LabTestOrder.query.all()
        
        search_pattern = f"%{search_term}%"
        return LabTestOrder.query.filter(
            (LabTestOrder.order_id.ilike(search_pattern)) |
            (LabTestOrder.patient_name.ilike(search_pattern))
        ).order_by(LabTestOrder.created_at.desc()).all()


class LabTestResultController:
    """Controller for Lab Test Result operations"""

    @staticmethod
    def create_result(order_id, result_value, technician_notes=None):
        """
        Create a new lab test result
        
        Business Rules:
        - Order must exist and status must be 'Ordered'
        - Result always starts in Draft status
        - Result value cannot be empty
        """
        # Validate order exists and is in Ordered status
        try:
            order = LabTestOrderController.get_order_by_id(order_id)
        except ValueError as e:
            raise ValueError(f"Invalid order: {str(e)}")

        if not order.can_create_result():
            raise ValueError(
                f"Result can only be created for orders in '{OrderStatusEnum.ORDERED.value}' status. "
                f"Current status: {order.status}"
            )

        # Validate result value
        if not result_value or not str(result_value).strip():
            raise ValueError("Result value is required")

        # Create result with Draft status
        result = LabTestResult(
            order_id=order_id,
            result_value=result_value,
            technician_notes=technician_notes,
            status=ResultStatusEnum.DRAFT.value
        )
        db.session.add(result)
        db.session.commit()
        return result

    @staticmethod
    def get_result_by_id(result_id):
        """Get a single result by ID"""
        result = LabTestResult.query.get(result_id)
        if not result:
            raise ValueError(f"Result with ID {result_id} not found")
        return result

    @staticmethod
    def get_result_by_order(order_id):
        """Get result(s) for a specific order"""
        order = LabTestOrderController.get_order_by_id(order_id)
        return LabTestResult.query.filter_by(order_id=order_id).all()

    @staticmethod
    def list_all_results():
        """Get all results"""
        return LabTestResult.query.order_by(LabTestResult.created_at.desc()).all()

    @staticmethod
    def list_completed_results():
        """Get all completed results"""
        return LabTestResult.query.filter_by(
            status=ResultStatusEnum.COMPLETED.value
        ).order_by(LabTestResult.created_at.desc()).all()

    @staticmethod
    def update_result(result_id, result_value=None, technician_notes=None):
        """
        Update result details (only for Draft results)
        """
        result = LabTestResultController.get_result_by_id(result_id)

        if result.status != ResultStatusEnum.DRAFT.value:
            raise ValueError(f"Can only update results in Draft status. Current status: {result.status}")

        if result_value is not None:
            if not str(result_value).strip():
                raise ValueError("Result value cannot be empty")
            result.result_value = result_value

        if technician_notes is not None:
            result.technician_notes = technician_notes

        result.updated_at = datetime.utcnow()
        db.session.commit()
        return result

    @staticmethod
    def complete_result(result_id):
        """
        Mark result as Completed
        
        Side Effect:
        - Automatically updates related order status to Completed
        """
        result = LabTestResultController.get_result_by_id(result_id)

        if not result.can_complete():
            raise ValueError(f"Result can only be completed from Draft status. Current status: {result.status}")

        # This will also update the order status
        result.mark_completed()
        return result
