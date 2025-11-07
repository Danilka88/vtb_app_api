"""
Модуль, определяющий Pydantic схемы для запросов, связанных с платежами.
Включает схемы для инициации разовых платежей и для работы с VRP (Variable Recurring Payments).
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Transaction(BaseModel):
    """
    Модель данных для финансовой транзакции.
    """
    transaction_id: str = Field(..., description="Уникальный идентификатор транзакции")
    bank_name: str = Field(..., description="Название банка, где произошла транзакция")
    account_id: str = Field(..., description="Идентификатор счета, к которому относится транзакция")
    description: str = Field(..., description="Описание транзакции")
    amount: float = Field(..., description="Сумма транзакции (положительная для дохода, отрицательная для расхода)")
    currency: str = Field(..., description="Валюта транзакции (например, 'RUB', 'USD')")
    type: str = Field(..., description="Тип транзакции ('income' или 'expense')")
    category: str = Field(..., description="Категория транзакции (например, 'Food', 'Salary')")
    date: str = Field(..., description="Дата и время транзакции в формате ISO 8601")


class CreditorAccount(BaseModel):

    """

    Схема для представления счета получателя платежа (кредитора).

    """

    scheme_name: str = Field(alias='schemeName') # Схема идентификации счета (например, RU.CBR.PAN)

    identification: str = Field(alias='identification') # Идентификатор счета

    name: str = Field(alias='Name') # Имя владельца счета

    model_config = ConfigDict(populate_by_name=True)



class DebtorAccount(BaseModel):

    """

    Схема для представления счета отправителя платежа (дебитора).

    """

    scheme_name: str = Field(alias='schemeName') # Схема идентификации счета (например, RU.CBR.PAN)

    identification: str = Field(alias='identification') # Идентификатор счета

    model_config = ConfigDict(populate_by_name=True)



class InstructedAmount(BaseModel):

    """

    Схема для представления суммы платежа.

    """

    amount: str = Field(alias='Amount') # Сумма платежа в виде строки (например, "100.00")

    currency: str = Field(alias='Currency') # Валюта платежа (например, "RUB")

    model_config = ConfigDict(populate_by_name=True)



class PaymentInitiation(BaseModel):

    """

    Вложенный объект Initiation, содержащий детали инструкции по платежу.

    """

    instructed_amount: InstructedAmount = Field(alias='InstructedAmount') # Сумма и валюта платежа

    debtor_account: DebtorAccount = Field(alias='DebtorAccount') # Счет дебитора

    creditor_account: CreditorAccount = Field(alias='CreditorAccount') # Счет кредитора

    instruction_identification: str = Field(alias='InstructionIdentification') # Уникальный идентификатор инструкции

    end_to_end_identification: str = Field(alias='EndToEndIdentification') # Сквозной идентификатор платежа

    model_config = ConfigDict(populate_by_name=True)



class PaymentData(BaseModel):

    """

    Объект Data, содержащий только объект Initiation для платежа.

    """

    initiation: PaymentInitiation = Field(alias='Initiation') # Детали инициации платежа

    model_config = ConfigDict(populate_by_name=True)



class PaymentRisk(BaseModel):

    """

    Объект Risk, содержащий информацию о рисках платежа.

    В песочнице может быть пустым, но в реальных условиях может содержать поля типа 'paymentContextCode'.

    """

    model_config = ConfigDict(populate_by_name=True)



class PaymentInitiationRequest(BaseModel):



    """



    Основная модель для запроса на инициацию разового платежа.



    Соответствует структуре запроса API банка.



    """



    data: PaymentData = Field(alias='Data') # Данные платежа



    risk: PaymentRisk = Field(alias='Risk') # Информация о рисках



    model_config = ConfigDict(populate_by_name=True)











class PaymentConsentCreateRequest(BaseModel):



    """



    Модель запроса для создания нового согласия на оплату.



    """



    bank_name: str



    user_id: str



    permissions: list[str] = ["CreateDomesticSinglePayment"]



    debtor_account: str



    amount: str










# --- Схемы для VRP ---

class VRPControlParameters(BaseModel):
    """
    Схема для параметров контроля VRP (Variable Recurring Payments).
    Определяет ограничения для периодических платежей.
    """
    MaximumIndividualAmount: InstructedAmount # Максимальная сумма одного платежа
    PeriodicLimits: list[dict] # Периодические лимиты (например, в день, неделю, месяц)
    ValidFromDateTime: Optional[str] = None # Дата и время начала действия согласия
    ValidToDateTime: Optional[str] = None # Дата и время окончания действия согласия
    model_config = ConfigDict(populate_by_name=True)

class VRPConsentRequest(BaseModel):
    """
    Схема для запроса на создание согласия VRP.
    """
    Data: 'VRPData' # Данные для VRP согласия
    model_config = ConfigDict(populate_by_name=True)

class VRPInstruction(BaseModel):
    """
    Схема для инструкции VRP платежа.
    """
    InstructionIdentification: str # Идентификатор инструкции
    EndToEndIdentification: str # Сквозной идентификатор
    InstructedAmount: InstructedAmount # Сумма и валюта
    CreditorAccount: CreditorAccount # Счет получателя
    model_config = ConfigDict(populate_by_name=True)

class VRPPaymentData(BaseModel):
    """
    Схема для данных VRP платежа.
    """
    ConsentId: str # Идентификатор VRP согласия
    Instruction: VRPInstruction # Инструкция по платежу
    model_config = ConfigDict(populate_by_name=True)

class VRPPaymentRequest(BaseModel):
    """
    Основная модель для запроса на выполнение VRP платежа.
    """
    Data: VRPPaymentData # Данные VRP платежа
    model_config = ConfigDict(populate_by_name=True)

class VRPData(BaseModel):
    """
    Схема для данных VRP согласия.
    """
    Permissions: list[str] = ["CreateDomesticVRPSinglePayment"] # Разрешения для VRP
    ControlParameters: VRPControlParameters # Параметры контроля VRP
    DebtorAccount: DebtorAccount # Счет дебитора
    model_config = ConfigDict(populate_by_name=True)

