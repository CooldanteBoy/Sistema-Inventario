from database import Database
from ui import LoginWindow


def main():
    db = Database()
    login = LoginWindow(db)
    login.mainloop()


if __name__ == "__main__":
    main()
