[Setup]
AppName=DUKON POS Kassa Tizimi
AppVersion=1.0
DefaultDirName={autopf}\DUKON_POS
DefaultGroupName=DUKON POS
OutputDir=Output
OutputBaseFilename=DUKON_POS_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Loyihadagi barcha fayllarni o'rnatuvchi ichiga yig'adi
Source: "C:\Users\user\PYCHARM\DO'KON\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DUKON POS"; Filename: "{app}\ishga_tushirish.bat"
Name: "{autodesktop}\DUKON POS"; Filename: "{app}\ishga_tushirish.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\ishga_tushirish.bat"; Description: "{cm:LaunchProgram,DUKON POS}"; Flags: shellexec postinstall skipifsilent