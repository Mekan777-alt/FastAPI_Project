from datetime import datetime
from datetime import date
from sqlalchemy import DateTime, Column, Float, Boolean, Integer, String, ForeignKey, Enum, VARCHAR, DATE
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

    apartments = relationship('ApartmentProfile', back_populates='object')
    news = relationship('News', back_populates='object')
    employees = relationship('EmployeeUK', back_populates='object')


class ApartmentProfile(Base):
    __tablename__ = 'apartment_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    apartment_name = Column(String, nullable=False)
    area = Column(Float, nullable=False)
    bathrooms = Column(Integer)
    garden = Column(Boolean)
    pool = Column(Boolean)
    internet_operator = Column(String)
    internet_speed = Column(Integer)
    internet_fee = Column(Float)
    key_holder = Column(String)
    object_id = Column(Integer, ForeignKey('object_profiles.id'))
    object = relationship('Object', back_populates='apartments')

    tenant_apartments = relationship('TenantApartments', back_populates='apartment')


class ExecutorsProfile(Base):
    __tablename__ = 'executor_profiles'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(100), unique=True)
    specialization = Column(String, nullable=False)
    photo_path = Column(String, nullable=True)
    bank_details_id = Column(Integer, ForeignKey('bank_detail_executors.id'))

    bank_details = relationship('BankDetailExecutors', back_populates='executors')
    invoices = relationship('InvoiceHistory', back_populates='performer')


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
    status = Column(String, default='не оплачен')
    issue_date = Column(DateTime, default=datetime.utcnow)
    payment_date = Column(DateTime)
    notification_sent = Column(Boolean, default=False)
    performer_id = Column(Integer, ForeignKey('executor_profiles.id'))
    performer = relationship('ExecutorsProfile', back_populates='invoices', foreign_keys=[performer_id])
    object_id = Column(Integer, ForeignKey('object_profiles.id'))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class TenantProfile(Base):
    __tablename__ = 'tenant_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(VARCHAR(100))
    photo_path = Column(String, nullable=True)
    active_request = Column(Integer, default=0)
    balance = Column(Float, default=0.0)

    tenant_apartment = relationship('TenantApartments', back_populates='tenant')


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

    additional_services_list = relationship("AdditionalServiceList", back_populates="service")
    orders = relationship("Order", back_populates="selected_service")


class AdditionalService(Base):
    __tablename__ = 'additional_services'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    name = Column(VARCHAR(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=True)


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
    address = Column(String, nullable=False)
    completion_date = Column(VARCHAR(20), nullable=False)
    completion_time = Column(VARCHAR(20), nullable=False)
    notes = Column(String, nullable=True)
    status = Column(String, nullable=False)
    selected_service_id = Column(Integer, ForeignKey('services.id'))

    selected_service = relationship("Service", foreign_keys=[selected_service_id], back_populates="orders")
    additional_services = relationship("AdditionalService", back_populates="order")
    documents = relationship("Document", back_populates="order")


AdditionalService.order = relationship("Order", back_populates="additional_services")
Document.order = relationship("Order", back_populates="documents")


class AdditionalServiceList(Base):
    __tablename__ = 'additional_services_list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    price = Column(Integer)
    service_id = Column(Integer, ForeignKey(Service.id))

    service = relationship("Service", back_populates="additional_services_list")


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
