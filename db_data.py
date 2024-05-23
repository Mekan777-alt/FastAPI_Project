import datetime

from config import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD
import psycopg2

try:
    conn = psycopg2.connect(dbname="fastAPI", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO uk_profiles (uuid, photo_path, name, device_token) VALUES (%s, %s, %s, %s)",
                           ('HtDEKpB94SYlSBnszZfDG3Vj2Gs2', 'null', 'UK_NAME', "dpqmvMwUST-gOWVf3KkG8P:APA91bFd8JXPRWf_VUlI7QFNBBTtdLX0_Tkbls_63csq9pbu-JAHDQBV2d6OTldOatfCAeLPxPDe1-7Byaw1gY9X7NUQG26shoU7WL_mh8HcNRmvAnbAY6b8LgYborGsSJv1NtXxXHmi"))

        cursor.execute("INSERT INTO uk_profiles (uuid, photo_path, name, device_token) VALUES (%s, %s, %s, %s)",
                       ('hnBiZATbISeH4k9vTtTmX4sA1LK2', 'null', 'UK_NAME - 2',
                        "dpqmvMwUST-gOWVf3KkG8P:APA91bFd8JXPRWf_VUlI7QFNBBTtdLX0_Tkbls_63csq9pbu-JAHDQBV2d6OTldOatfCAeLPxPDe1-7Byaw1gY9X7NUQG26shoU7WL_mh8HcNRmvAnbAY6b8LgYborGsSJv1NtXxXHmi"))
        conn.commit()
        # cursor.execute("INSERT INTO executor_profiles (uuid, specialization, photo_path) VALUES (%s, %s, %s)",
        #                ('uJd4bz7tRdaYq126edLI4aqLR9I3', 'Cleaning', 'null'))
        # cursor.execute("INSERT INTO executor_profiles (uuid, specialization, photo_path) VALUES (%s, %s, %s)",
        #                ('uajcF2r45nZE6lGZVQsk515zgXE3', 'Electrician', 'null'))
        # cursor.execute("INSERT INTO executor_profiles (uuid, specialization, photo_path) VALUES (%s, %s, %s)",
        #                ('BBEfkzQZVqcMwtiAvViEtdotyNj1', 'Roofer', 'null'))
        # cursor.execute("INSERT INTO executor_profiles (uuid, specialization, photo_path) VALUES (%s, %s, %s)",
        #                ('CTNhKAndVTOXE45KUrzCGMOGDos2', 'Painter', 'null'))
        # cursor.execute("INSERT INTO executor_profiles (uuid, specialization, photo_path) VALUES (%s, %s, %s)",
        #                ('Pyd59B6pARao3ewSFVf2Y1Ov1Co1', 'Plumber', 'null'))
        # conn.commit()
        # cursor.execute("INSERT INTO object_profiles (address, uk_id, object_name, photo_path) VALUES (%s, %s, %s, %s)", ('Object address', 1, 'Object name', 'http://217.25.95.113:8000/static/icons/big/object_main.jpg'))
        # conn.commit()
        # cursor.execute("INSERT INTO apartment_profiles (apartment_name, area, garden, "
        #                "pool, internet_operator, internet_speed, internet_fee, key_holder, object_id) "
        #                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        #                ('122-Floor-2nd floor, Smart, 17', 459.0, True, False, 'mts', 2000, 500.0, 'not', 1))
        # cursor.execute("INSERT INTO apartment_profiles (apartment_name, area, garden, "
        #                "pool, internet_operator, internet_speed, internet_fee, key_holder, object_id) "
        #                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        #                ('122-Floor-2nd floor, Smart, 18', 149.0, False, False, 'Beeline', 1500, 700.0, 'not', 1))
        # cursor.execute("INSERT INTO apartment_profiles (apartment_name, area, garden, "
        #                "pool, internet_operator, internet_speed, internet_fee, key_holder, object_id) "
        #                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        #                ('122-Floor-2nd floor, Smart, 19', 679.0, False, False, 'Megafon', 1889, 800.0, 'not', 1))
        # cursor.execute("INSERT INTO apartment_profiles (apartment_name, area, garden, "
        #                "pool, internet_operator, internet_speed, internet_fee, key_holder, object_id) "
        #                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        #                ('122-Floor-2nd floor, Smart, 120', 913.0, True, True, 'mts', 2500, 300.0, 'not', 1))
        #
        # conn.commit()
        # cursor.execute("INSERT INTO contacts (name, description, phone, email) VALUES (%s, %s, %s, %s)",
        #                ('Unified Contact Center', 'Unified Contact Center', '+7 (495) 150-08-02', 'smart17@sminex.com'))
        #
        # cursor.execute("INSERT INTO contacts (name, description, phone, email) VALUES (%s, %s, %s, %s)",
        #                ('Offers and Feedback', 'If you have any comments or suggestions regarding the quality of '
        #                                        'our services, please write to us', 'null', 'maintenance@sminex.com'))
        #
        # cursor.execute("INSERT INTO contacts (name, description, phone, email) VALUES (%s, %s, %s, %s)",
        #                ('Mobile Application Technical Support', 'Mobile Application Technical Support',
        #                 '+7 (495) 726-67-91', 'support@livenice.com'))
        #
        # conn.commit()

        # cursor.execute("""INSERT INTO tenant_profiles (uuid, photo_path, active_request, balance, device_token)
        # VALUES (%s, %s, %s, %s, %s)""", ("7A9ipzCF4EUVGZeruLCsOXL35j12", 'null', 0, 0, "dpqmvMwUST-gOWVf3KkG8P:APA91bFd8JXPRWf_VUlI7QFNBBTtdLX0_Tkbls_63csq9pbu-JAHDQBV2d6OTldOatfCAeLPxPDe1-7Byaw1gY9X7NUQG26shoU7WL_mh8HcNRmvAnbAY6b8LgYborGsSJv1NtXxXHmi"))
        #
        # conn.commit()
        #
        # cursor.execute("""INSERT INTO tenant_apartments (tenant_id, apartment_id) VALUES (%s, %s)""", (1, 1))
        # cursor.execute("""INSERT INTO tenant_apartments (tenant_id, apartment_id) VALUES (%s, %s)""", (1, 2))
        # conn.commit()

        cursor.execute("""INSERT INTO services (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                           ("Cleaning", "http://217.25.95.113:8000/static/icons/big/cleaning.jpg", "http://217.25.95.113:8000/static/icons/mini/cleaning.jpg"))
        cursor.execute("""INSERT INTO services (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                       ("Gardener", None, "http://217.25.95.113:8000/static/icons/mini/garden.jpg"))
        cursor.execute("""INSERT INTO services (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                       ("Pool", None, "http://217.25.95.113:8000/static/icons/mini/pool.jpg"))
        cursor.execute("""INSERT INTO services (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                       ("Trash removal", None, "http://217.25.95.113:8000/static/icons/mini/trash_removal.jpg"))
        cursor.execute("""INSERT INTO services (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                       ("Other", "http://217.25.95.113:8000/static/icons/big/other.jpg", "http://217.25.95.113:8000/static/icons/mini/other.jpg"))

        conn.commit()

        cursor.execute("""INSERT INTO additional_services_list (name, price, service_id) VALUES (%s, %s, %s)""",
                       ("Window cleaning", 50, 1))
        cursor.execute("""INSERT INTO additional_services_list (name, price, service_id) VALUES (%s, %s, %s)""",
                       ("Ironing", 5, 1))
        cursor.execute("""INSERT INTO additional_services_list (name, price, service_id) VALUES (%s, %s, %s)""",
                       ("Maintenance cleaning", 0, 1))
        cursor.execute("""INSERT INTO additional_services_list (name, price, service_id) VALUES (%s, %s, %s)""",
                       ("Garage cleaning", 0, 1))
        cursor.execute("""INSERT INTO additional_services_list (name, price, service_id) VALUES (%s, %s, %s)""",
                       ("Garden cleaning", 30, 2))
        cursor.execute("""INSERT INTO additional_services_list (name, price, service_id) VALUES (%s, %s, %s)""",
                       ("Pool cleaning", 5, 3))
        cursor.execute("""INSERT INTO additional_services_list (name, price, service_id) VALUES (%s, %s, %s)""",
                       ("Trash removal", 19, 4))

        conn.commit()

        # cursor.execute("""INSERT INTO news (name, description, uk_id, created_at) VALUES (%s, %s, %s, %s)""",
        #                ("Next to the playground, Comfort Services staff have added granite pathways...",
        #                 "Dear property owners and tenants!", 1, datetime.date.today()))
        # cursor.execute("""INSERT INTO news (name, description, uk_id, created_at) VALUES (%s, %s, %s, %s)""",
        #                ("Hot water supply shutdown",
        #                 "Good day, dear owners and tenants of Berzarina 12 clubhouse!...", 1, datetime.date.today()))
        # cursor.execute("""INSERT INTO news (name, description, uk_id, created_at) VALUES (%s, %s, %s, %s)""",
        #                ("New cleaning service from a trusted partner",
        #                 "Dear residents of Berzarina House 12! A new service is now available to you - apartment "
        #                 "cleaning...", 1, datetime.date.today()))
        # cursor.execute("""INSERT INTO news (name, description, uk_id, created_at) VALUES (%s, %s, %s, %s)""",
        #                ("Updating pedestrian pathways",
        #                 "Next to the playground, Comfort Services staff have added granite pathways...", 1,
        #                 datetime.date.today()))

        # conn.commit()
        #
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (1, 1))
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (1, 2))
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (1, 3))
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (1, 4))
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (2, 1))
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (2, 2))
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (2, 3))
        # cursor.execute("""INSERT INTO news_apartments (apartment_id, news_id) VALUES (%s, %s)""",
        #                (2, 4))
        # conn.commit()
        cursor.execute("""INSERT INTO payment_details_uk (recipient_name, inn, kpp, account, bic, correspondent_account, 
        okpo, bank_name, uk_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       ("Recipient", "5250000000", "525000000", "000000000000000000", "000000000000", "00000000000000000000000000",
                        "0000000000", "Bank name", 1))

        cursor.execute("""INSERT INTO payment_details_uk (recipient_name, inn, kpp, account, bic, correspondent_account, 
                okpo, bank_name, uk_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       ("Recipient", "5250000000", "525000000", "000000000000000000", "000000000000",
                        "00000000000000000000000000",
                        "0000000000", "Bank name", 2))
        conn.commit()

        cursor.execute("""INSERT INTO meter_service (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                       ("Water", None, "http://217.25.95.113:8000/static/icons/mini/water.jpg"))
        cursor.execute("""INSERT INTO meter_service (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                       ("Internet", None, "http://217.25.95.113:8000/static/icons/mini/wifi.jpg"))
        cursor.execute("""INSERT INTO meter_service (name, big_icons_path, mini_icons_path) VALUES (%s, %s, %s)""",
                       ("Electricity", "http://217.25.95.113:8000/static/icons/big/electric.jpg", "http://217.25.95.113:8000/static/icons/mini/electric.jpg"))
        conn.commit()

        cursor.close()

        print("done")

    else:

        pass
except Exception as e:
    print(e)
