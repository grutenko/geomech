# _*_ coding: UTF8 _*_

from sqlalchemy import (
    ForeignKey,
    Engine,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)
from typing import Callable
from typing import List
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from queue import Queue
import threading
import time
import wx

engine: Engine = None
session: Session = None

class xDatabaseInitError(BaseException):
    pass

def __exc():
    return xDatabaseInitError("Произошла ошибка во время попытки открытия соединения с базой данных." 
                              + "Возможно неверно введены авторизационные данные, или название базы.")

def __init(dsn) -> (Engine, Session):
    engine = create_engine(dsn)
    session = Session(bind=engine)
    try:
        session.execute(text("SELECT 1"))
    except UnicodeDecodeError as e:
        session.close()
        raise __exc()
    result = session.execute(text("select exists(select from pg_tables where schemaname='public'"
                                  +" and tablename='DischargeMeasurements')"))
    if result.first()[0] == False:
        raise __exc()
    return (engine, session)

'''
Выбросит исключение если подключится к бд не удалось
'''
def test_connection(dsn):
    try:
        _, session = __init(dsn)
    except:
        raise
    else:
        session.close()
        

def init_database(dsn: str) -> None:
    global engine, session
    _engine, _session = __init(dsn)
    engine = _engine
    session = _session

def get_session() -> Session:
    global session
    return session

def commit_changes(parent = None):
    def _thread(exc_bucket):
        try:
            get_session().commit()
        except Exception as e:
            get_session().rollback()
            exc_bucket.put(e)

    exc_bucket = Queue()
    t = threading.Thread(target=_thread, args=[exc_bucket])
    t.start()
    w = wx.ProgressDialog("Обновление", "Идет обновление базы данных...", style=0, parent=parent)
    while True:
        if not t.is_alive():
            if not exc_bucket.empty():
                w.Destroy()
                raise exc_bucket.get(False)
            else:
                break
        else:
            time.sleep(0.01)
            w.Pulse()
    w.Destroy()

def dry_commit_changes():
    try:
        get_session().flush()
    finally:
        get_session().rollback()

class Base(DeclarativeBase):
    pass

def gen_name_path(e: Base, parent_field: str) -> str:
    cur = e
    path = ''
    while cur != None:
        path = cur.Name + (' / ' if cur != e else '') + path
        cur = getattr(cur, parent_field)
        print(cur)
    return path

class MineObject(Base):
    __tablename__ = "MineObjects"

    RID: Mapped[int] = mapped_column(primary_key=True)
    PID: Mapped[int] = mapped_column()
    Level: Mapped[int] = mapped_column(nullable=False)
    HCode: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    Type: Mapped[str] = mapped_column(nullable=False)
    CSID: Mapped[int] = mapped_column(ForeignKey("CoordSystems.RID", ondelete="NOACTION"), nullable=False)
    X_Min: Mapped[float] = mapped_column(nullable=False)
    X_Max: Mapped[float] = mapped_column(nullable=False)
    Y_Min: Mapped[float] = mapped_column(nullable=False)
    Y_Max: Mapped[float] = mapped_column(nullable=False)
    Z_Min: Mapped[float] = mapped_column(nullable=False)
    Z_Max: Mapped[float] = mapped_column(nullable=False)

    parent: Mapped["MineObject"] = relationship(
        back_populates='childrens',
        primaryjoin='foreign(MineObject.PID) == MineObject.RID',
        remote_side=[RID]
    )

    childrens: Mapped[List["MineObject"]] = relationship(
        back_populates='parent',
        primaryjoin='foreign(MineObject.PID) == MineObject.RID',
        remote_side=[PID]
    )

    coord_system: Mapped["CoordSystem"] = relationship(
        back_populates='mine_objects',
        primaryjoin='MineObject.CSID == CoordSystem.RID'
    )

    orig_sample_sets: Mapped[List['OrigSampleSet']] = relationship(
        back_populates='mine_object',
        primaryjoin='OrigSampleSet.MOID == MineObject.RID'
    )

    bore_holes: Mapped[List['BoreHole']] = relationship(
        back_populates='mine_object',
        primaryjoin='foreign(BoreHole.MOID) == MineObject.RID'
    )

    stations: Mapped[List['Station']] = relationship(
        back_populates='mine_object',
        primaryjoin='foreign(Station.MOID) == MineObject.RID'
    )

