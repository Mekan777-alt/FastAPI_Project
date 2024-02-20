from datetime import datetime
from enum import Enum as BaseEnum

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import DateTime, Column, Float, Boolean, Integer, String, ForeignKey, Enum, UUID, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import mapped_column, Mapped

Base: DeclarativeMeta = declarative_base()


# class UK(Base):
#     __tablename__ = 'uk_profiles'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     login = Column(String, nullable=False)
#     password = Column(String, nullable=False)
#
#     # Один ко многим: УК может иметь много сотрудников
#     employees = relationship('Employee', back_populates='uk')
#
#     # Один ко многим: УК может иметь много платежных реквизитов
#     payment_details = relationship('PaymentDetails', back_populates='uk')
#
#
# class Employee(Base):
#     __tablename__ = 'employees'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     lastname = Column(String)
#     phone = Column(String)
#     email = Column(String)
#
#     uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
#     uk = relationship('UK', back_populates='employees')
#
#
# class PaymentDetails(Base):
#     __tablename__ = 'payment_details'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     bank_name = Column(String)
#     account_number = Column(String)
#
#     uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
#     uk = relationship('UK', back_populates='payment_details')
#
#
# class Object(Base):
#     __tablename__ = 'object_profiles'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     address = Column(String, nullable=False)
#
#     employees = relationship('Employee', back_populates='object')
#
#     service_personnel = relationship('ServicePersonnel', back_populates='object')
#
#     uk_id = Column(Integer, ForeignKey('uk_profiles.id'))
#     uk = relationship('UK', back_populates='objects')
#
#
# class ServicePersonnel(Base):
#     __tablename__ = 'service_personnel'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     phone = Column(String)
#     email = Column(String)
#
#     object_id = Column(Integer, ForeignKey('object_profiles.id'))
#     object = relationship('Object', back_populates='service_personnel')
#
#
# class ApartmentProfile(Base):
#     __tablename__ = 'apartment_profiles'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     apartment_number = Column(String, nullable=False)
#     area = Column(Float, nullable=False)
#     bathrooms = Column(Integer)
#     garden = Column(Boolean)
#     pool = Column(Boolean)
#     internet_operator = Column(String)
#     internet_speed = Column(Integer)
#     internet_fee = Column(Float)
#     key_holder = Column(String)
#
#     # Многие к одному: Профиль апартаментов принадлежит к одному объекту
#     object_id = Column(Integer, ForeignKey('object_profiles.id'))
#     object = relationship('Object', back_populates='apartment_profiles')
#
#
# # Добавим отношение к модели "Объект" для хранения профилей апартаментов и жильцов
# Object.apartment_profiles = relationship('ApartmentProfile', back_populates='object')
# Object.tenants = relationship('TenantProfile', back_populates='object')
#
#
# class InvoiceHistory(Base):
#     __tablename__ = 'invoice_history'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     amount = Column(Float, nullable=False)
#     status = Column(String, default='не оплачен')  # Статус: "оплачен" или "не оплачен"
#     issue_date = Column(DateTime, default=datetime.utcnow)
#     payment_date = Column(DateTime)
#     notification_sent = Column(Boolean, default=False)  # Флаг для уведомления жильцов
#
#     # Многие к одному: История счетов принадлежит к одному профилю исполнителя
#     performer_id = Column(Integer, ForeignKey('performer_profiles.id'))
#     performer = relationship('PerformerProfile', back_populates='invoices')
#
#     # Многие к одному: История счетов принадлежит к одному объекту
#     object_id = Column(Integer, ForeignKey('object_profiles.id'))
#     object = relationship('Object', back_populates='invoices')
#
#
# class MeterReading(Base):
#     __tablename__ = 'meter_readings'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     value = Column(Float, nullable=False)
#     reading_date = Column(DateTime, default=datetime.utcnow)
#
#     # Многие к одному: Показания счетчиков принадлежат к одному объекту
#     object_id = Column(Integer, ForeignKey('object_profiles.id'))
#     object = relationship('Object', back_populates='meter_readings')
#
#
# class Payment(Base):
#     __tablename__ = 'payments'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     amount = Column(Float, nullable=False)
#     payment_date = Column(DateTime, default=datetime.utcnow)
#     commission_fee = Column(Float, nullable=False, default=0.0)
#     service_fee = Column(Float, nullable=False, default=0.0)
#     payment_method = Column(String)  # Метод оплаты, например, "Stripe"
#     payment_status = Column(String, default='оплачен')  # Статус: "оплачен" или "не оплачен"
#
#     # Многие к одному: Оплата принадлежит к одному профилю жильца
#     tenant_id = Column(Integer, ForeignKey('tenant_profiles.id'))
#     tenant = relationship('TenantProfile', back_populates='payments')
#
#     # Многие к одному: Оплата принадлежит к одному счету
#     invoice_id = Column(Integer, ForeignKey('invoice_history.id'))
#     invoice = relationship('InvoiceHistory', back_populates='payments')
#
#
# class ChatMessage(Base):
#     __tablename__ = 'chat_messages'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     sender_id = Column(Integer, ForeignKey('user_profiles.id'))
#     receiver_id = Column(Integer, ForeignKey('user_profiles.id'))
#     content = Column(String, nullable=False)
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     is_read = Column(Boolean, default=False)
#
#     # Многие к одному: Сообщение принадлежит к одному отправителю
#     sender = relationship('UserProfile', foreign_keys=[sender_id], back_populates='sent_messages')
#
#     # Многие к одному: Сообщение принадлежит к одному получателю
#     receiver = relationship('UserProfile', foreign_keys=[receiver_id], back_populates='received_messages')
#
#
# class TenantProfile(Base):
#     __tablename__ = 'tenant_profiles'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     phone = Column(String)
#     email = Column(String)
#     is_master = Column(Boolean, default=False)
#     login = Column(String, nullable=False)
#     password = Column(String, nullable=False)
#
#     apartment_id = Column(Integer, ForeignKey('apartment_profiles.id'))
#     apartment = relationship('ApartmentProfile', back_populates='tenants')
#     orders = relationship('Order', back_populates='tenant')
#
#
# class UserProfile(Base):
#     __tablename__ = 'user_profiles'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_type = Column(String, nullable=False)  # 'УК' или 'Жилец'
#     name = Column(String, nullable=False)
#     phone = Column(String)
#     email = Column(String)
#
#     # Один к многим: УК может отправлять много сообщений
#     sent_messages = relationship('ChatMessage', foreign_keys=[ChatMessage.sender_id], back_populates='sender')
#
#     # Один к многим: УК может принимать много сообщений
#     received_messages = relationship('ChatMessage', foreign_keys=[ChatMessage.receiver_id], back_populates='receiver')
#     # Один ко многим: Диспетчер отправил много заказов
#     dispatched_orders = relationship('Order', back_populates='dispatcher')
#
#
# class PerformerProfile(Base):
#     __tablename__ = 'performer_profiles'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     contact_name = Column(String, nullable=False)
#     specialization = Column(String, nullable=False)
#     bank_details = Column(String, nullable=False)
#     # Один ко многим: Исполнитель выполнил много заказов
#     orders = relationship('Order', back_populates='performer')
#
#
# class Service(Base):
#     __tablename__ = 'services'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     description = Column(String)
#     price = Column(Float, nullable=False)
#
#     # Один ко многим: Услуга может быть частью множества заказов
#     orders = relationship('Order', back_populates='service')
#
#
# class OrderStatus(BaseEnum):
#     a = 'получен'
#     b = 'обработан УК'
#     c = 'передан исполнителю'
#     d = 'исполнен'
#     e = 'исполнен и оплачен'
#
#     @classmethod
#     def get_by_value(cls, value):
#         for enum_item in cls:
#             if enum_item.value == value:
#                 return enum_item
#         raise ValueError(f"'{value}' is not among the defined enum values.")
#
#
# class Order(Base):
#     __tablename__ = 'orders'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     service_id = Column(Integer, ForeignKey('services.id'))
#     tenant_id = Column(Integer, ForeignKey('tenant_profiles.id'))
#     dispatcher_id = Column(Integer, ForeignKey('user_profiles.id'))
#     performer_id = Column(Integer, ForeignKey('performer_profiles.id'))
#     status = Column(Enum(OrderStatus), name="order_status", nullable=False, default=OrderStatus.a)
#     request_date = Column(DateTime, default=datetime.utcnow)
#     execution_date = Column(DateTime)
#
#     # Многие к одному: Заказ принадлежит к одной услуге
#     service = relationship('Service', back_populates='orders')
#
#     # Многие к одному: Заказ принадлежит к одному жильцу
#     tenant = relationship('TenantProfile', back_populates='orders')
#
#     # Многие к одному: Заказ принадлежит к одному диспетчеру
#     dispatcher = relationship('UserProfile', foreign_keys=[dispatcher_id], back_populates='dispatched_orders')
#
#     # Многие к одному: Заказ принадлежит к одному исполнителю
#     performer = relationship('PerformerProfile', back_populates='orders')
#
#
# # Добавим отношение к модели "Объект" для хранения показаний счетчиков
# Object.meter_readings = relationship('MeterReading', back_populates='object')
#
# # Добавим отношение к модели "Профиль жильца" для хранения оплат
# TenantProfile.payments = relationship('Payment', back_populates='tenant')
# # Добавим отношение к модели "Профиль исполнителя" для хранения истории счетов
# PerformerProfile.invoices = relationship('InvoiceHistory', back_populates='performer')


class UserRole(str, BaseEnum):
    TENANT = "Tenant"
    STAFF = "StaffUC"
    PERFORMER = "PerformerUC"


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class User(Base):
    __tablename__ = 'user'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, unique=True, nullable=False)
    lastname = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    role_id = Column(Integer, ForeignKey(Role.id), nullable=False)
