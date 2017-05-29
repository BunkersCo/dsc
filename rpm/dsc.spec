Name:           dsc
Version:        2.5.1
Release:        1%{?dist}
Summary:        DNS Statistics Collector
Group:          Productivity/Networking/DNS/Utilities

License:        BSD-3-Clause
URL:            https://www.dns-oarc.net/oarc/data/dsc
# Using same naming as to build debs, get the source (and rename it) at
# https://www.dns-oarc.net/dsc/download and change %setup
Source0:        %{name}_%{version}.orig.tar.gz

BuildRequires:  libpcap-devel
BuildRequires:  perl
BuildRequires:  perl(Proc::PID::File)
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
Requires:       perl
Requires:       perl(Proc::PID::File)

%description
DNS Statistics Collector (DSC) is a tool used for collecting and exploring
statistics from busy DNS servers. It uses a distributed architecture with
collectors running on or near nameservers sending their data to one or more
central presenters for display and archiving. Collectors use pcap to sniff
network traffic. They transmit aggregated data to the presenter as XML data.

%prep
%setup -q -n %{name}_%{version}


%build
sh autogen.sh
%configure
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root)
%config %{_sysconfdir}/*
%{_bindir}/*
%{_libexecdir}/*
%{_datadir}/doc/*
%{_mandir}/man1/*
%{_mandir}/man5/*


%changelog
* Wed Mar 29 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 2.5.1-1
- Release 2.5.1
  * Various compatibility issues and a possible runtime bug, related to
    pcap-thread, fixed.
  * Commits:
    5ed03e3 Compat for OS X
    8605759 Fix compiler warnings
    5fbad26 Update pcap-thread to v2.1.2
    47ed110 Update pcap-thread to v2.1.1
* Thu Mar 02 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 2.5.0-1
- Release 2.5.0
  * Resolved memory leaks within the IP fragment reassembly code that was
    reported by Klaus Darilion (NIC.AT) and added config option to control
    some parts of the fragment handling.
  * Fixes:
    - Add `pcap_layers_clear_fragments()` to remove old fragments after
      `MAX_FRAG_IDLE` (60 seconds)
    - Use correct alloc/free functions for dataset hash
    - Fix spacing in dsc.conf(5) man-page
  * New config option:
    - `drop_ip_fragments` will disable IP fragmentation reassembling and
      drop any IP packet that is a fragment (even the first)
  * Commits:
    eaee6c0 Drop IP fragments
    3ebb687 Issue #146: Fix leak in fragment handling
    9a5e377 Use correct alloc/free
    35f663c Fix #107: add const
* Fri Jan 27 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 2.4.0-1
- Release 2.4.0
  * Since there have been a few major issues with the threaded capturing code
    it is now default disabled and have to be enabled with a configure option
    to use: `./configure --enable-threads ...`
  * A lot of work has been done to ensure stability and correct capturing,
    as of now `dsc` is continuously running on the testing platforms with
    simulated traffic and tests are performance every 5-15 minutes:
    - https://dev.dns-oarc.net/jenkins/view/dsctest/
  * With the rewrite of the config parser to C it was missed that Hapy allowed
    CR/LF within the values of the options.  Changing the C parser to allow
    it is a bit of work and having CR/LF within the value may lead to other
    issues so it is now documented that CR/LF are not allowed in config option
    values.
  * Fixes:
    - The `-T` flag was just controlling pcap-thread usage of threads, it now
      controls all usage of threads including how signals are caught.
    - Fix program name, was incorrectly set so it would be reported as `/dsc`.
    - Use thread safe functions (_r).
    - Handle very long config lines by not having a static buffer, instead
      let `getline()` allocate as needed.
    - Use new activation in pcap-thread to activate the capturing of pcaps
      after the initial interval sync have been done during start-up.
    - Use factions of second for start-up interval sync and interval wait.
    - Fix memory leaks if config options was specified more then once.
    - Use new absolute timed run in pcap-thread to more exactly end capturing
      at the interval.
    - Fix config parsing, was checking for tab when should look for line feed.
    - Exit correctly during pcap-thread run to honor `dump_reports_on_exit`.
    - Use 100ms as default pcap-thread timeout, was 1s before but the old code
      used 250ms.
    - Various enhancements to logging of errors.
  * New config options/features:
    - `pcap_buffer_size` can be used to increase the capture buffer within
      pcap-thread/libpcap, this can help mitigate dropped packets by the
      kernel during interval breaks.
    - `no_wait_interval` will skip the interval sync that happens during
      start-up and start capturing directly, the end of the interval will
      still be the modulus of the interval.
    - `pcap_thread_timeout` can be used to change the internal timeout use
      in pcap-thread to wait for packets (default 100ms).
    - Log non-fatal errors from pcap-thread w.r.t. setting the filter which
      can indicate that the filter is running in userland because lack of
      support or that it is too large for the kernel.
  * Special thanks to:
    - Anand Buddhdev, RIPE NCC
    - Klaus Darilion, NIC.AT
    - Vincent Charrade, Nameshield
  * Commits:
    ee59572 Fix #111, fix #116: Update pcap-thread to v2.0.0, remove debug
            code
    40a1fb4 Fix #139: Use 100ms as default pcap-thread timeout
    2a07185 Fix #137: Graceful exit on signal during run
    f1b3ec3 Issue #116: Try and make select issue more clear
    950ea96 Fix #133: Return from `Pcap_run()` on signal/errors
    667cc91 Issue #116: Add config option pcap_thread_timeout
    3c9e073 Notice if non-fatal errors was detected during activation
    4ea8f54 Fix #108: Document that CR/LF are not allowed within configuration
            line
    9fda332 Check for LF and not tab
    15a1dc0 Use pcap-thread timed run to interface
    1e98f8b Fix potential memory leaks if config options specified more then
            once
    a9b38e9 Add missing LF and indicate what config option was wrong if
            possible
    f8a2821 Use fractions of seconds for both start up interval sync and
            timed run, always adjust for inter-run processing delay
    f47069a Fix #121: Update to pcap-thread latest develop
    fc13d73 Issue #116: Feature for not waiting on the interval sync
    c832337 Fix #122: Update pcap-thread to v1.2.3 for fix in timed run
    4739111 Add `pcap_buffer_size` config option
    7d9bf90 Update pcap-thread to v1.2.2
    ef43335 Make threads optional and default disabled
    c2399cf getline() returns error on eof, don't report error if we are
    5c671e6 Clarify config error message and report `getline()` error
    8bd6a67 Fix #114: Handle very long lines
    47b1e1a Use _r thread safe functions when possible
    0f5d883 Update daemon.c
    f18e3ea Update doc, -T now disables all usage of threads
    57aacbe Honor the -T flag when installing signal handlers
* Thu Dec 22 2016 Jerry Lundström <lundstrom.jerry@gmail.com> 2.3.0-1
- Release 2.3.0
  * Rare lockup has been fixed that could happen if a signal was received
    in the wrong thread at the wrong time due to `pcap_thread_stop()`
    canceling and waiting on threads to join again. The handling of signals
    have been improved for threaded and non-threaded operations.
  * A couple of bugfixes, one to fix loading of GeoIP ASN database and
    another to use the lowest 32 bits of an IP address (being v4 or v6)
    in the IP hash making it a bit more efficient for v6 addresses.
  * New functionality for the configure option `local_address`, you can now
    specify a network mask (see `man 5 dsc.conf` for syntax).
  * Commits:
    e286298 Fix CID 158968 Bad bit shift operation
    c15db43 Update to pcap-thread v1.2.1
    1ac06ac Move stopping process to not require a packet
    597dd34 Handle signals better with and without pthreads
    bcf99e8 Add RPM spec and ACLOCAL_AMFLAGS to build on CentOS 6
    667fe69 fixed load geoIP ASN database from config-file
    e1304d4 Fix #97: Add optional mask to `local_address` so you can
            specify networks
    5dae7dd Fix #96: Hash the lowest 32 bits of IP addresses
* Tue Dec 13 2016 Jerry Lundström <lundstrom.jerry@gmail.com> 2.2.1-1
- Initial package
