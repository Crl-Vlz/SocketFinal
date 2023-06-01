import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import socket


def make_socket(ip: str, port: int):
    try:
        # Crea un socket TCP/IP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Attempting to connect to {ip}:{port}")
        # Conecta el cliente al servidor en la direccion y puerto especificados
        client_socket.connect((ip, port))
        return client_socket
    except ConnectionRefusedError:
        return None


def create_socket():
    # Crea un socket TCP/IP
    client_socket = make_socket("172.18.2.2", 5000)
    if not client_socket:
        client_socket = make_socket("172.18.2.2", 5001)
    return client_socket


def send_to_server(username, data, operation):
    if not username or not data:
        messagebox.showwarning("Error", "¨Please, fill all the fields")
        return

    # Crea un socket TCP/IP
    client_socket = create_socket()

    if operation == "Login":
        operation = 1
    elif operation == "Sign Up":
        operation = 2
    elif operation == "Join Group":
        operation = 3
    elif operation == "Create Group":
        operation = 4
    elif operation == "View Groups":
        operation = 5
    elif operation == "Enter Group":
        operation = 6
    elif operation == "Send message":
        operation = 7

    try:
        # Envía los valores de inicio de sesion al servidor
        # data puede ser password o groupname, dependiendo de la opcion seleccionada
        message = f"{username}:{data}:{operation}"
        print(message)
        message = encryption(message)
        print(f"{message}")
        client_socket.sendall(message.encode())

        # Espera la respuesta del servidor
        response = client_socket.recv(1024)
        response = encryption(response.decode())

    finally:
        # Cierra la conexion
        client_socket.close()
        if response != "accept" and operation != 5:
            messagebox.showwarning("Error", "Wrong username or password")
        return response


def encryption(data):
    key = "puropinchechensomanalv"
    encrypted = ""
    for i in range(len(data)):
        # Aplica el XOR entre el carácter del mensaje y el carácter de la clave
        # Utiliza la función chr() para convertir el resultado de nuevo en un carácter
        letter = ord(data[i]) ^ ord(key[i % len(key)])
        if data[i] == key[i % len(key)]:
            letter = ord(data[i])
        if letter == 0:
            letter = ord(key[i % len(key)])
        encrypted += chr(letter)

    return encrypted


# ------------------------------------------------------------------------------------------------------------------------------------------


def create_users_window(
    btn_function,
):  # crea la ventana de usuarios, donde el usuario puede registrarse o iniciar sesión
    # Crea la nueva ventana
    users_window = tk.Tk()
    users_window.geometry("300x150")
    users_window.title(btn_function)

    # Crea los elementos de la interfaz de usuario
    label_username = tk.Label(users_window, text="User:")
    entry_username = tk.Entry(users_window)
    label_password = tk.Label(users_window, text="Password:")
    entry_password = tk.Entry(users_window, show="*")
    # Envía a la funcion "send_to_server" los datos despues de verificar que los campos no estén vacíos como un parámetro,
    # así como el tipo de acción que realizará
    if btn_function == "Sign Up":
        button_action = tk.Button(
            users_window,
            text=btn_function,
            command=lambda: [
                send_to_server(entry_username.get(), entry_password.get(), btn_function)
            ],
        )
    elif btn_function == "Login":
        button_action = tk.Button(
            users_window,
            text=btn_function,
            command=lambda: create_users_options_window(
                entry_username.get(),
                send_to_server(
                    entry_username.get(), entry_password.get(), btn_function
                ),
                users_window,
            ),
        )

    button_main = tk.Button(
        users_window,
        text="Back",
        command=lambda: [users_window.destroy(), create_main_window()],
    )

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
    button_login = tk.Button(
        main_window,
        text="Login",
        command=lambda: [create_users_window("Login"), main_window.destroy()],
    )
    button_signup = tk.Button(
        main_window,
        text="Sign Up",
        command=lambda: [create_users_window("Sign Up"), main_window.destroy()],
    )

    label_welcome.pack()
    button_login.pack()
    button_signup.pack()
    main_window.mainloop()


def see_lobby(client_socket, username, data, operation):
    message = f"{username}:{data}:{operation}"
    print(message)
    message = encryption(message)
    client_socket.sendall(message.encode())


def create_users_options_window(
    user, auth, users_window
):  # ventana donde el usuario ve las opciones que tiene, crear grupo, unirse a grupo
    # o entrar al lobby donde puede ver los grupos a los que pertenece
    users_window.destroy()  # cierra la ventana anterior

    if (
        auth == "accept"
    ):  # si el usuario hizo login exitosamente, creará los elementos de la ventana
        user_options_window = tk.Tk()
        user_options_window.geometry("300x150")
        user_options_window.title("User Options")
        label_greetings = tk.Label(
            user_options_window, text=(f"Greetings, {user}! Please select an option")
        )
        button_join = tk.Button(
            user_options_window,
            text="Join an existing group",
            command=lambda: [
                create_groups_options_window("Join Group", user),
                user_options_window.destroy(),
            ],
        )
        button_create = tk.Button(
            user_options_window,
            text="Create a new group",
            command=lambda: [
                create_groups_options_window("Create Group", user),
                user_options_window.destroy(),
            ],
        )
        button_view = tk.Button(
            user_options_window,
            text="Lobby",
            command=lambda: [create_lobby_window(user), user_options_window.destroy()],
        )
        button_main = tk.Button(
            user_options_window,
            text="Return to main screen",
            command=lambda: [user_options_window.destroy(), create_main_window()],
        )
        label_greetings.pack()
        button_join.pack()
        button_create.pack()
        button_view.pack()
        button_main.pack()

    else:
        create_main_window()


