import tkinter as tk
from tkinter import messagebox

import socket

def send_to_server(data, operation):

    if data == False: return
     # Crea un socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conecta el cliente al servidor en la direccion y puerto especificados
    server_address = ('172.18.2.3', 5000)
    client_socket.connect((server_address))

    username = data[0]
    if operation == "Login": operation = 1
    elif operation == "Sign Up": operation = 2
    elif operation == "Join Group": operation = 3
    elif operation == "Create Group": operation = 4

    try:
        # Envía los valores de inicio de sesion al servidor
        # data[1] puede ser password o groupname, dependiendo de la opcion seleccionada
        message = f"{encryption(username)}:{encryption(data[1])}:{operation}"
        client_socket.sendall(message.encode())

        # Espera la respuesta del servidor
        response = client_socket.recv(1024)
        print(response.decode())

    finally:
        # Cierra la conexion
        client_socket.close()

def encryption(data):
    
    key = 'puropinchechensomanalv'
    encrypted = ""
    for i in range(len(data)):
        # Aplica el XOR entre el carácter del mensaje y el carácter de la clave
        # Utiliza la función chr() para convertir el resultado de nuevo en un carácter
        encrypted += chr(ord(data[i]) ^ ord(key[i % len(key)]))
        
    return encrypted


#------------------------------------------------------------------------------------------------------------------------------------------

def validate(data):

    # Verifica si los campos estan vacios
    if not data.get():
        messagebox.showwarning("Error", "¨Please, fill all the fields")
        return
    else: 
        return data.get()

def create_users_window(btn_function):
    
    # Crea la nueva ventana
    users_window = tk.Tk()
    users_window.geometry("300x150")
    users_window.title(btn_function)

    # Crea los elementos de la interfaz de usuario
    label_username = tk.Label(users_window, text="User:")
    entry_username = tk.Entry(users_window)
    label_password = tk.Label(users_window, text="Password:")
    entry_password = tk.Entry(users_window, show="*")
    # Envía a la funcion "send_to_server" los datos despues de verificar que los campos no estén vacíos como un parámetro, así como el tipo de acción que realizará
    if btn_function == "Sign Up":
        button_action = tk.Button(users_window, text=btn_function, command = lambda: [send_to_server([validate(entry_username), validate(entry_password)], btn_function)])
    elif btn_function == "Login":
        button_action = tk.Button(users_window, text=btn_function, command = lambda: [send_to_server([validate(entry_username), validate(entry_password)], btn_function), 
                                                                                      create_users_options_window(validate(entry_username)), users_window.destroy()])
        
    button_main = tk.Button(users_window, text="Back", command = lambda: [create_main_window(), users_window.destroy()])

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
    button_login = tk.Button(main_window, text="Login", command = lambda: [create_users_window("Login"), main_window.destroy()])
    button_signup = tk.Button(main_window, text="Sign Up", command = lambda: [create_users_window("Sign Up"), main_window.destroy()])

    label_welcome.pack()
    button_login.pack()
    button_signup.pack()
    main_window.mainloop()

def create_users_options_window(user):
    if user is not False:
        user_options_window = tk.Tk()
        user_options_window.geometry("300x150")
        user_options_window.title("User Options")
        label_greetings = tk.Label(user_options_window, text=(f"Greetings, {user}! Please select an option"))
        button_join = tk.Button(user_options_window, text="Join an existing group", command = lambda: [create_groups_window("Join Group", user), user_options_window.destroy()])
        button_create = tk.Button(user_options_window, text="Create a new group", command = lambda: [create_groups_window("Create Group", user), user_options_window.destroy()])
        button_main = tk.Button(user_options_window, text="Return to main screen", command = lambda: [user_options_window.destroy(), create_main_window()])

        label_greetings.pack()
        button_join.pack()
        button_create.pack()
        button_main.pack()

def create_groups_window(btn_function, user):
    # Crea la nueva ventana
    groups_window = tk.Tk()
    groups_window.geometry("300x150")
    groups_window.title(btn_function)

    # Crea los elementos de la interfaz de usuario
    label_groupname = tk.Label(groups_window, text="Group Name:")
    entry_groupname = tk.Entry(groups_window)
    # Envía a la funcion "send_to_server" los datos despues de verificar que los campos no estén vacíos como un parámetro, así como el tipo de acción que realizará
    button_action = tk.Button(groups_window, text=btn_function, command = lambda: send_to_server([user, validate(entry_groupname)], btn_function))
    button_main = tk.Button(groups_window, text="Back", command = lambda: [create_users_options_window(user), groups_window.destroy()])

    # Ubica los elementos en la ventana
    label_groupname.pack()
    entry_groupname.pack()
    button_action.pack()
    button_main.pack()

create_main_window()

# Ejecuta el bucle principal de la ventana
