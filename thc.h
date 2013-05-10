#ifndef _THC_INCLUDE
#define _THC_INCLUDE

#define ENSURE(expr) thc_run_check((expr), #expr, __func__, __FILE__, __LINE__, 0)
#define SILENT_ENSURE(expr) thc_run_check((expr), #expr, __func__, __FILE__, __LINE__, 1)

enum {
    THC_QUIET = 0x1,    /* 0001 */
    THC_VERBOSE = 0x2,  /* 0010 */
    THC_NOFORK = 0x4,   /* 0100 */
};

void thc_run_check(const int result, const char *expr, const char *func, const char *fname, const int fline, const int silent);
void thc_addtest(void (*f)(void));
int thc_run(int verbose);

#endif
