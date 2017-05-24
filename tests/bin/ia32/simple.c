#include <stdio.h>

int my_global = 1337;
extern int y;

void print_hello(void) {
    printf("Hello World!");
}

int main(int argc, char** argv, char**envp) {
    print_hello();
}
