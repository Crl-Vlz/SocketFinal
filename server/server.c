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

// Key used for XOR encryption
char *KEY = "puropinchechensomanalv";

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

void replace_char(char *string, char target, char to_replace)
{
    for (int i = 0; i < strlen(string); i++)
    {
        if (string[i] == target)
            string[i] = to_replace;
    }
}

void add_char(char *string, char to_add)
{
    int siz = strlen(string);
    string[siz] = to_add;
    string[siz + 1] = '\0';
}

/*
 * Encrypts and deencrypts a text using a specific key
 * param data: String to modify
 * param key: Key used as cipher
 * return: Modified text
 */
char *XORCipher(char *data, char *key)
{
    int len = strlen(data);
    int key_len = strlen(key);
    char *output = (char *)malloc(sizeof(char) * len + 1);

    for (int i = 0; i < len; ++i)
    {
        int ch = data[i] ^ key[i % key_len];
        if (data[i] == key[i % key_len])
        {
            ch = (int)key[i % key_len];
        }
        if (ch != 0)
        {
            output[i] = ch;
        }
        else
        {
            printf("Null terminator encountered\n");
            output[i] = key[i % key_len];
        }
    }
    output[len] = '\0'; // Add null terminator at the end

    return output;
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
    sprintf(userkey, "\n%s:%s", user, key);
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
    char userkey2[MAX_LENGTH];
    sprintf(userkey, "%s:%s\n", user, key);
    rewind(file);
    // Add validation for error in password
    while (fgets(buffer, MAX_LENGTH, file))
        if (strcmp(buffer, userkey) == 0)
        {
            printf("Found user\n");
            return SUCCESS;
        }
    return FAIL;
}

/*
 * Makes three different files: group members, group conversations, and updates user groups
 * param user: String representing the user name
 * param group: String representing the group name
 * return: Group creation success state
 */
int make_group(char *user, char *group)
{
    FILE *grp_file;
    char buffer[MAX_LENGTH];
    char *userp, *groupp; // Printable implementations of user and group
    sprintf(userp, "%s\n", user);
    sprintf(groupp, "%s\n", group);
    sprintf(buffer, "%s.cnv", group);
    if (access(buffer, F_OK) == 0)
    {
        return FAIL;
    }
    else
    {
        grp_file = fopen(buffer, "w");
        fclose(grp_file);
        sprintf(buffer, "%s.usr", group);
        grp_file = fopen(buffer, "w");
        fputs(userp, grp_file);
        fclose(grp_file);
        sprintf(buffer, "%s.grp", user);
        grp_file = fopen(buffer, "a+");
        fputs(groupp, grp_file);
        fclose(grp_file);
        grp_file = fopen("groups.lst", "a+");
        fputs(groupp, grp_file);
        free(userp);
        free(groupp);
        free(group);
        free(user);
        return SUCCESS;
    }
}

/*
 * Updates the files to add the user and add the group to the user's list
 * param user: String representing the user name
 * param group: String representing the group name
 * return: Group join success state
 */
int join_group(char *user, char *group)
{
    char fname[1024];
    sprintf(fname, "%s.usr", group);
    if (access(fname, F_OK) == 0)
    {
        FILE *fp = fopen(fname, "a+");
        char *usep;
        char *userfile;
        sprintf(userfile, "%s.grp", user);
        sprintf(usep, "%s\n", user);
        char buffer[MAX_LENGTH];
        while (fgets(buffer, MAX_LENGTH, fp))
        {
            replace_char(buffer, '\n', '\0');
            if (strcmp(buffer, user) == 0)
                return FAIL;
        }
        fputs(usep, fp);
        fclose(fp);
        free(usep);
        char *groupp;
        sprintf(groupp, "%s\n", group);
        fp = fopen(userfile, "a+");
        fputs(groupp, fp);
        fclose(fp);
        free(user);
        free(group);
        free(groupp);
        return SUCCESS;
    }
    else
    {
        return FAIL;
    }
}

/*
 * Adds a message to the group conversation file of a specific group
 * param group: Name of the group
 * param message: Message to append to the file
 * param user: Name of the user obtained from User array
 * return Succes state
 */
void send_conversations(char *group, char *message, char *user)
{
    char *group_file;
    sprintf(group_file, "%s.cnv", group);
    FILE *fp = fopen(group_file, "r");
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
    printf("%s\n", req);
    req = XORCipher(req, KEY);
    printf("%s\n", req);
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
    int op = atoi(&parts[2][0]);
    printf("%d\n", op);
    switch (atoi(&parts[2][0]))
    {
    case 1:
        return check_user(user, pass, file);
        break;
    case 2:
        return add_user(user, pass, file);
        break;
    case 3:
        return join_group(user, pass);
        break;
    case 4:
        return make_group(user, pass);
        break;
    case 5:
        printf("%d\n", op);
        return 0;
        break;
    case 6:
        printf("%d\n", op);
        return 0;
        break;
    default:
        printf("Code error\n");
        return FAIL;
    }
}

int main(void)
{
    struct user user_list[MAX_USERS];

    signal(SIGINT, (void (*)(int))sigint_handler);

    int nusers = 0;
    int server_fd, max_fds, activity;
    int client_sockets[MAX_USERS]; // C initializes the values to 0
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    fd_set read_fds;
    char buffer[MAX_LENGTH];

    for (int i = 0; i < MAX_USERS; i++)
    {
        client_sockets[i] = 0;
    }

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
            perror("Select Failure\n");
            continue;
        }

        if (FD_ISSET(server_fd, &read_fds))
        {
            int new_socket;
            if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                                     (socklen_t *)&addrlen)) < 0)
            {
                perror("Error accepting connection\n");
            }
            if (recv(new_socket, buffer, MAX_LENGTH, 0) < 0)
            {
                perror("Error reading data\n");
                close(new_socket);
            }
            if (manage_user_request(buffer, user_file) == SUCCESS)
            {
                send(new_socket, XORCipher("accept", KEY), strlen("accept"), 0);
                FD_SET(new_socket, &read_fds);
                client_sockets[nusers++] = new_socket;
            }
            else
            {
                send(new_socket, XORCipher("failure", KEY), strlen("failure"), 0);
                close(new_socket);
            }
        }

        for (int i = 0; i < MAX_USERS; i++)
        {
            int sd = client_sockets[i];

            if (FD_ISSET(sd, &read_fds))
            {
                // Checks if socket was closed
                if (read(sd, buffer, 1024) == 0)
                {
                    close(sd);
                    client_sockets[i] = 0;
                }

                else
                {
                    if (manage_user_request(buffer, user_file) == SUCCESS)
                    {
                        send(sd, XORCipher("accept", KEY), strlen("accept"), 0);
                    }
                    else
                    {
                        send(sd, XORCipher("failure", KEY), strlen("failure"), 0);
                    }
                }
            }
        }
    }
    fclose(user_file);
    return 0;
}