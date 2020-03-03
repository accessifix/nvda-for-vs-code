# NVDA Add-on For Microsoft Visual Studio Code

This NVDA add-on provides fixes and improvements mostly for the editor component of the Microsoft Visual Studio Code development environment.
Please note that Microsoft Visual Studio Code is not a Microsoft Visual Studio IDE. It is a lightweight code editor with very advanced features.

## Features of this add-on

* Keeping focus in the editor - preventing switching off forms mode after pressing escape to leave intelisense or cancel some other operation,
* Use NVDA key + space to leave forms mode when you need it,
* Handling completion of intelisense items, without reading the entire current line,
* Providing a settings.json file with settings, that should improve the coding experience,
* Place it in the c:\Users\<YourUsername>\appdata\roaming\(code or code - insiders)\user folder.

## Additional notes and issues

Microsoft Visual Studio Code is based on Chrome Electron , which lets create standalone applications based on JavaScript and HTML components. Therefore, it behaves alot like a web application.
The editor is a large textarea field. The content of that textarea is updated by Visual Studio Code specifically to enable screen reader support. It is a temporary work-around, for the wai-aria features, which would allow for native handling of the regular editor component are not yet fully implemented by Chrome Electron.
