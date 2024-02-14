from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, \
    UUID, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ProfileManagementCompany(Base):
    __tablename__ = 'profile_management_company'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    company_name = Column(String(250), nullable=False)
    photo = Column(String(250))
    login = Column(String(50))
    password_hash = Column(String(150))
    staff = relationship('StaffManagementCompany', back_populates='profile')
    requisites = relationship('RequisitesManagementCompany', back_populates='profile')


class StaffManagementCompany(Base):
    __tablename__ = 'staff_management_company'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    phone_number = Column(String(20))
    email = Column(String(30))
    company_uuid = Column(String, ForeignKey('profile_management_company.uuid'))
    object_uuid = Column(String, ForeignKey('object_management_company.uuid'))
    profile = relationship('ProfileManagementCompany', back_populates='staff')
    object_staff = relationship('ObjectManagementCompany', back_populates='staff')


class RequisitesManagementCompany(Base):
    __tablename__ = 'requisites_management_company'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    recipient = Column(String(200))
    inn = Column(String(100))
    kpp = Column(String(100))
    bank_account = Column(String(100))
    bic = Column(String(50))
    correspondent_account = Column(String(100))
    okpo = Column(String(100))
    bank_name = Column(String(100))
    profile_id = Column(String, ForeignKey('profile_management_company.uuid'))
    profile = relationship('ProfileManagementCompany', back_populates='requisites')


class ObjectManagementCompany(Base):
    __tablename__ = 'object_management_company'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    address = Column(String(250))
    staff = relationship('StaffManagementCompany', back_populates='object_staff')
    profile_of_apartments = relationship('ProfileOfApartments', back_populates='object')


class ObjectServiceStaff(Base):
    __tablename__ = 'object_service_staff'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    object_uuid = Column(UUID(as_uuid=True), ForeignKey('object_management_company.uuid', ondelete='CASCADE'))

    object = relationship('ObjectManagementCompany', back_populates='staff')


class ProfileOfApartments(Base):
    __tablename__ = 'profile_of_apartments'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    number_apartment = Column(Integer)
    area = Column(Float(precision=4))
    bathroom_count = Column(Integer)
    is_garden = Column(Boolean)
    is_pool = Column(Boolean)
    internet_operator = Column(String(100))
    internet_speed = Column(String(25))
    internet_price = Column(Float)
    key_holder = Column(String(100))
    object_uuid = Column(String, ForeignKey('object_management_company.uuid'))
    object = relationship('ObjectManagementCompany', back_populates='profile_of_apartments')
    tenants = relationship('ProfileTenant', back_populates='apartment')


class ProfileTenant(Base):
    __tablename__ = 'profile_tenant'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    master_tenant = Column(Boolean, nullable=False)
    firstname = Column(String(100))
    lastname = Column(String(100))
    patronymic = Column(String(100))
    phone_number = Column(String(20))
    email = Column(String(20))
    login = Column(String(50))
    password_hash = Column(String(100))
    apartment_id = Column(String, ForeignKey('profile_of_apartments.uuid'))
    apartment = relationship('ProfileOfApartments', back_populates='tenants')

class ProfilePerformer(Base):
    __tablename__ = 'profile_performer'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    fullname = Column(String(100), nullable=False)
    photo = Column(String(100))
    phone_number = Column(String(20), nullable=False)
    email = Column(String(20), nullable=False)
    is_legal = Column(Boolean, nullable=False)
    specializations = relationship('PerformerSpecializations', back_populates='performer')
    requisites = relationship('RequisitesPerformer', back_populates='performer')


class PerformerSpecializations(Base):
    __tablename__ = 'performer_specializations'

    performer_uuid = Column(UUID, ForeignKey('profile_performer.uuid'), primary_key=True)
    specialization = Column(String(50), primary_key=True)
    performer = relationship('ProfilePerformer', back_populates='specializations')


class RequisitesPerformer(Base):
    __tablename__ = 'requisites_performer'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    recipient = Column(String(200))
    inn = Column(String(100))
    kpp = Column(String(100))
    bank_account = Column(String(100))
    bic = Column(String(50))
    correspondent_account = Column(String(100))
    okpo = Column(String(100))
    bank_name = Column(String(100))
    performer_id = Column(String, ForeignKey('profile_performer.uuid'))
    performer = relationship('ProfilePerformer', back_populates='requisites')


class PaymentHistory(Base):
    __tablename__ = 'payment_history'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    creation_date = Column(DateTime)
    amount = Column(Float)
    bill_type = Column(String(50))
    is_paid = Column(Boolean)
    tenant_id = Column(String, ForeignKey('profile_tenant.uuid'))
    staff_id = Column(String, ForeignKey('staff_management_company.uuid'))


class MeterReadings(Base):
    __tablename__ = 'meter_readings'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    type_meters = Column(String(50))
    reading_date = Column(DateTime, nullable=False)
    electricity_reading = Column(Float)
    water_reading = Column(Float)
    staff_id = Column(String, ForeignKey('staff_management_company.uuid'))
    tenant_id = Column(String, ForeignKey('profile_tenant.uuid'))


class ServiceOrder(Base):
    __tablename__ = 'service_order'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    service_type = Column(String(50), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    execution_date = Column(DateTime)
    status = Column(String(50), default='Получен')
    total_cost = Column(DECIMAL(10, 2))
    commission_rate = Column(DECIMAL(4, 2), default=0.15)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('profile_tenant.uuid', ondelete='CASCADE'))
    performer_id = Column(UUID(as_uuid=True), ForeignKey('profile_performer.uuid', ondelete='CASCADE'))

    tenant = relationship('ProfileTenant', back_populates='service_orders')
    performer = relationship('ProfilePerformer', back_populates='service_orders')


class ServicePricelist(Base):
    __tablename__ = 'service_pricelist'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    service_type = Column(String(50), nullable=False)
    object_uuid = Column(UUID(as_uuid=True), ForeignKey('object_management_company.uuid', ondelete='CASCADE'))
    price = Column(DECIMAL(10, 2))

    __table_args__ = (
        UniqueConstraint('service_type', 'object_uuid'),
    )

    object = relationship('ObjectManagementCompany', back_populates='service_pricelist')
