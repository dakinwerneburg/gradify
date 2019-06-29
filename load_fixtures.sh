#!/usr/bin/env sh
# Loads all yaml/json fixtures found in $PWD/core/fixtures
# Add any additional fixtures directly to the existing loaddata command
# Django will automatically figure out the correct load order
# If any issues occur, try deleting db.sqlite3 and try again

echo "[+] Applying migrations"
python3 manage.py migrate

echo "[+] Loading fixtures"
ls core/fixtures/ | sed -e 's/.yaml//' -e 's/.json//' | xargs python3 manage.py loaddata

# Exit with an error if the load failed
if [ $? -ne 0 ]; then
    echo "[!] Failed to load fixtures"
    exit 1
fi

echo "[+] All fixtures loaded successfully"
