from pony.orm import *
from datetime import date

db = Database()


def init(config):
    global db
    db.bind(
        provider="postgres",
        user=config["login"],
        password=config["password"],
        host=config["host"],
        database=config["database"],
    )
    db.generate_mapping(create_tables=False)


class MineObject(db.Entity):
    _table_ = "MineObjects"

    parent = Optional("MineObject", column="PID")
    coord_system = Required("CoordSystem", column="CSID")
    childrens = Set("MineObject")
    stations = Set("Station")
    bore_holes = Set("BoreHole")
    orig_sample_sets = Set("OrigSampleSet")
    discharge_series = Set("DischargeSeries")
    rock_bursts = Set("RockBurst")
    pm_sample_set = Set("PMSampleSet")

    RID = PrimaryKey(int, auto=True, column="RID")
    Level = Required(int, column="Level")
    HCode = Required(str, column="HCode")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    Type = Required(str, column="Type")
    X_Min = Required(float, column="X_Min")
    Y_Min = Required(float, column="Y_Min")
    Z_Min = Required(float, column="Z_Min")
    X_Max = Required(float, column="X_Max")
    Y_Max = Required(float, column="Y_Max")
    Z_Max = Required(float, column="Z_Max")


class CoordSystem(db.Entity):
    _table_ = "CoordSystems"

    parent = Optional("CoordSystem", column="PID")
    childrens = Set("CoordSystem")
    mine_objects = Set(MineObject)

    RID = PrimaryKey(int, auto=True, column="RID")
    Level = Required(int, column="Level")
    HCode = Required(str, column="HCode")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    X_Min = Required(float, column="X_Min")
    Y_Min = Required(float, column="Y_Min")
    Z_Min = Required(float, column="Z_Min")
    X_Max = Required(float, column="X_Max")
    Y_Max = Required(float, column="Y_Max")
    Z_Max = Required(float, column="Z_Max")
    X_0 = Required(float, column="X_0")
    Y_0 = Required(float, column="Y_0")
    Z_0 = Required(float, column="Z_0")
    X_X = Required(float, column="X_X")
    X_Y = Required(float, column="X_Y")
    X_Z = Required(float, column="X_Z")
    Y_X = Required(float, column="Y_X")
    Y_Y = Required(float, column="Y_Y")
    Y_Z = Required(float, column="Y_Z")
    Z_X = Required(float, column="Z_X")
    Z_Y = Required(float, column="Z_Y")
    Z_Z = Required(float, column="Z_Z")


class Station(db.Entity):
    _table_ = "Stations"

    mine_object = Required(MineObject, column="MOID")
    bore_holes = Set("BoreHole")

    RID = PrimaryKey(int, auto=True, column="RID")
    Number = Required(str, column="Number")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    X = Required(float, column="X")
    Y = Required(float, column="Y")
    Z = Required(float, column="Z")
    HoleCount = Required(int, column="HoleCount")
    StartDate = Required(int, column="StartDate", size=64)
    EndDate = Optional(int, column="EndDate", size=64)


class BoreHole(db.Entity):
    _table_ = "BoreHoles"

    mine_object = Required(MineObject, column="MOID")
    orig_sample_sets = Set("OrigSampleSet")
    station = Optional(Station, column="SID")

    RID = PrimaryKey(int, auto=True, column="RID")
    Number = Required(str, column="Number")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    X = Required(float, column="X")
    Y = Required(float, column="Y")
    Z = Required(float, column="Z")
    Azimuth = Required(float, column="Azimuth")
    Tilt = Required(float, column="Tilt")
    Diameter = Required(float, column="Diameter")
    Length = Required(float, column="Length")
    StartDate = Required(int, column="StartDate", size=64)
    EndDate = Optional(int, column="EndDate", size=64)
    DestroyDate = Optional(int, column="DestroyDate", size=64)


class OrigSampleSet(db.Entity):
    _table_ = "OrigSampleSets"

    mine_object = Required(MineObject, column="MOID")
    bore_hole = Optional(BoreHole, column="HID")
    discharge_series = Set("DischargeSeries")
    discharge_measurements = Set("DischargeMeasurement")
    core_box_storage = Set("CoreBoxStorage")
    pm_samples = Set("PMSample")

    RID = PrimaryKey(int, auto=True, column="RID")
    Number = Required(str, column="Number")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    SampleType = Required(str, column="SampleType")
    X = Required(float, column="X")
    Y = Required(float, column="Y")
    Z = Required(float, column="Z")
    StartSetDate = Required(int, column="StartSetDate", size=64)
    EndSetDate = Optional(int, column="EndSetDate", size=64)


