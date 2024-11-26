# NVDA Add-on for Microsoft Visual studio Code
# Author: Pawel Urbanski <pawel@pawelurbanski.com>, under GPL licence.
# Contains shared code imported by release specific modules.

from enum import Enum
import appModuleHandler
import controlTypes
import globalVars
import speech
from controlTypes import Role, State
from scriptHandler import script
from NVDAObjects import NVDAObject
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible.chromium import Document
from NVDAObjects.behaviors import EditableTextWithoutAutoSelectDetection


class StatusFlags(Enum):
	readVSCodeLine = str.lower(str.strip('readVSCodeLine'))
	readVSCodeEditor = str.lower(str.strip('readVSCodeEditor'))


class VSCodeDocument(Document):
	# The only content in the root document node of Visual Studio code is the application object.
	# Creating a tree interceptor on this object causes a major slow down of Code.
	# Therefore, forcefully block tree interceptor creation.
	_get_treeInterceptorClass = NVDAObject._get_treeInterceptorClass


class CodeEditor(EditableTextWithoutAutoSelectDetection):
	# The main custom class for the editor and editable fields.
	announceNewLineText = False

	def __init__(self):
		# Use unprintable character to prevent speaking.
		self.roleText = chr(4)
		super().__init__()

	def _get_name(self):
		# Conditionally read the name of the file.
		shouldReadName = False
		if hasattr(globalVars, StatusFlags.readVSCodeEditor.value):
			shouldReadName = getattr(globalVars, StatusFlags.readVSCodeEditor.value)
		if shouldReadName:
			return
		else:
			# Use unprintable character to prevent speaking.
			return chr(4)

	def _get_roleText(self):
		# Use unprintable character to prevent speaking.
		return chr(4)

	def _get_states(self):
		# Remove states that are not needed to be announced on every focus.
		# We overwrite a default method for a control that returns states.
		states = super(CodeEditor, self).states
		states.discard(State.AUTOCOMPLETE)
		states.discard(State.MULTILINE)
		return states

	def event_typedCharacter(self, ch: str):
		# Set the flag to allow echoing typed characters.
		if hasattr(globalVars, StatusFlags.readVSCodeLine.value):
			setattr(globalVars, StatusFlags.readVSCodeLine.value, True)
		return super().event_typedCharacter(ch)

	def event_gainFocus(self):
		# Use unprintable character to prevent speaking.
		self.name = chr(4)
		self.roleText = chr(4)
		super().event_gainFocus()

	def event_focusEntered(self):
		# Use unprintable character to prevent speaking.
		self.name = chr(4)
		self.roleText = chr(4)
		super().event_focusEntered()

	def event_loseFocus(self):
		# Use unprintable character to prevent speaking.
		self.name = chr(4)
		self.roleText = chr(4)
		if hasattr(globalVars, StatusFlags.readVSCodeLine.value):
			setattr(globalVars, StatusFlags.readVSCodeLine.value, False)
		super().event_loseFocus()

	def event_valueChange(self):
		# This event is triggered after typing or completion, and other changes.
		# When the editor is focused and the flag is set speech is allowed.
		# Otherwise it is attempted to be canceled, to avoid rereading the line.
		# Gets the flag that allows to bypass speech cancelation.
		shouldReadName = False  # A local convenience variable.
		if hasattr(globalVars, StatusFlags.readVSCodeEditor.value):
			shouldReadName = getattr(globalVars, StatusFlags.readVSCodeEditor.value)
		shouldReadLine = False  # A local convenience variable.
		if hasattr(globalVars, StatusFlags.readVSCodeLine.value):
			shouldReadLine = getattr(globalVars, StatusFlags.readVSCodeLine.value)
		# Read the line after switching tabs or after typing or deletion.
		shouldRead = shouldReadName or shouldReadLine
		if self.hasFocus and shouldRead:
			setattr(globalVars, StatusFlags.readVSCodeLine.value, False)
			setattr(globalVars, StatusFlags.readVSCodeEditor.value, False)
			super().event_valueChange()
		else:
			setattr(globalVars, StatusFlags.readVSCodeLine.value, False)
			setattr(globalVars, StatusFlags.readVSCodeEditor.value, False)
			speech.cancelSpeech()

	@script(gesture='kb:delete', canPropagate=True)
	def script_speakAfterCaretDeleteCharacter(self, gesture):
		# Enable reading the focused cahracter after deletion.
		if hasattr(globalVars, StatusFlags.readVSCodeLine.value):
			setattr(globalVars, StatusFlags.readVSCodeLine.value, True)
		self.script_caret_deleteCharacter(gesture)

	@script(gesture='kb:control+delete', canPropagate=True)
	def script_speakAfterCaretDeleteWord(self, gesture):
		# Enable reading the focused cahracter after deletion.
		if hasattr(globalVars, StatusFlags.readVSCodeLine.value):
			setattr(globalVars, StatusFlags.readVSCodeLine.value, True)
		self.script_caret_deleteWord(gesture)


