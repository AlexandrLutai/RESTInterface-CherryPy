from pydantic import BaseModel, Field, RootModel
from typing import Optional, List


class EquipmentInput(BaseModel):
    serial_number: str = Field(..., min_length=1, max_length=50, description="Серийный номер оборудования")
    note: Optional[str] = Field(None, max_length=255, description="Примечание к оборудованию")


class EquipmentListInput(RootModel[List[EquipmentInput]]):
    """
    Корневая модель для списка объектов EquipmentInput.
    """
    pass


class EquipmentUpdateInput(BaseModel):
    """
    Модель для обновления оборудования.
    Все поля являются необязательными.
    """
    serial_number: Optional[str] = Field(None, min_length=1, max_length=50, description="Серийный номер оборудования")
    note: Optional[str] = Field(None, max_length=255, description="Примечание к оборудованию")