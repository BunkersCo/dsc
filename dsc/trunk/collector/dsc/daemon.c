/*
 * $Id$
 *
 * http://dnstop.measurement-factory.com/
 *
 * Copyright (c) 2002, The Measurement Factory, Inc.  All rights
 * reserved.  See the LICENSE file for details.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <syslog.h>
#include <stdarg.h>
#include <errno.h>
#include <fcntl.h>

#include "dns_message.h"
#include "ip_message.h"
#include "pcap.h"

char *progname = NULL;
int promisc_flag = 1;

extern void cip4_net_indexer_init(void);
extern void ParseConfig(const char *);

void
daemonize(void)
{
    int fd;
    pid_t pid;
    if ((pid = fork()) < 0) {
	syslog(LOG_ERR, "fork failed: %s", strerror(errno));
	exit(1);
    }
    if (pid > 0)
	exit(0);
    if (setsid() < 0)
	syslog(LOG_ERR, "setsid failed: %s", strerror(errno));
    closelog();
#ifdef TIOCNOTTY
    if ((fd = open("/dev/tty", O_RDWR)) >= 0) {
	ioctl(fd, TIOCNOTTY, NULL);
	close(fd);
    }
#endif
    fd = open("/dev/null", O_RDWR);
    if (fd < 0) {
	syslog(LOG_ERR, "/dev/null: %s\n", strerror(errno));
    } else {
	dup2(fd, 0);
	dup2(fd, 1);
	dup2(fd, 2);
	close(fd);
    }
    openlog(progname, LOG_PID | LOG_NDELAY, LOG_DAEMON);
}

void
usage(void)
{
    fprintf(stderr, "usage: %s [opts] dsc.conf\n",
	progname);
    fprintf(stderr, "\t-p\tDon't put interface in promiscuous mode\n");
    exit(1);
}

int
main(int argc, char *argv[])
{
    int x;
    extern DMC dns_message_handle;

    progname = strdup(strrchr(argv[0], '/') ? strchr(argv[0], '/') + 1 : argv[0]);
    srandom(time(NULL));
    openlog(progname, LOG_PID | LOG_NDELAY, LOG_DAEMON);

    while ((x = getopt(argc, argv, "p")) != -1) {
	switch (x) {
	case 'p':
	    promisc_flag = 0;
	    break;
	default:
	    usage();
	    break;
	}
    }
    argc -= optind;
    argv += optind;

    if (argc != 1)
	usage();
    ParseConfig(argv[0]);
    cip4_net_indexer_init();

    daemonize();

    /*
     * I'm using fork() in this loop, (a) out of laziness, and (b)
     * because I'm worried we might drop packets.  Making sure each
     * child collector runs for a small amount of time (60 secodns)
     * means I can be lazy about memory management (leaks).  To
     * minimize the chance for dropped packets, I'd like to spawn
     * a new collector as soon as (or even before) the current
     * collector exits.
     */

    syslog(LOG_INFO, "Running");
    for (;;) {
	pid_t cpid = fork();
	if (0 == cpid) {
	    Pcap_run(dns_message_handle, ip_message_handle);
	    if (0 == fork())
		dns_message_report();
	    ip_message_report();
	    _exit(0);
	} else {
	    int cstatus = 0;
	    syslog(LOG_DEBUG, "waiting for child pid %d", (int) cpid);
	    while (waitpid(cpid, &cstatus, 0) < 0)
		(void) 0;
	}
    }
    Pcap_close();
    return 0;
}