/**
 * Print one random number to stdout,
 * given a limit (exclusive) on the command line.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define DEFAULT_LIMIT	60

int main(int argc, char** argv) {
	int limit = DEFAULT_LIMIT;
	char* endptr;
	if (argc > 1) {
		limit = strtol(argv[1], &endptr, 10);
		if (*endptr != '\0') {
			fprintf(stderr, "random: error parsing %s, "
				"using default limit %d.\n",
				argv[1], DEFAULT_LIMIT);
			limit = DEFAULT_LIMIT;
		}
	}
	printf("%d", rand() % limit);
}
