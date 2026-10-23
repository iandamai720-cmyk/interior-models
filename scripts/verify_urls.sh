#!/bin/bash
# Verify every URL in urls.txt (+ api files) returns 200 and Access-Control-Allow-Origin
cd "$(dirname "$0")/.."
{ cat urls.txt; find api -name '*.json' | sed 's#^#https://iandamai720-cmyk.github.io/interior-models/#'; } | sort -u > tmp/verify_in.txt
xargs -P16 -I{} sh -c 'h=$(curl -sI --max-time 60 "{}"); c=$(echo "$h" | head -n1 | cut -d" " -f2); o=$(echo "$h" | grep -ci "^access-control-allow-origin: \*"); echo "$c $o {}"' < tmp/verify_in.txt > tmp/verify.txt
echo "total $(wc -l < tmp/verify.txt)  ok $(grep -c '^200 1 ' tmp/verify.txt)"; grep -v '^200 1 ' tmp/verify.txt | head -20
