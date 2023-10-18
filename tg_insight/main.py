# sourcery skip: none-compare
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.sql.operators import and_

from tg_insight.dao.database import DBSession
from tg_insight.dao.models import Room
from tg_insight.service.group_tagging import analyze_group

load_dotenv()


def fetch_no_tagged_rooms():
    return (
        session.query(Room)
        .filter(and_(Room.category == None, Room.status == "COLLECTED"))
        .all()
    )


def is_valid_room(room: Room):
    if room.name is None:
        room.name = ""
    if room.jhi_desc is None:
        room.jhi_desc = ""
    return room.name.strip() + room.jhi_desc.strip() != ""


def do_tag(rooms0: list[Room]):
    for room in rooms0:
        if not is_valid_room(room):
            logger.info(f"room {room.name} {room.link} is not valid")
            continue
        group = analyze_group(room.name, room.jhi_desc)
        room.lang = group.language
        room.category = group.category
        room.tags = ",".join(group.tags)
        logger.info(
            f"room {room.name} {room.link} analyzed, lang:{room.lang}, \
    category:{room.category}, tags:{room.tags}"
        )
        session.commit()


if __name__ == "__main__":
    with DBSession() as session:
        while True:
            rooms = fetch_no_tagged_rooms()
            try:
                if len(rooms) == 0:
                    logger.info("no room to analyze")
                    break
                do_tag(rooms)
            except Exception as e:
                logger.error(e)
