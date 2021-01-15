#!/usr/bin/env sh

cat > ~/.netc << EOF
machine api.heroku.com
  login $HEROKU_LOGIN
  password $HEROKU_KEY
machine git.heroku.com
  login $HEROKU_LOGIN
  password $HEROKU_KEY
EOF
