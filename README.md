# NVDA Add-on For Microsoft Visual Studio Code

This NVDA add-on provides fixes and improvements mostly for the editor component of the Microsoft Visual Studio Code development environment.
Please note that Microsoft Visual Studio Code is not a Microsoft Visual Studio IDE. It is a lightweight code editor with very advanced features.

## Features of this add-on

* Keeping focus in the editor - preventing switching off forms mode after pressing escape to leave intelisense or cancel some other operation,
* Use NVDA key + space to leave forms mode when you need it,
* Handling completion of intelisense items, and reading only the inserted item, without reading the entire current line,
* Providing a settings.json file with settings, that should improve the experience,
* Place it in the c:\Users\<YourUsername>\appdata\roaming\(code or code - insiders)\user folder.

## Additional notes and issues

Microsoft Visual Studio Code is based on Chrome Electron , which lets create standalone applications based on JavaScript and HTML components. Therefore, it behaves alot like a web application.
The editor is a large textarea field. The content of that textarea is updated by Visual Studio Code specifically to enable screen reader support. It is a temporary work-around, for the wai-aria features, which would allow for native ahnding of the regular editor component are not yet fully implemented by Chrome Electron.
Specifically the Intelisense, also known as code completion works by providing the suggested items ina form of an alert read by NVDA and other screen readers. It is not yet possible to schroll up and down with just an arrow up or down key through the lsit of suggestions. You can do it by using a combination of a control + up / down key. The items will be read aloud, but not shown on a braille display.