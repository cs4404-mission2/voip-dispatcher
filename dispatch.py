from pyVoIP.VoIP import VoIPPhone, InvalidStateError, CallState
import time
import wave

def incoming(call):
    print("got incoming call, rejecting.")
    call.deny()

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
    else:
        f = wave.open('failed.wav','rb')
    frames = f.getnframes()
    data = f.readframes(frames)
    f.close()
    call.write_audio(data)
    timeout = time.time() + (frames/8000)
    while (call.state == CallState.ANSWERED) and (time.time() < timeout):
        time.sleep(0.1)
    call.hangup()

phone = VoIPPhone(<SIP Server IP>, <SIP Server Port>, <SIP Server Username>, <SIP Server Password>, myIP=<Your computers local IP>, callCallback=incoming)
phone.start()
input('Press enter to disable the phone')
phone.stop()