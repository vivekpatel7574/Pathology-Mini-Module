"""
Database models for Pathology mini-module
Using SQLAlchemy ORM with MariaDB/MySQL backend
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum as PyEnum

db = SQLAlchemy()


class OrderStatusEnum(PyEnum):
    """Order status workflow enumeration"""
    DRAFT = "Draft"
    ORDERED = "Ordered"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ResultStatusEnum(PyEnum):
    """Result status workflow enumeration"""
    DRAFT = "Draft"
    COMPLETED = "Completed"


class PathologyTest(db.Model):
    """
    Test Master - Pathology tests available in the lab
    """
    __tablename__ = 'pathology_test'

    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), nullable=False, unique=True)
    test_code = db.Column(db.String(20), nullable=False, unique=True)
    sample_type = db.Column(db.String(50), nullable=False)  # e.g., Blood, Urine, etc.
    normal_range = db.Column(db.String(100), nullable=False)  # e.g., 4.5-11.0 (10^9/L)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lab_orders = db.relationship('LabTestOrder', backref='test', lazy=True)

    def __repr__(self):
        return f"<PathologyTest {self.test_code}: {self.test_name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'test_name': self.test_name,
            'test_code': self.test_code,
            'sample_type': self.sample_type,
            'normal_range': self.normal_range,
            'price': float(self.price),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }


class NamingSeries(db.Model):
    """
    Naming series for auto-generating Order IDs
    """
    __tablename__ = 'naming_series'

    id = db.Column(db.Integer, primary_key=True)
    series_name = db.Column(db.String(50), unique=True, nullable=False)
    series_prefix = db.Column(db.String(10), nullable=False)
    current_number = db.Column(db.Integer, default=1000, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_next_name(self):
        """Generate and return the next series name"""
        self.current_number += 1
        db.session.commit()
        return f"{self.series_prefix}{self.current_number}"

    def __repr__(self):
        return f"<NamingSeries {self.series_name}: {self.series_prefix}{self.current_number}>"


class LabTestOrder(db.Model):
    """
    Lab Test Order - Orders placed for pathology tests
    """
    __tablename__ = 'lab_test_order'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_phone = db.Column(db.String(15), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('pathology_test.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default=OrderStatusEnum.DRAFT.value, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_results = db.relationship('LabTestResult', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<LabTestOrder {self.order_id}: {self.patient_name} - {self.status}>"

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'patient_name': self.patient_name,
            'patient_phone': self.patient_phone,
            'test_id': self.test_id,
            'test_name': self.test.test_name if self.test else None,
            'order_date': self.order_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }

    def can_create_result(self):
        """Check if result can be created for this order"""
        return self.status == OrderStatusEnum.ORDERED.value

    def can_transition_to(self, new_status):
        """Validate status transition"""
        current = self.status
        valid_transitions = {
            OrderStatusEnum.DRAFT.value: [OrderStatusEnum.ORDERED.value, OrderStatusEnum.CANCELLED.value],
            OrderStatusEnum.ORDERED.value: [OrderStatusEnum.COMPLETED.value, OrderStatusEnum.CANCELLED.value],
            OrderStatusEnum.COMPLETED.value: [],  # Cannot transition from Completed
            OrderStatusEnum.CANCELLED.value: [],  # Cannot transition from Cancelled
        }
        return new_status in valid_transitions.get(current, [])


class LabTestResult(db.Model):
    """
    Lab Test Result - Results entered for completed tests
    """
    __tablename__ = 'lab_test_result'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('lab_test_order.id'), nullable=False)
    result_value = db.Column(db.String(100), nullable=False)
    technician_notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default=ResultStatusEnum.DRAFT.value, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LabTestResult Order:{self.order_id} - {self.status}>"

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'result_value': self.result_value,
            'technician_notes': self.technician_notes,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def can_complete(self):
        """Check if result can be marked as completed"""
        return self.status == ResultStatusEnum.DRAFT.value

    def mark_completed(self):
        """Mark result as completed and update related order"""
        if not self.can_complete():
            raise ValueError("Result can only be completed from Draft status")
        
        self.status = ResultStatusEnum.COMPLETED.value
        self.updated_at = datetime.utcnow()
        
        # Update order status to Completed
        if self.order:
            self.order.status = OrderStatusEnum.COMPLETED.value
            self.order.updated_at = datetime.utcnow()
        
        db.session.commit()
