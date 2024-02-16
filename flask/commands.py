from collections import namedtuple
from typing import Any, Tuple

from sqlalchemy import inspect

from app.app import db, app
from model.bricklet_model import Bricklet
from model.bricklet_pin_model import BrickletPin
from model.camera_settings_model import CameraSettings
from model.chat_message_model import ChatMessage
from model.chat_model import Chat
from model.motor_model import Motor
from model.personality_model import Personality
from model.program_model import Program


@app.cli.command("seed_db")
def seed_db() -> None:
    if not _is_empty_db():
        print("Seeding database failed - database already contains data.")
        return
    _create_bricklet_data()
    _create_camera_data()
    _create_program_data()
    _create_chat_data()
    db.session.commit()
    print("Seeded the database with default data.")


def _is_empty_db() -> bool:
    inspector = inspect(db.engine)

    for table in inspector.get_table_names():
        if table == "alembic_version":
            continue
        table_class = db.Model.metadata.tables[table]
        count = db.session.query(table_class).count()
        if count > 0:
            return False
    return True


def _create_bricklet_data() -> None:
    data = _get_motor_list()
    motor_settings = {"pulseWidthMin": 700, "pulseWidthMax": 2500, "rotationRangeMin": -4500,
                  "rotationRangeMax": 4500, "velocity": 16000, "acceleration": 10000, "deceleration": 5000,
                  "period": 19500,
                  "turnedOn": True, "visible": True}

    for item in data:
        motor = Motor(name=item["name"], **motor_settings)
        if motor.name == "tilt_sideways_motor":
            motor.visible = False
        db.session.add(motor)
        db.session.flush()

        bricklet_pins: [Tuple[int, int]] = item["bricklet_pins"]
        for bricklet_pin in bricklet_pins:
            bricklet_id, pin = bricklet_pin
            db.session.add(BrickletPin(motorId=motor.id, brickletId=bricklet_id, pin=pin))
        db.session.flush()

    b1 = Bricklet(uid="AAA", brickletNumber=1)
    b2 = Bricklet(uid="BBB", brickletNumber=2)
    b3 = Bricklet(uid="CCC", brickletNumber=3)
    db.session.add_all([b1, b2, b3])
    db.session.flush()


def _create_camera_data() -> None:
    camera_settings = CameraSettings(resolution="SD", refresh_rate=0.1, quality_factor=80, res_x=640, res_y=480)
    db.session.add(camera_settings)
    db.session.flush()


def _create_program_data() -> None:
    program = Program(name="hello_world", code_visual=_get_example_program())
    db.session.add(program)
    db.session.flush()


def _create_chat_data() -> None:
    p_eva = Personality(name="Eva", personalityId="8f73b580-927e-41c2-98ac-e5df070e7288", gender="female",
                        pauseThreshold=0.8)
    p_thomas = Personality(name="Adam", personalityId="8b310f95-92cd-4512-b42a-d3fe29c4bb8a", gender="male",
                           pauseThreshold=0.8)
    db.session.add_all([p_eva, p_thomas])
    db.session.flush()

    c1 = Chat(chatId="b4f01552-0c09-401c-8fde-fda753fb0261", topic="Nuernberg",
              personalityId="8f73b580-927e-41c2-98ac-e5df070e7288")
    c2 = Chat(chatId="ee3e80f9-c8f7-48c2-9f15-449ba9bbe4ab", topic="Home-Office",
              personalityId="8b310f95-92cd-4512-b42a-d3fe29c4bb8a")
    db.session.add_all([c1, c2])
    db.session.flush()

    m1 = ChatMessage(messageId="539ed3e6-9e3d-11ee-8c90-0242ac120002", isUser=True, content="hello pib!",
                     chatId="b4f01552-0c09-401c-8fde-fda753fb0261")
    m2 = ChatMessage(messageId="0a080706-9e3e-11ee-8c90-0242ac120002", isUser=False, content="hello user!",
                     chatId="b4f01552-0c09-401c-8fde-fda753fb0261")
    db.session.add_all([m1, m2])
    db.session.flush()


def _get_motor_list() -> [dict[str, Any]]:
    name: str = "name"
    bricklet_pins: str = "bricklet_pins"

    return [
        {name: "tilt_forward_motor", bricklet_pins: [(1, 0)]},
        {name: "tilt_sideways_motor", bricklet_pins: [(1, 1)]},
        {name: "turn_head_motor", bricklet_pins: [(2, 8)]},
        {name: "thumb_left_stretch", bricklet_pins: [(1, 9)]},
        {name: "thumb_left_opposition", bricklet_pins: [(2, 0)]},
        {name: "index_left_stretch", bricklet_pins: [(2, 1)]},
        {name: "middle_left_stretch", bricklet_pins: [(2, 2)]},
        {name: "ring_left_stretch", bricklet_pins: [(2, 3)]},
        {name: "pinky_left_stretch", bricklet_pins: [(2, 4)]},
        {name: "thumb_right_stretch", bricklet_pins: [(1, 3)]},
        {name: "thumb_right_opposition", bricklet_pins: [(1, 4)]},
        {name: "index_right_stretch", bricklet_pins: [(1, 5)]},
        {name: "middle_right_stretch", bricklet_pins: [(1, 6)]},
        {name: "ring_right_stretch", bricklet_pins: [(1, 7)]},
        {name: "pinky_right_stretch", bricklet_pins: [(1, 8)]},
        {name: "upper_arm_left_rotation", bricklet_pins: [(2, 5)]},
        {name: "elbow_left", bricklet_pins: [(2, 6)]},
        {name: "lower_arm_left_rotation", bricklet_pins: [(2, 7)]},
        {name: "wrist_left", bricklet_pins: [(1, 2)]},
        {name: "shoulder_vertical_left", bricklet_pins: [(3, 7), (3, 9)]},
        {name: "shoulder_horizontal_left", bricklet_pins: [(3, 9)]},
        {name: "upper_arm_right_rotation", bricklet_pins: [(3, 0)]},
        {name: "elbow_right", bricklet_pins: [(3, 1)]},
        {name: "lower_arm_right_rotation", bricklet_pins: [(3, 2)]},
        {name: "wrist_right", bricklet_pins: [(3, 4)]},
        {name: "shoulder_vertical_right", bricklet_pins: [(3, 8), (3, 5)]},
        {name: "shoulder_horizontal_right", bricklet_pins: [(3, 6)]},
    ]


def _get_example_program() -> str:
    return ''''{"blocks":{"languageVersion":0,"blocks":[{"type":"text_print","id":"]l,+vC{q$rZPVdSfyx=4","x":229,
    "y":67,"inputs":{"TEXT":{"shadow":{"type":"text","id":"v,}3JGN5d7og[X_/KJ)|","fields":{"TEXT":"hello 
    world"}}}}}]}}', "e1d46e2a-935e-4e2b-b2f9-0856af4257c5"'''
