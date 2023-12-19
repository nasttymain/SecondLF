# SecondLF 論理デバイスドライバ マニュアル
* 更新: 2023年12月19日

# 概要
SecondLF では、各灯体に関する個別の設定や操作手順を、「論理デバイスドライバ」という構造を用いて、個別のモジュールで管理しています。

# 記載事項
* 論理デバイスドライバの実体は、規定の方式に従って記述された Python モジュールです。
* 論理デバイスドライバは、`drivers` フォルダ内に格納されています。
* 各論理デバイスドライバは、SecondLF の起動時に1回だけ初期化されます。
* 論理デバイスドライバは、直接照明デバイスと通信しません。代わりに、Primary ドライバ、vulcbeat、物理デバイスドライバの3つを通して変換されます。

# モジュール構造
## 構造
* (モジュール名)
  - `class light_driver:`
    - `def __init__(self, mode: list, option: dict) -> None:`
    - `def reset(self) -> dict:`
    - `def close(self) -> dict:`
    - `def info(self) -> str:`
    - `def apiver(self) -> int:`
    - `def displayparam(self) -> list:`
    - `def paramlist(self) -> list:`
    - `def set(self, param_name: str, value: int|float, fader: int|float) -> dict:`
    - `def get(self, param_name: str) -> any:`

## メソッド解説

> [!]NOTE
> 
> パラメータリストを返す各関数について、各チャンネルに存在する `fader` フィールドは、論理デバイスドライバでは現在 **使用されていません**。フェーダーの設定はすべて Primary ドライバによって上書きされます。互換性維持のため、このフィールドには `0.0` を指定してください。


### `def __init__(self, mode: list, option: dict) -> None:`
論理デバイスドライバのコンストラクタです。
`mode` には `[DMX 開始チャンネル番号, DMX チャンネル割当の長さ]` という構造のリストが、`option` には、config.json の `option` 欄に記述されたデータがそのまま、それぞれ格納されます。

### `def reset(self) -> dict:`
対象の照明をリセットします。戻り値には、`{チャンネル番号: {"value": 設定値, "fade": フェーダーの設定値"}, ...}` という形式の dict を格納します。

### `def close(self) -> dict:`
予約済み。

### `def info(self) -> str:`
ドライバに関する簡単な説明文を返します。

### `def apiver(self) -> int:`
論理デバイスドライバ API のバージョンを返します。
`1` を返してください。

### `def displayparam(self) -> list:`
論理デバイスドライバのパラメータを、画面表示に適したフォーマットで返します。
SecondLF 上で、各色の現在の状態を表示するのに使用されています。

### `def paramlist(self) -> list:`
論理デバイスドライバのパラメータの名前一覧を格納したリストを返します。

### `def set(self, param_name: str, value: int|float, fader: int|float) -> dict:`
論理デバイスドライバにパラメータをセットします。
パラメータの変更に対して、各DMXパラメータの取る目標値が格納された dict が返されます。

### `def get(self, param_name: str) -> any:`
論理デバイスドライバの持つパラメータのうち、指定されたキーのものを返します。