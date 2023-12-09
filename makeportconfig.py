import serial
import serial.tools.list_ports
import json

print("COM ポートの設定を開始します。")
print("Arduino Bridge を PC に接続して、Enter キーを押してください。\nまたは、この設定を後で行う場合は、何もせずに Enter キーを押してください... ", end="")
input()

ports = serial.tools.list_ports.comports()

if ports == []:
    print("COM ポートが1つも接続されていません!")
    print("この設定を後で行うには、もう一度 setup-windows.bat を実行してください。")
else:
    print("以下のポートが見つかりました: ")
    pmax = len(ports)
    for pcnt, p in enumerate(ports):
        print("{:2d} : {:s}".format(pcnt + 1, p[1]))
    while(True):
        print("使用するポートの番号を入力してください: ", end="")
        pn = input()
        if pn.isnumeric():
            if 1 <= int(pn) and int(pn) <= pmax:
                j = None
                with open("config.json", mode="r") as f:
                    j = json.load(f)
                    j["deviceconf"]["physicallight"]["option"]["port"] = ports[int(pn) - 1][0][3:]
                with open("config.json", mode="w") as f:
                    json.dump(j, f, indent=2)
                print(str(ports[int(pn) - 1][1] + " を利用するように設定しました。"))
                break
