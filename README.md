# voip-dispatcher
Dispatcher for VOIP automated MFA requests

## Process
1. Query sqlite database for auth requests from webserver
2. place a call to any number pending authentication
3. play pre-recorded greeting
4. listen for pound key
5. Update database to "ok" if key pressed, "bad" if not
6. play outro message
7. hang up
8. goto 1