class CoordSystem(Base):
    __tablename__ = 'CoordSystems'

    RID: Mapped[int] = mapped_column(primary_key=True)
    PID: Mapped[int] = mapped_column()
    Level: Mapped[int] = mapped_column(nullable=False)
    HCode: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    X_Min: Mapped[float] = mapped_column(nullable=False)
    X_Max: Mapped[float] = mapped_column(nullable=False)
    Y_Min: Mapped[float] = mapped_column(nullable=False)
    Y_Max: Mapped[float] = mapped_column(nullable=False)
    Z_Min: Mapped[float] = mapped_column(nullable=False)
    Z_Max: Mapped[float] = mapped_column(nullable=False)
    X_0: Mapped[float] = mapped_column(nullable=False)
    Y_0: Mapped[float] = mapped_column(nullable=False)
    Z_0: Mapped[float] = mapped_column(nullable=False)
    X_X: Mapped[float] = mapped_column(nullable=False)
    X_Y: Mapped[float] = mapped_column(nullable=False)
    X_Z: Mapped[float] = mapped_column(nullable=False)
    Y_X: Mapped[float] = mapped_column(nullable=False)
    Y_Y: Mapped[float] = mapped_column(nullable=False)
    Y_Z: Mapped[float] = mapped_column(nullable=False)
    Z_X: Mapped[float] = mapped_column(nullable=False)
    Z_Y: Mapped[float] = mapped_column(nullable=False)
    Z_Z: Mapped[float] = mapped_column(nullable=False)

    parent: Mapped["CoordSystem"] = relationship(
        back_populates='childrens',
        primaryjoin='foreign(CoordSystem.PID) == CoordSystem.RID',
        remote_side=[RID]
    )

    childrens: Mapped[List["CoordSystem"]] = relationship(
        back_populates='parent',
        primaryjoin='foreign(CoordSystem.PID) == CoordSystem.RID',
        remote_side=[PID]
    )

    mine_objects: Mapped[List["MineObject"]] = relationship(
        back_populates='coord_system',
        primaryjoin='MineObject.CSID == CoordSystem.RID'
    )

class DischargeSeries(Base):
    __tablename__ = 'DischargeSeries'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    OSSID: Mapped[int] = mapped_column(ForeignKey('OrigSampleSets.RID', ondelete="NO ACTION"), nullable=False)
    MeasureDate: Mapped[int] = mapped_column(nullable=False)

    orig_sample_set: Mapped['OrigSampleSet'] = relationship(
        back_populates='discharge_series',
        primaryjoin='DischargeSeries.OSSID == OrigSampleSet.RID'
    )

    discharge_measurements: Mapped[List['DischargeMeasurement']] = relationship(
        back_populates='discharge_series',
        primaryjoin='DischargeSeries.RID == DischargeMeasurement.DSID'
    )

class OrigSampleSet(Base):
    __tablename__ = 'OrigSampleSets'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    SampleType: Mapped[str] = mapped_column(nullable=False)
    MOID: Mapped[int] = mapped_column(ForeignKey('MineObjects.RID', ondelete="NO ACTION"))
    HID: Mapped[int] = mapped_column(ForeignKey('BoreHoles.RID', ondelete="NO ACTION"))
    X: Mapped[float] = mapped_column(nullable=False)
    Y: Mapped[float] = mapped_column(nullable=False)
    Z: Mapped[float] = mapped_column(nullable=False)
    SetDate: Mapped[int] = mapped_column(nullable=False)

    mine_object: Mapped['MineObject'] = relationship(
        back_populates='orig_sample_sets',
        primaryjoin='OrigSampleSet.MOID == MineObject.RID'
    )

    bore_hole: Mapped['BoreHole'] = relationship(
        back_populates='orig_sample_sets',
        primaryjoin='OrigSampleSet.HID == BoreHole.RID'
    )

    discharge_series: Mapped[List['DischargeSeries']] = relationship(
        back_populates='orig_sample_set',
        primaryjoin='DischargeSeries.OSSID == OrigSampleSet.RID'
    )

