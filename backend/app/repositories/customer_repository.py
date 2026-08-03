from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_customer_id(self, customer_id: str) -> Customer | None:
        return (
            self._db.query(Customer).filter(Customer.customer_id == customer_id).first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        return self._db.query(Customer).offset(skip).limit(limit).all()

    def create(self, customer: Customer) -> Customer:
        self._db.add(customer)
        self._db.commit()
        self._db.refresh(customer)
        return customer

    def update(self, customer_id: str, updates: dict) -> Customer | None:
        customer = self.get_by_customer_id(customer_id)
        if customer is None:
            return None
        updates["updated_at"] = datetime.now(UTC)
        for key, value in updates.items():
            setattr(customer, key, value)
        self._db.commit()
        self._db.refresh(customer)
        return customer

    def delete(self, customer_id: str) -> bool:
        customer = self.get_by_customer_id(customer_id)
        if customer is None:
            return False
        self._db.delete(customer)
        self._db.commit()
        return True
