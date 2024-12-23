from dataclasses import dataclass


@dataclass
class Property:
    code: str
    name: str
    value: float | None = None


def find_all_used_property_codes(source): ...


def calc_property(source, properties):
    def _fn_(code):
        prop = None
        for _p in properties:
            if _p.code == code:
                prop = _p
                break

        if prop == None:
            raise Exception("Свойство с кодом: %s не найдено." % code)
        elif prop.value == None:
            raise Exception("В свойстве %s отсутвует значение." % prop.name)

        return prop.value

    result = eval(source, {"ЗНАЧ": _fn_})
    if not isinstance(result, (float, int)):
        raise Exception("Возвращаемое значение должно быть числом")

    return result