class BoreHole(Base):
    __tablename__ = 'BoreHoles'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    SID: Mapped[int] = mapped_column(ForeignKey('Stations.RID', ondelete="NO ACTION"))
    MOID: Mapped[int] = mapped_column(ForeignKey('MineObjects.RID', ondelete="NO ACTION"))
    X: Mapped[float] = mapped_column(nullable=False)
    Y: Mapped[float] = mapped_column(nullable=False)
    Z: Mapped[float] = mapped_column(nullable=False)
    Azimuth: Mapped[float] = mapped_column(nullable=False)
    Tilt: Mapped[float] = mapped_column(nullable=False)
    Diameter: Mapped[float] = mapped_column(nullable=False)
    Length: Mapped[float] = mapped_column(nullable=False)
    StartDate: Mapped[int] = mapped_column(nullable=False)
    EndDate: Mapped[int] = mapped_column(nullable=False)

    mine_object: Mapped['MineObject'] = relationship(
        back_populates='bore_holes',
        primaryjoin='foreign(BoreHole.MOID) == MineObject.RID'
    )

    station: Mapped['Station'] = relationship(
        back_populates='bore_holes',
        primaryjoin='BoreHole.SID == Station.RID'
    )

    orig_sample_sets: Mapped[List['OrigSampleSet']] = relationship(
        back_populates="bore_hole",
        primaryjoin='OrigSampleSet.HID == BoreHole.RID'
    )

class Station(Base):
    __tablename__ = 'Stations'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    MOID: Mapped[int] = mapped_column(ForeignKey('MineObjects.RID', ondelete="NO ACTION"))
    X: Mapped[float] = mapped_column(nullable=False)
    Y: Mapped[float] = mapped_column(nullable=False)
    Z: Mapped[float] = mapped_column(nullable=False)
    HoleCount: Mapped[int] = mapped_column(nullable=False)
    StartDate: Mapped[int] = mapped_column(nullable=False)
    EndDate: Mapped[int] = mapped_column(nullable=False)

    mine_object: Mapped['MineObject'] = relationship(
        back_populates='stations',
        primaryjoin='foreign(Station.MOID) == MineObject.RID'
    )

    bore_holes: Mapped[List['BoreHole']] = relationship(
        back_populates='station',
        primaryjoin='BoreHole.SID == Station.RID'
    )

class DischargeMeasurement(Base):
    __tablename__ = 'DischargeMeasurements'

    RID: Mapped[int] = mapped_column(primary_key=True)
    DSID: Mapped[int] = mapped_column(ForeignKey('DischargeSeries.RID', ondelete="NO ACTION"), nullable=False)
    SNumber: Mapped[int] = mapped_column(nullable=False)
    DschNumber: Mapped[int] = mapped_column(nullable=False)
    CoreNumber: Mapped[int] = mapped_column(nullable=False)
    Diameter: Mapped[float] = mapped_column(nullable=False)
    Length: Mapped[float] = mapped_column(nullable=False)
    Weight: Mapped[float] = mapped_column(nullable=False)
    CartNumber: Mapped[str] = mapped_column(nullable=False)
    PartNumber: Mapped[str] = mapped_column(nullable=False)
    R1: Mapped[float] = mapped_column(nullable=False)
    R2: Mapped[float] = mapped_column(nullable=False)
    R3: Mapped[float] = mapped_column(nullable=False)
    R4: Mapped[float] = mapped_column(nullable=False)
    RComp: Mapped[float] = mapped_column(nullable=False)
    Sensitivity: Mapped[float] = mapped_column(nullable=False)
    TP1_1: Mapped[float] = mapped_column()
    TP1_2: Mapped[float] = mapped_column()
    TP2_1: Mapped[float] = mapped_column()
    TP2_2: Mapped[float] = mapped_column()
    TR_1: Mapped[float] = mapped_column()
    TR_2: Mapped[float] = mapped_column()
    TS_1: Mapped[float] = mapped_column()
    TS_2: Mapped[float] = mapped_column()
    PuassonStatic: Mapped[float] = mapped_column()
    YungStatic: Mapped[float] = mapped_column()
    CoreDepth: Mapped[float] = mapped_column(nullable=False)
    E1: Mapped[float] = mapped_column(nullable=False)
    E2: Mapped[float] = mapped_column(nullable=False)
    E3: Mapped[float] = mapped_column(nullable=False)
    E4: Mapped[float] = mapped_column(nullable=False)
    Rotate: Mapped[float] = mapped_column(nullable=False)
    RockType: Mapped[str] = mapped_column(nullable=False)

    discharge_series: Mapped['DischargeSeries'] = relationship(
        back_populates='discharge_measurements',
        primaryjoin='foreign(DischargeMeasurement.DSID) == DischargeSeries.RID',
        lazy="joined",
        passive_deletes=False
    )