/* Multi-Architecture Kernel with Login Screen */

#include <stdio.h>
#include <stdlib.h>

void login() {
    char username[50];
    char password[50];

    printf("Enter username: ");
    scanf("%s", username);
    printf("Enter password: ");
    scanf("%s", password);

    // Placeholder for authentication logic
    printf("Welcome, %s!\n", username);
}

void kernel_main() {
    printf("Starting Multi-Architecture Kernel...\n");
    login();
}

int main() {
    kernel_main();
    return 0;
}