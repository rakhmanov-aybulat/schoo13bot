import datetime
from typing import List


class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn = conn

    async def add_user(
            self, chat_id, first_name,
            last_name, user_name) -> None:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    INSERT INTO users(chat_id, first_name,
                    last_name, username)
                    VALUES (%s, %s, %s, %s);
                    ''',
                    (chat_id, first_name,
                     last_name, user_name))

        return

    async def update_user(
            self, chat_id, first_name,
            last_name, user_name) -> None:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    UPDATE users SET
                    first_name = %s,
                    last_name = %s,
                    username = %s
                    WHERE chat_id = %s;
                    ''', (first_name, last_name,
                          user_name, chat_id))

        return

    async def get_grade_numbers_list(self) -> List[int]:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT DISTINCT grade_number
                    FROM grades
                    ORDER BY grade_number ASC;
                    ''')
                return cursor.fetchall()

    async def get_grade_letter_list(self, grade_number: int) -> List[str]:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT grade_letter
                    FROM grades
                    WHERE grade_number = %s;
                    ''', (grade_number,))

                return cursor.fetchall()

    async def add_user_grade(
            self, chat_id, grade_number,
            grade_letter) -> None:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    UPDATE users SET
                    grade_number = %s,
                    grade_letter = %s
                    WHERE chat_id = %s;
                    ''', (grade_number, grade_letter,
                          chat_id))

    async def get_current_and_next_events(self) -> tuple:
        today = datetime.datetime.today()
        time = today.time().isoformat(timespec='seconds')
        weekday = today.weekday()

        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    '''
                        SELECT current_event.event_name,
                        current_event_clarification.event_clarification,
                        next_event.event_name,
                        next_event_clarification.event_clarification,
                        next_event.event_start - %s
                        FROM event_schedule current_event
                        LEFT JOIN events_clarification current_event_clarification
                        ON current_event_clarification.event_id = current_event.event_id,
                        event_schedule next_event
                        LEFT JOIN events_clarification next_event_clarification
                        ON next_event_clarification.event_id = next_event.event_id
                        WHERE current_event.weekday = %s
                        AND current_event.event_start <= %s
                        AND current_event.event_end >= %s
                        AND next_event.event_id = current_event.next_event_id;
                    ''', (time, weekday, time, time))

                event = cursor.fetchone()
                if event is None:
                    event = ('можно отдохнуть', None, None, None, None)
                return event