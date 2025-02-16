# SecondLF config.json マニュアル
* 更新: 2023年12月15日

# 概要
SecondLFでは、ソフトの動作に関わる設定を config.json に集約しており、このファイルを編集することで挙動を変更することができます。

# 記載事項
* config.json は、SecondLFの起動時に一回だけ読み込まれます。設定を変更した場合、SecondLF を再起動しないと反映されません。

# データ構造

* `deviceconf` - デバイスに関する設定
  - `physicallight` - 物理デバイス(DMX生データ処理を担当するドライバ)に関する設定
    - `driver` - 物理デバイスドライバのモジュール名
    - `option` - デバイスドライバに渡すパラメータリスト
  - `logicaldevices` - 論理デバイス(各機器毎のドライバ)に関する設定
    - (リストの各項目, オブジェクト型)
      - `name` - 論理デバイスにつける固有の名称
      - `driver` - 論理デバイスに割り当てるドライバのモジュール名
      - `mode` - チャンネル設定 `(割り当てる開始チャンネル, チャンネル数)`
      - `option` - デバイスドライバに渡すパラメータリスト
  - `controller` - SecondLFの動作に関する設定
    - `keybd-modname` - キーボードドライバのモジュール名(未使用)
    - `fader-tickrate` - 物理デバイスにパラメータを渡すレート
    - `power-save-mode` - パワーセーブモード(フロントエンド)
    - `primary-controller` - プライマリコントローラに関する設定
      - `driver` - プライマリコントローラドライバのモジュール名
  - `keybdbinds` - キー割り当てに関する設定
    - (リストの各項目, オブジェクト型)
      - `charcode` (scancode と排他) - 割り当てるキーの文字コード
      - `scancode` (charcode と排他) - 割り当てるキーの Pygame キーコード
      - `command` - キーが押された時、長押しされた時に実行するコマンド