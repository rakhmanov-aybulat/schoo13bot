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

    async def list_users(self) -> List[int]:
        """List all bot users"""
        return [
            # row[0]
            # async for row in self.conn.execute(
            #     "select userid from tg_users",
            # )
        ]
