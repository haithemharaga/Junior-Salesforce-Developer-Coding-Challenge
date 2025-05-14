from enum import Enum
from typing import List, Optional, Dict # Updated typing
import unittest

# --- ENUM DEFINITION ---
class Position(Enum):
    CEO = 4
    OPERATIONAL_MANAGER = 3
    FINANCE = 2
    ADMINISTRATIVE = 1

    @classmethod
    def from_string(cls, s: str):
        try:
            # Normalize: uppercase and replace space with underscore
            normalized_s = s.upper().replace(" ", "_")
            return cls[normalized_s]
        except KeyError:
            # Provide a list of valid options in the error message for better UX
            valid_options = ", ".join([p.name for p in cls])
            raise ValueError(f"'{s}' is not a valid Position. Valid options are: {valid_options}")

# --- CONTACT CLASS ---
class Contact:
    def __init__(self, contact_id: int, first_name: str, last_name: str, 
                 salutation: str, position: Position, years_of_service: int, account_id: int):
        self.id: int = contact_id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.salutation: str = salutation
        self.position: Position = position
        self.years_of_service: int = years_of_service
        self.account_id: int = account_id

    def __repr__(self):
        return (f"Contact(id={self.id}, name='{self.salutation} {self.first_name} {self.last_name}', "
                f"position={self.position.name}, years={self.years_of_service}, account_id={self.account_id})")

# --- ACCOUNT CLASS ---
class Account:
    def __init__(self, account_id: int, account_name: str, account_number: int):
        self.id: int = account_id
        self.account_name: str = account_name
        self.account_number: int = account_number
        self.main_contact_id: Optional[int] = None
        self.total_number_of_contacts: int = 0
        self.number_of_finance_employees: int = 0
        self.contacts: List[Contact] = [] 

    def get_percentage_of_finance_employees(self) -> float:
        if self.total_number_of_contacts == 0:
            return 0.0
        return (self.number_of_finance_employees / self.total_number_of_contacts) * 100

    def __repr__(self):
        return (f"Account(id={self.id}, name='{self.account_name}', number={self.account_number}, "
                f"main_contact_id={self.main_contact_id}, total_contacts={self.total_number_of_contacts}, "
                f"finance_employees={self.number_of_finance_employees})")

# --- SERVICE CLASS ---
class CompanyService:
    def __init__(self):
        self._accounts: Dict[int, Account] = {}
        self._contacts: Dict[int, Contact] = {}
        self._next_account_id: int = 1
        self._next_contact_id: int = 1

    def create_account(self, account_name: str, account_number: int) -> Account:
        account_id = self._next_account_id
        self._next_account_id += 1
        account = Account(account_id, account_name, account_number)
        self._accounts[account_id] = account
        return account

    def get_account(self, account_id: int) -> Optional[Account]:
        return self._accounts.get(account_id)

    def get_contact(self, contact_id: int) -> Optional[Contact]:
        return self._contacts.get(contact_id)

    def create_contact(self, account_id: int, first_name: str, last_name: str,
                       salutation: str, position_str: str, years_of_service: int) -> Optional[Contact]:
        parent_account = self.get_account(account_id)
        if not parent_account:
            # In a real app, might log this or raise a specific exception
            # print(f"Error: Account with ID {account_id} not found.") 
            return None 

        try:
            position_enum = Position.from_string(position_str)
        except ValueError:
            # print(f"Error creating contact: {e}")
            return None

        contact_id = self._next_contact_id
        self._next_contact_id += 1

        new_contact = Contact(
            contact_id=contact_id, first_name=first_name, last_name=last_name,
            salutation=salutation, position=position_enum,
            years_of_service=years_of_service, account_id=parent_account.id
        )

        self._contacts[contact_id] = new_contact
        parent_account.contacts.append(new_contact)
        parent_account.total_number_of_contacts += 1
        if new_contact.position == Position.FINANCE:
            parent_account.number_of_finance_employees += 1
        
        return new_contact

    def set_main_contact_on_account(self, account_id: int) -> Optional[Contact]:
        account = self.get_account(account_id)
        if not account:
            return None

        if not account.contacts:
            account.main_contact_id = None
            return None

        sorted_contacts = sorted(
            account.contacts,
            key=lambda c: (c.position.value, c.years_of_service),
            reverse=True
        )

        main_contact = sorted_contacts[0]
        account.main_contact_id = main_contact.id
        return main_contact

