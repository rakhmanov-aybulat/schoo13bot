from typing import List


class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn = conn

    async def add_user(self, chat_id, first_name, last_name, user_name) -> None:
        with self.conn as conn:
            with conn.cursor() as cursor:  
                cursor.execute(
                    '''INSERT INTO users(chatid, firstname, lastname, username) 
                    VALUES (%s, %s, %s, %s);''',
                    (chat_id, first_name, last_name, user_name))
                  
        return

    async def update_user(self, chat_id, first_name, last_name, user_name) -> None:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''UPDATE users SET 
                        firstname = %s,
                        lastname = %s,
                        username = %s
                        WHERE chatid = %s;''',
                    (first_name, last_name, user_name, chat_id))

        return

    async def get_grade_numbers_list(self) -> List[int]:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT DISTINCT gradenumber 
                    FROM grades 
                    ORDER BY gradenumber ASC;
                    ''')

                return cursor.fetchall()

    async def get_grade_letter_list(self, grade_number: int) -> List[str]:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT gradeletter 
                    FROM grades
                    WHERE gradenumber = %s;
                    ''', (grade_number,))

                return cursor.fetchall()

    async def has_user_grade(self, chat_id: int) -> bool:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT gradenumber
                    FROM users
                    WHERE chatid = %s;
                    ''', (chat_id,))
                return cursor.fetchone()[0] is not None

    async def add_user_grade(self, chat_id, grade_number, grade_letter) -> None:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''UPDATE users SET 
                        gradenumber = %s,
                        gradeletter = %s
                        WHERE chatid = %s;''',
                    (grade_number, grade_letter, chat_id))
