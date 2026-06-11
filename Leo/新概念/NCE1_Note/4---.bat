@echo off
for /L %%i in (18,1,140) do (
    type nul > "NCE1-L%%i.md"
)
pause