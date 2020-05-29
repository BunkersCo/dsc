#!/bin/sh -e

echo "/* autogenerated by mk-knowntlds.sh at `date --iso-8601=seconds -u` */"
echo "static const char* KnownTLDS_static[] = {"
echo "\".\","
(
  curl https://data.iana.org/TLD/tlds-alpha-by-domain.txt || \
  wget -O - https://data.iana.org/TLD/tlds-alpha-by-domain.txt
) | grep -v '^#' | awk '{print "\"" tolower($1) "\","}'
echo "0 };"