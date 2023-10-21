# sourcery skip: none-compare
import openai
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.sql.operators import and_

from tg_insight.dao.database import DBSession
from tg_insight.dao.models import Room
from tg_insight.service.group_tagging import analyze_group

# load_dotenv()
openai.api_base = "http://localhost:7001"

def fetch_no_tagged_rooms(session):
    return (
        session.query(Room)
        .filter(and_(Room.category == None, Room.status == "COLLECTED"))
        .limit(100)
        .all()
    )


def is_valid_room(room: Room):
    if room.name is None:
        room.name = ""
    if room.jhi_desc is None:
        room.jhi_desc = ""
    return room.name.strip() + room.jhi_desc.strip() != ""


from concurrent.futures import ThreadPoolExecutor

def do_tag(rooms0: list[Room]):
    def process_room(room):
        if not is_valid_room(room):
            logger.info(f"room {room.name} {room.link} is not valid")
            return

        group = analyze_group(room.name, room.jhi_desc)
        room.lang = group.language
        room.category = group.category
        room.tags = ",".join(group.tags)
        logger.info(f"room {room.name} {room.link} analyzed, lang:{room.lang}, category:{room.category}, tags:{room.tags}")

        session.commit()

    with ThreadPoolExecutor(max_workers=130) as executor:
        executor.map(process_room, rooms0)




if __name__ == "__main__":
    with DBSession() as session:
        while True:
            rooms = fetch_no_tagged_rooms(session)
            try:
                if len(rooms) == 0:
                    logger.info("no room to analyze")
                    break
                do_tag(rooms)
            except Exception as e:
                logger.error(e)
