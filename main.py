from auth.login import LoginWindow
from db.database import inicializar_banco

if __name__ == "__main__":
    inicializar_banco()
    LoginWindow().mainloop()

