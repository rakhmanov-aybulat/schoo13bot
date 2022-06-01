import datetime
from typing import Tuple, Union

from ..exceptions import CantGetCurrentAndNextEvents, CantGetGradeLetterList, CantGetGradeNumberList
from ..models.db import Event, CurrentAndNextEvents


class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn = conn

    async def add_user(
            self, chat_id: int, first_name: str,
            last_name: Union[str, None] = None,
            user_name: Union[str, None] = None) -> None:
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
            self, chat_id: int, first_name: str,
            last_name: Union[str, None] = None,
            user_name: Union[str, None] = None) -> None:
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

    async def get_grade_number_list(self) -> Tuple[int, ...]:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT DISTINCT grade_number
                    FROM grades
                    ORDER BY grade_number ASC;
                    ''')
                numbers = cursor.fetchall()

                if numbers is None:
                    raise CantGetGradeNumberList

                return tuple(map(lambda n: int(n[0]), numbers))

    async def get_grade_letter_list(self, grade_number: int) -> Tuple[str, ...]:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT grade_letter
                    FROM grades
                    WHERE grade_number = %s;
                    ''', (grade_number,))
                letters = cursor.fetchall()

                if letters is None:
                    raise CantGetGradeLetterList

                return tuple(map(lambda l: str(l[0]), letters))

    async def add_user_grade(
            self, chat_id: int, grade_number: int,
            grade_letter: str) -> None:
        grade = f'{grade_number}{grade_letter}'
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    UPDATE users SET
                    grade = %s
                    WHERE chat_id = %s;
                    ''', (grade, chat_id))

    async def get_current_and_next_events(self, chat_id: int) -> CurrentAndNextEvents:
        today = datetime.datetime.today()
        current_time = today.time().isoformat(timespec='seconds')
        weekday = today.weekday()

        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    '''
                        SELECT es.event_id,
                        es.event_name,
                        ec.event_clarification,
                        es.weekday,
                        es.event_start,
                        es.event_end
                        FROM event_schedule es
                        LEFT JOIN events_clarification ec
                        ON es.event_id = ec.event_id
                        AND ec.grade = (SELECT grade FROM users WHERE chat_id = %s)
                        WHERE es.weekday = %s
                        AND es.event_start <= %s
                        AND es.event_end >= %s
                    ''', (chat_id, weekday, current_time, current_time))

                res = cursor.fetchone()
                current_event = None if res is None else Event(*res)

                cursor.execute(
                    '''
                        SELECT es.event_id,
                        es.event_name,
                        ec.event_clarification,
                        es.weekday,
                        es.event_start,
                        es.event_end
                        FROM event_schedule es
                        LEFT JOIN events_clarification ec
                        ON es.event_id = ec.event_id
                        AND ec.grade = (SELECT grade FROM users WHERE chat_id = %s)
                        WHERE es.weekday = %s
                        AND es.event_start >= %s
                        ORDER BY event_start
                        LIMIT 1;
                    ''', (chat_id, weekday, current_event.end if current_event else current_time))

                res2 = cursor.fetchone()
                next_event = None if res2 is None else Event(*res2)

                if current_event is None and next_event is None:
                    raise CantGetCurrentAndNextEvents

                return CurrentAndNextEvents(current_event, next_event)
