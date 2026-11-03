; Doğruluk v0.1 — installeur Windows (Inno Setup 6)
; Éditeur : David HARPUTOGLU — aidé par IA — kasparof57@gmail.com
#define MyAppName "Doğruluk"
#define MyAppVersion "0.1"
#define MyAppPublisher "David HARPUTOGLU"
#define MyAppURL "https://github.com/davidharputoglu/dogruluk"
#define MyAppExeName "dogruluk.exe"

[Setup]
AppId={{B4E1D2F0-9C3A-4D77-8A5E-DOGRULUK01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\dogruluk
DefaultGroupName={#MyAppName}
OutputBaseFilename=dogruluk-{#MyAppVersion}-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
LicenseFile=..\..\LICENSE
InfoAfterPage=yes
PrivilegesRequired=admin

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer une raccourci sur le Bureau"

[Files]
Source: "..\..\*"; DestDir: "{app}"; \
  Excludes: "..\..\.git\*,..\..\data\*,..\..\exports\*,..\..\tests\*,*.pyc"; \
  Flags: recursesubdirs ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\NOTICE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\scripts\run_windows.bat"; \
  Comment: "Démarrer {#MyAppName} (ouvre http://localhost:8000)"
Name: "{group}\Mentions légales"; Filename: "{#MyAppURL}"
Name: "{group}\Licence"; Filename: "{app}\LICENSE"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\scripts\run_windows.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\scripts\run_windows.bat"; Description: "Lancer {#MyAppName} maintenant"; \
  Flags: nowait postinstall skipifsilent

[Code]
// Avertissement si Python absent : la version portable nécessite Python 3.10+.
procedure CurStepChanged(CurStep: TSetupStep);
var R: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    R := Exec('cmd.exe', '/c where python', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    if ResultCode <> 0 then
      MsgBox('Python n''a pas été détecté.' + #13#10 +
             'Installez Python 3.10+ depuis https://www.python.org/downloads/' + #13#10 +
             '(cochez "Add python.exe to PATH") puis lancez scripts\run_windows.bat.',
             mbInformation, MBOK);
  end;
end;
