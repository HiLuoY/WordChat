from database.db_utils import get_db_connection

class User:
    @staticmethod
    def create_user(email, password, nickname):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Users (email, password, nickname, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                """
                cursor.execute(sql, (email, password, nickname))
                connection.commit()
                return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def get_user_by_email(email):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Users WHERE email = %s"
                cursor.execute(sql, (email,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        finally:
            connection.close()