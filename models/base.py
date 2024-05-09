from datetime import datetime
from datetime import date, time
from enum import Enum
from sqlalchemy import DateTime, Column, Float, Boolean, Integer, String, ForeignKey, VARCHAR, DATE, TIME
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class UK(Base):
    __tablename__ = 'uk_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, unique=True)
    photo_path = Column(String, nullable=True, default=None)
    name = Column(String)
    employees = relationship('EmployeeUK', back_populates='uk')
    payment_details = relationship('PaymentDetails', back_populates='uk')
    objects = relationship('Object', back_populates='uk')


class EmployeeUK(Base):
    __tablename__ = 'uk_employees'

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    photo_path = Column(String, nullable=True, default=None)
    is_admin = Column(Boolean, default=False)
    uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
    object_id = Column(Integer, ForeignKey('object_profiles.id'))

    uk = relationship('UK', back_populates='employees')
    object = relationship('Object', back_populates='employees')

    def to_dict(self):
        return {
            'id': self.id,
            'photo_path': self.photo_path,
            'is_admin': self.is_admin,
            'object_id': self.object_id
        }


class PaymentDetails(Base):
    __tablename__ = 'payment_details_uk'
    id = Column(Integer, primary_key=True)
    recipient_name = Column(String, nullable=False)
    inn = Column(String, nullable=False)
    kpp = Column(String, nullable=False)
    account = Column(String, nullable=False)
    bic = Column(String, nullable=False)
    correspondent_account = Column(String, nullable=False)
    okpo = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)

    uk_id = Column(Integer, ForeignKey("uk_profiles.id", ondelete="CASCADE"))
    uk = relationship('UK', back_populates='payment_details')


class Object(Base):
    __tablename__ = 'object_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    object_name = Column(String, nullable=True)
    address = Column(String, nullable=False)
    uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
    uk = relationship('UK', back_populates='objects')
    photo_path = Column(String)

    apartments = relationship('ApartmentProfile', back_populates='object')
    news = relationship('News', back_populates='object')
    employees = relationship('EmployeeUK', back_populates='object')
    service_list_object = relationship('ServiceObjectList', back_populates='object')


class ApartmentProfile(Base):
    __tablename__ = 'apartment_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    apartment_name = Column(String, nullable=False)
    area = Column(Float, nullable=False)
    garden = Column(Boolean)
    pool = Column(Boolean)
    internet_operator = Column(String)
    internet_speed = Column(Integer)
    internet_fee = Column(Float)
    key_holder = Column(String)
    object_id = Column(Integer, ForeignKey('object_profiles.id'))
    object = relationship('Object', back_populates='apartments')

    tenant_apartments = relationship('TenantApartments', back_populates='apartment')
    orders = relationship('Order', back_populates='apartments')
    bathroom_apartments = relationship('BathroomApartment', back_populates='apartments')
    meters = relationship("Meters", back_populates="apartment")
    invoice_history = relationship("InvoiceHistory", back_populates="apartment")
    guest_pass = relationship("GuestPass", back_populates="apartment")

    def to_dict(self):
        return {
            "id": self.id,
            "apartment_name": self.apartment_name,
            "area": self.area,
            "garden": self.garden,
            "pool": self.pool,
            "internet_operator": self.internet_operator,
            "internet_speed": str(self.internet_speed),
            "internet_fee": str(self.internet_fee),
            "key_holder": self.key_holder
        }


class ExecutorsProfile(Base):
    __tablename__ = 'executor_profiles'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(100), unique=True)
    specialization = Column(String, nullable=False)
    photo_path = Column(String, nullable=True)
    bank_details_id = Column(Integer, ForeignKey('bank_detail_executors.id'))

    bank_details = relationship('BankDetailExecutors', back_populates='executors')
    executor_order = relationship('ExecutorOrders', back_populates='executor')


class BankDetailExecutors(Base):
    __tablename__ = 'bank_detail_executors'
    id = Column(Integer, primary_key=True)
    recipient_name = Column(String, nullable=False)
    account = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    purpose_of_payment = Column(String, nullable=False)
    bic = Column(String, nullable=False)
    correspondent_account = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    inn = Column(String, nullable=False)
    kpp = Column(String, nullable=False)

    executors = relationship('ExecutorsProfile', back_populates='bank_details')


class InvoiceHistory(Base):
    __tablename__ = 'invoice_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default='not paid')
    issue_date = Column(DateTime, default=datetime.utcnow)
    payment_date = Column(DateTime)
    photo_path = Column(String)
    notification_sent = Column(Boolean, default=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    apartment_id = Column(Integer, ForeignKey(ApartmentProfile.id))
    comment = Column(String)
    service_id = Column(Integer, ForeignKey('services.id'))
    meter_service_id = Column(Integer, ForeignKey('meter_service.id'))
    bill_number = Column(String)

    apartment = relationship('ApartmentProfile', back_populates='invoice_history')
    service = relationship('Service', back_populates='invoice_history')
    meter_service = relationship('MeterService', back_populates='invoice_history')

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "status": self.status,
            "apartment_id": self.apartment_id
        }


class TenantProfile(Base):
    __tablename__ = 'tenant_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(VARCHAR(100))
    photo_path = Column(String, nullable=True)
    active_request = Column(Integer, default=0)
    balance = Column(Float, default=0.0)

    tenant_apartment = relationship('TenantApartments', back_populates='tenant')

    def to_dict(self):
        return {
            "id": self.id,
            "active_request": self.active_request,
            "balance": self.balance
        }


