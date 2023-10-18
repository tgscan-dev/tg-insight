# sourcery skip: none-compare
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.sql.operators import and_

from tg_insight.dao.database import DBSession
from tg_insight.dao.models import Room
from tg_insight.service.group_tagging import analyze_group

load_dotenv()


if __name__ == "__main__":
    with DBSession() as session:
        while True:
            rooms = (
                session.query(Room)
                .filter(and_(Room.category == None, Room.status == "COLLECTED"))
                .all()
            )
            if len(rooms) == 0:
                logger.info("no room to analyze")
                break
            for room in rooms:
                group = analyze_group(room.name, room.jhi_desc)
                room.lang = group.language
                room.category = group.category
                room.tags = ",".join(group.tags)
                logger.info(
                    f"room {room.name} {room.link} analyzed, lang:{room.lang}, category:{room.category}, tags:{room.tags}"
                )
                session.commit()