def create_groups_options_window(
    btn_function, user
):  # ventana donde puedes crear o unirte a un grupo
    # depende de la opción que se eligió, mostrará botón para crear o unirse
    # Crea la nueva ventana
    group_options_window = tk.Tk()
    group_options_window.geometry("300x150")
    group_options_window.title(btn_function)

    # Crea los elementos de la interfaz de usuario
    label_groupname = tk.Label(group_options_window, text="Group Name:")
    entry_groupname = tk.Entry(group_options_window)
    # Envía a la funcion "send_to_server" los datos entrados, así como el tipo de acción que realizará
    button_action = tk.Button(
        group_options_window,
        text=btn_function,
        command=lambda: send_to_server(user, entry_groupname.get(), btn_function),
    )
    button_back = tk.Button(
        group_options_window,
        text="Back",
        command=lambda: [
            create_users_options_window(user, "accept", group_options_window),
            group_options_window.destroy(),
        ],
    )

    # Ubica los elementos en la ventana
    label_groupname.pack()
    entry_groupname.pack()
    button_action.pack()
    button_back.pack()


def see_chat(username, data, operation):
    client_socket = create_socket()
    message = f"{username}:{data}:{operation}"
    print(message)
    message = encryption(message)
    client_socket.sendall(message.encode())  # type: ignore
    client_socket.close()  # type: ignore


def create_lobby_window(
    user,
):  # ventana del lobby, donde se muestran los usuarios registrados y los grupos a los que se pertenece
    lobby_window = tk.Tk()
    lobby_window.geometry("300x150")
    lobby_window.title(f"{user}'s Lobby")
    client_socket = create_socket()

    see_lobby(client_socket, user, "", 5)

    # Crear un widget Canvas
    canvas = tk.Canvas(lobby_window)
    # Crear un frame dentro del Canvas para contener los botones
    frame = tk.Frame(canvas)
    frame.pack(side=tk.RIGHT, fill=tk.X)

    # Agregar un scrollbar al Canvas
    scrollbar = ttk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    canvas.configure(yscrollcommand=scrollbar.set)

    # existing_groups = 20  # simulador de grupos, se ejecutará esta linea cuando ya se tengan los grupos en un archivo
    buttons = []
    response = ""
    # los grupos se muestran como botones, cuando das click a uno te abre la ventana del chatroom de ese grupo
    response = client_socket.recv(1024)
    arr = response.decode().split()
    for i in range(len(arr)):
        if arr[i] != "\x11\x16\x11" and arr[i] != "p":
            buttons.append(tk.Button(frame, text=f"{arr[i]}"))

    client_socket.close()

    for button in buttons:
        groupname = button.cget("text").split("(")

        # Utilizar una función de fábrica para crear una lambda con su propia copia de groupname
        def create_lambda(group):
            return lambda: [
                create_chatroom_window(user, f"{group[0]}"),
                lobby_window.destroy(),
            ]

        button["command"] = create_lambda(groupname)
        button.pack(pady=2)

    frame.update_idletasks()  # Actualizar el tamaño del frame interior
    canvas.config(scrollregion=canvas.bbox("all"))  # Configurar el tamaño del Canvas

    button_back = tk.Button(
        lobby_window,
        text="Back",
        command=lambda: [create_users_options_window(user, "accept", lobby_window)],
    )
    button_requests = tk.Button(
        lobby_window,
        text="Members requests",
        command=lambda: [create_requests_window(user), lobby_window.destroy()],
    )
    button_requests.pack()
    button_back.pack()


def create_requests_window(
    user,
):  # ventana para ver las solicitudes de usuarios que quieren entrar a grupos
    # Crea la nueva ventana
    requests_window = tk.Tk()
    requests_window.geometry("300x150")
    requests_window.title("Requests")

    # Crear un widget Canvas
    canvas = tk.Canvas(requests_window)
    # Crear un frame dentro del Canvas para contener los botones
    frame = tk.Frame(canvas)
    frame.pack(side=tk.RIGHT, fill=tk.X)

    # Agregar un scrollbar al Canvas
    scrollbar = ttk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    canvas.configure(yscrollcommand=scrollbar.set)

    num_requests = 10
    requests = []
    buttons = []

    while num_requests > 0:  # simulador de solicitudes
        requests.append(
            tk.Label(frame, text=(f"member{num_requests} wants to join to groupname"))
        )
        buttons.append(
            [tk.Button(frame, text=f"Accept"), tk.Button(frame, text=f"Reject")]
        )
        num_requests -= 1

    for request in requests:
        request.pack(pady=2)
        buttons[num_requests][0].pack(pady=2)
        buttons[num_requests][1].pack(pady=2)
        num_requests += 1

    button_back = tk.Button(
        requests_window,
        text="Back",
        command=lambda: [create_lobby_window(user), requests_window.destroy()],
    )
    button_back.pack()

    frame.update_idletasks()  # Actualizar el tamaño del frame interior
    canvas.config(scrollregion=canvas.bbox("all"))  # Configurar el tamaño del Canvas