class TenantApartments(Base):
    __tablename__ = 'tenant_apartments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey(TenantProfile.id))
    apartment_id = Column(Integer, ForeignKey(ApartmentProfile.id))

    tenant = relationship('TenantProfile', back_populates='tenant_apartment')
    apartment = relationship('ApartmentProfile', back_populates='tenant_apartments')


class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    big_icons_path = Column(String)
    mini_icons_path = Column(String)

    additional_services_list = relationship("AdditionalServiceList", back_populates="service")
    orders = relationship("Order", back_populates="selected_service")
    service_list_service = relationship("ServiceObjectList", back_populates="service")
    invoice_history = relationship("InvoiceHistory", back_populates="service")


class ServiceObjectList(Base):
    __tablename__ = 'service_objects_list'

    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, ForeignKey(Object.id))
    service_id = Column(Integer, ForeignKey(Service.id))

    object = relationship("Object", back_populates="service_list_object")
    service = relationship("Service", back_populates="service_list_service")


class AdditionalService(Base):
    __tablename__ = 'additional_services'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    additional_service_id = Column(Integer, ForeignKey('additional_services_list.id'))
    quantity = Column(Integer, nullable=True)

    # order = relationship("Order", back_populates="additional_services")
    # service = relationship("Service", back_populates="additional_services")
    additional_service = relationship("AdditionalServiceList", back_populates="additional_services_list")


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenant_profiles.id'))
    apartment_id = Column(Integer, ForeignKey(ApartmentProfile.id))
    completion_date = Column(VARCHAR(20), nullable=False)
    completion_time = Column(VARCHAR(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    status = Column(String, nullable=False)
    selected_service_id = Column(Integer, ForeignKey('services.id'))

    apartments = relationship("ApartmentProfile", back_populates="orders")
    selected_service = relationship("Service", foreign_keys=[selected_service_id], back_populates="orders")
    additional_services = relationship("AdditionalService", back_populates="order")
    documents = relationship("Document", back_populates="order")
    executor_order = relationship("ExecutorOrders", back_populates="order")


AdditionalService.order = relationship("Order", back_populates="additional_services")
Document.order = relationship("Order", back_populates="documents")


class AdditionalServiceList(Base):
    __tablename__ = 'additional_services_list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    price = Column(Integer)
    service_id = Column(Integer, ForeignKey(Service.id))

    service = relationship("Service", back_populates="additional_services_list")
    additional_services_list = relationship("AdditionalService", back_populates="additional_service")


class Contacts(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    description = Column(VARCHAR(100), nullable=False)
    phone = Column(VARCHAR(100), nullable=True)
    email = Column(VARCHAR(100), nullable=True)


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_at = Column(DATE, default=date.today())
    object_id = Column(Integer, ForeignKey(Object.id))

    object = relationship('Object', back_populates="news")


class ExecutorOrders(Base):
    __tablename__ = 'orders_executors'

    id = Column(Integer, primary_key=True)
    executor_id = Column(Integer, ForeignKey(ExecutorsProfile.id), unique=True)
    order_id = Column(Integer, ForeignKey(Order.id), unique=True)

    order = relationship("Order", back_populates="executor_order")
    executor = relationship("ExecutorsProfile", back_populates="executor_order")


class BathroomApartment(Base):
    __tablename__ = 'bathroom_apartments'

    id = Column(Integer, primary_key=True)
    characteristic = Column(String)
    apartment_id = Column(Integer, ForeignKey(ApartmentProfile.id))

    apartments = relationship("ApartmentProfile", back_populates="bathroom_apartments")

    def to_dict(self):
        return {
            "id": self.id,
            "characteristic": self.characteristic,
            "apartment_id": self.apartment_id
        }


class MeterService(Base):
    __tablename__ = 'meter_service'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    big_icons_path = Column(String)
    mini_icons_path = Column(String)

    meters = relationship("Meters", back_populates="meter_service")
    invoice_history = relationship("InvoiceHistory", back_populates="meter_service")


class Meters(Base):
    __tablename__ = 'meters'

    id = Column(Integer, primary_key=True)
    apartment_id = Column(Integer, ForeignKey(ApartmentProfile.id))
    meter_service_id = Column(Integer, ForeignKey(MeterService.id))
    bill_number = Column(String)
    meters_for = Column(String)
    meter_readings = Column(String)
    comment = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    apartment = relationship("ApartmentProfile", back_populates="meters")
    meter_service = relationship("MeterService", back_populates="meters")

    def to_dict(self):
        return {
            "id": self.id,
            "apartment_id": self.apartment_id,
            "meter_service_id": self.meter_service_id,
            "bill_number": self.bill_number,
            "status": self.status
        }


class GuestPass(Base):
    __tablename__ = 'guest_pass'

    id = Column(Integer, primary_key=True)
    visit_date = Column(DATE)
    visit_time = Column(TIME)
    full_name = Column(String)
    apartment_id = Column(Integer, ForeignKey(ApartmentProfile.id))
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    apartment = relationship("ApartmentProfile", back_populates="guest_pass")
    guest_pass = relationship("GuestPassDocuments", back_populates="guest_pass_doc")

    def to_dict(self):
        return {
            "id": self.id,
            "visit_date": self.visit_date,
            "visit_time": self.visit_time,
            "full_name": self.full_name,
            "apartment_id": self.apartment_id,
            "note": self.note
        }


class GuestPassDocuments(Base):
    __tablename__ = 'guest_pass_documents'

    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    mime_type = Column(String)
    file_path = Column(String)
    guest_pass_id = Column(Integer, ForeignKey(GuestPass.id))

    guest_pass_doc = relationship("GuestPass", back_populates="guest_pass")

    def to_dict(self):

        return {
            "id": self.id,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_path": self.file_path,
            "guest_pass_id": self.guest_pass_id
        }
