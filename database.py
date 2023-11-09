from typing import (
    List,
    Type
)
from sqlalchemy import (
    ForeignKey,
    create_engine
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    Session
)

session: Session | None = None

def initDatabase(url):
    global session
    engine = create_engine(url)
    session = sessionmaker(bind=engine)()

class Base(DeclarativeBase):
    pass

class MineObject(Base):
    __tablename__ = "MineObjects"

    RID: Mapped[int] = mapped_column(primary_key=True)
    PID: Mapped[int] = mapped_column()
    Level: Mapped[int] = mapped_column(nullable=False)
    HCode: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    Type: Mapped[str] = mapped_column(nullable=False)
    CSID: Mapped[int] = mapped_column(ForeignKey("CoordSystems.RID"), nullable=False)
    X_Min: Mapped[float] = mapped_column(nullable=False)
    X_Max: Mapped[float] = mapped_column(nullable=False)
    Y_Min: Mapped[float] = mapped_column(nullable=False)
    Y_Max: Mapped[float] = mapped_column(nullable=False)
    Z_Min: Mapped[float] = mapped_column(nullable=False)
    Z_Max: Mapped[float] = mapped_column(nullable=False)

    parent: Mapped["MineObject"] = relationship(
        backref='childrens',
        primaryjoin='foreign(MineObject.PID) == MineObject.RID',
        remote_side=[RID]
    )

    coord_system: Mapped["CoordSystem"] = relationship(
        backref='mine_objects',
        primaryjoin='MineObject.CSID == CoordSystem.RID'
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
    X_0: Mapped[float] = mapped_column(nullable=False)
    Y_0: Mapped[float] = mapped_column(nullable=False)
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
        backref='childrens',
        primaryjoin='foreign(CoordSystem.PID) == CoordSystem.RID',
        remote_side=[RID]
    )

class DischargeSeries(Base):
    __tablename__ = 'DischargeSeries'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    OSSID: Mapped[int] = mapped_column(ForeignKey('OrigSampleSets.RID'), nullable=False)
    MeasureDate: Mapped[int] = mapped_column(nullable=False)

    orig_sample_set: Mapped['OrigSampleSet'] = relationship(
        backref='discharge_series',
        primaryjoin='DischargeSeries.OSSID == OrigSampleSet.RID'
    )

class OrigSampleSet(Base):
    __tablename__ = 'OrigSampleSets'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str] = mapped_column()
    SampleType: Mapped[str] = mapped_column(nullable=False)
    MOID: Mapped[int] = mapped_column(ForeignKey('MineObjects.RID'))
    HID: Mapped[int] = mapped_column(ForeignKey('BoreHoles.RID'))
    X: Mapped[float] = mapped_column(nullable=False)
    Y: Mapped[float] = mapped_column(nullable=False)
    Z: Mapped[float] = mapped_column(nullable=False)

    mine_object: Mapped['MineObject'] = relationship(
        backref='orig_sample_sets',
        primaryjoin='OrigSampleSet.MOID == MineObject.RID'
    )

    bore_hole: Mapped['BoreHole'] = relationship(
        backref='orig_sample_sets',
        primaryjoin='OrigSampleSet.HID == BoreHole.RID'
    )

class BoreHole(Base):
    __tablename__ = 'BoreHoles'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str | None] = mapped_column()
    SID: Mapped[int] = mapped_column(ForeignKey('Stations.RID'))
    MOID: Mapped[int] = mapped_column(ForeignKey('MineObjects.RID'))
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
        backref='bore_hole',
        primaryjoin='foreign(BoreHole.MOID) == MineObject.RID'
    )

    station: Mapped['Station'] = relationship(
        backref='bore_holes',
        primaryjoin='BoreHole.SID == Station.RID'
    )

class Station(Base):
    __tablename__ = 'Stations'

    RID: Mapped[int] = mapped_column(primary_key=True)
    Number: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Comment: Mapped[str | None] = mapped_column()
    MOID: Mapped[int] = mapped_column(ForeignKey('MineObject.RID'))
    X: Mapped[float] = mapped_column(nullable=False)
    Y: Mapped[float] = mapped_column(nullable=False)
    Z: Mapped[float] = mapped_column(nullable=False)
    HoleCount: Mapped[int] = mapped_column(nullable=False)
    StartDate: Mapped[int] = mapped_column(nullable=False)
    EndDate: Mapped[int] = mapped_column(nullable=False)

    mine_object: Mapped['MineObject'] = relationship(
        backref='stations',
        primaryjoin='foreign(Station.MOID) == MineObject.RID'
    )

class DischargeMeasurement(Base):
    __tablename__ = 'DischargeMeasurements'

    RID: Mapped[int] = mapped_column(primary_key=True)
    DSID: Mapped[int] = mapped_column(nullable=False)
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

    dischange_series: Mapped['DischargeSeries'] = relationship(
        backref='dischage_measurements',
        primaryjoin='foreign(DischargeMeasurement.DSID) == DischargeSeries.RID'
    )

