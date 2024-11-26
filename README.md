# NVDA Add-on For the Microsoft Visual Studio Code

This NVDA add-on provides fixes and improvements mostly for the editor component of the Microsoft Visual Studio Code editor. Please note that Microsoft Visual Studio Code is not a Microsoft Visual Studio IDE. It is a lightweight code editor.

The add-on is in maintenance mode, developed on the best effort basis. Changes are introduced only when something serious is broken, or the implementation of improvements requires little effort. The author is looking for the new maintainer, whom he will introduce to the design and help in transition.

## Features of this add-on

* The add-on supports all the editions, including: stable, insider, or local development,
* Provides filtering of states that make speech output unnecessarily verbose,
* Canceling reading the entire line from the beginning after completion is attempted, subject to certain limitations.

## Additional notes and issues

* Keeping Visual Studio Code updated brings many improvements for the team is actively improving its accessibility,
* Microsoft Visual Studio Code is based on Chrome Electron , which lets create standalone applications based on JavaScript and HTML components. Therefore, it behaves alot like a web application.
* The editor is a large textarea field. The content of that textarea is updated by Visual Studio Code specifically to enable screen reader support. It is a temporary work-around, for the wai-aria features, which would allow for native handling of the regular editor component are not yet fully implemented by Chrome Electron.
* The mentioned updates cause occasional speaking of the entire line after completion, due to additional edits performed by the editor.