def see_msg(username, data, operation, msg):
    client_socket = create_socket()
    message = f"{username}:{data}:{operation}:{msg}"
    print(message)
    message = encryption(message)
    client_socket.sendall(message.encode())  # type: ignore
    client_socket.close()  # type: ignore


def create_chatroom_window(
    user, groupname
):  # ventana del chatroom, donde lees mensajes y pueder mandar mensajes
    chatroom_window = tk.Tk()
    chatroom_window.geometry("300x150")
    chatroom_window.title(groupname)
    # ------------------------- rol de usuario------------------------------------------------------------------------------------
    admin = True  # si es true, mostrará un boton para ver todos los miembros del grupo

    client_socket = create_socket()
    see_lobby(client_socket, user, groupname, 6)

    # Crear un widget Canvas
    canvas = tk.Canvas(chatroom_window)
    # Crear un frame dentro del Canvas para contener los botones
    frame = tk.Frame(canvas)
    frame.pack(side=tk.RIGHT, fill=tk.X)

    # Agregar un scrollbar al Canvas
    scrollbar = ttk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    canvas.configure(yscrollcommand=scrollbar.set)

    msgs = []
    arr = []
    response = ""
    for i in range(100):
        response = client_socket.recv(1024)
        if response.decode() == "finish":
            break
        arr = arr + response.decode().split("\n")
        print(arr)
    for i in range(len(arr)):
        if (
            arr[i] != "\x11\x16\x11"
            and arr[i] != "p"
            and arr[i] != "p\x1d"
            and arr[i] != ""
        ):
            msg = arr[i].split(":")
            msgs.append(tk.Label(frame, text=(f"{msg[0]}:{msg[1]}")))

    client_socket.close()
    for message in msgs:
        message.pack(pady=2)

    entry_message = tk.Entry(frame)
    button_send = tk.Button(
        frame,
        text="Send",
        command=lambda: [see_msg(user, groupname, 7, entry_message.get())],
    )
    button_back = tk.Button(
        chatroom_window,
        text="Back",
        command=lambda: [create_lobby_window(user), chatroom_window.destroy()],
    )
    button_refr = tk.Button(
        chatroom_window,
        text="Refresh",
        command=lambda: [
            chatroom_window.destroy(),
            create_chatroom_window(user, f"{groupname}"),
        ],
    )
    entry_message.pack()
    button_send.pack()
    frame.update_idletasks()  # Actualizar el tamaño del frame interior
    canvas.config(scrollregion=canvas.bbox("all"))  # Configurar el tamaño del Canvas
    if (
        admin == True
    ):  # si es admin, llama a la función para crear una ventana donde se muestran los membros del grupo
        button_members = tk.Button(
            chatroom_window,
            text="View Members",
            command=lambda: [
                create_group_members_window(user, groupname),
                chatroom_window.destroy(),
            ],
        )
        button_members.pack()
    button_back.pack()
    button_refr.pack()


def create_group_members_window(
    user, groupname
):  # ventana donde si eres admin, muestra los miembros de tu grupo
    groupmembers_window = tk.Tk()
    groupmembers_window.geometry("300x150")
    groupmembers_window.title(groupname)

    # Crear un widget Canvas
    canvas = tk.Canvas(groupmembers_window)
    # Crear un frame dentro del Canvas para contener los botones
    frame = tk.Frame(canvas)
    frame.pack(side=tk.RIGHT, fill=tk.X)

    # Agregar un scrollbar al Canvas
    scrollbar = ttk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    canvas.configure(yscrollcommand=scrollbar.set)

    num_members = 10
    members = []

    while num_members > 0:
        members.append(tk.Label(frame, text=(f"member{num_members}")))
        num_members -= 1

    for member in members:
        member.pack(pady=2)

    button_back = tk.Button(
        groupmembers_window,
        text="Back",
        command=lambda: [
            create_chatroom_window(user, groupname),
            groupmembers_window.destroy(),
        ],
    )
    button_back.pack()

    frame.update_idletasks()  # Actualizar el tamaño del frame interior
    canvas.config(scrollregion=canvas.bbox("all"))  # Configurar el tamaño del Canvas


# -------------------------------------------------------------------------------------------------------------------------------------------------

create_main_window()  # Ejecuta el bucle principal de la ventana, Aquí empieza el programa
