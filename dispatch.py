from pyVoIP.VoIP import VoIPPhone, CallState
import time
import wave
import yaml
from flask import Flask,request
import requests

app = Flask(__name__)
class authrequest:
    def __init__(self, number:str):
        self.number = number
        self.inprog = False
verifylist = []

@app.route('/verify', methods=["POST"])
def verify_num():
    global verifylist
    num = request.args.get("num", str)
    for i in verifylist:
        if i.number == num:
            return "ok"
    verifylist.append(authrequest(num))
    return "ok"

conffile = open("/etc/mfa/voip.yaml","r")
conf = yaml.safe_load(conffile)
def placecall(phone: VoIPPhone, req: authrequest):
    global verifylist
    ok = False
    call = phone.call(req.number)
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
        stat = "ok"
    else:
        f = wave.open('failed.wav','rb')
        stat = "bad"

    requests.post("http://hyperion.internal/endpoint",data={"number":req.number,"status":stat})
    frames = f.getnframes()
    data = f.readframes(frames)
    f.close()
    call.write_audio(data)
    timeout = time.time() + (frames/8000)
    while (call.state == CallState.ANSWERED) and (time.time() < timeout):
        time.sleep(0.1)
    call.hangup()
    verifylist.remove(req)

phone = VoIPPhone(conf["server_addr"], 5060, conf["server_user"], conf["server_passwd"], myIP="0.0.0.0")
phone.start()
app.run()
while True:
    try:
        time.sleep(0.1)
        for n in verifylist:
            if not n.inprog:
                n.inprog = True
                placecall(phone, n)
    except KeyboardInterrupt:
        break

phone.stop()
