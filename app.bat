@echo off
echo 注: このウィンドウを閉じるとコントローラーが終了します
echo WARN: Closing this window will cause TERMINATION of the controller app.
echo.
%1 secondlf.py

IF NOT %ERRORLEVEL% == 0 pause