import enum

class UserRole(str, enum.Enum):
    ADMINISTRADOR = "administrador"
    OPERATIVO = "operativo"
    JURIDICO = "juridico"
    FINANCIERO = "financiero"

class ModuleType(str, enum.Enum):
    DASHBOARD = "dashboard"
    SITES = "sites"
    CONTRACTS = "contracts"
    INCIDENTS = "incidents"
    MAINTENANCE = "maintenance"
    INVENTORY = "inventory"
    REPORTS = "reports"
    FINANCES = "finances"
    USERS = "users"

class PermissionAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"

class PaymentFrequency(str, enum.Enum):
    SINGLE = "single"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"

class ExpenseCategory(str, enum.Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    RENT = "rent"
    INSURANCE = "insurance"
    EQUIPMENT = "equipment"
    SERVICES = "services"
    OTHER = "other"

class ContractType(str, enum.Enum):
    LEASE = "lease"
    SERVICE = "service"
    MAINTENANCE = "maintenance"
    SUPPLY = "supply"
    OTHER = "other"

class ContractStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

class NotificationTypeEnum(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class PriorityEnum(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationPriorityEnum(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"