# --- TEST CLASS ---
class TestCompanyService(unittest.TestCase):
    def setUp(self):
        self.service = CompanyService()
        self.account1 = self.service.create_account("TestCorp", 101)
        self.account2 = self.service.create_account("FinanceInc", 102)

    def test_create_contact_increments_totals(self):
        self.assertEqual(self.account1.total_number_of_contacts, 0)
        self.assertEqual(self.account1.number_of_finance_employees, 0)

        contact1 = self.service.create_contact(
            self.account1.id, "John", "Doe", "Mr.", "Operational Manager", 5)
        self.assertIsNotNone(contact1)
        self.assertEqual(self.account1.total_number_of_contacts, 1)
        self.assertEqual(self.account1.number_of_finance_employees, 0)
        self.assertIn(contact1, self.account1.contacts)

        contact2 = self.service.create_contact(
            self.account1.id, "Jane", "Smith", "Ms.", "Finance", 3)
        self.assertIsNotNone(contact2)
        self.assertEqual(self.account1.total_number_of_contacts, 2)
        self.assertEqual(self.account1.number_of_finance_employees, 1)
        self.assertIn(contact2, self.account1.contacts)
        self.assertAlmostEqual(self.account1.get_percentage_of_finance_employees(), 50.0)

    def test_create_contact_invalid_account(self):
        contact = self.service.create_contact(999, "Ghost", "User", "Mx.", "CEO", 10)
        self.assertIsNone(contact)

    def test_create_contact_invalid_position(self):
        contact = self.service.create_contact(
            self.account1.id, "Error", "Prone", "Dr.", "NonExistentPosition", 1)
        self.assertIsNone(contact)
        self.assertEqual(self.account1.total_number_of_contacts, 0)

    def test_set_main_contact_highest_position(self):
        contact_admin = self.service.create_contact(self.account1.id, "Admin", "User", "Mx.", "Administrative", 2)
        contact_ceo = self.service.create_contact(self.account1.id, "CEO", "Boss", "Mr.", "CEO", 5)
        contact_finance = self.service.create_contact(self.account1.id, "Finance", "Guy", "Ms.", "Finance", 10)

        main_contact_obj = self.service.set_main_contact_on_account(self.account1.id)
        self.assertIsNotNone(main_contact_obj)
        self.assertEqual(self.account1.main_contact_id, contact_ceo.id)
        self.assertEqual(main_contact_obj.id, contact_ceo.id)

    def test_set_main_contact_tie_breaker_years_of_service(self):
        ceo_junior = self.service.create_contact(self.account1.id, "Junior", "CEO", "Ms.", "CEO", 5)
        ceo_senior = self.service.create_contact(self.account1.id, "Senior", "CEO", "Mr.", "CEO", 10)
        self.service.create_contact(self.account1.id, "Ops", "Manager", "Mx.", "Operational Manager", 12)

        self.service.set_main_contact_on_account(self.account1.id)
        self.assertEqual(self.account1.main_contact_id, ceo_senior.id)

    def test_set_main_contact_single_contact(self):
        contact1 = self.service.create_contact(self.account1.id, "Solo", "Person", "Dr.", "Finance", 3)
        self.service.set_main_contact_on_account(self.account1.id)
        self.assertEqual(self.account1.main_contact_id, contact1.id)

    def test_set_main_contact_no_contacts(self):
        self.service.set_main_contact_on_account(self.account2.id)
        self.assertIsNone(self.account2.main_contact_id)

    def test_percentage_of_finance_employees(self):
        self.assertEqual(self.account2.get_percentage_of_finance_employees(), 0.0)
        self.service.create_contact(self.account2.id, "Fin", "One", "Mr.", "Finance", 5)
        self.service.create_contact(self.account2.id, "Ops", "Two", "Ms.", "Operational Manager", 3)
        self.service.create_contact(self.account2.id, "Fin", "Three", "Mx.", "Finance", 1)
        self.service.create_contact(self.account2.id, "Admin", "Four", "Dr.", "Administrative", 7)
        
        self.assertEqual(self.account2.number_of_finance_employees, 2)
        self.assertEqual(self.account2.total_number_of_contacts, 4)
        self.assertAlmostEqual(self.account2.get_percentage_of_finance_employees(), 50.0)

        self.service.create_contact(self.account2.id, "CEO", "Five", "Mr.", "CEO", 10)
        self.assertEqual(self.account2.number_of_finance_employees, 2)
        self.assertEqual(self.account2.total_number_of_contacts, 5)
        self.assertAlmostEqual(self.account2.get_percentage_of_finance_employees(), 40.0)

if __name__ == '__main__':
    unittest.main()