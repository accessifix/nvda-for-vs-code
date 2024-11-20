# NVDA Add-on for Microsoft Visual studio Code
# Author: Pawel Urbanski <pawel@pawelurbanski.com>, under GPL licence.
# Contains shared code imported by release specific modules.

import appModuleHandler
import controlTypes
import globalVars
import speech
from controlTypes import Role, State
from scriptHandler import script
from NVDAObjects import NVDAObject
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible.chromium import Document
from NVDAObjects.IAccessible import EditableTextWithAutoSelectDetection as BaseEditor


class VSCodeDocument(Document):
	# The only content in the root document node of Visual Studio code is the application object.
	# Creating a tree interceptor on this object causes a major slow down of Code.
	# Therefore, forcefully block tree interceptor creation.
	_get_treeInterceptorClass = NVDAObject._get_treeInterceptorClass


class CodeEditor(BaseEditor):
	announceNewLineText = False

	def __init__(self):
		# Use unprintable character to prevent speaking.
		self.name = chr(4)
		self.roleText = None
		super().__init__()

	def _get_name(self):
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
		self.appModule.shouldSpeak = True
		return super().event_typedCharacter(ch)

	def event_gainFocus(self):
		self.roleText = None
		# Use unprintable character to prevent speaking.
		self.name = chr(4)
		speech.cancelSpeech()
		super().event_gainFocus()
		self.initAutoSelectDetection()

	def event_focusEntered(self):
		self.roleText = None
		# Use unprintable character to prevent speaking.
		self.name = chr(4)
		speech.cancelSpeech()
		super().event_focusEntered()

	def event_valueChange(self):
		# This event is triggered after typing or completion, and other changes.
		# When the editor is focused and the flag is set sppech is allowed.
		# Otherwise it is attempted to be canceled, to avoid rereading the line.
		if self.hasFocus and self.appModule.shouldSpeak:
			self.appModule.shouldSpeak = False
			return
		else:
			speech.cancelSpeech()
		super().event_valueChange()
		if self.hasFocus and self.appModule.shouldSpeak:
			self.appModule.shouldSpeak = False
			return
		else:
			speech.cancelSpeech()


class CustomListItem(IAccessible):
	# A custom list item for code completion values.
	# Remove states that are not needed to be announced on every focus.
	# We overwrite a default method for a control that returns states.
	def _get_states(self):
		states = super(CustomListItem, self).states
		states.discard(State.SELECTABLE)
		states.discard(State.SELECTED)
		return states

	def __init__(self):
		# Set the role label text for braille to an empty string.
		self.roleText = None
		self.roleTextBraille = None
		super().__init__()


class CustomTreeviewItem(IAccessible):

	def _get_states(self):
		# Remove states that are not needed to be announced on every focus.
		# We overwrite a default method for a control that returns states.
		states = super(CustomTreeviewItem, self).states
		states.discard(State.SELECTABLE)
		return states


class AppModule(appModuleHandler.AppModule):

	def __init__(self, *args, **kwargs):
		self.shouldSpeak: bool = False
		super(AppModule, self).__init__(*args, **kwargs)
		# It will prevent speaking the type on every focus.
		controlTypes.silentRolesOnFocus.add(Role.TREEVIEW)

	# It is declared on a module scope to not be reset within a editor class.
	# The normalized name of the last focused editor.
		if not hasattr(globalVars, 'lastEditorName'):
			setattr(globalVars, 'lastEditorName', 'Editor')

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

	@script(gesture="kb:escape")
	def script_FixFocus(self, gesture):
		# Send escape key to the application
		# We must capture escape to prevent losing focus when leaving completion.
		gesture.send()

	def terminate(self):
		# Add back TREVIEW and TREEVIEWITEM to roles spoken on focus.
		controlTypes.silentRolesOnFocus.discard(Role.TREEVIEW)
