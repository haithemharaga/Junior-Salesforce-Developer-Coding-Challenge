"# Junior-Salesforce-Developer-Coding-Challenge" 
1. Python Coding Challenge Solution
Design Choices & Rationale
Language: Python, as requested.
Object-Oriented Approach:
Position Enum: To represent the defined positions and their hierarchy. Using an Enum makes the code more readable and less prone to typos with string comparisons. I'll assign integer values to the enum members to easily represent seniority for sorting.
Contact Class: To represent a contact, holding their details and a reference to their parent account's ID.
Account Class: To represent an account, holding its details, a list of its Contact objects, and the summary fields (total_number_of_contacts, number_of_finance_employees, main_contact_id).
CompanyService Class: This will act as a wrapper or service layer to manage accounts and contacts, and implement the two required methods. This separates the core business logic from the data models themselves. It will also simulate a "database" using in-memory lists for simplicity.
ID Generation: For simplicity in this challenge, I'll use simple incrementing integers for Account and Contact IDs, managed by the CompanyService. In a real application, UUIDs or database-generated IDs would be preferred.
Main Contact Logic: The sorting for the main contact will use Python's sorted function with a custom key, prioritizing Position (higher value is better) and then Years Of Service (higher value is better).
Error Handling: Basic error handling (e.g., account not found) will be included.

Class Definitions Code explaination

Explanation:
Position(Enum):
Defines the allowed job positions.
Assigns integer values: CEO=4 (highest) down to ADMINISTRATIVE=1 (lowest). This makes sorting by position straightforward.
from_string class method: A utility to convert a string like "Finance" or "Operational Manager" into the corresponding Position enum member. It handles case-insensitivity and spaces.
Contact Class:
__init__: Constructor to initialize a Contact object with its attributes.
account_id: Stores the ID of the Account this Contact belongs to. This establishes the link.
__repr__: Provides a string representation of the object, useful for debugging.
Account Class:
__init__: Constructor for Account objects.
main_contact_id: Will store the ID of the main Contact. Initialized to None.
total_number_of_contacts, number_of_finance_employees: Counters, initialized to 0.
contacts: List[Contact]: An important attribute. Instead of just storing IDs, this Account object will hold a list of its actual Contact objects. This makes accessing contacts for an account very easy within our Python model.
get_percentage_of_finance_employees(): A method to calculate the percentage as per Q2 of the Salesforce questions. It's part of the Python model here but represents the formula field logic.
__repr__: String representation for debugging.



Service Class (CompanyService)
This class will manage the creation of contacts and setting the main contact. It will also act as a simple in-memory "database" for our accounts and contacts.

__init__:
_accounts, _contacts: Dictionaries to store Account and Contact objects, keyed by their respective IDs. This simulates database tables.
_next_account_id, _next_contact_id: Simple counters for generating unique IDs.
create_account: A helper method mainly for setting up test data.
get_account, get_contact: Helper methods to retrieve objects by ID.
create_contact method (Method 1):
Finds the parent_account using account_id. If not found, it prints an error and returns None.
Converts the position_str (e.g., "Finance") into a Position enum member using Position.from_string().
Generates a new contact_id.
Creates a Contact object.
Adds the new contact to the _contacts dictionary (our global contact list) and, importantly, appends it to the parent_account.contacts list. This directly links the contact object to its account object.
Increments parent_account.total_number_of_contacts.
Checks if new_contact.position is Position.FINANCE and, if so, increments parent_account.number_of_finance_employees.
Returns the created Contact object.
set_main_contact_on_account method (Method 2):
Finds the account using account_id.
Checks if the account has any contacts. If not, sets main_contact_id to None.
Sorting Logic: This is the core.
sorted(account.contacts, key=lambda c: (c.position.value, c.years_of_service), reverse=True)
It sorts the account.contacts list.
The key is a lambda function that tells sorted what to sort by.
lambda c: (c.position.value, c.years_of_service): For each contact c, it creates a tuple: (position_value, years_of_service).
c.position.value: Uses the integer value of the enum (e.g., CEO is 4, Finance is 2).
reverse=True: Sorts in descending order. So, higher position values come first. If position values are tied, higher years of service come first.
The first contact in sorted_contacts (i.e., sorted_contacts[0]) is the most senior one.
Sets account.main_contact_id to the ID of this most senior contact.
Returns the main Contact object.


Test Class (unittest)

Explanation of TestCompanyService:
import unittest: Imports the testing framework.
class TestCompanyService(unittest.TestCase): Defines a test suite. All test methods must start with test_.
setUp(self): This method is run before each test method. It's used to set up a clean environment for each test (e.g., creating a new CompanyService instance and some default accounts).
Test Methods:
test_create_contact_increments_totals: Verifies that creating contacts correctly updates total_number_of_contacts and number_of_finance_employees on the Account. Also checks if the contact object is correctly added to the account's internal list.
test_create_contact_invalid_account: Checks behavior when trying to create a contact for a non-existent account.
test_create_contact_invalid_position: Checks behavior with an invalid position string.
test_set_main_contact_highest_position: Verifies that the contact with the highest position (CEO) is chosen, even if another contact has more years of service but a lower position.
test_set_main_contact_tie_breaker_years_of_service: Verifies that if multiple contacts have the same highest position, the one with more years of service is chosen.
test_set_main_contact_single_contact: Checks the simple case where an account has only one contact.
test_set_main_contact_no_contacts: Verifies that main_contact_id remains None (or is set to None) if an account has no contacts.
test_percentage_of_finance_employees: Specifically tests the percentage calculation logic.
self.assertEqual(), self.assertIsNotNone(), self.assertIsNone(), self.assertIn(), self.assertAlmostEqual(): These are assertion methods from unittest used to check if conditions are met.