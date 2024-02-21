from datetime import datetime
from enum import Enum as BaseEnum
from sqlalchemy import DateTime, Column, Float, Boolean, Integer, String, ForeignKey, Enum, TIMESTAMP, UUID
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship

Base: DeclarativeMeta = declarative_base()

class UK(Base):
    __tablename__ = 'uk_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)

    employees = relationship('Employee', back_populates='uk')
    payment_details = relationship('PaymentDetails', back_populates='uk')


class Employee(Base):
    __tablename__ = 'employees'

    uuid = Column(UUID(as_uuid=True), primary_key=True)

    uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
    uk = relationship('UK', back_populates='employees')


class PaymentDetails(Base):
    __tablename__ = 'payment_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_name = Column(String)
    account_number = Column(String)

    uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
    uk = relationship('UK', back_populates='payment_details')


class Object(Base):
    __tablename__ = 'object_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False)

    employees = relationship('Employee', back_populates='object')
    uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
    uk = relationship('UK', back_populates='objects')


class ApartmentProfile(Base):
    __tablename__ = 'apartment_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    apartment_number = Column(String, nullable=False)
    area = Column(Float, nullable=False)
    bathrooms = Column(Integer)
    garden = Column(Boolean)
    pool = Column(Boolean)
    internet_operator = Column(String)
    internet_speed = Column(Integer)
    internet_fee = Column(Float)
    key_holder = Column(String)

    object_id = Column(Integer, ForeignKey('object_profiles.id'))
    object = relationship('Object', back_populates='apartment_profiles')


class InvoiceHistory(Base):
    __tablename__ = 'invoice_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default='не оплачен')
    issue_date = Column(DateTime, default=datetime.utcnow)
    payment_date = Column(DateTime)
    notification_sent = Column(Boolean, default=False)

    performer_id = Column(UUID(as_uuid=True), ForeignKey('performer_profiles.uuid'))
    performer = relationship('PerformerProfile', back_populates='invoices')

    object_id = Column(Integer, ForeignKey('object_profiles.id'))
    object = relationship('Object', back_populates='invoices')


class TenantProfile(Base):
    __tablename__ = 'tenant_profiles'

    uuid = Column(UUID(as_uuid=True), primary_key=True)

    apartment_id = Column(Integer, ForeignKey('apartment_profiles.id'))
    apartment = relationship('ApartmentProfile', back_populates='tenants')
    orders = relationship('Order', back_populates='tenant')


class PerformerProfile(Base):
    __tablename__ = 'performer_profiles'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    contact_name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    bank_details = Column(String, nullable=False)
    orders = relationship('Order', back_populates='performer')


class ServiceType(Base):
    __tablename__ = 'service_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    orders = relationship('Order', back_populates='service_type')


class ServiceDescription(Base):
    __tablename__ = 'service_descriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    count = Column(Integer)
    price = Column(Integer, nullable=False)

    service_id = Column(Integer, ForeignKey("service_type.id"))


class OrderStatus(BaseEnum):
    a = 'получен'
    b = 'обработан УК'
    c = 'передан исполнителю'
    d = 'исполнен'
    e = 'исполнен и оплачен'

    @classmethod
    def get_by_value(cls, value):
        for enum_item in cls:
            if enum_item.value == value:
                return enum_item
        raise ValueError(f"'{value}' is not among the defined enum values.")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey('service_type.id'))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenant_profiles.uuid'))
    performer_id = Column(UUID(as_uuid=True), ForeignKey('performer_profiles.uuid'))
    status = Column(Enum(OrderStatus), name="order_status", nullable=False, default=OrderStatus.a)
    request_date = Column(DateTime, default=datetime.utcnow)
    execution_date = Column(DateTime)

    service = relationship('ServiceType', back_populates='orders')
    tenant = relationship('TenantProfile', back_populates='orders')
    performer = relationship('PerformerProfile', back_populates='orders')


class UserRole(str, BaseEnum):
    TENANT = "Tenant"
    STAFF = "StaffUC"
    PERFORMER = "PerformerUC"


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
