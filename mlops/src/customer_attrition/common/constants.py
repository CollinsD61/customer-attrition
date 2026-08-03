CUSTOMER_ID = "customer_id"
SIGNUP_DATE = "signup_date"
AGE = "age"
GENDER = "gender"
ANNUAL_INCOME = "annual_income"
EDUCATION = "education"
MARITAL_STATUS = "marital_status"
DEPENDENTS = "dependents"
TENURE = "tenure"
CONTRACT = "contract"
PAYMENT_METHOD = "payment_method"
PAPERLESS_BILLING = "paperless_billing"
SENIOR_CITIZEN = "senior_citizen"
MONTHLYCHARGES = "monthlycharges"
TOTALCHARGES = "totalcharges"
NUM_SERVICES = "num_services"
HAS_PHONE_SERVICE = "has_phone_service"
HAS_INTERNET_SERVICE = "has_internet_service"
HAS_ONLINE_SECURITY = "has_online_security"
HAS_ONLINE_BACKUP = "has_online_backup"
HAS_DEVICE_PROTECTION = "has_device_protection"
HAS_TECH_SUPPORT = "has_tech_support"
HAS_STREAMING_TV = "has_streaming_tv"
HAS_STREAMING_MOVIES = "has_streaming_movies"
CUSTOMER_SATISFACTION = "customer_satisfaction"
NUM_COMPLAINTS = "num_complaints"
NUM_SERVICE_CALLS = "num_service_calls"
LATE_PAYMENTS = "late_payments"
AVG_MONTHLY_GB = "avg_monthly_gb"
DAYS_SINCE_LAST_INTERACTION = "days_since_last_interaction"
CREDIT_SCORE = "credit_score"
CHURN = "churn"

CATEGORICAL_COLS = [
    GENDER,
    EDUCATION,
    MARITAL_STATUS,
    CONTRACT,
    PAYMENT_METHOD,
    PAPERLESS_BILLING,
]

NUMERIC_COLS = [
    AGE,
    ANNUAL_INCOME,
    DEPENDENTS,
    TENURE,
    MONTHLYCHARGES,
    TOTALCHARGES,
    NUM_SERVICES,
    CUSTOMER_SATISFACTION,
    NUM_COMPLAINTS,
    NUM_SERVICE_CALLS,
    LATE_PAYMENTS,
    AVG_MONTHLY_GB,
    DAYS_SINCE_LAST_INTERACTION,
    CREDIT_SCORE,
]

BOOLEAN_COLS = [
    SENIOR_CITIZEN,
    HAS_PHONE_SERVICE,
    HAS_INTERNET_SERVICE,
    HAS_ONLINE_SECURITY,
    HAS_ONLINE_BACKUP,
    HAS_DEVICE_PROTECTION,
    HAS_TECH_SUPPORT,
    HAS_STREAMING_TV,
    HAS_STREAMING_MOVIES,
]
