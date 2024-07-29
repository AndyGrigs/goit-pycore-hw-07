import re
from collections import UserDict
from datetime import timedelta, datetime, date

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def validate(self):
        pattern = r'^\d{10}$'
        if not re.match(pattern, self.value):
            raise ValueError('Invalid phone number format. Must be 10 digits.')

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        phone_obj.validate()  # Let the exception propagate if invalid
        self.phones.append(phone_obj)

    def remove_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                self.phones.remove(phone)
                break

    def edit_phone(self, old_phone_value, new_phone_value):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone_value:
                phone_obj = Phone(new_phone_value)
                phone_obj.validate()
                self.phones[i] = phone_obj
                break

    def find_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                return phone
        return None
    
    def add_birthday(self, birthday_date):
        self.birthday = Birthday(birthday_date)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.__setitem__(record.name.value, record)

    def find(self, name):
        return self.get(name)

    def delete(self, name):
        del self[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming_birthdays = []
        one_week_from_today = today + timedelta(days=days)

        for record in self.values():
            birthday = getattr(record, 'birthday', None)
            if birthday is not None:
                # Create a birthday date object for the current year
                birthday_this_year = date(today.year, birthday.date.month, birthday.date.day)
                
                # If birthday has already passed this year, use the next year
                if birthday_this_year < today:
                    birthday_this_year = date(today.year + 1, birthday.date.month, birthday.date.day)
                
                if birthday_this_year <= one_week_from_today:
                    if birthday_this_year.weekday() >= 5:  # If birthday falls on a weekend
                        next_monday = birthday_this_year + timedelta(days=(7 - birthday_this_year.weekday()))
                        congratulation_date = next_monday
                    else:
                        congratulation_date = birthday_this_year
                    
                    upcoming_birthdays.append({
                        'name': record.name.value,
                        'congratulation_date': congratulation_date.strftime("%d.%m.%Y")
                    })

        return upcoming_birthdays

def input_error(handler):
    def wrapper(args, book):
        try:
            return handler(args, book)
        except (ValueError, IndexError) as e:
            return f"Error: {e}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    phones = "; ".join(str(phone) for phone in record.phones)
    return f"Phones for {name}: {phones}"

@input_error
def show_all(args, book: AddressBook):
    if not book:
        return "Address book is empty."
    result = []
    for name, record in book.items():
        phones = "; ".join(str(phone) for phone in record.phones)
        result.append(f"{name}: {phones}")
    return "\n".join(result)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None or not record.birthday:
        return "Birthday not found."
    return f"Birthday for {name}: {record.birthday.date.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays(7)
    if not upcoming_birthdays:
        return "No birthdays in the upcoming week."
    return "\n".join(f"{entry['name']}: {entry['congratulation_date']}" for entry in upcoming_birthdays)

def parse_input(user_input):
    return user_input.strip().split()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
