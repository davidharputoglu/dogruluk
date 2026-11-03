; Doğruluk v0.1 — installeur Windows (Inno Setup 6)
; Éditeur : David HARPUTOGLU — aidé par IA — kasparof57@gmail.com
; Installation personnalisée : choix de la langue, du répertoire, des composants.
#define MyAppName "Doğruluk"
#define MyAppVersion "0.1"
#define MyAppPublisher "David HARPUTOGLU"
#define MyAppURL "https://github.com/davidharputoglu/dogruluk"

[Setup]
AppId={{B4E1D2F0-9C3A-4D77-8A5E-D06RULUK01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=dogruluk-{#MyAppVersion}-setup
OutputDir=Output
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible arm64
ArchitecturesInstallIn64BitMode=x64compatible arm64
WizardStyle=modern
LicenseFile=..\..\LICENSE
InfoBeforeFile=avant-installation.txt
DisableWelcomePage=no
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\installer\windows\dogruluk.ico
SetupIconFile=dogruluk.ico

[Languages]
; L'utilisateur choisit la langue de l'installeur sur la première page.
; Les .isl manquants dans votre version d'Inno Setup doivent être téléchargés
; via « Tools → Download custom language files » (ou copiés dans compiler:Languages).
Name: "french";       MessagesFile: "compiler:Languages\French.isl"
Name: "english";      MessagesFile: "compiler:Default.isl"
Name: "turkish";      MessagesFile: "compiler:Languages\Turkish.isl"
Name: "german";       MessagesFile: "compiler:Languages\German.isl"
Name: "italian";      MessagesFile: "compiler:Languages\Italian.isl"
Name: "spanish";      MessagesFile: "compiler:Languages\Spanish.isl"
Name: "portuguese";   MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "portuguesebr"; MessagesFile: "compiler:Languages\PortugueseBR.isl"
Name: "arabic";       MessagesFile: "compiler:Languages\Arabic.isl"
; Kazakh et Ouzbek sont disponibles en langage « non Unicode » (Inno Setup 6) :
Name: "kazakh";       MessagesFile: "compiler:Languages\NonUnicode\Kazakh.isl"
Name: "uzbek";        MessagesFile: "compiler:Languages\NonUnicode\Uzbek.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Components]
; Choix personnalisés : cochez/décochez selon vos besoins.
Name: "app";              Description: "Application Doğruluk (code + interface web)"; Flags: fixed; Types: full custom
Name: "app:samples";      Description: "Fichiers d'exemple (liste de prix, factures)"; Types: full
Name: "deps:venv";        Description: "Environnement Python dédié (.venv + dépendances) — recommandé"; Types: full custom
Name: "deps:python";      Description: "Télécharger et installer Python 3.12 embeddable si absent"; Types: full

[Files]
Source: "..\..\*"; DestDir: "{app}"; \
  Excludes: "..\..\..\..\.git\*,..\..\data\*,..\..\exports\*,..\..\tests\*,*.pyc,__pycache__\*"; \
  Components: app; Flags: recursesubdirs ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Components: app; Flags: ignoreversion
Source: "..\..\NOTICE"; DestDir: "{app}"; Components: app; Flags: ignoreversion
Source: "run_portable.bat"; DestDir: "{app}"; Components: app; Flags: ignoreversion
Source: "dogruluk.ico"; DestDir: "{app}\installer\windows"; Components: app; Flags: ignoreversion

[Dirs]
Name: "{app}\data"; Components: app
Name: "{app}\exports"; Components: app

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\run_portable.bat"; \
  Comment: "Démarrer {#MyAppName} (ouvre http://localhost:8000)"; Components: app
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\run_portable.bat"; Tasks: desktopicon; Components: app
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\run_portable.bat"; Tasks: quicklaunchicon; Components: app

[Registry]
; Mémorise la langue choisie pour l'installeur → utilisée au premier lancement de l'app.
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "Language"; \
  ValueData: "{code:GetDetectedLanguageCode}"; Flags: uninsdeletekey

[Run]
Filename: "{app}\run_portable.bat"; \
  Description: "Lancer {#MyAppName} maintenant"; \
  Parameters: "--setup"; Flags: nowait postinstall skipifsilent; Components: app

[UninstallDelete]
Type: filesandordirs; Name: "{app}\.venv"

[Code]
// ---------- Fonctions additionnelles Inno Setup (téléchargement Python) ----------
function GetDetectedLanguageCode(Param: String): String;
begin
  case ActiveLanguage of
    'french':       Result := 'fr';
    'turkish':      Result := 'tr';
    'german':       Result := 'de';
    'italian':      Result := 'it';
    'spanish':      Result := 'es';
    'portuguese',
    'portuguesebr': Result := 'pt';
    'arabic':       Result := 'ar';
    'kazakh':       Result := 'kk';
    'uzbek':        Result := 'uz';
  else
    Result := 'en';
  end;
end;

function PythonFound(): Boolean;
var R: Integer;
begin
  Result := (Exec('cmd.exe', '/c where py', '', SW_HIDE, ewWaitUntilTerminated, R) and (R = 0)) or
            (Exec('cmd.exe', '/c where python', '', SW_HIDE, ewWaitUntilTerminated, R) and (R = 0));
end;

procedure InitializeWizard();
begin
  // Si Python est déjà présent, on décoche l'option de téléchargement.
  if PythonFound() then
    WizardSelectComponents(False, False, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Url, Dest: String;
begin
  if (CurStep = ssPostInstall) and
     IsComponentSelected('deps:python') and (not PythonFound()) then
  begin
    // Téléchargement silencieux de Python 3.12 depuis python.org ;
    // l'utilisateur final valide lui-même l'installeur (Add to PATH coché).
    Url := 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe';
    Dest := ExpandConstant('{tmp}\python-installer.exe');
    if DownloadFile(Url, Dest, 0) then
      Exec(Dest, '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0', '',
           SW_SHOW, ewWaitUntilTerminated, ResultCode)
    else
      MsgBox('Téléchargement de Python impossible. Installez-le manuellement depuis ' +
             'https://www.python.org/downloads/ (cochez "Add python.exe to PATH"), ' +
             'puis lancez run_portable.bat.', mbInformation, MBOK);
  end;
end;
