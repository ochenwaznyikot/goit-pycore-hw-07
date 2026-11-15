from collections import UserDict
from datetime import datetime, date, timedelta


def input_error(func):
    """Перехоплює помилки введення й повертає зрозуміле повідомлення."""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter the argument for the command."
        except KeyError:
            return "Contact not found."
    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            parsed = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(parsed)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "-"
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, number):
        for p in self.phones:
            if p.value == number:
                return p
        return None

    def remove_phone(self, number):
        phone = self.find_phone(number)
        if phone is None:
            raise ValueError("Phone number not found.")
        self.phones.remove(phone)

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if phone is None:
            raise ValueError("Phone number not found.")
        new_phone = Phone(new_number)  # спочатку перевіряємо новий номер
        self.phones[self.phones.index(phone)] = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)  # поле одне, нове замінює старе


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue
            born = record.birthday.value

            try:
                this_year = born.replace(year=today.year)
            except ValueError:  # 29 лютого
                this_year = date(today.year, 3, 1)
            if this_year < today:
                try:
                    this_year = born.replace(year=today.year + 1)
                except ValueError:
                    this_year = date(today.year + 1, 3, 1)

            if 0 <= (this_year - today).days <= 7:
                congratulation = this_year
                if congratulation.weekday() >= 5:  # субота/неділя -> понеділок
                    congratulation += timedelta(days=7 - congratulation.weekday())
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation.strftime("%d.%m.%Y"),
                })
        return upcoming


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.lower(), args


@input_error
def add_contact(args, book):
    name, phone = args[0], args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args[0], args[1], args[2]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book):
    record = book.find(args[0])
    if record is None:
        raise KeyError(args[0])
    return "; ".join(p.value for p in record.phones) or "No phones saved."


@input_error
def show_all(args, book):
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    name, birthday = args[0], args[1]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book):
    record = book.find(args[0])
    if record is None:
        raise KeyError(args[0])
    if record.birthday is None:
        return "Birthday not set."
    return str(record.birthday)


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next week."
    return "\n".join(f"{u['name']}: {u['congratulation_date']}" for u in upcoming)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

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