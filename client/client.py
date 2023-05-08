import tkinter as tk
from tkinter import messagebox

import socket

def send_to_server(data, operation):

    username = data[0]
    password = data[1]
    if operation == "Login": operation = 1
    elif operation == "Sign Up": operation = 2

    # Crea un socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conecta el cliente al servidor en la direccion y puerto especificados
    server_address = ('172.18.2.2', 5000)
    client_socket.connect((server_address))

    try:
        # Envía los valores de inicio de sesion al servidor
        message = f"{username}:{password}:{operation}"
        client_socket.sendall(message.encode())

        # Espera la respuesta del servidor
        response = client_socket.recv(1024)
        print(response.decode())

    finally:
        # Cierra la conexion
        client_socket.close()

#------------------------------------------------------------------------------------------------------------------------------------------

def validate(user, user_password):
    # Obtiene los valores ingresados por el usuario
    username = user.get()
    password = user_password.get() 

    # Verifica si los campos estan vacios
    if not username or not password:
        messagebox.showwarning("Error", "¨Please, fill all the fields")
        return
    else: 
        entered_data = [username, password]
        return entered_data

def create_action_window(btn_function):
    # Crea la nueva ventana
    window = tk.Tk()
    window.geometry("300x150")
    window.title(btn_function)

    # Crea los elementos de la interfaz de usuario
    label_username = tk.Label(window, text="User:")
    entry_username = tk.Entry(window)
    label_password = tk.Label(window, text="Password:")
    entry_password = tk.Entry(window, show="*")
    button_action = tk.Button(window, text=btn_function, command = lambda: send_to_server(validate(entry_username, entry_password), btn_function))
    button_main = tk.Button(window, text="Back", command = lambda: [window.destroy(), create_main_window()])

    # Ubica los elementos en la ventana
    label_username.pack()
    entry_username.pack()
    label_password.pack()
    entry_password.pack()
    button_action.pack()
    button_main.pack()

def create_main_window():
    main_window = tk.Tk()
    main_window.geometry("300x150")
    main_window.title("Main")
    label_welcome = tk.Label(main_window, text="Welcome!")
    button_login = tk.Button(main_window, text="Login", command = lambda: [main_window.destroy(), create_action_window("Login")])
    button_signup = tk.Button(main_window, text="Sign Up", command = lambda: [main_window.destroy(), create_action_window("Sign Up")])

    label_welcome.pack()
    button_login.pack()
    button_signup.pack()
    main_window.mainloop()

create_main_window()

# Ejecuta el bucle principal de la ventana
