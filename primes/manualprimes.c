#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "vamos-buffers/shmbuf/buffer.h"
#include "vamos-buffers/shmbuf/client.h"
#include "vamos-buffers/core/source.h"
#include "vamos-buffers/core/event.h"

typedef struct ulonglist {
    unsigned long     number;
    struct ulonglist *next;
} intlist;

int isPrime(long number) {
    intlist       base    = {.number = 2, .next = NULL};
    intlist      *last    = &base;
    unsigned long current = 3;
    if (number == 2) {
        return 1;
    }
    while (current <= number) {
        intlist *curnode = &base;
        int      found   = 0;
        while (curnode != NULL) {
            if (current % curnode->number == 0) {
                found = 1;
                break;
            }
            curnode = curnode->next;
        }
        if (!found) {
            if (current == number) {
                return 1;
            } else {
                intlist *newnode = (intlist *)malloc(sizeof(intlist));
                newnode->number  = current;
                newnode->next    = NULL;
                last->next       = newnode;
                last             = newnode;
            }
        }
        current += 2;
    }
    last = base.next;
    while (last != NULL) {
        intlist *node = last;
        last          = last->next;
        free(node);
    }
    return 0;
}

long findPrime(int target) {
    intlist       base    = {.number = 2, .next = NULL};
    intlist      *last    = &base;
    unsigned long count   = 1;
    unsigned long current = 3;
    if (target <= 1) {
        return 2;
    }
    while (count < target) {
        intlist *curnode = &base;
        int      found   = 0;
        while (curnode != NULL) {
            if (current % curnode->number == 0) {
                found = 1;
                break;
            }
            curnode = curnode->next;
        }
        if (!found) {
            intlist *newnode = (intlist *)malloc(sizeof(intlist));
            newnode->number  = current;
            newnode->next    = NULL;
            last->next       = newnode;
            last             = newnode;
            count++;
        }
        current++;
    }
    current = last->number;
    last    = base.next;
    while (last != NULL) {
        intlist *node = last;
        last          = last->next;
        free(node);
    }
    return current;
}


vms_shm_buffer* vmsbuf;

void push_event(int n, int p) {
	void * ev=vms_shm_buffer_start_push(vmsbuf);
	if(!ev) {
		printf("Could not create event!");
		exit(-1);
	}
    static vms_event event;
    event.kind=VMS_EVENT_LAST_SPECIAL_KIND+1;
    event.id++;
	ev=vms_shm_buffer_partial_push(vmsbuf, ev, &event, sizeof(event));
	ev=vms_shm_buffer_partial_push(vmsbuf, ev, &n, sizeof(n));
	ev=vms_shm_buffer_partial_push(vmsbuf, ev, &p, sizeof(n));

	vms_shm_buffer_finish_push(vmsbuf);
}

void printPrime(size_t n, size_t p) {
    printf("#%lu: %lu\n", n, p);
	push_event(n, p);
}

int main(int argc, char **argv) {
    struct timespec begin, end;
    int             target      = 10;
    int             interactive = 0;
	const char * name = "Prime";
	const char * signature = "ii";
	char* sourcename="/primes";
    struct vms_source_control *control = vms_source_control_define_pairwise(
        1, &name, &signature);
	if(!control) {
		printf("Could not create VMS control!");
		return -1;
	}
    for(int ai=1;ai<argc;ai++) {
        if (strcmp(argv[ai], "-i") == 0) {
            interactive = 1;
        } else if(strcmp(argv[ai], "-n") == 0 && argc>ai+1) {
			ai++;
			sourcename=argv[ai];
		} else {
            target = atoi(argv[ai]);
        }
    }
	vmsbuf = vms_shm_buffer_create(sourcename, 1024, control);
	vms_shm_buffer_wait_for_reader(vmsbuf);
	if(!vmsbuf) {
		printf("Could not create VMS buffer!");
		return -1;
	}
    if (interactive) {
        char buffer[256];
        char ipb[8];
        while (1) {
            int index;
            if (fgets(buffer, 256, stdin) == NULL) {
                printf("byeeof\n");
                break;
            }
            if (strcmp(buffer, "quit\n") == 0) {
                printf("byequit\n");
                break;
            }
            strncpy(ipb, buffer, 8);
            ipb[7] = 0;
            if (strcmp(ipb, "isprime") == 0) {
                long num;
                if (strlen(buffer) <= 8) {
                    continue;
                }
                num = atol(buffer + 8);
                printf("%li is%s prime\n", num, (isPrime(num) ? "" : " not"));
                continue;
            }
            index = atoi(buffer);
            if (index < 1) {
                index = 1;
            }
            printf("#%i: %lu\n", index, findPrime(index));
        }
    } else {
        if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &begin) == -1) {
            perror("clock_gettime");
            return 1;
        }
        intlist  base = {.number = 2, .next = NULL};
        intlist *last = &base;

        unsigned long current = 3;
        unsigned long count   = 1;
        if (target > 0) {
            printPrime(1, 2);
        }
        while (count < target) {
            intlist *curnode = &base;
            int      found   = 0;
            while (curnode != NULL) {
                if (current % curnode->number == 0) {
                    found = 1;
                    break;
                }
                curnode = curnode->next;
            }
            if (!found) {
                intlist *newnode = (intlist *)malloc(sizeof(intlist));
                newnode->number  = current;
                newnode->next    = NULL;
                last->next       = newnode;
                last             = newnode;
                count++;
                printPrime(count, current);
            }
            current++;
        }

        if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end) == -1) {
            perror("clock_gettime");
            return 1;
        }
        long   seconds     = end.tv_sec - begin.tv_sec;
        long   nanoseconds = end.tv_nsec - begin.tv_nsec;
        double elapsed     = seconds + nanoseconds * 1e-9;
        fprintf(stderr, "time: %lf seconds.\n", elapsed);
    }
	vms_shm_buffer_destroy(vmsbuf);
}
