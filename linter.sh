#!/usr/bin/env bash
if [[ $(pycodestyle .) ]]; then
	echo "FAIL: see above"
	exit 1
else
	echo "PASS"
	exit 0
fi