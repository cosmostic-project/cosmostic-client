#define AppName "COSMOSTIC"
#define AppVersion "1.0"
#define AppPublisher "COSMOSTIC"
#define AppURL "https://cosmostic.letz.dev/"
#define AppExeName "cosmostic.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={userappdata}\{#AppName}
UsePreviousAppDir=no
DisableDirPage=yes
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#AppExeName}
OutputBaseFilename=cosmostic_setup
SetupIconFile=logo.ico
WizardSmallImageFile=logo.bmp
WizardImageFile=logo.bmp
WizardImageStretch=no
CloseApplications=force
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{tmp}\{#AppExeName}"; DestDir: "{app}"; Flags: external

[Run]
Filename: "{cmd}"; Parameters: "/c echo 127.0.0.1 s.optifine.net >> {sys}\Drivers\Etc\Hosts"; Flags: nowait runhidden
Filename: "{cmd}"; Parameters: "/c schtasks /create /tn {#AppName} /tr {%|%22}{cmd} /c start /d {app} {app}\{#AppExeName}{%|%22} /sc onlogon /ru {username} /f"; Flags: waituntilterminated runhidden
Filename: "{cmd}"; Parameters: "/c schtasks /run /tn {#AppName}"; Flags: nowait runhidden

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c taskkill /im {#AppExeName} /t /f"; Flags: waituntilterminated runhidden
Filename: "{cmd}"; Parameters: "/c powershell /c {%|%22}(Get-Content {sys}\Drivers\Etc\Hosts) -replace '127.0.0.1 s.optifine.net', '' | Set-Content {sys}\Drivers\Etc\Hosts{%|%22}"; Flags: nowait runhidden
Filename: "{cmd}"; Parameters: "/c schtasks /delete /tn {#AppName} /f"; Flags: nowait runhidden

[UninstallDelete]
Type: files; Name: "{app}\cosmostic.log"
Type: filesandordirs; Name: "{app}\cache"

[Code]
var
  DownloadPage: TDownloadWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    DownloadPage.Add('https://github.com/cosmostic-project/cosmostic-client/releases/latest/download/cosmostic_client.exe', '{#AppExeName}', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        Result := True;
      except
        if DownloadPage.AbortedByUser then
          Log('Aborted by user.')
        else
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end else
    Result := True;
end;
