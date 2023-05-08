/*
 * Server code for a chat application
 * Uses TCP communication
 * Manages user communication and signup options
 *
 * Author: Carlos Manuel Velez
 * Date: 2023/05/06
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

// Max length for use in strings
#define MAX_LENGTH 1024
// Max number of users
#define MAX_USERS 30
// Port for communications
#define PORT 5000
// Code for successful operations
#define SUCCESS 1
// Code for failed operations
#define FAIL 0

/*
 * User init format
 * user name:password:operation
 * Operation: 1 for login, 2 for signup
 * Example: admin:root:1
 * Logins user admin with password root
 */

/*
 * User key file, stores all users and passwords
 */
FILE *user_file;

/*
 * Struct for use with users
 * Stores the user info along with currently connected socket
 */
struct user
{
    int socket; // Socket to which the user is connected
    char *name; // Username
    char *pass; // Password
};

/*
 * Closes the user key file when ctr+c is pressed whiloe program is running
 * param sig: Signal, in this case ctrl+c
 * param *fp: User key file
 */
void sigint_handler(int sig)
{
    if (user_file != NULL)
        fclose(user_file);
    exit(0);
}

/*
 * Adds a user to the user key file
 * param user: User name string
 * param key: Password string
 * param file: User key file
 * return: 1 for successful append, 0 for error
 */

int add_user(char *user, char *key, FILE *file)
{
    char buffer[MAX_LENGTH];
    char userkey[MAX_LENGTH];
    sprintf(userkey, "%s:%s\n", user, key);
    rewind(file);
    // Change this to only look for user
    while (fgets(buffer, MAX_LENGTH, file))
        if (strcmp(buffer, userkey) == 0)
            return FAIL;
    fputs(userkey, file);
    return SUCCESS;
}

/*
 * Validates user and password in user key file
 * param user: User name string
 * param key: Password string
 * param file: User key file
 * return: 1 for successful validation, 0 for error
 */
int check_user(char *user, char *key, FILE *file)
{
    char buffer[MAX_LENGTH];
    char userkey[MAX_LENGTH];
    sprintf(userkey, "%s:%s\n", user, key);
    rewind(file);
    // Add validation for error in password
    while (fgets(buffer, MAX_LENGTH, file))
        if (strcmp(buffer, userkey) == 0)
            return SUCCESS;
    return FAIL;
}

/*
 * Manages the request of a new user, in that case logs them in or
 * signs them up, should add them then to the active user list.
 * param req: A string with user init format
 * param file: User key file
 * return: 0 for error, 1 for success
 */
int manage_user_request(char *req, FILE *file)
{
    char parts[3][MAX_LENGTH];
    char buffer[MAX_LENGTH];
    char user[MAX_LENGTH];
    char pass[MAX_LENGTH];
    int dest = 0;
    int j = 0;
    // Code for split by ':' character
    for (int i = 0; i < strlen(req); i++)
    {
        if (req[i] == ':')
        {
            strcpy(parts[dest], buffer);
            dest++;
            memset(buffer, 0, sizeof(buffer));
            j = 0;
            continue;
        }
        buffer[j++] = req[i];
        buffer[j] = 0;
    }
    strcpy(parts[dest], buffer);
    strcpy(user, parts[0]);
    strcpy(pass, parts[1]);
    switch (atoi(parts[2]))
    {
    case 1:
        return check_user(user, pass, file);
        break;
    case 2:
        return add_user(user, pass, file);
        break;
    default:
        perror("Code error");
        return FAIL;
    }
}

int main(void)
{
    struct user user_list[MAX_USERS];

    signal(SIGINT, (void (*)(int))sigint_handler);

    int nusers = 0;
    int server_fd, max_fds, activity;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    fd_set read_fds;
    char buffer[MAX_LENGTH];

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("Socket creation failed\n");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
        perror("Failure binding socket\n");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, MAX_USERS) < 0)
    {
        perror("Failure listening\n");
        exit(EXIT_FAILURE);
    }

    user_file = fopen("users.key", "a+");

    FD_ZERO(&read_fds);
    FD_SET(server_fd, &read_fds);
    max_fds = server_fd;

    while (1)
    {

        if (activity = select(max_fds + 1, &read_fds, NULL, NULL, NULL) < 0)
        {
            perror("Select Failure");
            continue;
        }

        if (FD_ISSET(server_fd, &read_fds))
        {
            int new_socket;
            if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                                     (socklen_t *)&addrlen)) < 0)
            {
                perror("Error accepting connection");
            }
            if (recv(new_socket, buffer, MAX_LENGTH, 0) < 0)
            {
                perror("Error reading data");
                close(new_socket);
            }
            if (manage_user_request(buffer, user_file) == SUCCESS)
            {
                send(new_socket, "accept", strlen("accept"), 0);
                FD_SET(new_socket, &read_fds);
            }
            else
            {
                send(new_socket, "failure", strlen("failure"), 0);
                close(new_socket);
            }
        }
        else
        {
            // Recv logic goes here
        }
    }
    fclose(user_file);
    return 0;
}