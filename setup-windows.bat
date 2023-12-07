@ECHO OFF
REM
REM SecondLF Windows�����Z�b�g�A�b�v�X�N���v�g
REM
REM (C) 2023 /\/asTTY
REM

:START_SETUP
python --version
IF %ERRORLEVEL%==0 GOTO PYTHON_CONFIRMED
python3 --version
IF %ERRORLEVEL%==0 GOTO PYTHON3_CONFIRMED

ECHO (E1) Python ���Ăяo���܂���
PAUSE
EXIT /B

:PYTHON_CONFIRMED
echo @call app.bat python > start-windows.bat
GOTO STARTBAT_SET

:PYTHON3_CONFIRMED
echo @call app.bat python3 > start-windows.bat
DOSKEY PYTHON=PYTHON3
GOTO STARTBAT_SET

:STARTBAT_SET
python -c "import sys;sys.exit(0 if (sys.version_info[0]==3 and sys.version_info[1] >= 8) else 2)"
IF %ERRORLEVEL%==0 GOTO PYTHON_VER_CONFIRMED

ECHO (E2) Python �̃o�[�W�������K�����܂���
PAUSE
EXIT /B

:PYTHON_VER_CONFIRMED
python -m pip --version
IF %ERRORLEVEL%==0 GOTO PIP_CONFIRMED


ECHO (E3) pip ���Ăяo���܂���/���삪����������܂���

:PIP_CONFIRMED
python -m pip install pyserial
IF NOT %ERRORLEVEL%==0 GOTO PIP_ERROR
python -m pip install pygame
IF NOT %ERRORLEVEL%==0 GOTO PIP_ERROR

ECHO (SC) �Z�b�g�A�b�v���������܂���
PAUSE
EXIT /B

:PIP_ERROR
ECHO (E4) pip install�Ɏ��s���܂���
PAUSE
EXIT /B