class CustomListItem(IAccessible):

	def __init__(self):
		# Set the role label text for braille to an empty string.
		self.roleText = chr(4)
		self.roleTextBraille = chr(4)
		super().__init__()

	def _get_states(self):
		# Remove states that are not needed to be announced on every focus.
		# We overwrite a default method for a control that returns states.
		states = super(CustomListItem, self).states
		states.discard(State.SELECTABLE)
		states.discard(State.SELECTED)
		return states


class CustomTreeviewItem(IAccessible):

	def _get_states(self):
		# Remove states that are not needed to be announced on every focus.
		# We overwrite a default method for a control that returns states.
		states = super(CustomTreeviewItem, self).states
		states.discard(State.SELECTABLE)
		return states


class AppModule(appModuleHandler.AppModule):

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		# It will prevent speaking the treeview type on every focus.
		controlTypes.silentRolesOnFocus.add(Role.TREEVIEW)
		self.shouldSpeak: bool = False
		# It is declared on a module scope to not be reset within a editor class.
		# Set this flag to allow or cancel reading the line.
		# It mostly applies to the code completion.
		if not hasattr(globalVars, StatusFlags.readVSCodeLine.value):
			setattr(globalVars, StatusFlags.readVSCodeLine.value, True)
		# Allow to read the editor file name after focus changes.
		if not hasattr(globalVars, StatusFlags.readVSCodeEditor.value):
			setattr(globalVars, StatusFlags.readVSCodeEditor.value, True)

	def event_NVDAObject_init(self, obj):
		# Assign a custom list class to the code completion item only.
		roleIsList = obj.role == Role.LIST
		classIsList = "monaco-list" in str(obj.IA2Attributes.get("class"))
		nameIsSuggest = str(obj.name).lower() == "suggest"
		if (roleIsList and classIsList and nameIsSuggest):
			obj.name = chr(4)
			obj.roleText = chr(4)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(AppModule, self).chooseNVDAObjectOverlayClasses(obj, clsList)
		# Overwrite the tree interceptor class.
		if Document in clsList and obj.IA2Attributes.get("tag") == "#document":
			clsList.insert(0, VSCodeDocument)
		# Overwrite the standard editor class with a custom for Visual Studio Code.
		isElectron = obj.windowClassName == "Chrome_RenderWidgetHostHWND"
		roleIsEditableText = obj.role == Role.EDITABLETEXT
		stateIsMultiline = State.MULTILINE in obj.states
		isInputArea = 'inputarea' in str(obj.IA2Attributes.get('class'))
		if (isElectron and roleIsEditableText and stateIsMultiline or isInputArea):
			clsList.insert(0, CodeEditor)
		# Assign a custom list item class to the code completion item only.
		if (obj.role == Role.LISTITEM and 'monaco-list-row' in str(obj.IA2Attributes.get("class"))):
			clsList.insert(0, CustomListItem)
		if (obj.role == Role.TREEVIEWITEM):
			clsList.insert(0, CustomTreeviewItem)

	def script_fixFocus(self, gesture):
		# Send escape key to the application
		# We must capture escape to prevent losing focus when canceling completion.
		gesture.send()

	def script_shouldSpeakEditorName(self, gesture):
		# Allow to read the tab file name after focus changes, or tab switching.
		if hasattr(globalVars, StatusFlags.readVSCodeEditor.value):
			setattr(globalVars, StatusFlags.readVSCodeEditor.value, True)
		gesture.send()

	__gestures = {
		'kb:escape': script_fixFocus,
		'kb:control+tab': script_shouldSpeakEditorName,
		'kb:shift+control+tab': script_shouldSpeakEditorName,
		'kb:alt+1': script_shouldSpeakEditorName,
		'kb:alt+2': script_shouldSpeakEditorName,
		'kb:alt+3': script_shouldSpeakEditorName,
		'kb:alt+4': script_shouldSpeakEditorName,
		'kb:alt+5': script_shouldSpeakEditorName,
		'kb:alt+6': script_shouldSpeakEditorName,
		'kb:alt+7': script_shouldSpeakEditorName,
		'kb:alt+8': script_shouldSpeakEditorName,
		'kb:alt+9': script_shouldSpeakEditorName,
	}

	def terminate(self):
		# Add back TREVIEW and TREEVIEWITEM to roles spoken on focus.
		controlTypes.silentRolesOnFocus.discard(Role.TREEVIEW)
		# Remove the custom class attribute.
		delattr(globalVars, StatusFlags.readVSCodeLine.value)
		delattr(globalVars, StatusFlags.readVSCodeEditor.value)