class FoundationDocument(db.Entity):
    _table_ = "FoundationDocuments"

    discharge_series = Set("DischargeSeries")
    pm_test_series = Set("PMTestSeries")

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    Type = Optional(str, column="Type")
    Number = Optional(str, column="Number")


class DischargeSeries(db.Entity):
    _table_ = "DischargeSeries"

    mine_object = Required(MineObject, column="MOID")
    orig_sample_set = Required(OrigSampleSet, column="OSSID")
    foundation_document = Optional(FoundationDocument, column="FDID")

    RID = PrimaryKey(int, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    StartMeasure = Required(int, column="StartMeasure", size=64)
    EndMeasure = Optional(int, column="EndMeasure", size=64)


class DischargeMeasurement(db.Entity):
    _table_ = "DischargeMeasurements"

    orig_sample_set = Required(OrigSampleSet, column="OSSID")

    RID = PrimaryKey(int, auto=True, column="RID")
    DschNumber = Required(str, column="DschNumber")
    SampleNumber = Required(str, column="SampleNumber")
    Diameter = Required(float, column="Diameter")
    Length = Required(float, column="Length")
    Weight = Required(float, column="Weight")
    RockType = Optional(str, column="RockType")
    PartNumber = Required(str, column="PartNumber")
    RTens = Required(float, column="RTens")
    Sensitivity = Required(float, column="Sensitivity")
    TP1_1 = Optional(float, column="TP1_1")
    TP1_2 = Optional(float, column="TP1_2")
    TP2_1 = Optional(float, column="TP2_1")
    TP2_2 = Optional(float, column="TP2_2")
    TR_1 = Optional(float, column="TR_1")
    TR_2 = Optional(float, column="TR_2")
    TS_1 = Optional(float, column="TS_1")
    TS_2 = Optional(float, column="TS_2")
    PWSpeed = Optional(float, column="PWSpeed")
    RWSpeed = Optional(float, column="RWSpeed")
    SWSpeed = Optional(float, column="SWSpeed")
    PuassonStatic = Optional(float, column="PuassonStatic")
    YungStatic = Optional(float, column="YungStatic")
    CoreDepth = Required(float, column="CoreDepth")
    E1 = Required(float, column="E1")
    E2 = Required(float, column="E2")
    E3 = Required(float, column="E3")
    E4 = Required(float, column="E4")
    Rotate = Required(float, column="Rotate")


class SuppliedData(db.Entity):
    _table_ = "SuppliedData"

    parts = Set("SuppliedDataPart")

    RID = PrimaryKey(int, auto=True, column="RID")
    OwnID = Required(int, column="OwnID")
    OwnType = Required(str, column="OwnType")
    Number = Optional(str, column="Number")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    DataDate = Optional(int, column="DataDate", size=64)


class SuppliedDataPart(db.Entity):
    _table_ = "SuppliedDataParts"

    parent = Required(SuppliedData, column="SDID")

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    DType = Required(str, column="DType")
    FileName = Required(str, column="FileName")
    DataContent = Required(bytes, column="DataContent", lazy=True)


class RockBurst(db.Entity):
    _table_ = "RockBursts"

    mine_object = Required(MineObject, column="MOID")

    RID = PrimaryKey(int, auto=True, column="RID")
    Number = Required(str, column="Number")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    X = Required(float, column="X")
    Y = Required(float, column="Y")
    Z = Required(float, column="Z")
    BurstDate = Required(int, column="BurstDate", size=64)


class CoreBoxStorage(db.Entity):
    _table_ = "CoreBoxStorage"

    orig_sample_set = Required(OrigSampleSet, column="OSSID")

    BoxNumber = Required(str, column="BoxNumber")
    PartNumber = PrimaryKey(str, column="PartNumber")
    StartPosition = Required(int, column="StartPosition")
    EndPosition = Required(int, column="EndPosition")


class Petrotype(db.Entity):
    _table_ = "Petrotypes"

    petrotype_structs = Set("PetrotypeStruct")

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")


class PetrotypeStruct(db.Entity):
    _table_ = "PetrotypeStructs"

    petrotype = Required(Petrotype, column="PTID")
    pm_sample_sets = Set("PMSampleSet")

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")


class PMTestSeries(db.Entity):
    _table_ = "PMTestSeries"

    foundation_document = Optional(FoundationDocument, column="FDID")
    pm_sample_sets = Set("PMSampleSet")

    RID = PrimaryKey(int, auto=True, column="RID")
    Number = Required(str, column="Number")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    Location = Optional(str, column="Location")


class PMSampleSet(db.Entity):
    _table_ = "PMSampleSets"

    mine_object = Required(MineObject, column="MOID")
    test_series = Required(PMTestSeries, column="TSID")
    petrotype_struct = Required(PetrotypeStruct, column="PTSID")
    pm_samples = Set("PMSample")

    RID = PrimaryKey(int, auto=True, column="RID")
    Number = Required(str, column="Number")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    SetDate = Optional(int, column="SetDate", size=64)
    TestDate = Optional(int, column="TestDate", size=64)
    CrackDescr = Optional(str, column="CrackDescr")
    RealDetails = Required(bool, column="RealDetails")
    SampleCount = Optional(int, column="SampleCount")


class PMSample(db.Entity):
    _table_ = "PMSamples"

    pm_sample_set = Required(PMSampleSet, column="SSID")
    orig_sample_set = Required(OrigSampleSet, column="OSSID")
    pm_sample_property_values = Set("PmSamplePropertyValue")

    RID = PrimaryKey(int, auto=True, column="RID")
    Number = Required(str, column="Number")
    SetDate = Required(int, column="SetDate", size=64)
    StartPosition = Required(float, column="StartPosition")
    EndPosition = Optional(float, column="EndPosition")
    BoxNumber = Optional(str, column="BoxNumber")
    Length1 = Optional(float, column="Length1")
    Length2 = Optional(float, column="Length2")
    Height = Optional(float, column="Height")
    MassAirDry = Optional(float, column="MassAirDry")
    MassNatMoist = Optional(float, column="MassNatMoist")
    MassWater = Optional(float, column="MassWater")
    MassWaterSatur = Optional(float, column="MassWaterSatur")
    MassWaterSatWater = Optional(float, column="MassWaterSatWater")
    MassDry = Optional(float, column="MassDry")
    UniAxCompDistort = Optional(float, column="UniAxCompDistort")
    UniAxTensDistort = Optional(float, column="UniAxTensDistort")
    ElasticityModulus = Optional(float, column="ElasticityModulus")
    DeclineModulus = Optional(float, column="DeclineModulus")
    PuassonCoeff = Optional(float, column="PuassonCoeff")
    DiffStrength = Optional(float, column="DiffStrength")


class PmTestMethod(db.Entity):
    _table_ = "PMTestMethods"

    pm_sample_property_values = Set("PmSamplePropertyValue")

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    StartDate = Required(int, column="StartDate", size=64)
    EndDate = Optional(int, column="EndDate", size=64)
    Analytic = Optional(bool, column="Analytic")


class PmTestEquipment(db.Entity):
    _table_ = "PMTestEquipment"

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    SerialNo = Optional(str, column="SerialNo")
    StartDate = Required(int, column="StartDate", size=64)


class PmPropertyClass(db.Entity):
    _table_ = "PMPropertyClasses"

    pm_properties = Set("PmProperty")

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")


class PmProperty(db.Entity):
    _table_ = "PMProperties"

    pm_property_class = Required(PmPropertyClass, column="PCID")
    pm_sample_property_values = Set("PmSamplePropertyValue")

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")
    Unit = Optional(str, column="Unit")


class PmSamplePropertyValue(db.Entity):
    _table_ = "PMSamplePropertyValues"

    pm_sample = Required(PMSample, column="RSID")
    pm_test_method = Required(PmTestMethod, column="TMID")
    pm_property = Required(PmProperty, column="PRID")

    RID = PrimaryKey(int, auto=True, column="RID")
    Value = Required(float, column="Value")

class PmPerformedTasks(db.Entity):
    _table_ = "PMPerformedTasks"

    RID = PrimaryKey(int, auto=True, column="RID")
    Name = Required(str, column="Name")
    Comment = Optional(str, column="Comment")