# SecondLF コントロールコマンド マニュアル
* 更新: 2023年12月15日

# 概要
SecondLF では、各キー・プロファイルに機能を割り当てるのに、コントロールコマンドと呼ばれる独自コマンドを使用します。

# 基本文法
コマンドは、コマンド名とパラメータ(無い場合もある)から構成されています。
コマンドとパラメータ、パラメータとパラメータの間は、すべて半角スペース1個で区切ります。
コマンド文字列では大文字小文字は区別されません。

```secondlfcc
// BPM を 120 に設定
bpm.set 120
```


このようなコマンドをconfig.jsonや各プロファイルに記述することで、キーやプロファイルに割り当てることができます。

```json
// A キーに赤色を割り当てる場合。config.json に記述
  "keybdbinds": [
    // 省略
    {
      "charcode": "A",
      "command": "color.toggle #FF0000 A"
    },
    // 省略
  ]
```

複数のコマンドを1つのキーやプロファイルに割り当てる場合は、コマンドとコマンドの間を `;` で区切ります。

```secondlfcc
// 現在指定されている色を削除し、新たに緑と青を追加し、BPMを135にセットする
color.clear;color.toggle #00FF00 GR;color.toggle $0000FF BL;bpm.set 135
```

# コマンド一覧

## `color` 系列
照明で使用する色に関する設定を行います。

### `color.toggle`
* 文法: `color.toggle P1 P2`
  - `P1` : `int` 設定する色
  - `P2` : `str` 色に設定するカラーコード

色リストに、色 `P1` をラベル `P2` の名の下で設定します。また、ラベル `P2` が既に色リストに存在する場合、その色を色リストから削除します。

### `color.clear`
* 文法: `color.clear`

色リストからすべての色を削除します。

### `color.blackout.toggle`
* 文法: `color.blackout.toggle`

BLACKOUT の ON - OFF を切り替えます。BLACKOUT とは、すべての色出力を停止する機能です。
ON の場合、すべての照明を消灯させます。

### `color.blackout.set`
* 文法: `color.blackout.set P1`
  - `P1` : `int` BLACKOUT の設定値

BLACKOUT の ON - OFF を設定します。`1` で ON、`0` で OFF となります。範囲外の値を設定しないでください。

### `color.brightness.settarget`
* 文法: `color.brightness.settarget P1`
  - `P1` : `int` BRIGHTNESS の目標値

BRIGHTNESS 値を設定します。BRIGHTNESS とは、照明パラメータ全体の強度を表す値で、`0` ～ `255` の範囲で表します。
`0` で消灯し、 `255` で最大の明るさになります。

## `bpm` 系列
BPM の設定を行います。

### `bpm.set`
* 文法: `bpm.set P1`
  - `P1` : `float` bpm の設定値
  
BPM を `P1` に設定します。ここで設定した BPM 値は、拍カウンタと照明パターンの速度調整に使われます。

### `bpm.increase`
* 文法: `bpm.increase P1`
  - `P1` : `float` BPM の増加値
  
BPM を `P1` だけ増加させます。

### `bpm.decrease`
* 文法: `bpm.decrease P1`
  - `P1` : `float` BPM の減少値
  
BPM を `P1` だけ減少させます。

### `bpm.double`
* 文法: `bpm.double`
  
BPM を現在の設定値の倍に設定します。

### `bpm.half`
* 文法: `bpm.half`
  
BPM を現在の設定値の半分に設定します。


## `beats` 系列
拍カウンタに関する設定を行います。拍情報は primary driver が受け取ることができ、照明パターンの変化・調整に使用され得ます。

### `beats.set`
* 文法: `beats.set P1`
  - `P1` : `int` 拍子の設定値
  
拍子を `P1` 拍子に設定します。

### `beats.align`
* 文法: `beats.align`

拍を次の小節の 1 拍目に設定します。小節カウンタは 1 大きくなり、拍カウンタは 1 に設定されます。

## `pattern` 系列
primary driver に送信するパラメータに関する設定を行います。

### `pattern.bank.set`
* 文法: `pattern.bank.set P1`
  - `P1` : 照明パターンバンクの設定値
  
照明パターンのバンクを変更します。バンクとは、どのようなパターンで照明を制御するかを表す整数値です。

### `pattern.fader.set`
* 文法: `pattern.fader.set P1`
  - `P1` : フェーダーの設定値
  
フェーダーの値を変更します。フェーダーの単位は拍です。`0.0` で即色変更され、`1.0` では1拍ぶんの時間をかけて色が変更されます。この値がどのように使用されるかはprimary driverの実装に依存します。

### `pattern.fader.increase`
* 文法: `pattern.fader.increase P1`
  - `P1` : フェーダーの増加値
  
フェーダーの設定値を、現在の設定値から `P1` だけ増加させます。

### `pattern.fader.decrease`
* 文法: `pattern.fader.decrease P1`
  - `P1` : フェーダーの減少値
  
フェーダーの設定値を、現在の設定値から `P1` だけ減少させます。

## `profile` 系列
プロファイルの設定を行います