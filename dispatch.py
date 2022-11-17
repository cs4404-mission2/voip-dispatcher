from pyVoIP.VoIP import VoIPPhone, InvalidStateError, CallState
import time
import wave
import sqlite3
db = sqlite3.connect("/etc/mfa/user.db")
cursor = db.cursor()

def placecall(phone: VoIPPhone, number: str):
    ok = False
    call = phone.call(str)
    while call.state == CallState.DIALING:
        time.sleep(0.1)
    f = wave.open('greeting.wav', 'rb')
    frames = f.getnframes()
    data = f.readframes(frames)
    f.close()
    call.write_audio(data)
    timeout = time.time() + 40
    while (call.state == CallState.ANSWERED) and (time.time() < timeout):
        if call.get_dtmf() == "#":
            ok = True
            timeout = 0
        time.sleep(0.1)
    if ok:
        f = wave.open('confirmed.wav', 'rb')
        tmp = "ok"
    else:
        f = wave.open('failed.wav','rb')
        tmp = "bad"
    cursor.execute("UPDATE users SET mfa = '{}' WHERE number = {}".format(tmp, number))
    frames = f.getnframes()
    data = f.readframes(frames)
    f.close()
    call.write_audio(data)
    timeout = time.time() + (frames/8000)
    while (call.state == CallState.ANSWERED) and (time.time() < timeout):
        time.sleep(0.1)
    call.hangup()

phone = VoIPPhone("sip-server-addr-replaceme", "sip-port-replaceme", "sip-username-replaceme", "password-replaceme", myIP="0.0.0.0")
phone.start()
while True:
    try:
        time.sleep(0.1)
        result = cursor.execute("SELECT number FROM users WHERE mfa = 'pend'")
        for n in result.fetchall():
            print("Placing call to",n[0])
            placecall(phone, n[0])
    except KeyboardInterrupt:
        break

phone.stop()