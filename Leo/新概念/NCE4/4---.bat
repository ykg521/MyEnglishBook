@echo off
for /L %%i in (1,1,48) do (
    type nul > "4-%%i.md"
)
pause